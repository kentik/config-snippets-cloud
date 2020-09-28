resource "aws_s3_bucket" "vpc_logs" {
  for_each = toset(var.vpc_id_list)
  bucket   = join("-", [var.s3_bucket_prefix, each.key, "flow-logs"])
  acl      = "private"
}

resource "aws_s3_bucket_public_access_block" "vpc_logs" {
  for_each                = toset(var.vpc_id_list)
  bucket                  = aws_s3_bucket.vpc_logs[each.key].id
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}

resource "aws_flow_log" "vpc_logs" {
  for_each                 = toset(var.vpc_id_list)
  log_destination          = (var.s3_flowlogs_path == "" ? "${aws_s3_bucket.vpc_logs[each.key].arn}/" : "${aws_s3_bucket.vpc_logs[each.key].arn}/${var.s3_flowlogs_path}/")
  log_destination_type     = "s3"
  log_format               = "$${version} $${account-id} $${interface-id} $${srcaddr} $${dstaddr} $${srcport} $${dstport} $${protocol} $${packets} $${bytes} $${start} $${end} $${action} $${log-status}"
  traffic_type             = "ALL"
  max_aggregation_interval = (var.store_logs_more_frequently == false ? 600 : 60)
  vpc_id                   = each.key
}
