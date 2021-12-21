# All Network Security Groups in Resource Group

Configuration in this directory creates configuration for all Network Security Group in Resource Group.

## Usage

To run this example you need to execute:
```
$ terraform init
$ terraform plan
$ terraform apply
```

## Requirements

* Example requires location, resource group name, principal id, subscription
* Installed az-cli - [Installation](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
* Logged-in az-cli - [Logging-in](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli)
    ```bash
    az login # default web browser should open with login page
    ```
* Kentik API credentials present in execution environment:
  ```bash
  export KTAPI_AUTH_EMAIL="joe.doe@email.com"
  export KTAPI_AUTH_TOKEN="token123"
  ```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| subscription_id | Id of the subscription in which resource are located | `string` | `` | yes |
| resource_group_name | Name of the resource group to gather logs from | `string` | `` | yes |
| principal_id | Id of the Service Principal Id for kentik app connection | `string` | `` | yes |

## Outputs

| Name | Description |
|------|-------------|
| network_security_groups | Id's of the Network Security groups that logs will be gathered from |
| subscription_id | Subscription Id |
| resource_group | Resource group name |
| storage_account | Storage account name where logs will be gathered |
