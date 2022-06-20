# AWS Kentik integration Terraform module

Module supporting management of AWS and Kentik resources required for VPC flow logs export from AWS to Kentik.

Module creates:
* IAM role according to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Create_an_AWS_Role)
* S3 bucket per region (reduces AWS costs)
* ---- one unique sub-folder per VPC - according to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Create_an_S3_Bucket)
* Flow log for VPC according to [Kentik documentation](https://kb.kentik.com/Fc14.htm#Fc14-Configure_Log_Publishing)
* Registers VPC in Kentik platform according to [Kentik documentation](https://kb.kentik.com/v0/Bd06.htm#Bd06-Create_a_Cloud_in_Kentik).

## Usage examples

* [Single VPC in single region, single AWS account](examples/single-vpc) - export flow logs from a single VPC in a single region in a single AWS account
* [All VPCs in single region, single AWS account](examples/all-vpc-from-region) - export flow logs from all VPCs in a single region in a single AWS account
* [All VPCs in single region, multiple AWS accounts](examples/multiple-aws-accounts-multiple-vpc-setup) - export flow logs from all VPCs in a region associated with AWS account; uses Python wrapper to iterate over multiple AWS accounts
* [Create EKS cluster with sock shop and configured VPC](examples/sock-shop-eks)
## Demo

* [Demo showing how add single VPC to Kentik portal using this module](demo)

## Requirements

| Name | Version |
|------|---------|
| terraform | >=1.0.0 |
| aws provider | >=4.0.0 |
| kentik-cloudexport provider | >=0.4.0 |


## Inputs

| Name | Description                                                                                                      | Type | Default | Required |
|------|------------------------------------------------------------------------------------------------------------------|------|---------|:--------:|
| rw\_s3\_access | If set to true, Kentik platform will be able to delete old logs from s3 buckets                                  | `bool` | ` ` | yes |
| vpc\_id\_list | List of VPC IDs for which Kentik should gather logs                                                              | `list(string)` | `[]` | yes |
| s3\_bucket\_prefix | Prefix to use with s3 bucket name                                                                                | `string` | `kentik` | no |
| s3\_use\_one\_bucket | If we should use one or more buckets                                                                             | `bool` | `true` | no |
| s3\_flowlogs\_path | Path on the S3 bucket for saving logs                                                                            | `string` | `` | no |
| s3\_base\_name | Base name for s3 bucket. Used in single bucket mode                                                              | `string` | `ingest-bucket` | no |
| s3_delete_nonempty_buckets | On terraform destroy, delete bucket even if it is not empty                                                      | `bool` | `false` | no |
| iam\_role\_prefix | Prefix to use with IAM roles                                                                                     | `string` | `Kentik` | no |
| store\_logs\_more\_frequently | Allows to chose how often save logs to s3. Default is once per 10 minutes. When enabled it saves once per minute | `bool` | `false` | no |
| create\_role | If to create kentik role                                                                                         | `bool` | `true` | no |
| name | Cloudexport entry name in Kentik                                                                                 | `string` | `terraform_aws_exported_cloud` | no |
| enabled | If cloud exported to Kentik is enabled                                                                           | `bool` | `true` | no |
| description | Cloudexport entry description in Kentik                                                                          | `string` | `` | no |
| plan\_id | Billing plan ID.                                                                                                 | `string` | | no |
| delete\_after\_read | If to delete after read                                                                                          | `bool` | `false` | no |
| multiple\_buckets | If to use multiple buckets                                                                                       | `bool` | `false` | no |
| region | Specifies AWS region passed to Kentik Portal                                                                     | `string` | | yes |
| external_id | Company ID assigned by Kentik passed to assume role policy of TerraformIngestRole ([External ID][1])             | `string` | `` | no |

[1]: https://aws.amazon.com/blogs/security/how-to-use-external-id-when-granting-access-to-your-aws-resources/

## Outputs

| Name | Description |
|------|-------------|
| iam\_role\_arn | ARN of created IAM role |
| bucket\_name\_list | List of all created buckets - one per VPC |
