# Single VPC

Configuration in this directory creates configuration for single VPC.

## Requirements

- Installed and configured AWS CLI
  - [installation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
  - [configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- Created VPC
- Exported Kentik API credentials:

  ```shell
  export KTAPI_AUTH_EMAIL="joe.doe@email.com"
  export KTAPI_AUTH_TOKEN="token123"
  ```

## Usage

Run the example:

```shell
terraform init
terraform apply --var vpc_id=<vpc-id>
```

Clean up created resources:

```shell
terraform destroy --var vpc_id=<vpc-id>
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
