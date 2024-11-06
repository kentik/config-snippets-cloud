# Enable network watcher feature
resource "null_resource" "feature_allow_watcher" {
  provisioner "local-exec" {
    command = "az feature register --namespace Microsoft.Network --name AllowNetworkWatcher"
  }

  provisioner "local-exec" {
    command = "az provider register -n Microsoft.Network"
  }
}

# Enable Microsoft Insights
resource "null_resource" "feature_insights_register" {
  provisioner "local-exec" {
    command = "az provider register -n Microsoft.Insights"
  }
}
