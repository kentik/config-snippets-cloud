# No cloud export

Configuration in this directory creates configuration for single VPC without registering cloud export in Kentik.
To achieve that, the _plan_id_ is not set.

## Requirements

- Installed and configured AWS CLI
  - [installation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
  - [configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- Created VPC

## Usage

Run the example:

```shell
terraform init
terraform apply --vpc_id=<vpc-id>
```

Clean up created resources:

```shell
aws s3 rm s3://terraform-example-ingest-bucket-flow-logs
terraform destroy --vpc_id=<vpc-id>
```

## Inputs

| Name | Description | Type |
|------|-------------|------|
| vpc\_id | ID of VPC to configure | `string` |

## Outputs

| Name | Description |
|------|-------------|
| iam\_role\_arn | ARN of created IAM role |
| bucket\_name\_list | List of all created buckets - exactly one in this case |
