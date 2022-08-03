# Multiple VPC's from different regions

The configuration in this directory creates a configuration for all vpc located in regions from multi_region_data.ini file.

## Requirements (in addition to [module requirements](../../README.md#requirements))

1. python >= 3.7.0

- Installed and configured AWS CLI
    - [installation](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
    - [configuration](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)
- Existing VPC in each target region
- Exported Kentik API credentials:

  ```shell
  export KTAPI_AUTH_EMAIL="joe.doe@email.com"
  export KTAPI_AUTH_TOKEN="token123"
  ```

## Prepare

Execute:
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
terraform -chdir=./bucket init && terraform -chdir=./cloud_iam init
```

## Usage

Run the example:

```shell
python3 aws_multi_regions.py plan
python3 aws_multi_regions.py apply
```

Clean up created resources:

```shell
python3 aws_multi_regions.py destroy
```

## Inputs

| Name             | Description                                                                                          | Type     | Required |
|------------------|------------------------------------------------------------------------------------------------------|----------|----------|
| external_id      | Company ID assigned by Kentik passed to assume role policy of TerraformIngestRole ([External ID][1]) | `string` | true     |
| plan_id          | Billing plan ID                                                                                      | `string` | true     |
| region           | AWS region name                                                                                      | `string` | true     |
| s3_bucket_prefix | Prefix to use with s3 bucket name                                                                    | `string` | false    |


### Example multi_region_data.ini

```ini
[DEFAULT]
external_id = 1234
plan_id = 5678

[first-region]
region = us-west-2
s3_bucket_prefix = tf-multi-region

[second-region]
region = eu-west-1
s3_bucket_prefix = tf-multi-region
```

## Outputs

| Name                    | Description                                    |
|-------------------------|------------------------------------------------|
| iam_role_arn            | ARN of created IAM role                        |
| kentik_bucket_name      | List of all created buckets for provided vpc's |
| kentik_bucket_arn_list  | List of all created buckets arn's              |
