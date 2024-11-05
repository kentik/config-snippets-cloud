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

# Install dependencies
resource "null_resource" "install_dependencies" {
  provisioner "local-exec" {
    command = <<EOT
      virtualenv venv
      source venv/bin/activate
      pip install -r requirements.txt
    EOT
  }
}
