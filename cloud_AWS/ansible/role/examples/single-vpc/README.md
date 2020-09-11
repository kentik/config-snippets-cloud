# Single VPC

Configuration in this directory enables integration for a single VPC.

## Usage

To run this example you need to execute:
```bash
$ ansible-playbook main.yml -i inventory.yml
```

## Requirements

The example requires a single-element VPC ID list. Input the ID of your VPC into:
```yaml
vpc_id_list: []
```

in the `main.yml` file.

## Outputs

Successful run will produce an output similar to the following:
```json
"msg": [
        "S3 Buckets ARNs: ['arn:aws:s3:::kentik-vpc-081ec835f3EXAMPLE-flow-logs']",
        "IAM Role ARN: arn:aws:iam::000000000000:role/KentikAnsibleIngestRole"
    ]
```

