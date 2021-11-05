# Multiple AWS accounts multiple VPC setup

Configuration in this directory creates configuration for multiple AWS accounts; all VPCs in selected region are considered.  
Note: this example works with profiles. A profile is credentials keys + profile name + region.  
Profile name is later translated to terraform workspace.
## Requirements

1. Installed python >= 3.9
1. Installed virtualenv >= 20.4.0
1. Installed terraform >= 0.12.0
1. Configured AWS profiles: ~/.aws/credentials (keys), ~/.aws/config (regions); to setup profiles, do: ```pip install awscli && aws configure```
1. Exported Kentik API credentials:
  ```shell
  export KTAPI_AUTH_EMAIL="joe.doe@email.com"
  export KTAPI_AUTH_TOKEN="token123"
  ```

## Prepare

1. ```virtualenv venv && source venv/bin/activate```
1. ```pip install -r requirements.txt```
1. ```terraform init```

## Usage

- multi-plan  
```python tf_multi_exec.py --action=plan```
- multi-apply  
```python tf_multi_exec.py --action=apply```
- multi-destroy  
```python tf_multi_exec.py --action=destroy```
- multi-apply (selected aws profiles only)  
```python tf_multi_exec.py --action=apply --profiles=test,integration```
- help  
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

