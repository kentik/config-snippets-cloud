# Azure Kentik integration Terraform module

Module supporting management of Azure and Kentik resources required for flow log export from Azure to Kentik.

Module enables:
* Flow logs in all Virtual Networks (VNets) found in requested Resource Groups

Module creates:
* Service Principal for Kentik VNet Flow Exporter application
* Reader and Contributor Roles for above mentioned Service Principal
* One Storage Account for flow logs per requested Resource Group
* Registers flow in Kentik platform per requested Resource Group

All resources created in Azure are tagged, see variable "resource_tag" in [variables.tf](./variables.tf)

Module assumes that NetworkWatcher resource exists in NetworkWatcherRG resource group in specified Azure location (see variable "location" in [variables.tf](./variables.tf)).
For example, in location "eastus" there should be "NetworkWatcher_eastus" in "NetworkWatcherRG" resource group.
NetworkWatcher is automatically created by Azure when VirtualNetwork is created or updated, [as per documentation.](https://docs.microsoft.com/en-us/azure/network-watcher/network-watcher-create). This happens eg. when launching a new virtual machine.

## Usage examples

* [All Network Security Groups in requested Resource Groups in single Azure Account](examples/single_account_multiple_resource_groups)
* [All Network Security Groups in requested Resource Groups in multiple Azure Accounts](examples/multiple_accounts_multiple_resource_group)

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.0.0 |
| python | >= 3.7.5 |
| pip | >= 20.2.4 |

## Providers

| Name | Version |
|------|---------|
| azurerm | >= 2.85.0 |
| azuread | >= 2.14.0 |
| kentik-cloudexport | >= 0.4.1 |
| null | >= 2.1.2 |
| external | >= 2.0.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| subscription_id | Azure subscription ID | `string` | none | yes |
| location | Azure location  | `string` | none | yes |
| resource_group_names | Names of Resource Groups from which to collect flow logs | `list of strings` | none | yes |
| email | Kentik account email | `string` | none | yes |
| token | Kentik account token | `string` | none | yes |
| plan_id | Kentik billing plan ID | `string` | none | yes |
| name | Cloudexport entry name in Kentik | `string` | none | yes |
| enabled | Defines if cloud export to Kentik is enabled | `bool` | true | no |
| description | Cloudexport entry description in Kentik | `string` | `Created using Terraform` | no |
| resource_tag | Azure Tag value to apply to created resources | `string` | `flow_log_exporter` | no |
| flow_exporter_application_id | Kentik VNet Flow Exporter application ID | `string` | `a20ce222-63c0-46db-86d5-58551eeee89f` | no |
| storage_account_names | Names of Storage Accounts for storing flow logs. Names must meet Azure Storage Account naming restrictions.<br>The list should either contain 1 Storage Account name for each Resource Group, or be empty, in which case names will be generated automatically. | `list of strings` | `[]` | no |


## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Virtual Networks which to collect flow logs |
| subscription_id | Azure subscription ID |
| resource_group_names | Names of Resource Groups from which to collect flow logs |
| storage_accounts | Storage Account names where flow logs will be collected |
| principal_id | Service Principal ID created for Kentik VNet Flow Exporter application |
