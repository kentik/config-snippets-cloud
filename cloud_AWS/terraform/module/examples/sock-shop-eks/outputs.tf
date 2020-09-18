output "aws_k8s_cmd" {
  value = "aws eks --region ${var.region} update-kubeconfig --name ${module.eks.cluster_id}"
}

output "vpc_id" {
  value = module.aws_vpc.vpc_id
}

output "iam_role_arn_for_use_with_kentik" {
  value = module.kentik_integration.iam_role_arn
}

output "s3_buckets_for_use_with_kentik" {
  value = module.kentik_integration.bucket_name_list
}
