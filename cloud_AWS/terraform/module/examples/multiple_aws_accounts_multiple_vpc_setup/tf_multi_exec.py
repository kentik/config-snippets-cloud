import argparse
import os
from dataclasses import dataclass
from typing import Callable, List, Optional, Tuple

import boto3.session as aws
from botocore import credentials
from python_terraform import IsFlagged, Terraform


@dataclass
class AwsCredentials:
    profile: str
    access_key: str
    secret_key: str


TerraformOutput = Tuple[int, Optional[str], Optional[str]]  # terraform command: return code, stdout, stderr
TerraformAction = Callable[[Terraform], None]  # terraform plan/apply/destroy
AwsProfileList = Optional[List[str]]  # AWS profile list matching profiles in ~/.aws/credentials


def multi_execute_action(action: TerraformAction, credentials: List[AwsCredentials]) -> None:
    t = Terraform()
    for cred in credentials:
        os.environ["AWS_ACCESS_KEY_ID"] = cred.access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = cred.secret_key
        workspace = make_workspace_name(cred.profile)  # AWS profiles are mapped to Terraform workspaces

        create_workspace_if_needed(t, workspace)
        switch_workspace_if_needed(t, workspace)
        action(t)
    print("Multi-account execution done for {} AWS account(s).".format(len(credentials)))


def create_workspace_if_needed(t: Terraform, workspace: str) -> None:
    _, stdout, _ = t.cmd("workspace", "list")
    existing_workspaces = [s.strip("* ") for s in stdout.splitlines() if s]
    if workspace not in existing_workspaces:
        print(f'Creating workspace "{workspace}"...')
        terraform_diag(t.create_workspace(workspace))


def switch_workspace_if_needed(t: Terraform, workspace: str) -> None:
    _, stdout, _ = t.show_workspace()
    current_workspace = stdout.strip()
    if workspace != current_workspace:
        print(f'Switching workspace to "{workspace}"...')
        terraform_diag(t.set_workspace(workspace))


# TerraformAction
def action_plan(t: Terraform) -> None:
    print("Terraform plan...")
    terraform_diag(t.plan())


# TerraformAction
def action_apply(t: Terraform) -> None:
    print("Terraform apply...")
    terraform_diag(t.apply(skip_plan=True))  # skip_plan means auto-approve


# TerraformAction
def action_destroy(t: Terraform) -> None:
    print("Terraform destroy...")
    terraform_diag(t.apply(destroy=IsFlagged, skip_plan=True))  # skip_plan means auto-approve


def make_workspace_name(s: str) -> str:
    # workspace name is used as a suffix to certain AWS and Kentik resource names to make them unique
    # only lowercase alphanumeric characters and hyphens are allowed - S3 bucket name limitation
    s = s.lower().replace("_", "-")
    return "".join(c for c in s if c.isalnum() or c == "-")


def terraform_diag(output: TerraformOutput) -> None:
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


def get_aws_credentials(requested: AwsProfileList) -> List[AwsCredentials]:
    credentials: List[AwsCredentials] = []
    filtered_profiles = [p for p in aws.Session().available_profiles if not requested or p in requested]
    for profile in filtered_profiles:
        c = aws.Session(profile_name=profile).get_credentials()
        credentials.append(AwsCredentials(profile, c.access_key, c.secret_key))
    return credentials


def parse_cmd_line() -> Tuple[TerraformAction, AwsProfileList]:
    ACTIONS = {"plan": action_plan, "apply": action_apply, "destroy": action_destroy}
    parser = argparse.ArgumentParser("multi-exec")
    parser.add_argument("--action", choices=["plan", "apply", "destroy"], default="plan", help="default: plan")
    parser.add_argument("--profiles", default="", help="optional list of AWS profiles, eg. profile1,profile2,profile3")
    args = parser.parse_args()
    return ACTIONS[args.action], args.profiles.split(",") if args.profiles else None


if __name__ == "__main__":
    check_kentik_credentials()
    action, requested_profiles = parse_cmd_line()
    credentials = get_aws_credentials(requested_profiles)
    multi_execute_action(action, credentials)
