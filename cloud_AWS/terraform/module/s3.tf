resource "aws_s3_bucket" "vpc_logs" {
  for_each = toset(var.vpc_id_list)
  bucket = join("-",[var.s3_bucket_prefix,each.key,"flow-logs"])
  acl = "private"
}

resource "aws_s3_bucket_public_access_block" "vpc_logs" {
  for_each = toset(var.vpc_id_list)
  bucket = aws_s3_bucket.vpc_logs[each.key].id
  block_public_acls = true
  block_public_policy = true
  restrict_public_buckets = true
  ignore_public_acls = true
}

resource "aws_flow_log" "vpc_logs" {
  for_each = toset(var.vpc_id_list)
  log_destination = aws_s3_bucket.vpc_logs[each.key].arn
  log_destination_type = "s3"
  traffic_type = "ALL"
  vpc_id = each.key
}
