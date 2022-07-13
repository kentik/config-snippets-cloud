# config-snippets-cloud

# Kentik swagger documents for creating Cloud Exports
* https://portal.kentik.com/v4/core/api-tester/cloud_export-202101beta1/swagger

# Automate AWS
## Terraform
* [Terraform](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/terraform)
### Demo
* [Terraform Demo](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/terraform/module/demo)
### Examples
#### Single VPC, Single Region
* [single-vpc](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/terraform/module/examples/single-vpc)
#### All VPC, Single Region
* [all-vpc-from-region](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/terraform/module/examples/all-vpc-from-region)
#### Multiple VPC, Multiple Region
* [multiple-vpc-regions](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/terraform/module/examples/multiple-vpc-regions)
#### Deploy Sock Shop as an example micro-service architecture
* [sock-shop-eks](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/terraform/module/examples/sock-shop-eks)

## Ansible
* [Ansible](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/ansible/role)
### Demo
* [Ansible Demo](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/ansible/role/demo)
### Examples
#### Single VPC, Single Region
* [single-vpc](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_AWS/ansible/role/examples/single-vpc)


# Stage 2 - Automate GCP
## Terraform
* [Terraform](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_GCP/terraform)
### Demo
* [Terraform Demo](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_GCP/terraform/module/demo) (TODO)
### Examples
#### Subnet-list, Single region
* [subnet-list](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_GCP/terraform/module/examples/subnet-list)
#### All Subnets in network, Single Region
* [all-network-subnets](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_GCP/terraform/module/examples/all-network-subnets)

## Ansible
* [Ansible](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_GCP/terraform)
### Demo
* [Ansible Demo](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_GCP/terraform/module/demo)(TODO)

# Stage 3 - Automate Azure
## Terraform
* [Tearraform](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_Azure/terraform)
### Demo
* [Terraform Demo](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_Azure/terraform/module/demo) (TODO)
### Examples
#### Subnet-list, Single region
* [all_nsg](https://github.com/kentik/config-snippets-cloud/tree/master/cloud_Azure/terraform/module/examples/all_nsg)

## Ansible
* [Ansible](cloud_Azure/ansible/roles/kentik_az)
### Examples
#### All NSG from resource group
* [all_nsg](cloud_Azure/ansible/examples/all_nsg)

# Stage 4 - Automate IBM Cloud
## Timing TBD

# General needs for automation
## Identity and Access Management
## Creation of Storage location
## Role permitting access from Kentik account into specific customer account resources
## Enablement of VPC Flowlogs
## Creation of pointer to Flowlog storage location
