# Subnet list

Configuration in this directory creates configuration for subnet list.

## Usage

To run this example you need to execute:
```
$ terraform init
$ terraform plan
$ terraform apply
```

## Requirements

* Example requires subnet name
* Installed and logged Google CLoud SDK [Installation](https://cloud.google.com/sdk/docs/install) [Logging](https://cloud.google.com/sdk/gcloud/reference/auth/activate-service-account)

## Inputs

| Name | Description | Type |
|------|-------------|------|
| project | GCP project to use| `string` |
| region | GCP region to use | `string` |
| credentials | Credentials json file to log in to GCP | `string` |
| subnet_names | List of subnet names to gather logs | `list(string)` |
| name | Cloudexport entry name in Kentik | `string` |
| description | Cloudexport entry description in Kentik | `string` |
| plan\_id | Kentik billing plan ID | `string` |

## Outputs

| Name | Description |
|------|-------------|
| kentik_subscription | Name of the subscription |
| project | Name of the project |