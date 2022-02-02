# Azure Kentik integration Terraform module

Module supporting management of Azure and Kentik resources required for flow log export from Azure to Kentik.

Module enables:
* Flow logs in all Network Security Groups (NSG) found in requested Resource Groups

Module creates:
* Service Principal for Kentik NSG Flow Exporter application
* Reader and Contributor Roles for above mentioned Service Principal
* One Storage Account for flow logs per requested Resource Group
* Registers flow in Kentik platform per requested Resource Group

All resources created in Azure are tagged with:  
`app = "kentik_flow_log_exporter"`  

Module assumes that NetworkWatcher resource exists in NetworkWatcherRG resource group in specified Azure location (see variable "location" in [variables.tf](./variables.tf)).  
For example, in location "eastus" there should be "NetworkWatcher_eastus" in "NetworkWatcherRG" resource group.  
NetworkWatcher is automatically created by Azure when VirtualNetwork is created or updated, [as per documentation.](https://docs.microsoft.com/en-us/azure/network-watcher/network-watcher-create), this happens eg. when launching a new virtual machine.

## Usage examples

* [All Network Security Groups in requested Resource Groups in single Azure Account](examples/single_account_multiple_resource_groups)
* [All Network Security Groups in requested Resource Groups in multiple Azure Accounts](examples/multiple_accounts_multiple_resource_group)

## Demo

* [Demo showing how to add list of subnets to Kentik portal using this module](demo) (TBD)

## Requirements

| Name | Version |
|------|---------|
| terraform | >= 1.0.0 |
| python | >= 3.7.5 |
| pip | >= 20.2.4 |
| az.cli python package | >= 0.4 |
| terraform-external-data python package | >= 1.0.3 |

## Providers

| Name | Version |
|------|---------|
| azurerm | >= 2.85.0 |
| azuread | >= 2.14.0 |
| kentik-cloudexport | >= 0.4.1 |
| null | >= 2.1.2 |
| external | >= 2.0.0 |

## Python and dependencies

This module uses python to gather all Network Security Groups from specified Resource Groups and expose them to terraform as external data source.
To install python and its requirements:
* [Install Python 3](https://docs.python.org/3/using/index.html)
* [Install pip3](https://pip.pypa.io/en/stable/installing/)
* Install packages: in module directory, run:
```bash
pip3 install -r requirements.txt
```
## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| subscription_id | Azure subscription ID | `string` | `` | yes |
| location | Azure location  | `string` | `` | yes |
| resource_group_names | Resource Group names for which flow logs are to be collected | `list of strings` | `[]` | yes |
| email | Kentik account email | `string` | `` | yes |
| token | Kentik account token | `string` | `` | yes |
| plan_id | Kentik billing plan ID | `string` | `` | yes |
| name | Cloudexport entry name in Kentik | `string` | `` | yes |
| enabled | Defines if cloud export to Kentik is enabled | `bool` | true | no |
| description | Cloudexport entry description in Kentik | `string` | `Created using Terraform` | no |
| flow_exporter_application_id | Kentik NSG Flow Exporter application ID | `string` | `a20ce222-63c0-46db-86d5-58551eeee89f` | no |


## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Network Security Groups which flow logs will be collected |
| subscription_id | Azure subscription ID |
| resource_group_names | Resource Group names for which flow logs will be collected |
| storage_accounts | Storage Account names where flow logs will be collected |
| principal_id | Service Principal ID created for Kentik NSG Flow Exporter application |