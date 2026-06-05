# OCI Kentik Integration Terraform Module

Module supporting management of OCI and Kentik resources required for VCN flow logs export from OCI to Kentik.

Module creates:
* Object Storage bucket to receive VCN flow logs
* OCI Logging Log Group to aggregate flow logs
* Capture Filter to control flow log sampling rate
* OCI Logging Log resource per VCN (enables flow log collection)
* Service Connector Hub connector to route logs from the Log Group to the bucket
* IAM Group and optional IAM User with API key for Kentik access
* IAM Policies granting Kentik read access to OCI resources and networking metadata
* Registers the OCI cloud in the Kentik portal via the `kentik-cloudexport` provider

## Usage examples

* [Single VCN](examples/single-vcn) — export flow logs from a single VCN in a single OCI region

## Requirements

| Name | Version |
|------|---------|
| terraform | >=1.0.0 |
| oracle/oci provider | ~>5.0 |
| kentik-cloudexport provider | ~>0.4 |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| tenancy\_id | OCI Tenancy OCID | `string` | | yes |
| compartment\_id | OCI Compartment OCID for resource creation. Defaults to tenancy root. | `string` | `""` | no |
| region | OCI region (e.g. `us-ashburn-1`) | `string` | | yes |
| vcn\_id\_list | List of VCN OCIDs for which Kentik should gather flow logs | `list(string)` | | yes |
| bucket\_name\_prefix | Prefix for the Object Storage bucket name | `string` | `kentik` | no |
| object\_name\_prefix | Prefix for flow log objects in the bucket | `string` | `flow-logs` | no |
| create\_user | If true, creates an OCI IAM user for Kentik access | `bool` | `true` | no |
| iam\_prefix | Prefix for IAM resource names | `string` | `kentik` | no |
| kentik\_user\_email | Email address for the OCI IAM user created for Kentik access. Required when `create_user` is true. | `string` | `""` | no |
| kentik\_api\_public\_key | Kentik public key for OCI API authentication (from Kentik portal). Required when `create_user` is true. | `string` | `""` | no |
| flow\_log\_sampling\_rate | Flow log sampling rate as a percentage (1–100) | `number` | `100` | no |
| log\_prefix | Prefix for Log Group, capture filter, and log resource names | `string` | `kentik` | no |
| name | Cloudexport entry name in Kentik | `string` | `terraform_oci_exported_cloud` | no |
| enabled | If cloud exported to Kentik is enabled | `bool` | `true` | no |
| description | Cloudexport entry description in Kentik | `string` | `""` | no |
| plan\_id | Kentik billing plan ID. When empty, Kentik registration is skipped. | `string` | `""` | no |

## Outputs

| Name | Description |
|------|-------------|
| bucket\_name | Name of the Object Storage bucket receiving flow logs |
| bucket\_namespace | Object Storage namespace |
| log\_group\_id | OCID of the Log Group created for VCN flow logs |
| service\_connector\_id | OCID of the Service Connector routing flow logs to Object Storage |
| kentik\_group\_id | OCID of the IAM group created for Kentik access |
| kentik\_user\_id | OCID of the IAM user created for Kentik access (null if `create_user` is false) |

## How to run

### 1. Gather OCI values from the Console

| Value | Where to find it |
|-------|-----------------|
| Tenancy OCID | Identity > Tenancy |
| User OCID | Identity > Users > your user |
| API key fingerprint + private key | Identity > Users > your user > API Keys |
| Compartment OCID | Identity > Compartments (leave empty to use tenancy root) |
| VCN OCID(s) | Networking > Virtual Cloud Networks |

### 2. Set Kentik API credentials

```bash
export KTAPI_AUTH_EMAIL=you@example.com
export KTAPI_AUTH_TOKEN=your-kentik-api-token
```

### 3. Create a tfvars file

Navigate to the example directory and create `terraform.tfvars`:

```bash
cd examples/single-vcn
```

```hcl
tenancy_id           = "ocid1.tenancy.oc1..aaaa..."
compartment_id       = "ocid1.compartment.oc1..aaaa..."
region               = "us-ashburn-1"
vcn_id_list          = ["ocid1.vcn.oc1.iad.aaaa..."]

oci_user_id          = "ocid1.user.oc1..aaaa..."
oci_fingerprint      = "xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
oci_private_key_path = "~/.oci/oci_api_key.pem"

plan_id              = "your-kentik-plan-id"
name                 = "my-oci-export"
```

Leave `plan_id` empty (`""`) to skip Kentik registration and only provision OCI resources.

### 4. Apply

```bash
terraform init
terraform plan
terraform apply
```

### 5. Upload the Kentik API public key (when create_user = true)

After the first apply, the Kentik IAM user exists in OCI. To complete authentication:

1. Go to Kentik portal → Settings → Cloud Exports → your OCI export
2. Download the Kentik public key
3. Add it to `terraform.tfvars`:
   ```hcl
   kentik_api_public_key = "-----BEGIN PUBLIC KEY-----\n..."
   ```
4. Run `terraform apply` again to upload the key to the user's API Keys

### 6. Tear down

```bash
terraform destroy
```

## Notes

### IAM user vs cross-tenancy policy
By default (`create_user = true`) the module creates a dedicated OCI IAM user and uploads the Kentik API public key. Alternatively, set `create_user = false` and follow the cross-tenancy policy instructions in the [Kentik OCI documentation](https://kb.kentik.com/docs/kentik-for-oci) to authorize Kentik's tenant directly — no custom user needed.

### OCI Identity Domains
If your OCI tenancy uses Identity Domains (OCI IAM with Identity Domain), you may need to manage users through `oci_identity_domains_user` instead. The group and policy resources in this module use the legacy `oci_identity_*` resources which work for both domain types in most configurations.

### Capture filter association
The capture filter created by this module defines the sampling rules. OCI associates the capture filter with the VCN flow logs when you set it during flow log enablement. If you need to update the capture filter linked to an existing flow log, use the OCI Console under Networking > Network Command Center > Flow Logs.
