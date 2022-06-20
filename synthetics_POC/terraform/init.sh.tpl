#!/bin/bash

curl -s https://packagecloud.io/install/repositories/kentik/ksynth/script.deb.sh | sudo bash
sudo apt install -y ksynth awscli

sudo systemctl stop ksynth
# shellcheck disable=SC2154,SC2140
sudo bash -c "aws secretsmanager  get-secret-value --secret-id ${secret_name} --query "SecretBinary" --output text --region us-west-1 | base64 --decode > /var/lib/ksynth/ksynth.id"

sudo systemctl start ksynth
