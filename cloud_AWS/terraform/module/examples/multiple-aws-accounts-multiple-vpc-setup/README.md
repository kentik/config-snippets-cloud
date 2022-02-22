# Multiple AWS accounts multiple VPCs

This example creates cloud export configuration for all VPCs in given region in multiple AWS accounts.  
Handling of multiple regions per AWS profile is possible by means of profiles.  
A profile consits of profile name + credentials keys + region, profiles are stored in:
- `~/.aws/credentials` (name -> credentials)
- `~/.aws/config` (name -> region)

Example profile "test-profile":  
```ini
; ~/.aws/credentials
[test-profile] ; <-- profile name
aws_access_key_id = AKIA6YTS...5ZOZTCHCK ; <-- credentials
aws_secret_access_key = iWRORVVBDrtC5FlJ...9v12brUtHnT0L1GlZ8Uv ; <-- credentials

; ~/.aws/config
[profile test-profile] ; profile name same as above
region = us-west-2 ; <-- region
```

## The process

1. Information on available AWS profiles is read from configuration files under `~/.aws/`
1. Information on desired profiles to export flow logs for is read from command line
1. Iterate over desired profiles:
    1. Derive Terraform workspace name by hashing the AWS profile name (so only lower case alphanumeric characters are used)
    1. Create Terraform workspace and activate it
    1. Apply Terraform configuration in activated workspace

## Requirements (in addition to [module requirements](../../README.md#requirements))

1. python >= 3.7.0
1. virtualenv >= 20.4.0
1. terraform >= 1.0.0

1. Configured AWS profiles. To configure profiles, run in shell: `pip install awscli && aws configure`
1. Kentik API credentials present in execution environment:
  ```bash
  export KTAPI_AUTH_EMAIL="joe.doe@email.com"
  export KTAPI_AUTH_TOKEN="token123"
  ```

## Prepare

Execute:
```bash
virtualenv venv && source venv/bin/activate
pip install -r requirements.txt
terraform init
```

## Usage

- Execute **terraform plan** step on multiple AWS accounts:  
  ```bash
  python aws_onboarder.py plan --profiles=*
  ```
- Execute **terraform apply** step on multiple AWS accounts  
  ```bash
  python aws_onboarder.py apply --profiles=*
  ```
- Execute **terraform destroy** step on multiple AWS accounts  
  ```bash
  python aws_onboarder.py destroy --profiles=*
  ```
- Execute **terraform apply** step on multiple AWS accounts (selected profiles only)  
  ```bash
  python aws_onboarder.py apply --profiles=test,integration
  ```
- Help  
  ```bash
  python aws_onboarder.py --help
  ```

**Note:** "destroy" action will also delete AWS S3 buckets where the flow logs are stored. See: `s3_delete_nonempty_buckets` in [main.tf](main.tf)



## Inputs

| Name | Description | Type |
|------|-------------|------|
| ~/.aws/credentials | List of AWS credentials (keys) | `INI file` |
| ~/.aws/config | List of AWS regions | `INI file` |

## Outputs

| Name | Description |
|------|-------------|
| kentik_iam_role_arn | ARN of created IAM role - exactly one per AWS profile |
| kentik_bucket_name | Created S3 bucket - exactly one per AWS profile |

