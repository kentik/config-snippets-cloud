import argparse
import configparser
import logging
import os
import sys
from dataclasses import dataclass
from hashlib import blake2b
from typing import Any, Callable, Dict, List, Optional, Tuple

from az.cli import az
from python_terraform import IsFlagged, IsNotFlagged, Terraform

log = logging.getLogger(__name__)
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.WARNING)
EX_FAILED: int = 1  # exit  code for failed command
PROFILES_FILE: str = "profiles.ini"


@dataclass
class AzureProfile:
    name: str
    subscription_id: str
    tenant_id: str
    principal_id: str
    principal_secret: str
    location: str
    resource_group_names: List[str]


TerraformVars = Dict[str, Any]  # variables passed in terraform plan/apply/destroy call
TerraformAction = Callable[[Terraform, TerraformVars], bool]  # terraform plan/apply/destroy
RequestedProfileNames = Optional[List[str]]  # list of profile names matching profiles in profiles.ini

# execute an action for every profile
def execute_action(action: TerraformAction, profiles: List[AzureProfile]) -> bool:
    t = Terraform()
    successful_count = 0
    for profile in profiles:
        print(f'Profile: "{profile.name}" ({profile.location})')

        workspace = prepare_workspace_name(profile.subscription_id)  # subscriptions are mapped to Terraform workspaces
        tf_vars = {
            "subscription_id": profile.subscription_id,
            "tenant_id": profile.tenant_id,
            "principal_id": profile.principal_id,
            "principal_secret": profile.principal_secret,
            "location": profile.location,
            "resource_group_names": profile.resource_group_names,
        }

        if prepare_workspace(t, workspace) and azure_login(profile) and action(t, tf_vars):
            successful_count += 1

    if successful_count > 0:
        azure_logout()

    print(f"Terraform action successfully executed for {successful_count}/{len(profiles)} Azure profile(s).")
    return successful_count == len(profiles)


# az login is required prior to calling terraform: "get_nsg.py" uses Azure CLI to gather Network Security Group names
def azure_login(profile: AzureProfile) -> bool:
    azure_login_command = f"login --service-principal -u {profile.principal_id} -p {profile.principal_secret} --tenant {profile.tenant_id}"
    exit_code, _, logs = az(azure_login_command)
    if exit_code != os.EX_OK:
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
    if return_code == os.EX_OK:
        print("Workspace activated")
        return True

    # probably no such worskpace exists, try to create it
    return_code, stdout, stderr = t.create_workspace(workspace)
    if return_code == os.EX_OK:
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


def prepare_workspace_name(name: str, workspace_names={}) -> str:  # pylint: disable=dangerous-default-value
    # workspace name is used as a suffix to certain Azure and Kentik resource names to make them unique;
    # only lower case alphanumeric characters are allowed - Azure StorageAccount name limitation

    # produce a name made of 20 lower case alpha num characters
    ws_name = blake2b(name.encode("utf-8"), digest_size=10).hexdigest()

    # ensure name uniqueness
    while ws_name in workspace_names:
        log.debug(
            "Workspace name collision for '%s'. '%s' already used for '%s'", name, ws_name, workspace_names[ws_name]
        )
        ws_name += "-"
        log.debug("Changing to %s", ws_name)
    workspace_names[ws_name] = name
    return ws_name


def report_tf_output(return_code: int, stdout: str, stderr: str) -> None:
    if stdout:
        print(stdout.strip())

    if stderr:
        print(stderr.strip(), file=sys.stderr)

    if return_code == os.EX_OK:
        print("Success")
    elif return_code == EX_FAILED:
        print("FAILED", file=sys.stderr)
    else:
        print("Return code: ", return_code)  # Terraform uses codes > 1 for reporting detailed status

    print()


def get_azure_profiles(requested: RequestedProfileNames) -> List[AzureProfile]:
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
    filtered_profiles: List[str] = [p for p in available_profiles if not requested or p in requested]
    for profile_name in filtered_profiles:
        profile = config[profile_name]
        try:
            azure_profile = AzureProfile(
                name=profile_name,
                subscription_id=profile["subscription_id"],
                tenant_id=profile["tenant_id"],
                location=profile["location"],
                resource_group_names=[name.strip() for name in profile["resource_group_names"].split(",")],
                principal_id=profile["principal_id"],
                principal_secret=profile["principal_secret"],
            )
        except KeyError as err:
            log.warning("Error reading profile data '%s'. Profile skipped. Error message: '%s'", profile_name, str(err))
            continue
        output_profiles.append(azure_profile)

    if requested:
        missing_profiles = list(set(requested) - set(available_profiles))
        if missing_profiles:
            log.warning("Missing config for profiles: %s in `%s`. Profiles skipped", missing_profiles, PROFILES_FILE)
    return output_profiles


def parse_cmd_line() -> Tuple[TerraformAction, RequestedProfileNames]:
    ACTIONS = {"plan": action_plan, "apply": action_apply, "destroy": action_destroy}
    ALL_PROFILES = "*"
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "apply", "destroy"], help="Terraform step to execute")
    parser.add_argument(
        "--profiles",
        required=True,
        help=f'Required. List of Azure profiles, eg. profile1,profile2,profile3. Use "{ALL_PROFILES}" to select all profiles',
    )
    args = parser.parse_args()
    return ACTIONS[args.action], args.profiles.split(",") if args.profiles != ALL_PROFILES else None


if __name__ == "__main__":
    terraform_action, requested_profiles = parse_cmd_line()
    azure_profiles = get_azure_profiles(requested_profiles)
    execution_successful = execute_action(terraform_action, azure_profiles)
    RETURN_CODE = os.EX_OK if execution_successful else EX_FAILED
    sys.exit(RETURN_CODE)
