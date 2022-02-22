# Multiple Resource Groups

This example creates cloud export configuration for all Network Security Groups in requested Resource Groups.

## Requirements (in addition to [module requirements](../../README.md#requirements))

None.

## Prepare

1. Prepare configuration in [terraform.tfvars](./terraform.tfvars) file. Example:
    ```hcl
    # Azure
    subscription_id = "a37491e5-fdc6-4fad-96ce-ec33c4f7e99d"
    location = "eastus"
    resource_group_names = ["resource-group-1", "resource-group-2", "resource-group-3"] # groups must exist in selected location
    storage_account_names = []
    
    # Kentik
    email = "dummy@test.mail"
    token = "dummy_token"
    plan_id = "12345"
    name = "testexport"
    ```
1. Log into Azure account using Azure CLI - [Logging-in](https://docs.microsoft.com/en-us/cli/azure/authenticate-azure-cli)
    ```bash
    az login
    ```

1. Execute:
    ```bash
    virtualenv venv && source venv/bin/activate
    pip install -r ../../requirements.txt
    terraform init
    ```

## Usage

Execute:
```bash
terraform apply
```


## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| [variables.tf](./variables.tf) | Terraform configuration | `HCL file` | [terraform.tfvars](./terraform.tfvars ) | yes |

## Outputs

| Name | Description |
|------|-------------|
| [output.tf](./output.tf) | Terraform output attributes |
