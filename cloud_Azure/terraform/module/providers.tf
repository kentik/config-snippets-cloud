# Enable network watcher feature
resource "null_resource" "feature_allow_watcher" {
  provisioner "local-exec" {
    command     = "az feature register --namespace Microsoft.Network --name AllowNetworkWatcher && az provider register -n Microsoft.Network"
    interpreter = ["/bin/bash", "-c"]
  }
}

# Enable Microsoft Insights
resource "null_resource" "feature_insights_register" {
  provisioner "local-exec" {
    command     = "az provider register -n Microsoft.Insights"
    interpreter = ["/bin/bash", "-c"]
  }
}