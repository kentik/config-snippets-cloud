# All Network Security Groups in requested Resource Groups

This example creates cloud export configuration for all Network Security Groups in requested Resource Groups.

## Requirements

* Information about Azure deployment: location, resource group names, subscription ID
* Information about Kentik subscription: plan ID
* Azure CLI - [Installation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
* Authenticating Azure CLI to your account - [Logging-in](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli)
* Kentik API credentials present in execution environment:
  ```bash
  export KTAPI_AUTH_EMAIL="joe.doe@email.com"
  export KTAPI_AUTH_TOKEN="token123"
  ```

## Usage

To run this example you need to execute:
```
$ terraform init
$ terraform apply \  
  --var subscription_id=<azure_subscription_id> \  
  --var location=<azure_location> \
  --var resource_group_names=<resource_group_names> \
  --var prefix=<unique_prefix_for_azure_resources> \
  --var plan_id=<kentik_plan_id> \
  --var name=<kentik_cloudexport_name>
```


## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| subscription_id | Id of the subscription in which resource are located | `string` | `` | yes |
| resource_group_names | List of Resource Group names to gather logs from | `list of strings` | `` | yes |
| prefix| Prefix for the naming resources | `string` | `` | yes |
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
