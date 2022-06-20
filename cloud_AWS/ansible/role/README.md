# AWS Kentik integration Ansible Role

Ansible role that enforces AWS state required for the Kentik to enable integration

This role creates:
* IAM role acording to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Create_an_AWS_Role)
* S3 bucket - one per VPC - acording to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Create_an_S3_Bucket)
* Flow log for VPC acording to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Configure_Log_Publishing)

## Usage

First, clone the snippets repository and copy the `cloud_AWS/ansibe/role` contents into your Ansible roles directory structure, for example:
```bash
git clone https://github.com/kentik/config-snippets-cloud /tmp/
mkdir /my_ansible_working_dir/roles/kentik_aws_integration
cp -ar /tmp/cloud_AWS/ansible/role/* /my_ansible_working_dir/roles/kentik_aws_integration
```

Next, add the role into your playbook accordingly, for example:
```yaml
- hosts: 127.0.0.1
  connection: local
  gather_facts: false
  roles:
  - role: "kentik_aws_integration"
    vars:
      vpc_id_list:
      - "vpc-081ec835f3EXAMPLE"
```

Note however, instead of copying the role into your Ansible directory structure, the role could also be configured by specifying the right path, for example:
```yaml
- host: 127.0.0.1
  connection: local
  gather_facts: false
  roles:
  - role: "/tmp/cloud_AWS/ansible/role/"
    vars:
      vpc_id_list:
      - "vpc-081ec835f3EXAMPLE"
```

## Examples

* [Prepare single VPC](examples/single-vpc)

## Demo

* [Integrate role into existing playbook](demo)

## Note
* this role requires user to have the AWS access configured. Please refer to the [AWS documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) for guidance.
* this role uses the AWS CloudFormation for creating S3 Buckets and enabling VPC Flow Logs. It is due to lack of dedicated Ansible modules for these tasks. In fact, module for S3 exists, however it does not support every configuration option.
* this role requires additional Python's modules. Please refer to the [PiP](https://pip.pypa.io/en/stable/) to install them, otherwise the role will fail.
* this role creates AWS resources only. This won't register VPC in Kentik platform automaticaly.

## Requirements

| Name | Version |
|------|---------|
| python | >= 3 |
| python's boto3 | >= 1.14 |
| python's botocore | >= 1.17 |
| awscli | >= 1.18 |
| ansible | >= 2.9 |

## Variables

| Name | Description                                                                                                       | Type | Default | Required |
|------|-------------------------------------------------------------------------------------------------------------------|------|---------|:--------:|
| vpc\_id\_list | List of VPC IDs for which Kentik should gather logs                                                               | `list(string)` | `[]` | yes |
| rw\_s3\_access | If set to true, Kentik platform will be able to delete old logs from s3 buckets                                   | `bool` | `false` | no |
| s3\_bucket\_prefix | Prefix to use with s3 bucket name                                                                                 | `string` | `kentik` | no |
| s3\_flowlogs\_bucket | An existing S3 bucket for saving logs                                                                             | `string` | `` | no |
| s3\_flowlogs\_path | Path on the S3 bucket for saving logs                                                                             | `string` | `` | no |
| iam\_role\_prefix | Prefix to use with IAM roles                                                                                      | `string` | `Kentik` | no |
| store\_logs\_more\_frequently | Allows to choose how often save logs to s3. Default is once per 10 minutes. When enabled it saves once per minute | `bool` | `false` | no |
