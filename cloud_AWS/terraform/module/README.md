# AWS Kentik integration Terraform module

Terraform module which creates AWS resources required for Kentik to enable integration

Module is creating:
* IAM role acording to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Create_an_AWS_Role)
* S3 bucket - one per VPC - acording to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Create_an_S3_Bucket)
* Flow log for VPC acording to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Configure_Log_Publishing)

## Usage

```hcl
data "aws_vpcs" "all-vpc" {}

module "kentik_aws_integration" {
  source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  rw_s3_access = true
  vpc_id_list = data.aws_vpcs.all-vpc.ids
}
```

## Examples

* [Prepare single VPC](examples/single-vpc)
* [Prepare all VPCs from certain region](examples/all-vpc-from-region)
* [Create EKS cluster with Boutique and configured VPC](examples/boutique-eks)

## Demo
* [Demo showing how add single VPC to Kentik portal using this module](examples)

## Note
* this project use `for_each` in code. If it is meant to be used with VPC creation, VPC should be created first for example using `terraform apply -target="aws_vpc.test-vpc"`
* this module creates AWS resources only. This won't register VPC in Kentik platform automaticaly.

## Requirements

| Name | Version |
|------|---------|
| terraform | >=0.12.0 |
| aws | >= 2.28.1 |

## Providers

| Name | Version |
|------|---------|
| aws | >= 2.28.1 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| rw\_s3\_access | If set to true, Kentik platform will be able to delete old logs from s3 buckets | `bool` | ` ` | yes |
| vpc\_id\_list | List of VPC ids for which Kentik should gather logs | `list(string)` | `[]` | yes |
| s3\_bucket\_prefix | Prefix to use with s3 bucket name | `string` | `kentik` | no |
| iam\_role\_prefix | Prefix to use with IAM roles | `string` | `Kentik` | no |
| store\_logs\_more\_frequently | Allows to chose how often save logs to s3. Default is once per 10 minutes. When enabled it saves once per minute | `bool` | `false` | no |

## Outputs

| Name | Description |
|------|-------------|
| iam\_role\_arn | ARN of created IAM role |
| bucket\_name\_list | List of all created buckets - one per VPC |
