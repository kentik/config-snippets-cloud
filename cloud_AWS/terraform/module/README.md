# AWS Kentik integration Terraform module

Terraform module facilitating creation of AWS resources required for automatic export of VPC flow logs to Kentik.

Module is creating:
* IAM role according to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Create_an_AWS_Role)
* S3 bucket per region (reduces AWS costs)
* ---- one unique sub-folder per VPC - according to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Create_an_S3_Bucket)
* Flow log for VPC according to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Configure_Log_Publishing)
* Registers VPC in Kentik platform according to [Kentik documentation](https://kb.kentik.com/v0/Bd06.htm#Bd06-Create_a_Cloud_in_Kentik).

## Usage

```hcl
data "aws_vpcs" "all-vpc" {}

module "kentik_aws_integration" {
  source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"

  rw_s3_access = true
  vpc_id_list = data.aws_vpcs.all-vpc.ids
  store_logs_more_frequently = true
  name                       = "example-aws-terraform-name"
  plan_id                    = "11467"
  region                     = "us-east-2"
}
```

## Examples

* [Prepare single VPC](examples/single-vpc)
* [Prepare multiple VPCs on multiple AWS accounts](examples/multiple_aws_accounts_multiple_vpc_setup)
* [Prepare all VPCs from certain region](examples/all-vpc-from-region)
* [Create EKS cluster with sock shop and configured VPC](examples/sock-shop-eks)
## Demo

* [Demo showing how add single VPC to Kentik portal using this module](demo)

## Requirements

| Name | Version |
|------|---------|
| terraform | >=0.12.0 |
| aws | >= 2.28.1 |
| kentik-cloudexport | >=0.1.0 |

## Providers

| Name | Version |
|------|---------|
| aws | >= 2.28.1 |
| kentik-cloudexport | >=0.1.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| rw\_s3\_access | If set to true, Kentik platform will be able to delete old logs from s3 buckets | `bool` | ` ` | yes |
| vpc\_id\_list | List of VPC ids for which Kentik should gather logs | `list(string)` | `[]` | yes |
| s3\_bucket\_prefix | Prefix to use with s3 bucket name | `string` | `kentik` | no |
| s3\_use\_one\_bucket | If we should use one or more buckets | `bool` | `true` | no |
| s3\_flowlogs\_path | Path on the S3 bucket for saving logs | `string` | `` | no |
| s3\_base\_name | Base name for s3 bucket. Used in single bucket mode | `string` | `ingest-bucket` | no |
| iam\_role\_prefix | Prefix to use with IAM roles | `string` | `Kentik` | no |
| store\_logs\_more\_frequently | Allows to chose how often save logs to s3. Default is once per 10 minutes. When enabled it saves once per minute | `bool` | `false` | no |
| create\_role | If to create kentik role | `bool` | `true` | no |
| name | Exported cloud name in Kentik Portal | `string` | `terraform_aws_exported_cloud` | no |
| enabled | If cloud exported to Kentik is enabled | `bool` | `true` | no |
| description | Description in Kentik Portal | `string` | `` | no |
| plan\_id | Billing plan ID. | `string` | | no |
| delete\_after\_read | If to delete after read | `bool` | `false` | no |
| multiple\_buckets | If to use multiple buckets | `bool` | `false` | no |
| region | Specifies AWS region passed to Kentik Portal | `string` | | yes |
| external_id | Company ID assigned by Kentik passed to assume role policy of TerraformIngestRole ([External ID][1]) | `string` | `` | no |

[1]: https://aws.amazon.com/blogs/security/how-to-use-external-id-when-granting-access-to-your-aws-resources/

## Outputs

| Name | Description |
|------|-------------|
| iam\_role\_arn | ARN of created IAM role |
| bucket\_name\_list | List of all created buckets - one per VPC |
