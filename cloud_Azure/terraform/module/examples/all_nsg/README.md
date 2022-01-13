# All Network Security Groups in Resource Group

Configuration in this directory creates configuration for all Network Security Group in Resource Group.

## Requirements

* Information about Azure deployment: location, resource group name, subscription ID
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
  --var resource_group_name=<resource_group> \
  --var prefix=<unique_prefix_for_azure_resources> \
  --var plan_id=<kentik_plan_id> \
  --var name=<kentik_cloudexport_name>
```


## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| subscription_id | Id of the subscription in which resource are located | `string` | `` | yes |
| resource_group_name | Name of the resource group to gather logs from | `string` | `` | yes |
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
