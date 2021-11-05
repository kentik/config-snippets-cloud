import argparse
import os
from dataclasses import dataclass
from typing import Callable, Final, List, Optional, Tuple

import boto3.session as aws
from python_terraform import IsFlagged, Terraform


@dataclass
class AwsProfile:
    name: str
    region: str
    access_key: str
    secret_key: str


TerraformOutput = Tuple[int, Optional[str], Optional[str]]  # terraform command: return code, stdout, stderr
TerraformAction = Callable[[Terraform, str], None]  # terraform plan/apply/destroy for specified region
RequestedProfileNames = Optional[List[str]]  # list of profile names matching profiles in ~/.aws/credentials


def multi_execute_action(action: TerraformAction, profiles: List[AwsProfile]) -> None:
    t = Terraform()
    for profile in profiles:
        os.environ["AWS_ACCESS_KEY_ID"] = profile.access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = profile.secret_key
        workspace = make_workspace_name(profile.name)  # AWS profiles are mapped to Terraform workspaces

        create_workspace_if_needed(t, workspace)
        switch_workspace_if_needed(t, workspace)
        action(t, profile.region)
    print("Multi-account execution done for {} AWS account(s).".format(len(profiles)))


def create_workspace_if_needed(t: Terraform, workspace: str) -> None:
    _, stdout, _ = t.cmd("workspace", "list")
    existing_workspaces = [s.strip("* ") for s in stdout.splitlines() if s]
    if workspace not in existing_workspaces:
        print(f'Creating workspace "{workspace}"...')
        report_tf_output(t.create_workspace(workspace))


def switch_workspace_if_needed(t: Terraform, workspace: str) -> None:
    _, stdout, _ = t.show_workspace()
    current_workspace = stdout.strip()
    if workspace == current_workspace:
        print(f'Current workspace is "{workspace}"')
    else:
        print(f'Switching workspace to "{workspace}"...')
        report_tf_output(t.set_workspace(workspace))


# TerraformAction
def action_plan(t: Terraform, region: str) -> None:
    print(f'Terraform plan ("{region}")...')
    report_tf_output(t.plan(var=f"region={region}"))


# TerraformAction
def action_apply(t: Terraform, region: str) -> None:
    print(f'Terraform apply ("{region}")...')
    report_tf_output(t.apply(skip_plan=True, var=f"region={region}"))  # skip_plan means auto-approve


# TerraformAction
def action_destroy(t: Terraform, region: str) -> None:
    print(f'Terraform destroy ("{region}")...')
    report_tf_output(t.apply(destroy=IsFlagged, skip_plan=True, var=f"region={region}"))  # skip_plan means auto-approve


def make_workspace_name(s: str) -> str:
    # workspace name is used as a suffix to certain AWS and Kentik resource names to make them unique
    # only lowercase alphanumeric characters and hyphens are allowed - S3 bucket name limitation
    s = s.lower().replace("_", "-")
    return "".join(c for c in s if c.isalnum() or c == "-")


def report_tf_output(output: TerraformOutput) -> None:
    return_code, stdout, stderr = output

    if stdout:
        print(stdout.strip())

    if stderr:
        print(stderr.strip())

    if not stderr and not stdout:
        if return_code == 0:
            print("Success")
        else:
            print("Return code: ", return_code)

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
        sesesion = aws.Session(profile_name=profile)
        try:
            cred = sesesion.get_credentials()
        except:
            print(f'Skipping profile "{profile}" as credentials couldn\'t be obtained')
            continue

        if not cred:
            print(f'Skipping profile "{profile}" as no credentials are configured')
            continue

        region = sesesion.region_name
        if not region:
            print(f'Skipping profile "{profile}" as no region name is configured')
            continue

        profiles.append(AwsProfile(profile, region, cred.access_key, cred.secret_key))

    return profiles


def parse_cmd_line() -> Tuple[TerraformAction, RequestedProfileNames]:
    ACTIONS: Final = {"plan": action_plan, "apply": action_apply, "destroy": action_destroy}
    parser = argparse.ArgumentParser("multi-exec")
    parser.add_argument("--action", choices=["plan", "apply", "destroy"], default="plan", help="default: plan")
    parser.add_argument("--profiles", default="", help="optional list of AWS profiles, eg. profile1,profile2,profile3")
    args = parser.parse_args()
    return ACTIONS[args.action], args.profiles.split(",") if args.profiles else None


if __name__ == "__main__":
    check_kentik_credentials()
    action, requested_profiles = parse_cmd_line()
    profiles = get_aws_profiles(requested_profiles)
    multi_execute_action(action, profiles)
