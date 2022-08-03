import argparse
import logging
import os
import sys
from typing import Any, Callable, Dict, Tuple

from python_terraform import IsFlagged, IsNotFlagged, Terraform

from multi_region_data import MultiRegionData, load_multi_region_data

log = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=logging.INFO, filename="multiregion.log"
)

EX_OK: int = 0  # exit code for successful command
EX_FAILED: int = 1  # exit  code for failed command

DEFAULT_MULTI_REGION_DATA_FILE: str = "multi_region_data.ini"

TerraformVars = Dict[str, Any]  # variables passed in terraform plan/apply/destroy call
TerraformAction = Callable[[Terraform, TerraformVars], bool]  # terraform plan/apply/destroy


def validate_multi_region_data(data: MultiRegionData) -> bool:
    if not data.plan_id:
        print_log("plan_id is required.")
        return False
    if not data.external_id:
        print_log("external_id is required.")
        return False
    for region in data.regions:
        if not region.aws_region_name:
            print_log("region is required.")
            return False
    return True


def execute_action(action: TerraformAction, data: MultiRegionData) -> bool:
    """Execute an action for every region"""

    if not validate_multi_region_data(data):
        return False

    t_bucket = Terraform(working_dir="bucket/")
    bucket_region_name = []
    bucket_arn_list = []
    execution_success = True
    tf_vars: Dict[str, Any] = {}

    # invoke action for each region on terraform configuration located in bucket/
    for region in data.regions:
        print_log(f"Region: {region.aws_region_name}")
        tf_vars = {
            "region": region.aws_region_name,
            "s3_bucket_prefix": region.s3_bucket_prefix,
            # "create_cloudexport": False
        }

        if not (prepare_workspace(t_bucket, region.aws_region_name) and action(t_bucket, tf_vars)):
            return False

        if t_bucket.output().get("kentik_bucket_name") and t_bucket.output()["kentik_bucket_name"].get("value"):
            for bucket_name in t_bucket.output()["kentik_bucket_name"]["value"]:
                bucket_region_name.append([region.aws_region_name, bucket_name])
        if t_bucket.output().get("kentik_bucket_arn_list") and t_bucket.output()["kentik_bucket_arn_list"].get("value"):
            bucket_arn_list.extend(t_bucket.output()["kentik_bucket_arn_list"]["value"])

    # invoke action on terraform configuration located in cloud_iam/
    t_cloud_iam = Terraform(working_dir="cloud_iam/")
    tf_vars = {
        "region": data.regions[0].aws_region_name,  # used only in provider region
        "plan_id": data.plan_id,
        "external_id": data.external_id,
        "bucket_region_name": bucket_region_name,
        "bucket_arn_list": bucket_arn_list,
    }
    if not action(t_cloud_iam, tf_vars):
        execution_success = False

    return execution_success


def prepare_workspace(t: Terraform, workspace: str) -> bool:
    """Create or just switch workspace"""

    log.info('Preparing Terraform workspace "%s"', workspace)

    # try switch to workspace
    return_code, _, _ = t.set_workspace(workspace)
    if return_code == EX_OK:
        log.info("Workspace activated")
        return True

    # probably no such workspace exists, try to create it
    return_code, stdout, stderr = t.create_workspace(workspace)
    if return_code == EX_OK:
        log.info("Workspace created and activated")
        return True

    # failure
    report_tf_output(return_code, stdout, stderr)
    return False


def action_plan(t: Terraform, tf_vars: TerraformVars) -> bool:
    """TerraformAction"""

    print_log("Terraform plan...")
    code, stdout, stderr = t.plan(detailed_exitcode=IsNotFlagged, var=tf_vars)
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


def action_apply(t: Terraform, tf_vars: TerraformVars) -> bool:
    """TerraformAction"""

    print_log("Terraform apply...")
    code, stdout, stderr = t.apply(skip_plan=True, var=tf_vars)  # skip_plan means auto-approve
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


def action_destroy(t: Terraform, tf_vars: TerraformVars) -> bool:
    """TerraformAction"""

    print_log("Terraform destroy...")
    code, stdout, stderr = t.apply(destroy=IsFlagged, skip_plan=True, var=tf_vars)  # auto-approve
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


def report_tf_output(return_code: int, stdout: str, stderr: str) -> None:
    """Report Terraform operation result to the user"""

    if stdout:
        print_log(stdout.strip())

    if stderr:
        print_log(stderr.strip(), file=sys.stderr, level=logging.ERROR)

    if return_code == EX_OK:
        print_log("Terraform action successful")
    elif return_code == EX_FAILED:
        print_log("Terraform action FAILED", file=sys.stderr, level=logging.ERROR)
    else:
        # Terraform uses codes > 1 for reporting detailed status, eg. for resource configuration diff to be applied
        print_log("Terraform action successful, return code: ", return_code)

    print_log()


def parse_cmd_line() -> Tuple[TerraformAction, str]:
    ACTIONS = {"plan": action_plan, "apply": action_apply, "destroy": action_destroy}
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "apply", "destroy"], help="Terraform step to execute")
    parser.add_argument("--filename", default=DEFAULT_MULTI_REGION_DATA_FILE, help="Input data file name")
    args = parser.parse_args()
    return ACTIONS[args.action], args.filename


def load_multi_regions_or_exit(file_path: str) -> MultiRegionData:
    """
    Return MultiRegionData list on success
    Exit with code FAILED when file not found or file reading error
    """

    if not os.path.exists(file_path):
        print_log(f"File '{file_path}' doesn't exist", file=sys.stderr, level=logging.FATAL)
        sys.exit(EX_FAILED)

    try:
        return load_multi_region_data(file_path)

    except (ValueError, TypeError) as err:
        log.exception("Failed to read input file '%d'", file_path)
        print(err, file=sys.stderr)
        sys.exit(EX_FAILED)


def print_log(msg: str = "", level: int = logging.INFO, file=sys.stdout) -> None:
    print(msg, file=file)
    log.log(level=level, msg=msg)


if __name__ == "__main__":
    terraform_action, multi_regions_file = parse_cmd_line()
    multi_region_data = load_multi_regions_or_exit(multi_regions_file)
    execution_successful = execute_action(terraform_action, multi_region_data)
    exit_code = EX_OK if execution_successful else EX_FAILED
    sys.exit(exit_code)
