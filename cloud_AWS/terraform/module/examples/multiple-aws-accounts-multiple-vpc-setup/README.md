# Multiple AWS accounts multiple VPC setup

Files in this directory support configuring export of flow logs from all VPCs in given region in multiple AWS accounts into a single Kentik account.  
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
## Requirements

1. python >= 3.7.0
1. virtualenv >= 20.4.0
1. terraform >= 0.12.0
1. Configured AWS profiles. To configure profiles, run in shell: `pip install awscli && aws configure`
1. Kentik API credentials present in execution environment:
  ```bash
  export KTAPI_AUTH_EMAIL="joe.doe@email.com"
  export KTAPI_AUTH_TOKEN="token123"
  ```

## Prepare

1. ```virtualenv venv && source venv/bin/activate```
1. ```pip install -r requirements.txt```
1. ```terraform init```

## Usage

- Execute **terraform plan** step on multiple AWS accounts:  
```python tf_multi_exec.py plan --profiles=*```
- Execute **terraform apply** step on multiple AWS accounts  
```python tf_multi_exec.py apply  --profiles=*```
- Execute **terraform destroy** step on multiple AWS accounts  
```python tf_multi_exec.py destroy  --profiles=*```
- Execute **terraform apply** step on multiple AWS accounts (selected profiles only)  
```python tf_multi_exec.py apply --profiles=test,integration```
- Help  
```python tf_multi_exec.py --help```

**Note:** "destroy" action will also delete AWS S3 buckets where the flow logs are stored. See: `s3_delete_nonempty_buckets` in [main.tf](main.tf)



## Inputs

| Name | Description | Type |
|------|-------------|------|
| ~/.aws/credentials | List of AWS credentials (keys) | `text file` |
| ~/.aws/config | List of AWS regions | `text file` |

## Outputs

| Name | Description |
|------|-------------|
| kentik_iam_role_arn | ARN of created IAM role - exactly one per AWS profile |
| kentik_bucket_name | Created S3 bucket - exactly one per AWS profile |

