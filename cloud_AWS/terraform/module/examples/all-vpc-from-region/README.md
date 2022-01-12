# All VPC from current region

Configuration in this directory creates configuration for single VPC.

## Requirements

- Installed and configured AWS CLI
  - [installation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
  - [configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- At least one created VPC
- Exported Kentik API credentials:

  ```shell
  export KTAPI_AUTH_EMAIL="joe.doe@email.com"
  export KTAPI_AUTH_TOKEN="token123"
  ```

## Usage

Run the example:

```shell
terraform init
terraform apply
```

Clean up created resources:

```shell
aws s3 rm s3://terraform-example-ingest-bucket-flow-logs
terraform destroy
```

## Inputs

None

## Outputs

| Name | Description |
|------|-------------|
| iam\_role\_arn | ARN of created IAM role |
| bucket\_name\_list | List of all created buckets - one per VPC |
