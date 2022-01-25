# All Network Security Groups in requested Resource Groups

This example creates cloud export configuration for all Network Security Groups in requested Resource Groups.

## Requirements

* Information about Azure deployment: location, resource group names, subscription ID
* Information about Kentik subscription: plan ID
* Azure CLI - [Installation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
* Authenticating Azure CLI to your account - [Logging-in](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli)

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
resource_group_names = ["resource-group-1", "resource-group-2", "resource-group-3"]

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
| resource_group_names | List of Resource Group names to gather logs from | `list of strings` | `` | yes |
| prefix| Prefix for the naming resources | `string` | `` | yes |
| email | Kentik account email | `string` | `` | yes |
| token | Kentik account token | `string` | `` | yes |
| plan_id | Billing plan ID | `string` | `` | yes |
| name | Cloudexport entry name in Kentik | `string` | `` | yes |

## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Network Security groups that logs will be gathered from |
| subscription_id | Subscription Id |
| resource_group_names | Resource group names |
| storage_accounts | Storage account names where logs will be gathered |
| principal_id | Principal ID created for Kentik NSG Flow Exporter application |
