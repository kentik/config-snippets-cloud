data "template_file" "ksynth_install_script" {
  for_each = var.vm_names
  template = "${file("init.sh.tpl")}"

  vars = {
    secret_name = each.value
  }
}

data "template_cloudinit_config" "ksynth_cloudconfig" {
  for_each = var.vm_names
  gzip          = true
  base64_encode = true

  # Main cloud-config configuration file.
  part {
    content_type = "text/x-shellscript"
    content      = "${data.template_file.ksynth_install_script[each.key].rendered}"
  }
}
