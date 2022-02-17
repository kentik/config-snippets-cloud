import argparse
import logging
import os
import sys
from typing import Any, Callable, Dict, List, Tuple

from python_terraform import IsFlagged, IsNotFlagged, Terraform

from azure_cli import az_cli
from profiles import AzureProfile, load_profiles

log = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)

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
        print(f'Profile: "{profile.name}" ({profile.location})')

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

    print(f"Terraform action successfully executed for {successful_count}/{len(profiles)} Azure profile(s).")
    return successful_count == len(profiles)


def azure_login(profile: AzureProfile) -> bool:
    """az login is required prior to calling terraform: "get_nsg.py" uses Azure CLI to gather Network Security Group names"""

    command = f"login --service-principal -u {profile.principal_id} -p {profile.principal_secret} --tenant {profile.tenant_id}"  # returns a list
    output_list = az_cli(command)
    if not isinstance(output_list, list):
        log.error("Failed to login to Azure account using profile '%s' credentials", profile.name)
        return False
    return True


def azure_logout() -> None:
    az_cli("logout")


def prepare_workspace(t: Terraform, workspace: str) -> bool:
    """Create or just switch workspace"""

    log.info('Preparing TF workspace "%s"', workspace)

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

    code, stdout, stderr = t.plan(detailed_exitcode=IsNotFlagged, var=tf_vars)
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


def action_apply(t: Terraform, tf_vars: TerraformVars) -> bool:
    """TerraformAction"""

    code, stdout, stderr = t.apply(skip_plan=True, var=tf_vars)  # skip_plan means auto-approve
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


def action_destroy(t: Terraform, tf_vars: TerraformVars) -> bool:
    """TerraformAction"""

    code, stdout, stderr = t.apply(destroy=IsFlagged, skip_plan=True, var=tf_vars)  # auto-approve
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


def report_tf_output(return_code: int, stdout: str, stderr: str) -> None:
    if stdout:
        print(stdout.strip())

    if stderr:
        print(stderr.strip(), file=sys.stderr)

    if return_code == EX_OK:
        print("Success")
    elif return_code == EX_FAILED:
        print("FAILED", file=sys.stderr)
    else:
        print("Return code: ", return_code)  # Terraform uses codes > 1 for reporting detailed status

    print()


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
        print(f"File '{file_path}' doesn't exist")
        sys.exit(EX_FAILED)

    profiles = load_profiles(file_path)
    if profiles is None:
        print(f"Failed to read profiles file '{file_path}'")
        sys.exit(EX_FAILED)

    return profiles


if __name__ == "__main__":
    terraform_action, profiles_file_name = parse_cmd_line()
    azure_profiles = load_profiles_or_exit(profiles_file_name)
    execution_successful = execute_action(terraform_action, azure_profiles)
    exit_code = EX_OK if execution_successful else EX_FAILED
    sys.exit(exit_code)
