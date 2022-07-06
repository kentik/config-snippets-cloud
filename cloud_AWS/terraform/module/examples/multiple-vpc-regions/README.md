# Multiple VPC's from different regions

The configuration in this directory creates a configuration for each VPC ID located in the input_data.json file.


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
terraform -chdir=./bucket init && terraform -chdir=./cloud_iam init
python3 aws_multiregions.py apply
```

Clean up created resources:

```shell
python3 aws_multiregions.py destroy
```

## Inputs

| Name             | Description                                                                                          | Type           | Required |
|------------------|------------------------------------------------------------------------------------------------------|----------------|----------|
| external_id      | Company ID assigned by Kentik passed to assume role policy of TerraformIngestRole ([External ID][1]) | `string`       | true     |
| plan_id          | Billing plan ID.                                                                                     | `string`       | true     |
| regions          | Dict object with key's as regions names                                                              | `dict`         | true     |
| vpc_id_list      | List of VPC ids for which Kentik should gather logs                                                  | `list(string)` | true     |
| s3_bucket_prefix | Prefix to use with s3 bucket name                                                                    | `string`       | false    |


### Example input_data.json

```json
{
  "external_id" : "12345",
  "plan_id" : "55555",
  "regions": {
    "us-west-1": {
      "vpc_id_list": [
        "vpc-0f2f43b3fef212f3c",
        "vpc-0ce56af6e5c980294"
      ],
      "s3_bucket_prefix": "tf-multi-region"
    },
    "eu-west-1": {
      "vpc_id_list": [
        "vpc-019399c7bcc3772d6"
      ],
      "s3_bucket_prefix": "tf-multi-region"
      }
  }
}
```

## Outputs

| Name                    | Description                                    |
|-------------------------|------------------------------------------------|
| iam_role_arn            | ARN of created IAM role                        |
| kentik_bucket_name      | List of all created buckets for provided vpc's |
| kentik_bucket_arn_list  | List of all created buckets arn's              |
