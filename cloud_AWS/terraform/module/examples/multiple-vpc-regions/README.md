# Single VPC

Configuration in this directory creates configuration for two VPC's located in two different locations.


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
terraform apply --var vpc_id_1=<vpc-id-1> --var vpc_id_2=<vpc-id-2>
```

Clean up created resources:

```shell
terraform destroy --var vpc_id_1=<vpc-id-1> --var vpc_id_2=<vpc-id-2>
```

## Inputs

| Name      | Description                   | Type |
|-----------|-------------------------------|------|
| vpc\_id_1 | ID of first VPC to configure  | `string`|
| vpc\_id_2 | ID of second VPC to configure | `string`|

## Outputs

| Name                 | Description                                |
|----------------------|--------------------------------------------|
| iam\_role\_arn       | ARN of created IAM role                    |
| bucket\_name\_list_1 | List of all created buckets for first vpc  |
| bucket\_name\_list_2 | List of all created buckets for second vpc |
