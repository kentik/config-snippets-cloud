import os
from pathlib import Path
import re
from python_terraform import *


def set_env():
    KTAPI_AUTH_EMAIL_VAL = ""  # input your email
    KTAPI_AUTH_TOKEN_VAL = ""  # input your token

    os.environ["KTAPI_AUTH_EMAIL"] = KTAPI_AUTH_EMAIL_VAL
    os.environ["KTAPI_AUTH_TOKEN"] = KTAPI_AUTH_TOKEN_VAL


def read_credentials():
    workspace_regex = "\[(.*)\]"
    aws_access_key_id_regex = "(aws_access_key_id = )(.*)"
    aws_secret_access_key_regex = "(aws_secret_access_key = )(.*)"

    credentials_file = str(Path.home()) + "/.aws/credentials"
    credentials = []
    with open(credentials_file) as file:
        workspace = ""
        aws_access_key = ""
        aws_secret_access_key = ""
        for line in file.readlines():
            results = re.findall(workspace_regex, line)

            if len(results) != 0:
                workspace = results[0]
                continue
            else:
                results = re.findall(aws_access_key_id_regex, line)

            if len(results) != 0:
                aws_access_key = results[0][1]
                continue
            else:
                results = re.findall(aws_secret_access_key_regex, line)

            if len(results) != 0:
                aws_secret_access_key = results[0][1]
            else:
                continue

            if workspace != "" and aws_access_key != "" and aws_secret_access_key != "":
                credentials.append({"workspace": workspace,
                                    "aws_access_key": aws_access_key,
                                    "aws_secret_access_key": aws_secret_access_key})
                workspace = aws_access_key = aws_secret_access_key = ""

    return credentials


def apply_terraform_configuration():
    set_env()
    t = Terraform()
    for credentials_set in read_credentials():
        os.environ["AWS_ACCESS_KEY_ID"] = credentials_set["aws_access_key"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = credentials_set["aws_secret_access_key"]

        return_code, stdout, stderr = t.create_workspace(credentials_set["workspace"])
        print(return_code, stdout, stderr)

        if f'Workspace "{credentials_set["workspace"]}" already exists' in stderr:
            return_code, stdout, stderr = t.set_workspace(credentials_set["workspace"])
            print(return_code, stdout, stderr)

        t.plan()
        return_code, stdout, stderr = t.apply(var={'vpc_id': "vpc-0eeb173de06765d0a"}, skip_plan=True)
        print(return_code, stdout, stderr)


def destroy_terraform_configuration():
    set_env()
    t = Terraform()
    for credentials_set in read_credentials():
        os.environ["AWS_ACCESS_KEY_ID"] = credentials_set["aws_access_key"]
        os.environ["AWS_SECRET_ACCESS_KEY"] = credentials_set["aws_secret_access_key"]

        return_code, stdout, stderr = t.create_workspace(credentials_set["workspace"])
        print(return_code, stdout, stderr)

        if f'Workspace "{credentials_set["workspace"]}" already exists' in stderr:
            return_code, stdout, stderr = t.set_workspace(credentials_set["workspace"])
            print(return_code, stdout, stderr)

        t.plan()

        vpc_id = ""  # input vpc_id
        return_code, stdout, stderr = t.apply(destroy=IsFlagged, var={'vpc_id': vpc_id}, skip_plan=True)
        print(return_code, stdout, stderr)


# apply_terraform_configuration()
# destroy_terraform_configuration()
