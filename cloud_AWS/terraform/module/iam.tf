resource "aws_iam_role" "kentik_role" {
  name                  = "${var.iam_role_prefix}TerraformIngestRole"
  description           = "This role allows Kentik to ingest the VPC flow logs."
  force_detach_policies = true
  tags = {
    Provisioner = "Terraform"
  }
  assume_role_policy = file("${path.module}/files/kentikIngestRole.json")
}

resource "aws_iam_policy" "kentik_ec2_access" {
  name        = "${var.iam_role_prefix}EC2Access"
  description = "Defines required accesses for Kentik platform to EC2 resources"
  path        = "/"
  policy      = file("${path.module}/files/kentikEC2Access.json")
}

resource "aws_iam_policy" "kentik_s3_ro_access" {
  name        = "${var.iam_role_prefix}S3ROAccess"
  description = "Defines read-only accesses for Kentik platform to S3 resources"
  path        = "/"
  policy      = templatefile("${path.module}/templates/kentikS3RO.json.tmpl",{buckets_list = [for bucketobject in aws_s3_bucket.vpc_logs : bucketobject.bucket]})
}

resource "aws_iam_policy" "kentik_s3_rw_access" {
  name        = "${var.iam_role_prefix}S3RWAccess"
  description = "Defines read-write accesses for Kentik platform to S3 resources"
  path        = "/"
  policy      = templatefile("${path.module}/templates/kentikS3RW.json.tmpl",{buckets_list = [for bucketobject in aws_s3_bucket.vpc_logs : bucketobject.bucket]})

}

resource "aws_iam_policy_attachment" "kentik_s3_access" {
  name       = "${var.iam_role_prefix}-s3-access"
  roles      = [aws_iam_role.kentik_role.name]
  policy_arn = (var.rw_s3_access == true ? aws_iam_policy.kentik_s3_rw_access.arn : aws_iam_policy.kentik_s3_ro_access.arn)
}

resource "aws_iam_policy_attachment" "kentik_ec2_access" {
  name       = "${var.iam_role_prefix}-ec2-access"
  roles      = [aws_iam_role.kentik_role.name]
  policy_arn = aws_iam_policy.kentik_ec2_access.arn
}
