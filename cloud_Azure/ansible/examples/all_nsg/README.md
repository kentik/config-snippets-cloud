# All Network Security Groups in Resource Group

Configuration in this directory creates configuration for all Network Security Group in Resource Group.

## Usage

To run this example you need to:
* Authorize access to Azure for Kentik. You can do this on ["Add cloud" dialog](https://portal.kentik.com/v4/settings/clouds)
* execute:
```
$ ansible-playbook main.yml
```

## Requirements

* Example requires location, resource group name and subscription id
* Installed and logged az-cli [Installation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) [Logging](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli)

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| kentik\_az\_resourcegroupname | Name of the resource group to gather logs from | `string` | `` | yes |
| kentik\_az\_principal\_id | Id of the Service Principal Id for kentik app connection | `string` | `` | yes |

## Outputs

| Name | Description |
|------|-------------|
| Subscription ID | Subscription Id |
| Resource Group | Resource group name |
| Location | Name of used location |
| Storage Account Name | Storage account name where logs will be gathered |
