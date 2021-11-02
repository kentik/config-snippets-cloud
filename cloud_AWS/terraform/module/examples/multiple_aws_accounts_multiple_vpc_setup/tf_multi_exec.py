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
TerraformAction = Callable[[Terraform], TerraformOutput]  # terraform plan/apply/destroy
AwsProfileList = Optional[List[str]]  # AWS profile list matching profiles in ~/.aws/credentials


def multi_execute_action(action: TerraformAction, credentials: List[AwsCredentials]) -> None:
    t = Terraform()
    for cred in credentials:
        os.environ["AWS_ACCESS_KEY_ID"] = cred.access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = cred.secret_key
        workspace = cred.profile  # AWS profiles are mapped to Terraform workspaces

        print(f'Creating workspace "{workspace}"...')
        terraform_diag(t.create_workspace(workspace))

        print(f'Setting workspace to "{workspace}"...')
        terraform_diag(t.set_workspace(workspace))

        terraform_diag(action(t))
    print("Multi-account execution done for {} AWS accounts.".format(len(credentials)))


# TerraformAction
def action_plan(t: Terraform) -> TerraformOutput:
    print("Terraform plan...")
    return t.plan()


# TerraformAction
def action_apply(t: Terraform) -> TerraformOutput:
    print("Terraform apply...")
    return t.apply(skip_plan=True)  # skip_plan means auto-approve


# TerraformAction
def action_destroy(t: Terraform) -> TerraformOutput:
    print("Terraform destroy...")
    return t.apply(destroy=IsFlagged, skip_plan=True)  # skip_plan means auto-approve


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