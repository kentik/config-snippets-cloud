import argparse
import logging
import os
import sys
from typing import Any, Callable, Dict, List, Tuple

from python_terraform import IsFlagged, IsNotFlagged, Terraform

from azure_cli import az_cli
from profiles import AzureProfile, load_complete_profiles

log = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s", level=logging.INFO, filename="onboarder.log"
)

EX_OK: int = 0  # exit code for successful command
EX_FAILED: int = 1  # exit  code for failed command

DEFAULT_PROFILES_FILE_NAME: str = "profiles.ini"


TerraformVars = Dict[str, Any]  # variables passed in terraform plan/apply/destroy call
TerraformAction = Callable[[Terraform, TerraformVars], bool]  # terraform plan/apply/destroy


def execute_action(action: TerraformAction, profiles: List[AzureProfile]) -> bool:
    """Execute an action for every profile"""

    t = Terraform()
    successful_count = 0
    for profile in profiles:
        print_log(f'Profile: "{profile.name}" ({profile.location})')

        tf_vars = {
            "subscription_id": profile.subscription_id,
            "tenant_id": profile.tenant_id,
            "principal_id": profile.principal_id,
            "principal_secret": profile.principal_secret,
            "location": profile.location,
            "resource_group_names": profile.resource_group_names,
            "storage_account_names": profile.storage_account_names,
        }

        if azure_login(profile) and prepare_workspace(t, profile.name) and action(t, tf_vars):
            successful_count += 1

    azure_logout()

    print_log(f"Terraform action successfully executed for {successful_count}/{len(profiles)} Azure profile(s).")
    return successful_count == len(profiles)


def azure_login(profile: AzureProfile) -> bool:
    """az login is required prior to calling terraform: "get_nsg.py" uses Azure CLI to gather Network Security Group names"""

    command = f"login --service-principal -u {profile.principal_id} -p {profile.principal_secret} --tenant {profile.tenant_id}"  # returns a list
    output_list = az_cli(command)
    if not isinstance(output_list, list):
        print_log(
            f"Failed to login to Azure account using profile '{profile.name}' credentials",
            file=sys.stderr,
            level=logging.ERROR,
        )
        return False

    log.info("Logged into Azure account using profile '%s' credentials", profile.name)
    return True


def azure_logout() -> None:
    az_cli("logout")


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
    parser.add_argument("--filename", default=DEFAULT_PROFILES_FILE_NAME, help="Profiles file name")
    args = parser.parse_args()
    return (ACTIONS[args.action], args.filename)


def load_profiles_or_exit(file_path: str) -> List[AzureProfile]:
    """
    Return profile list on success
    Exit with code FAILED when file not found or file reading error
    """

    if not os.path.exists(file_path):
        print_log(f"File '{file_path}' doesn't exist", file=sys.stderr, level=logging.FATAL)
        sys.exit(EX_FAILED)

    try:
        return load_complete_profiles(file_path)
    except RuntimeError as err:
        log.exception(err)
        print(f"Failed to read profiles file '{file_path}'", file=sys.stderr)
        sys.exit(EX_FAILED)


def print_log(msg: str = "", level: int = logging.INFO, file=sys.stdout) -> None:
    print(msg, file=file)
    log.log(level=level, msg=msg)


if __name__ == "__main__":
    terraform_action, profiles_file_name = parse_cmd_line()
    azure_profiles = load_profiles_or_exit(profiles_file_name)
    execution_successful = execute_action(terraform_action, azure_profiles)
    exit_code = EX_OK if execution_successful else EX_FAILED
    sys.exit(exit_code)
