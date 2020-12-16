data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_instance" "synth_agent_test" {
  for_each = var.vm_names

  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"
  user_data_base64 = "${data.template_cloudinit_config.ksynth_cloudconfig[each.key].rendered}"
  key_name = var.key_pair_name
  iam_instance_profile = "${aws_iam_instance_profile.get_secrets_profile[each.key].name}"
  tags = {
    Name = each.key
  }
}
