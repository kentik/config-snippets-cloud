## Preserving ksynth instance identity across VM rebuild


The `ksynth.id` file contains unique identity for a `ksynth` instance. It needs to be preserved across VM upgrade in order to keep the instance associated with the tracking data in Kentik.

In case of `ksynth` hosted in AWS VM, this can be achieved by storing the `ksynth.id` in AWS Secrets Manager, using following steps:
- install AWS CLI on your workstation [install aws-cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) and configure it for the target account (`aws configure`)
- copy `ksynth.id` from the running VM to your local workstation: `scp <ksynth_VM>:/var/lib/ksynth/ksynth.id <ksynth_instance_name>.id`
- create entry in AWS Secrets Manager: `aws secretsmanager create-secret --name <ksynth_instance_name> --secret-binary fileb:<ksynth_instance_name>.id`

Note that you have to use unique `ksynth_instance_name` for each unique `ksynth` instance (i.e. for each instance represented as a separate agent in Kentik. The `ksynth.id` identity cannot be shared among instances.
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
