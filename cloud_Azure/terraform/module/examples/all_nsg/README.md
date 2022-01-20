# All Network Security Groups in Resource Group

Configuration in this directory creates configuration for all Network Security Group in Resource Group.

## Requirements

* Information about Azure deployment: location, resource group name, subscription ID
* Information about Kentik subscription: plan ID
* Azure CLI - [Installation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
* Authenticating Azure CLI to your account - [Logging-in](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli)

## Usage

Prepare `terraform.tfvars` file. Example:
```terraform
# Azure section
subscription_id = "a37491e5-fdc6-4fad-96ce-ec33c4f7e99d"
location = "eastus"
resource_group_name = "resource-group-1"

# Kentik section
email = "dummy@test.mail"
token = "dummy_token"
plan_id = "12345"
prefix = "jotta"
name = "jotta"
```

Then execute:
```
$ terraform init
$ terraform apply
```


## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| subscription_id | Id of the subscription in which resource are located | `string` | `` | yes |
| resource_group_name | Name of the resource group to gather logs from | `string` | `` | yes |
| email | Kentik account email | `string` | `` | yes |
| token | Kentik account token | `string` | `` | yes |
| plan_id | Billing plan ID | `string` | `` | yes |
| name | Cloudexport entry name in Kentik | `string` | `` | yes |

## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Network Security groups that logs will be gathered from |
| subscription_id | Subscription Id |
| resource_group | Resource group name |
| storage_account | Storage account name where logs will be gathered |
| principal_id | Principal ID created for Kentik NSG Flow Exporter application |
