# Multiple Azure accounts multiple Resource Groups

This example creates cloud export configuration for all Network Security Groups in requested Resource Groups in multiple Azure accounts.  
Handling of multiple Azure accounts is possible by means of profiles.  
Profiles are stored in [profiles.ini](./profiles.ini) file.

## The process

1. Information on Azure profiles is read from [profiles.ini](./profiles.ini)
1. Iterate over the profiles:
    1. Use profile name as Terraform workspace name
    1. Create Terraform workspace and activate it
    1. Apply Terraform configuration in activated workspace

## Prepare

1. Prepare your Azure profiles in [profiles.ini](./profiles.ini)  
   Entries in this file must contain following data for all Azure Accounts and Resource Groups from which flow logs are to be collected.  
   Example:
    ```ini
    [first-profile] 
    subscription_id = abc543ce-6e3b-4f4d-83da-0f7b0762e75f
    tenant_id = 934cbdb4-6e26-7e5e-8146-f598249437a0
    principal_id = 73eb43bb-5c85-9234-b214-4fb17097a3c3
    principal_secret = rjdpGCOtUpGd12mne7W8w3dGnMLMC-PE8R
    location = eastus
    resource_group_names = dev-resource-group,test-resource-group
    storage_account_names = developmentflowlogs,testingflowlogs

    [second-profile] 
    subscription_id = e0ae040b-2d16-41ad-bd29-faaa3ec975b9
    ...
    ```

   | Name | Description | Type | Default | Required |
   |------|-------------|------|---------|:--------:|
   | subscription_id | Azure subscription ID | `string` | none | yes |
   | tenant_id | Azure Tenant ID | `string` | none | yes |
   | principal_id | Service Principal ID, see: [Azure Service Principal](./README.md#azure-service-principal) | `string` | none | yes |
   | principal_secret | Service Principal secret (aka. password), see: [Azure Service Principal](./README.md#azure-service-principal) | `string` | none | yes |
   | location | Azure location  | `string` | none | yes |
   | resource_group_names | Names of Resource Groups from which to collect flow logs | `comma-separated strings` | none | yes |
   | storage_account_names | Names of Storage Accounts for storing flow logs. Names must meet Azure Storage Account naming restrictions.<br>The list should either contain 1 Storage Account name for each Resource Group, or be empty, in which case names will be generated automatically. | `comma-separated strings` | `` | no |

1. Prepare configuration in [terraform.tfvars](./terraform.tfvars) file.  
    Example:
    ```hcl
    # Azure
    resource_tag = "flow_log_exporter"
    
    # Kentik
    email= "john.doe@example.com"
    token = "4e88742accb6f31bcb5a6fe90a068974"
    plan_id = "11467"
    name = "testexport"
    description = "Created by Terraform"
    enabled = true
    ```
    | Name | Description | Type | Default | Required |
    |------|-------------|------|---------|:--------:|
    | email | Kentik account email | `string` | none | yes |
    | token | Kentik account token | `string` | none | yes |
    | plan_id | Kentik billing plan ID | `string` | none | yes |
    | name | Cloudexport entry name in Kentik | `string` | none | yes |
    | description | Cloudexport entry description in Kentik | `string` | `Created using Terraform` | no |
    | enabled | Defines if cloud export to Kentik is enabled | `bool` | true | no |
    | resource_tag | Azure Tag value to apply to created resources | `string` | `flow_log_exporter` | no |

1. Execute:  
    PowerShell:
    ```powershell
    virtualenv venv
    .\venv\Scripts\activate
    pip install -r ..\..\requirements.txt
    pip install -r requirements.txt
    terraform init
    ```

    or Bash:
    ```bash
    virtualenv venv
    source venv/bin/activate
    pip install -r ../../requirements.txt
    pip install -r requirements.txt
    terraform init
    ```

## Usage (PowerShell or Bash)

- Execute **terraform plan** step on multiple Azure accounts:  
    ```bash
    python azure_onboarder.py plan
    ```
- Execute **terraform apply** step on multiple Azure accounts  
    ```bash
    python azure_onboarder.py apply
    ```
- Execute **terraform destroy** step on multiple Azure accounts  
    ```bash
    python azure_onboarder.py destroy
    ```
- Execute **terraform plan** step on multiple Azure accounts, custom profiles file:  
    ```bash
    python azure_onboarder.py --filename custom_profiles.ini plan
    ```
- Help  
    ```bash
    python azure_onboarder.py --help
    ```

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| [profiles.ini](./profiles.ini) | List of Azure profiles | `INI file` | none | yes |
| [variables.tf](./variables.tf) | Terraform configuration | `HCL file` | [terraform.tfvars](./terraform.tfvars ) | yes |

## Outputs

| Name | Description |
|------|-------------|
| (none) |

## Azure Service Principal

Terraform requires Service Principal with "Owner" role and "Application.ReadWrite.All" permission to assign roles and create resources in the Azure Account.   
Terraform will use the principal_id and principal_secret credentials loaded from [profiles.ini](./profiles.ini) to authenticate into Azure Account. 

### Create Service Principal using Azure CLI (`az`)

```sh
# login as privileged user
az login

# create service principal. Write down the outputted appId and password. These are your principal_id_ and principal_secret
az ad sp create-for-rbac --role="Owner" --scopes="/subscriptions/<azure subscription id>" --name KentikTerraformOnboarder

# add Application.ReadWrite.All permission (1bfefb4e-e0b5-418b-a88f-73c46d2cc8e9) in Microsoft Graph API (00000003-0000-0000-c000-000000000000) to just created service principal
az ad app permission add --id <service principal id> --api-permissions 1bfefb4e-e0b5-418b-a88f-73c46d2cc8e9=Role --api 00000003-0000-0000-c000-000000000000

# activate the newly added permission
az ad app permission grant --id <service principal id> --api 00000003-0000-0000-c000-000000000000
az ad app permission admin-consent --id <service principal id>
```

## Profiles tool

The profiles_tool.py tool allows semi-automatic addition of profiles to the profiles.ini file.  
For every specified profile name, it will:
- login you to Azure Account
- lookup required ServicePrincipal, or create one if it doesn't exist yet
- ask for Azure location
- ask to select Resource Groups from the list

On every execution the tool creates backup copy of the profiles file in directory `backup_profiles` (the directory is created if it does not exist) and stores new/updated set of profiles.
### Usage (PowerShell or Bash)

- Add multiple profiles to `profiles.ini` - interactively ask user for profile names:  
    ```bash
    python profiles_tool.py add 
    ```
- Add multiple profiles to `profiles.ini` - profile names specified on command line:  
    ```bash
    python profiles_tool.py add --profiles dev test prod
    ```
- Add multiple profiles to `profiles.ini` - verbose logging:  
    ```bash
    python profiles_tool.py add --verbose
    ```
- Add multiple profiles to custom file:  
    ```bash
    python profiles_tool.py add --filename custom_profiles.ini
    ```
- Only fill missing profiles information in `profiles.ini` - ask user for data if needed:  
    ```bash
    python profiles_tool.py complete
    ```
- Validate profiles information in `profiles.ini`:  
    ```bash
    python profiles_tool.py validate
    ```
- Help  
    ```bash
    python profiles_tool.py --help
    ```