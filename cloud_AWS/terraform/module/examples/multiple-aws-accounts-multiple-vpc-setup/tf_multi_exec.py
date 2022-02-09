import argparse
import logging
import os
import sys
from dataclasses import dataclass
from hashlib import blake2b
from typing import Callable, List, Optional, Tuple

import boto3.session as aws
from botocore.exceptions import BotoCoreError
from python_terraform import IsFlagged, IsNotFlagged, Terraform

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)
EX_FAILED: int = 1  # exit  code for failed command


@dataclass
class AwsProfile:
    name: str
    region: str
    access_key: str
    secret_key: str


TerraformAction = Callable[[Terraform, str], bool]  # terraform plan/apply/destroy for specified region
RequestedProfileNames = Optional[List[str]]  # list of profile names matching profiles in ~/.aws/credentials


# execute an action for every profile
def execute_action(action: TerraformAction, profiles: List[AwsProfile]) -> bool:
    t = Terraform()
    successful_count = 0
    for profile in profiles:
        print(f'Profile: "{profile.name}" ({profile.region})')

        os.environ["AWS_ACCESS_KEY_ID"] = profile.access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = profile.secret_key
        workspace = prepare_workspace_name(profile.name)  # AWS profiles are mapped to Terraform workspaces

        if prepare_workspace(t, workspace) and action(t, profile.region):
            successful_count += 1

    print(f"Terraform action successfully executed for {successful_count}/{len(profiles)} AWS profile(s).")
    return successful_count == len(profiles)


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
def action_plan(t: Terraform, region: str) -> bool:
    code, stdout, stderr = t.plan(detailed_exitcode=IsNotFlagged, var=f"region={region}")
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


# TerraformAction
def action_apply(t: Terraform, region: str) -> bool:
    code, stdout, stderr = t.apply(skip_plan=True, var=f"region={region}")  # skip_plan means auto-approve
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


# TerraformAction
def action_destroy(t: Terraform, region: str) -> bool:
    code, stdout, stderr = t.apply(destroy=IsFlagged, skip_plan=True, var=f"region={region}")  # auto-approve
    report_tf_output(code, stdout, stderr)
    return code != EX_FAILED


def prepare_workspace_name(name: str, workspace_names={}) -> str:  # pylint: disable=dangerous-default-value
    # workspace name is used as a suffix to certain AWS and Kentik resource names to make them unique;
    # only lower case alphanumeric characters and hyphens are allowed - S3 bucket name limitation

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


def check_kentik_credentials() -> None:
    # credentials as env variables are necessary for Terraform "kentik-cloudexport" provider
    for env_var in ["KTAPI_AUTH_EMAIL", "KTAPI_AUTH_TOKEN"]:
        if env_var not in os.environ:
            raise Exception(f"{env_var} environment variable is missing")


def get_aws_profiles(requested: RequestedProfileNames) -> List[AwsProfile]:
    profiles: List[AwsProfile] = []
    available_profiles = aws.Session().available_profiles  # loaded from ~/.aws/credentials and ~/.aws/config
    filtered_profiles = [p for p in available_profiles if not requested or p in requested]
    for profile in filtered_profiles:
        session = aws.Session(profile_name=profile)
        try:
            cred = session.get_credentials()
        except BotoCoreError as e:
            print(f'Failed to obtain credentials for profile "{profile}". Profile skipped. Error message: {e}')
            continue

        if not cred:
            print(f'No credentials configured for profile "{profile}". Profile skipped.')
            continue

        if not session.region_name:
            print(f'No region name configured for profile "{profile}". Profile skipped')
            continue

        profiles.append(AwsProfile(profile, session.region_name, cred.access_key, cred.secret_key))

    if requested:
        missing_profiles = list(set(requested) - set(available_profiles))
        if missing_profiles:
            print("Missing config for profiles:", missing_profiles, ". Profiles skipped")
    return profiles


def parse_cmd_line() -> Tuple[TerraformAction, RequestedProfileNames]:
    ACTIONS = {"plan": action_plan, "apply": action_apply, "destroy": action_destroy}
    ALL_PROFILES = "*"
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "apply", "destroy"], help="Terraform step to execute")
    parser.add_argument(
        "--profiles",
        required=True,
        help=f'Required. List of AWS profiles, eg. profile1,profile2,profile3. Use "{ALL_PROFILES}" to select all profiles',
    )
    args = parser.parse_args()
    return ACTIONS[args.action], args.profiles.split(",") if args.profiles != ALL_PROFILES else None


if __name__ == "__main__":
    check_kentik_credentials()
    terraform_action, requested_profiles = parse_cmd_line()
    aws_profiles = get_aws_profiles(requested_profiles)
    execution_successful = execute_action(terraform_action, aws_profiles)
    exit_code = os.EX_OK if execution_successful else EX_FAILED
    sys.exit(exit_code)
