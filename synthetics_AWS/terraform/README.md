# Synthetics agent deployment on AWS ec2 instance

The module creates ec2 instance with provided configuration and deploys `ksynth` agent.

## Requirements

| Name         | Version |
|--------------|---------|
| terraform    | ~> 1.0  |
| aws provider | ~> 4.0  |
| AWS CLI      | ~> 4.0  |


## Inputs

| Name                   | Description                                      | Type         | Default | Required |
|------------------------|--------------------------------------------------|--------------|---------|----------|
| vpc_security_group_ids | List of security groups IDs                      | list(string) |         | true     |
| plan_id                | Kentik plan ID                                   | string       |         | true     |
| region                 | Specifies AWS provider region                    | string       |         | false    |
| key_name               | Key name of the Key Pair to use for the instance | string       |         | false    |
| iam_instance_profile   | IAM role ID                                      | string       |         | false    |
| subnet_id              | Subnet ID                                        | string       |         | false    |


## Usage

  ```bash
  terraform init
  terraform apply \
  -var='vpc_security_group_ids=["<vpc-security-group-id>"]' \
  -var='plan_id=<plan-id>' \
  -var='region=<region-name>' \
  -var='key_name=<key-name>' \
  -var='iam_instance_profile=<iam-instance-profile>' \
  -var='subnet_id=<subnet-id>'
  ```