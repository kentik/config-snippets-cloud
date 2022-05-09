resource "aws_s3_bucket" "vpc_logs" {
  count         = (var.s3_use_one_bucket == false ? length(var.vpc_id_list) : 1)
  bucket        = join("-", [var.s3_bucket_prefix, (var.s3_use_one_bucket == false ? var.vpc_id_list[count.index] : var.s3_base_name), "flow-logs", terraform.workspace]) # bucket name must be globally unique
  force_destroy = var.s3_delete_nonempty_buckets
}

resource "aws_s3_bucket_acl" "acl" {
  count  = (var.s3_use_one_bucket == false ? length(var.vpc_id_list) : 1)
  bucket = aws_s3_bucket.vpc_logs[count.index].id
  acl    = "private"
}

resource "aws_s3_bucket_policy" "policy" {
  count  = (var.s3_use_one_bucket == false ? length(var.vpc_id_list) : 1)
  bucket = aws_s3_bucket.vpc_logs[count.index].id
  policy = templatefile(
    "${path.module}/templates/flowLogsS3Policy.json.tmpl",
    { bucket = join("-", [var.s3_bucket_prefix, (var.s3_use_one_bucket == false ? var.vpc_id_list[count.index] : var.s3_base_name), "flow-logs", terraform.workspace]) # bucket name must be globally unique
  })
}

resource "aws_s3_bucket_public_access_block" "vpc_logs" {
  count                   = (var.s3_use_one_bucket == false ? length(var.vpc_id_list) : 1)
  bucket                  = aws_s3_bucket.vpc_logs[count.index].id
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}

resource "aws_flow_log" "vpc_logs" {
  count = length(var.vpc_id_list)
  log_destination = (var.s3_use_one_bucket == false ?
    (var.s3_flowlogs_path == "" ? "${aws_s3_bucket.vpc_logs[count.index].arn}/" : "${aws_s3_bucket.vpc_logs[count.index].arn}/${var.s3_flowlogs_path}/") :
  (var.s3_flowlogs_path == "" ? "${aws_s3_bucket.vpc_logs[0].arn}/${var.vpc_id_list[count.index]}/" : "${aws_s3_bucket.vpc_logs[0].arn}/${var.s3_flowlogs_path}/${var.vpc_id_list[count.index]}/"))
  log_destination_type     = "s3"
  log_format               = "$${version} $${account-id} $${interface-id} $${srcaddr} $${dstaddr} $${srcport} $${dstport} $${protocol} $${packets} $${bytes} $${start} $${end} $${action} $${log-status} $${vpc-id} $${subnet-id} $${instance-id} $${tcp-flags} $${type} $${pkt-srcaddr} $${pkt-dstaddr} $${region} $${az-id} $${sublocation-type} $${sublocation-id} $${pkt-src-aws-service} $${pkt-dst-aws-service} $${flow-direction} $${traffic-path}"
  traffic_type             = "ALL"
  max_aggregation_interval = (var.store_logs_more_frequently == false ? 600 : 60)
  vpc_id                   = var.vpc_id_list[count.index]
}
