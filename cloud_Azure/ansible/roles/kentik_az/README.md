# Azure Kentik integration Ansible role

Ansible role which creates Azure resources required for Kentik to enable integration

Role enables:
* Flow logs in existing Network Security Groups

Role creates:
* Storage account allowing access to logs for Kentik portal


## Usage

### All Network Security Groups in Resource Group

```yaml
- role: "{{ playbook_dir }}/../../roles/kentik_az/"
  vars:
    kentik_az_sub: "{{ subscription_id }}"
    kentik_az_principal_id: "{{ principal_id }}"
    kentik_az_resourcegroupname: {{ resource_group_name }}
    location: {{ location }}
```

## Examples

* [All Network Security Groups in Resource Group](../../examples/all_nsg)

## Demo
* [Demo showing how to add list of subnets to Kentik portal using this role](demo) (TBD)

## Note
* this role creates Azure resources only. This won't register resources in Kentik platform automatically.

## Requirements

| Name | Version |
|------|---------|
| python | >=3.7.0 |
| pip3 | >= 20.2.4 |
| ansible | >= 2.10.0 |
| az.cli python package | >= 0.4 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| location | Azure location of the resources to gather logs | `string` | `` | yes |
| kentik\_az\_sub | Id of the subscription in which resource are located | `string` | `` | yes |
| kentik\_az\_resourcegroupname | Name of the resource group to gather logs from | `string` | `` | yes |
| kentik\_az\_principal\_id | Id of the Service Principal Id for kentik app connection | `string` | `` | yes |
| kentik\_az\_storageaccount | Storage account name to create for logs | `string` | `export2kentik` | no |
| kentik\_az\_app\_id | Kentik Application ID | `string` | `a20ce222-63c0-46db-86d5-58551eeee89f` | no |
| kentik\_az\_installdeps | Should Ansible install dependencies using pip or not | `bool` | true | no |
| kentik\_az\_nsg\_store\_interval | Interval in minutes for logs storage | `int` | 60 | no |




## Outputs

| Name | Description |
|------|-------------|
| Subscription ID | Subscription Id |
| Resource Group | Resource group name |
| Location | Name of used location |
| Storage Account Name | Storage account name where logs will be gathered |
