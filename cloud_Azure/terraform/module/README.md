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
NetworkWatcher is automatically created by Azure when VirtualNetwork is created or updated, [as per documentation.](https://docs.microsoft.com/en-us/azure/network-watcher/network-watcher-create). This happens eg. when launching a new virtual machine.

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
| [requirements.txt](./requirements.txt) | (as specified) |

## Providers

| Name | Version |
|------|---------|
| azurerm | >= 2.85.0 |
| azuread | >= 2.14.0 |
| kentik-cloudexport | >= 0.4.1 |
| null | >= 2.1.2 |
| external | >= 2.0.0 |

## Python and dependencies

This module uses Python to gather all Network Security Groups from specified Resource Groups and expose them to Terraform as external data source.  
To install Python and required packages:
* [Install Python and PIP](https://docs.python.org/3/using/index.html)
* Install packages - in module directory, execute:  
    PowerShell:
    ```powershell
    pip install virtualenv
    virtualenv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

    or Bash:
    ```bash
    pip install virtualenv
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
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
| flow_exporter_application_id | Kentik NSG Flow Exporter application ID | `string` | `a20ce222-63c0-46db-86d5-58551eeee89f` | no |
| storage_account_names | Storage Account names to store the flow logs in. They must meet Azure Storage Account naming restrictions.<br>There should be either one Storage Account name per Resource Group name, or none (in that case, names will be generated) | `list of strings` | `[]` | no |


## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Network Security Groups which flow logs will be collected |
| subscription_id | Azure subscription ID |
| resource_group_names | Names of Resource Groups from which to collect flow logs |
| storage_accounts | Storage Account names where flow logs will be collected |
| principal_id | Service Principal ID created for Kentik NSG Flow Exporter application |