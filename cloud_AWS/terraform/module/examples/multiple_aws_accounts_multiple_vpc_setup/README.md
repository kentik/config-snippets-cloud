# Terraform multi-aws-account executor

## Brief

The goal of this example is to create both AWS and Kentik resources for multiple AWS accounts (stored under ~/.aws/credentials)

## Preconditions
1. python >= 3.9 is installed
1. virtualenv >= 20.4.0 is installed
1. terraform >= 1.0.0 is installed
1. AWS credentials are in place: ~/.aws/credentials  (to setup credentials, do: ```pip install awscli && aws configure```)

## Steps

1. ```virtualenv venv && source venv/bin/activate```
1. ```pip install -r requirements.txt```
1. ```terraform init```
1. ```python tf_multi_exec.py --help```

## Examples

1. multi-plan  
```python tf_multi_exec.py --action=plan```
1. multi-apply  
```python tf_multi_exec.py --action=apply```
1. multi-destroy  
```python tf_multi_exec.py --action=destroy```
1. multi-apply (selected aws profiles only)  
```python tf_multi_exec.py --action=apply --profiles=test,integration```

## Note

"destroy" action will also delete AWS S3 buckets where the flow logs are stored. See: `s3_delete_nonempty_buckets` in [main.tf](main.tf)