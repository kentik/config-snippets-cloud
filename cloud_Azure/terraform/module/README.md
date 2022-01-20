# Azure Kentik integration Terraform module

Terraform module, which creates Azure and Kentik resources, for Azure cloud integration in Kentik.  

Module enables:
* Flow logs in existing Network Security Groups (NSG)

Module creates:
* Service Principal for Kentik NSG Flow Exporter
* Roles for above mentioned Service Principal
* Storage Account for NSG flow logs
* Network Watcher
* Registers Azure flow log export in the Kentik platform

## Usage

### All Network Security Groups in Resource Group

```hcl
module kentik_azure_integration {
  source  = "../../"
  location = var.location
  resource_group_name = var.resource_group_name
  subscription_id = var.subscription_id
  prefix = var.prefix
  plan_id = var.plan_id
  name = var.name
}
```

## Examples

* [All Network Security Groups in Resource Group](examples/all_nsg)

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

This module uses python to gather all NSG from Resource Group and expose it to terraform as external data source.
To install python and its requirements:
* [Install Python 3](https://docs.python.org/3/using/index.html)
* [Install pip3](https://pip.pypa.io/en/stable/installing/)
* Install packages: run `pip3 install -r ../../requirements.txt` in example directory

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| subscription_id | Id of the subscription in which resource are located | `string` | `` | yes |
| resource_group_name | Name of the resource group to gather logs from | `string` | `` | yes |
| prefix| Prefix for the naming resources created by this module | `string` | `` | yes |
| email | Kentik account email | `string` | `` | yes |
| token | Kentik account token | `string` | `` | yes |
| plan_id | Billing plan ID | `string` | `` | yes |
| name | Cloudexport entry name in Kentik | `string` | `` | yes |
| enabled | Defines if cloud export to Kentik is enabled | `bool` | true | no |
| description | Cloudexport entry description in Kentik | `string` | `Created using Terraform` | no |


## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Network Security groups that logs will be gathered from |
| subscription_id | Subscription Id |
| resource_group | Resource group name |
| storage_account | Storage account name where logs will be gathered |
| principal_id | Principal ID created for Kentik NSG Flow Exporter application |