# Single VPC

Configuration in this directory creates configuration for single VPC.

## Usage

To run this example you need to execute:
```
$ terraform init
$ terraform plan
$ terraform apply
```

## Requirements

Example requires VPC ID

## Inputs

| Name | Description | Type |
|------|-------------|------|
| vpc\_id | ID of VPC to configure | `string` |

## Outputs

| Name | Description |
|------|-------------|
| iam\_role\_arn | ARN of created IAM role |
| bucket\_name\_list | List of all created buckets - exactly one in this case |