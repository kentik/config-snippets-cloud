# OCI Kentik Integration

Terraform module for exporting VCN flow logs from Oracle Cloud Infrastructure (OCI) to Kentik.

The module provisions all required OCI resources and registers the cloud export in the Kentik portal.

## Documentation

* [Kentik for OCI](https://kb.kentik.com/docs/kentik-for-oci)
* [Terraform module](terraform/module/README.md)

## How to run

### Prerequisites

- Terraform >= 1.0
- OCI CLI configured, or an API key for the user you want Terraform to authenticate as
- Kentik API credentials (`KTAPI_AUTH_EMAIL` and `KTAPI_AUTH_TOKEN`)

### 1. Set Kentik API credentials

```bash
export KTAPI_AUTH_EMAIL=you@example.com
export KTAPI_AUTH_TOKEN=your-kentik-api-token
```

### 2. Choose or create a deployment directory

Use one of the existing environments under `terraform/deployments/`, or copy one to create a new environment:

```bash
cp -r terraform/deployments/staging terraform/deployments/myenv
```

### 3. Create your tfvars file

```bash
cd terraform/deployments/myenv
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` and fill in your OCI values:

| Field | Where to find it |
|-------|-----------------|
| `tenancy_id` | OCI Console → Identity → Tenancy |
| `compartment_id` | OCI Console → Identity → Compartments (leave empty for tenancy root) |
| `region` | OCI Console → top-right region selector (e.g. `us-ashburn-1`) |
| `vcn_id_list` | OCI Console → Networking → Virtual Cloud Networks |
| `oci_user_id` | OCI Console → Identity → Users → your user |
| `oci_fingerprint` | OCI Console → Identity → Users → your user → API Keys |
| `oci_private_key_path` | Local path to the private key matching the fingerprint above |
| `kentik_user_email` | Email address for the new OCI IAM user Kentik will use |
| `plan_id` | Kentik portal → Settings → Plans (leave empty to skip Kentik registration) |

### 4. Apply

```bash
terraform init
terraform plan
terraform apply
```

### 5. Upload the Kentik public key (when `create_user = true`)

After the first apply, the Kentik IAM user exists in OCI but has no API key yet:

1. Go to Kentik portal → Settings → Cloud Exports → your OCI export
2. Download the Kentik public key
3. Add it to `terraform.tfvars`:
   ```hcl
   kentik_api_public_key = "-----BEGIN PUBLIC KEY-----\n..."
   ```
4. Run `terraform apply` again to upload the key

### 6. Tear down

```bash
terraform destroy
```

## Quick start

See the [single-vcn example](terraform/module/examples/single-vcn) for a minimal working configuration.

## Architecture

```
VCN(s)
  │  flow logs
  ▼
OCI Logging Log Group
  │  (via capture filter sampling)
  ▼
Service Connector Hub
  │
  ▼
Object Storage Bucket ◄── Kentik reads logs from here
```
