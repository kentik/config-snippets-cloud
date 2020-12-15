data "aws_secretsmanager_secret" "get_ksynth_secret" {
  for_each = var.vm_names
  name = each.value
}

resource "aws_iam_role" "get_secrets_role" {
  for_each = var.vm_names
  name = "get_secrets_role_${each.value}"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "get_secrets_policy" {
  for_each = var.vm_names
  name = "ksynth_secret_policy_${each.value}"
  role = "${aws_iam_role.get_secrets_role[each.key].id}"

  policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
        "Effect": "Allow",
        "Action": [
            "secretsmanager:GetSecretValue"
            ],
        "Resource": [
            "${data.aws_secretsmanager_secret.get_ksynth_secret[each.key].arn}"
            ]
        }
    ]
}
EOF
}

resource "aws_iam_instance_profile" "get_secrets_profile" {
  for_each = var.vm_names
  name = "get_secrets_profile_${each.value}"
  role = "${aws_iam_role.get_secrets_role[each.key].name}"
}
