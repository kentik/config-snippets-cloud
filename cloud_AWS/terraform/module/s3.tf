locals {
  sources = merge(
    {
      for vpc_id in var.vpc_ids :
      vpc_id => {
        vpc_id    = vpc_id
        subnet_id = null
        eni_id    = null
      }
    },
    {
      for subnet_id in var.subnet_ids : subnet_id => {
        vpc_id    = null
        subnet_id = subnet_id
        eni_id    = null
      }
    },
    {
      for eni_id in var.eni_ids : eni_id => {
        vpc_id    = null
        subnet_id = null
        eni_id    = eni_id
      }
    }
  )
  flow_logs = {
    for id, flow_log in local.sources :
    id => merge(flow_log, {
      destination = var.s3_usvar.s3_use_one_bucket ? join(
        "/",
        concat(
          [
            aws_s3_bucket.vpc_logs.default.arn,
            id,
          ],
          var.s3_flowlogs_path != "" ? [var.s3_flowlogs_path] : []
        )
        ) : join(
        "/",
        concat(
          [
            aws_s3_bucket.vpc_logs[id].arn,
          ],
          var.s3_flowlogs_path != "" ? [var.s3_flowlogs_path] : []
        )
      )
    })
  }
  buckets = var.s3_use_one_bucket ? {
    default = join("-", concat(
      [
        var.s3_bucket_prefix,
        var.s3_base_name,
        "flow-logs"
      ],
      var.include_workspace ? [terraform.workspace] : []
    ))
    } : {
    for id, flow_log in local.sources :
    id => join("-", concat(
      [
        var.s3_bucket_prefix,
        id,
        "flow-logs"
      ],
      var.include_workspace ? [terraform.workspace] : []
    ))
  }
}

resource "aws_s3_bucket" "vpc_logs" {
  for_each      = local.buckets
  bucket        = each.value
  force_destroy = var.s3_delete_nonempty_buckets
}

resource "aws_s3_bucket_acl" "acl" {
  for_each = local.buckets
  bucket   = aws_s3_bucket.vpc_logs[each.key].id
  acl      = "private"
  # This `depends_on` is to prevent "AccessControlListNotSupported: The bucket does not allow ACLs."
  depends_on = [aws_s3_bucket_ownership_controls.ownership]
}

resource "aws_s3_bucket_policy" "policy" {
  for_each = local.buckets
  bucket   = aws_s3_bucket.vpc_logs[each.key].id
  policy = templatefile(
    "${path.module}/templates/flowLogsS3Policy.json.tmpl",
    {
      bucket = each.key
    }
  )
}

resource "aws_s3_bucket_ownership_controls" "ownership" {
  for_each = local.buckets
  bucket   = aws_s3_bucket.vpc_logs[each.key].id
  rule {
    object_ownership = "ObjectWriter"
  }
}

resource "aws_s3_bucket_public_access_block" "vpc_logs" {
  for_each                = local.buckets
  bucket                  = aws_s3_bucket.vpc_logs[each.key].id
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}

resource "aws_flow_log" "vpc_logs" {
  for_each                 = var.enable_flow_logs ? local.flow_logs : {}
  log_destination          = each.value.destination
  log_destination_type     = "s3"
  log_format               = "$${version} $${account-id} $${interface-id} $${srcaddr} $${dstaddr} $${srcport} $${dstport} $${protocol} $${packets} $${bytes} $${start} $${end} $${action} $${log-status} $${vpc-id} $${subnet-id} $${instance-id} $${tcp-flags} $${type} $${pkt-srcaddr} $${pkt-dstaddr} $${region} $${az-id} $${sublocation-type} $${sublocation-id} $${pkt-src-aws-service} $${pkt-dst-aws-service} $${flow-direction} $${traffic-path}"
  traffic_type             = "ALL"
  max_aggregation_interval = (var.store_logs_more_frequently == false ? 600 : 60)
  vpc_id                   = each.value.vpc_id
  subnet_id                = each.value.subnet_id
  eni_id                   = each.value.eni_id
}
