import argparse
import configparser
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple

from az.cli import az
from python_terraform import IsFlagged, IsNotFlagged, Terraform

log = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)
EX_OK: int = 0  # exit code for successful command
EX_FAILED: int = 1  # exit  code for failed command
PROFILES_FILE: str = "profiles.ini"


# pylint: disable=too-many-instance-attributes
@dataclass
class AzureProfile:
    name: str
    subscription_id: str
    tenant_id: str
    principal_id: str
    principal_secret: str
    location: str
    resource_group_names: List[str]
    storage_account_names: List[str]


TerraformVars = Dict[str, Any]  # variables passed in terraform plan/apply/destroy call
TerraformAction = Callable[[Terraform, TerraformVars], bool]  # terraform plan/apply/destroy

# execute an action for every profile
def execute_action(action: TerraformAction, profiles: List[AzureProfile]) -> bool:
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

        if prepare_workspace(t, profile.name) and azure_login(profile) and action(t, tf_vars):
            successful_count += 1

    if successful_count > 0:
        azure_logout()

    print(f"Terraform action successfully executed for {successful_count}/{len(profiles)} Azure profile(s).")
    return successful_count == len(profiles)


# az login is required prior to calling terraform: "get_nsg.py" uses Azure CLI to gather Network Security Group names
def azure_login(profile: AzureProfile) -> bool:
    azure_login_command = f"login --service-principal -u {profile.principal_id} -p {profile.principal_secret} --tenant {profile.tenant_id}"
    return_code, _, logs = az(azure_login_command)
    if return_code != EX_OK:
        log.warning(
            "Failed to sign into Azure using profile '%s' credentials. Skipping profile. Error message: '%s'",
            profile.name,
            logs,
        )
        return False
    return True


def azure_logout() -> None:
    az("logout")


# create or just switch workspace
def prepare_workspace(t: Terraform, workspace: str) -> bool:
    print(f'Preparing TF workspace "{workspace}"')

    # try switch to workspace
    return_code, _, _ = t.set_workspace(workspace)
    if return_code == EX_OK:
        print("Workspace activated")
        return True

    # probably no such worskpace exists, try to create it
    return_code, stdout, stderr = t.create_workspace(workspace)
    if return_code == EX_OK:
        print("Workspace created and activated")
        return True

    # failure
    report_tf_output(return_code, stdout, stderr)
    return False


# TerraformAction
def action_plan(t: Terraform, tf_vars: TerraformVars) -> bool:
    code, stdout, stderr = t.plan(detailed_exitcode=IsNotFlagged, var=tf_vars)
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


# TerraformAction
def action_apply(t: Terraform, tf_vars: TerraformVars) -> bool:
    code, stdout, stderr = t.apply(skip_plan=True, var=tf_vars)  # skip_plan means auto-approve
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


# TerraformAction
def action_destroy(t: Terraform, tf_vars: TerraformVars) -> bool:
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


def get_azure_profiles() -> List[AzureProfile]:
    # configparser.read silently ignores the fact that ini file doesn't exist, so need to check manually
    if not os.path.exists(PROFILES_FILE):
        log.fatal("Azure profiles input file '%s' doesn't exists", PROFILES_FILE)
        sys.exit(EX_FAILED)

    config = configparser.ConfigParser()
    try:
        config.read(PROFILES_FILE)
    except configparser.Error as err:
        log.fatal("Error reading Azure profiles file '%s'. Error message: '%s'", PROFILES_FILE, str(err))
        sys.exit(EX_FAILED)

    output_profiles: List[AzureProfile] = []
    available_profiles: List[str] = [p for p in config.keys() if p != "DEFAULT"]  # skip ini file "DEFAULT" section
    for profile_name in available_profiles:
        profile = config[profile_name]
        try:
            resource_groups, storage_accounts = get_resource_groups_and_storage_accounts(profile_name, dict(profile))
            azure_profile = AzureProfile(
                name=profile_name,
                subscription_id=profile["subscription_id"],
                tenant_id=profile["tenant_id"],
                location=profile["location"],
                resource_group_names=resource_groups,
                storage_account_names=storage_accounts,
                principal_id=profile["principal_id"],
                principal_secret=profile["principal_secret"],
            )
        except KeyError as err:
            log.warning("Error reading profile data '%s'. Profile skipped. Error message: '%s'", profile_name, str(err))
            continue
        output_profiles.append(azure_profile)

    return output_profiles


def get_resource_groups_and_storage_accounts(name: str, profile: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    split_names = lambda names: [name.strip() for name in names.split(",")] if names else []

    # get resource groups and storage accounts
    resource_groups = split_names(profile["resource_group_names"])  # required
    storage_accounts = split_names(profile.get("storage_account_names", ""))  # optional

    # if storage_accounts are specified, there should be a Storage Account name specified for every Resource Group name
    if storage_accounts and len(storage_accounts) != len(resource_groups):
        log.warning(
            "In profile '%s', 'storage_account_names' is specified but has different item count than 'resource_group_names'. Ignoring",
            name,
        )
        return (resource_groups, [])

    # Storage Account names should meet Azure Storage Account naming restrictions
    valid_names = map(is_valid_azure_storage_account_name, storage_accounts)
    if not all(valid_names):
        log.warning(
            "In profile '%s', 'storage_account_names' is specified but does not meet Azure Storage Account naming restrictions. Ignoring",
            name,
        )
        return (resource_groups, [])

    return (resource_groups, storage_accounts)


def is_valid_azure_storage_account_name(name: str) -> bool:
    return len(name) >= 3 and len(name) <= 24 and name.isalnum() and name.islower()


def parse_cmd_line() -> TerraformAction:
    ACTIONS = {"plan": action_plan, "apply": action_apply, "destroy": action_destroy}
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "apply", "destroy"], help="Terraform step to execute")
    args = parser.parse_args()
    return ACTIONS[args.action]


if __name__ == "__main__":
    terraform_action = parse_cmd_line()
    azure_profiles = get_azure_profiles()
    execution_successful = execute_action(terraform_action, azure_profiles)
    exit_code = EX_OK if execution_successful else EX_FAILED
    sys.exit(exit_code)