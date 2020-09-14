# Example for creating EKS cluster with Boutique app and flow logs prepared for Kentik

This example is setting simple EKS cluster with [Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) provided by Google. It also configures flow flog for created VPC to be stored on dedicated S3 bucket.
As output you will get *aws_cli* command to configure *kubectl*, IAM role and s3 bucket for use with Kentik portal.

## Usage
### Create resources
Applying terraform code:
```
$ terraform init
$ terraform plan -target=module.aws_vpc
$ terraform apply -target=module.aws_vpc
$ terraform plan
$ terraform apply
Apply complete! Resources: 50 added, 0 changed, 0 destroyed.

Outputs:

aws_k8s_cmd = aws eks --region us-east-2 update-kubeconfig --name boutique-k8s-kentik
iam_role_arn_for_use_with_kentik = arn:aws:iam::003740049406:role/kentik-access-to-boutique-logsTerraformIngestRole
s3_buckets_for_use_with_kentik = [
  "butique-cluster-logs-vpc-016bf0a811bbe963a-flow-logs",
]
vpc_id = vpc-016bf0a811bbe963a
```
Installing boutique app:
```
aws eks --region us-east-2 update-kubeconfig --name boutique-k8s-kentik
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.35.0/deploy/static/provider/aws/deploy.yaml
kubectl apply -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/v0.2.0/release/kubernetes-manifests.yaml
```
To get public endpoint of application we need to find it external-ip:
```
$ kubectl get svc frontend-external 
NAME                TYPE           CLUSTER-IP     EXTERNAL-IP                                                              PORT(S)        AGE
frontend-external   LoadBalancer   172.20.99.29   a66462127e51a439f812a14fe1dc40f6-224536610.us-east-2.elb.amazonaws.com   80:30081/TCP   38s
$ curl http://a66462127e51a439f812a14fe1dc40f6-224536610.us-east-2.elb.amazonaws.com
```

### Clean environment
```
$ kubectl delete -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/v0.2.0/release/kubernetes-manifests.yaml
$ kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v0.35.0/deploy/static/provider/aws/deploy.yaml
$ terraform destroy
Error: error deleting S3 Bucket (butique-cluster-logs-vpc-016bf0a811bbe963a-flow-logs): BucketNotEmpty: The bucket you tried to delete is not empty
        status code: 409, request id: 9FFCAC728B961F17, host id: twSVy/5G9K4IiAbGMNDVV9MmoxuR517VE2DhTjz1NCLzo+/o3FsUw2u9CvEURZ9bK1XtFQRdDgQ=

# This is because we have data on s3 bucket - we need to clean it and destroy again

$ aws s3 rm s3://butique-cluster-logs-vpc-016bf0a811bbe963a-flow-logs --recursive
$ terraform destroy
```
