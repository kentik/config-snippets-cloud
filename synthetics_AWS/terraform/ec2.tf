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

  owners = ["099720109477"]
}

resource "aws_instance" "instance" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t2.micro"

  iam_instance_profile =  var.iam_instance_profile
  key_name = var.key_name
  vpc_security_group_ids = var.vpc_security_group_ids
  subnet_id = var.subnet_id

  user_data = <<EOF
#!/bin/bash
curl -s https://packagecloud.io/install/repositories/kentik/ksynth/script.deb.sh | sudo bash
apt-get install ksynth
echo "KENTIK_COMPANY=${var.plan_id}" >> /etc/default/ksynth
systemctl start ksynth
systemctl stop ksynth && systemctl start ksynth
EOF

  tags = {
    Name = "ksynth_agent"
  }
}