// Turns on flow logs in provided subnets. Uses gcloud to make changes in GCP
resource "null_resource" "test" {
  for_each = toset(var.subnets_names_list)
  provisioner "local-exec" {
    command     = "gcloud compute networks subnets update ${each.key} --enable-flow-logs --region ${var.region}"
    interpreter = ["/bin/bash", "-c"]
  }
}
