resource "aws_iam_role" "kentik_role" {
  count                 = var.create_role ? 1 : 0
  name                  = "${var.iam_role_prefix}TerraformIngestRole"

  description           = "This role allows Kentik to ingest the VPC flow logs."
  force_detach_policies = true
  tags = {
    Provisioner = "Terraform"
  }
  assume_role_policy = templatefile(
    "${path.module}/templates/kentikIngestRole.json.tmpl", {
      external_id = var.external_id
    }
  )
}

resource "aws_iam_policy" "kentik_ec2_access" {
  count       = var.create_role ? 1 : 0
  name        = "${var.iam_role_prefix}EC2Access"
  description = "Defines required accesses for Kentik platform to EC2 resources"
  path        = "/"
  policy      = file("${path.module}/files/kentikEC2Access.json")
}

resource "aws_iam_policy" "kentik_s3_policy" {
  count       = var.create_role ? 1 : 0
  name        = "${var.iam_role_prefix}S3PolicyAccess"
  description = "Defines accesses for Kentik platform to S3 resources"
  path        = "/"
  policy = templatefile(
    "${path.module}/templates/kentikS3Policy.json.tmpl",
    {
      actions_list = (var.rw_s3_access == false ? ["s3:Get*", "s3:List*", "s3:HeadBucket"] : ["s3:*"]),
      buckets_list = [for bucketobject in aws_s3_bucket.vpc_logs : bucketobject.arn],
      sub_path     = (var.s3_flowlogs_path == "" ? "*" : "${var.s3_flowlogs_path}/*")
    }
  )
}

resource "aws_iam_policy_attachment" "kentik_s3_access" {
  count      = var.create_role ? 1 : 0
  name       = "${var.iam_role_prefix}-s3-access"
  roles      = [aws_iam_role.kentik_role[count.index].name]
  policy_arn = aws_iam_policy.kentik_s3_policy[count.index].arn
}

resource "aws_iam_policy_attachment" "kentik_ec2_access" {
  count      = var.create_role ? 1 : 0
  name       = "${var.iam_role_prefix}-ec2-access"
  roles      = [aws_iam_role.kentik_role[count.index].name]
  policy_arn = aws_iam_policy.kentik_ec2_access[count.index].arn
}
