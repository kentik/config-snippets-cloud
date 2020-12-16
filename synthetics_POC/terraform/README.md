## Create secret from existing ksynth installation

To create a secret that can be used in terraform automation script for new instances you have to follow this steps:
- ssh in to VM which has ksynth agent installed
- [install aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html)
- run `aws configure` to log in to AWS account that you will use to store secrets. It must be the same that VM's run on.
- run `aws secretsmanager create-secret --name <secret_name> --secret-binary fileb:///var/lib/ksynth/ksynth.id`

## Run terraform

- create tfvars file
    ```
    vm_names     = {
        "<instance_name_1>" = "<secret_name_1>"
        "<instance_name_n>" = "<secret_name_n>"
    }
    key_pair_name = "<ssh_key_name>"
    ```
- `terraform init`
- `terraform apply --var-file=example.tfvars`
