# Single VCN — OCI Kentik integration example

Exports flow logs from a single VCN to Kentik using the OCI Kentik integration module.

## What this creates

* Object Storage bucket for flow logs
* Log Group + Capture Filter + OCI Logging Log for the target VCN
* Service Connector routing logs from the Log Group to the bucket
* IAM group, user, and policies for Kentik access
* Kentik Cloud Export entry (when `plan_id` is provided)

## Usage

1. Copy `terraform.tfvars.example` to `terraform.tfvars` and fill in your values.

2. Set Kentik API credentials as environment variables:
   ```
   export KTAPI_AUTH_EMAIL=<your-kentik-email>
   export KTAPI_AUTH_TOKEN=<your-kentik-api-token>
   ```

3. Run Terraform:
   ```
   terraform init
   terraform plan
   terraform apply
   ```

## Variables

See [variables.tf](variables.tf) for all inputs. Minimum required values:

```hcl
tenancy_id           = "ocid1.tenancy.oc1..xxxx"
region               = "us-ashburn-1"
vcn_id_list          = ["ocid1.vcn.oc1.iad.xxxx"]
oci_user_id          = "ocid1.user.oc1..xxxx"
oci_fingerprint      = "xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx:xx"
oci_private_key_path = "~/.oci/oci_api_key.pem"

# From Kentik portal
plan_id              = "your-kentik-plan-id"
kentik_api_public_key = "-----BEGIN PUBLIC KEY-----\n..."
```
