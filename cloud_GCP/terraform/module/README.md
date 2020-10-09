# GCP Kentik integration Terraform module

Terraform module which creates GCP resources required for Kentik to enable integration

Module enables:
* Flow logs in egzisting subnets acording to [Kentik documentation](https://kb.kentik.com/Fc12.htm#Fc12-Enable_VPC_Flow_Logs)

Module creates:
* Sinks to gather logs acording to [Kentik documentation](https://kb.kentik.com/Fc12.htm#Fc12-Create_a_New_Topic)
* IAM binding of publisher role to each sink 
* Pub/Sub topics for logs acording to [Kentik documentation](https://kb.kentik.com/Fc12.htm#Fc12-Create_a_New_Topic)
* Pub/Sub Pull subscription for Kentik’s flow log collection application acording to [Kentik documentation](https://kb.kentik.com/Fc12.htm#Fc12-Create_a_Pull_Subscription)
* Permission for Kentik to access it from the Google Cloud account on which flow logs are collected [Kentik documentation](https://kb.kentik.com/Fc12.htm#Fc12-Set_Permissions)

## Usage

### List of subnets

```hcl
module "kentik_gcp_integration" {
  source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"
  subnets_names_list = var.subnet_names
  region = var.region
}
```

### All subnets in one network

```hcl
data "google_compute_network" "network" {
  name = var.network
}

data "google_compute_subnetwork" "subnetworks" {
  count  = "${length(data.google_compute_network.network.subnetworks_self_links)}"
  name = "${element(split("/", data.google_compute_network.network.subnetworks_self_links[count.index]), 10)}"
}

module "kentik_gcp_integration" {
  source = "github.com/kentik/config-snippets-cloud/cloud_AWS/terraform/module"
  subnets_names_list = [ for subnet in data.google_compute_subnetwork.subnetworks : subnet.name ]
  region = var.region
}
```

## Examples

* [Prepare subnets from list](examples/subnet-list)
* [Prepare all subnets from network](examples/all-network-subnets)

## Demo
* [Demo showing how add list of subnets to Kentik portal using this module](demo) (TBD)

## Note
* this project use `for_each` in code. If it is meant to be used with VPC creation, VPC should be created first for example using `terraform apply -target="(TODO)"`
* this module creates GCP resources only. This won't register VPC in Kentik platform automaticaly.

## Requirements

| Name | Version |
|------|---------|
| terraform | >=0.12.0 |
| google | >= 3.41.0 |
| null | >= 2.1.2 |

## Providers

| Name | Version |
|------|---------|
| google | >= 3.41.0 |
| null | >= 2.1.2 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| subnet_names_list | List of subnets names for which Kentik should gather logs | `list(string)` | `[]` | yes |
| region | Subnets region | `string` | `` | yes |
| topic_prefix | Pub/Sub topic prefix and subscription prefix | `string` | `kentik_topic` | no |
| sink_prefix | Prefix to use with logs sink | `string` | `kentik_pubsub_sink` | no |



## Outputs

| Name | Description |
|------|-------------|
| subscription | Subscribtion name for kentik config |