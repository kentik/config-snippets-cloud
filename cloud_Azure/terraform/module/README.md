# Azure Kentik integration Terraform module

Terraform module, which creates Azure and Kentik resources, for Azure cloud integration in Kentik.  

Module enables:
* Flow logs in all Network Security Groups (NSG) found in requested Resource Groups

Module creates:
* Service Principal for Kentik NSG Flow Exporter application
* Reader and Contributor Roles for above mentioned Service Principal
* One Storage Account for flow logs per requested Resource Group
* One Flow log per NSG across all requested Resource Groups
* Registers flow in Kentik platform per requested Resource Group according to [Kentik documentation](https://kb.kentik.com/v0/Bd08.htm#Bd08-Azure_Logging_Setup_Overview).

All created resources are tagged with:  
`app = "kentik_flow_log_exporter"`  

Module assumes that NetworkWatcher resource exists in NetworkWatcherRG resource group in specified Azure location (see variable "location"). It is automatically created by Azure when VirtualNetwork is created or updated, [as per documentation.](https://docs.microsoft.com/en-us/azure/network-watcher/network-watcher-create)

## Usage

### All Network Security Groups in Resource Group

```hcl
module kentik_azure_integration {
  source  = "../../"
  location = var.location
  subscription_id = var.subscription_id
  resource_group_names = var.resource_group_names
  prefix = var.prefix
  plan_id = var.plan_id
  name = var.name
}
```

## Examples

* [All Network Security Groups in requested Resource Groups](examples/all_nsg)

## Demo
* [Demo showing how to add list of subnets to Kentik portal using this module](demo) (TBD)

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.0.0 |
| azurerm provider | >= 2.85.0 |
| azuread provider | >= 2.14.0 |
| kentik-cloudexport provider | >= 0.4.1 |
| null provider | >= 2.1.2 |
| external provider | >= 2.0.0 |
| python | >= 3.7.5 |
| pip | >= 20.2.4 |
| az.cli python package | >= 0.4 |
| terraform-external-data python package | >= 1.1.0 |

### Python and dependencies

This module uses python to gather all NSG from Resource Groups and expose it to terraform as external data source.
To install python and its requirements:
* [Install Python 3](https://docs.python.org/3/using/index.html)
* [Install pip3](https://pip.pypa.io/en/stable/installing/)
* Install packages: run `pip3 install -r ../../requirements.txt` in example directory

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| subscription_id | Id of the subscription in which resource are located | `string` | `` | yes |
| resource_group_names | List of Resource Group names to gather logs from | `list of strings` | `` | yes |
| prefix| Prefix for the naming resources created by this module | `string` | `` | yes |
| plan_id | Billing plan ID | `string` | `` | yes |
| name | Cloudexport entry name in Kentik | `string` | `` | yes |
| flow_exporter_application_id | Kentik NSG Flow Exporter application ID | `string` | `a20ce222-63c0-46db-86d5-58551eeee89f` | no |
| enabled | Defines if cloud export to Kentik is enabled | `bool` | true | no |
| description | Cloudexport entry description in Kentik | `string` | `` | no |


## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Network Security groups that logs will be gathered from |
| subscription_id | Subscription Id |
| resource_group_names | Resource group names |
| storage_accounts | Storage account names where logs will be gathered |
| principal_id | Principal ID created for Kentik NSG Flow Exporter application |