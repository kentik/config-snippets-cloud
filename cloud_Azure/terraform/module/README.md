# Azure Kentik integration Terraform module

Terraform module which creates Azure resources required for Kentik to enable integration

Module enables:
* Flow logs in existing Network Security Groups

Module creates:


## Usage

### All Network Security Groups in Resource Group

```hcl
module kentik_azure_integration {
  source  = "../../"
  location = var.location
  resource_group_name = var.resource_group_name
  principal_id = var.principal_id
  subscription_id = var.subscription_id
}
```

## Examples

* [All Network Security Groups in Resource Group](examples/all_nsg)

## Demo
* [Demo showing how to add list of subnets to Kentik portal using this module](demo) (TBD)

## Note
* this module creates Azure resources only. This won't register resources in Kentik platform automatically.

## Requirements

| Name | Version |
|------|---------|
| terraform | >=0.12.0 |
| azurem provider | >= =2.20.0 |
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

## Providers

| Name | Version |
|------|---------|
| azurem | >= =2.20.0 |
| null | >= 2.1.2 |
| external | >= 2.0.0 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| subscription_id | Id of the subscription in which resource are located | `string` | `` | yes |
| resource_group_name | Name of the resource group to gather logs from | `string` | `` | yes |
| principal_id | Id of the Service Principal Id for kentik app connection | `string` | `` | yes |
| prefix| Prefix for the naming resources created by this module | `string` | `kentik` | no |



## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Network Security groups that logs will be gathered from |
| subscription_id | Subscription Id |
| resource_group | Resource group name |
| storage_account | Storage account name where logs will be gathered |
