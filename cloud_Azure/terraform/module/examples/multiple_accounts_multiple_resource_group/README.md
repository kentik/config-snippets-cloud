# Multiple Azure accounts multiple Resource Groups

This example creates cloud export configuration for all Network Security Groups in requested Resource Groups in multiple Azure accounts.  
Handling of multiple Azure accounts is possible by means of profiles.  
Profiles are stored in [profiles.ini](./profiles.ini) file. For example:
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

## The process

1. Information on Azure profiles is read from [profiles.ini](./profiles.ini)
1. Iterate over the profiles:
    1. Use profile name as Terraform workspace name
    1. Create Terraform workspace and activate it
    1. Apply Terraform configuration in activated workspace

## Requirements (in addition to [module requirements](../../README.md#requirements))

None.

## Prepare

1. Prepare your Azure profiles in [profiles.ini](./profiles.ini)  
   These profiles should represent details of Azure accounts and Resource Groups from which to collect flow logs.  
   For `principal_id` and `principal_secret`, see: [Azure Service Principal](./README.md#azure-service-principal)
1. Prepare configuration in [terraform.tfvars](./terraform.tfvars) file. Example:
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
    python tf_multi_exec.py plan
    ```
- Execute **terraform apply** step on multiple Azure accounts  
    ```bash
    python tf_multi_exec.py apply
    ```
- Execute **terraform destroy** step on multiple Azure accounts  
    ```bash
    python tf_multi_exec.py destroy
    ```
- Help  
    ```bash
    python tf_multi_exec.py --help
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

For Terraform to authenticate and make changes in Azure account, a Service Principal with Owner role and Application.ReadWrite.All permission is required to assign roles and create resources.  
Terraform will use the principal_id and principal_secret credentials loaded from [profiles.ini](./profiles.ini) to authenticate into Azure Account. 

### Create Service Principal using az cli

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