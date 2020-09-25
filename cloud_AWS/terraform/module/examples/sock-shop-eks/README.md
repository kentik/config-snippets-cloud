# Example for creating EKS cluster with sockshop-istio demo and flow logs prepared for Kentik

This example is setting simple EKS cluster with [sock-shop-istio](https://github.com/infracloudio/sockshop-istio) but modified to work with k8s 1.16 [here](https://github.com/patrykPietka/sockshop-istio/tree/support-k8s-1.16). It also configures flow flog for created VPC to be stored on dedicated S3 bucket.
As output you will get *aws_cli* command to configure *kubectl*, IAM role and s3 bucket for use with Kentik portal.

## Usage
### Create resources

> If you would like to use non-default aws profile add ```-var='aws_profile={{ your profile}}'``` to each command

Applying terraform code:
```
$ terraform init
$ terraform plan -target=module.aws_vpc
$ terraform apply -target=module.aws_vpc
$ terraform plan
$ terraform apply
Apply complete! Resources: 50 added, 0 changed, 0 destroyed.

Outputs:

aws_k8s_cmd = aws --profile default eks --region us-east-2 update-kubeconfig --name sock-shop-k8s-kentik
iam_role_arn_for_use_with_kentik = {{ iam }}
s3_buckets_for_use_with_kentik = [
  "sock-shop-cluster-logs-vpc-056445edb0295f98e-flow-logs",
]
vpc_id = vpc-056445edb0295f98e
```
Installing sock-shop app:

```bash
$ aws --profile {{your profile}} eks --region us-east-2 update-kubeconfig --name sock-shop-k8s-kentik
$ # install istioctl at the time of writing version 1.7.2
$ curl -L https://istio.io/downloadIstio | sh - # add ./bin/istioctl to your PATH
$ istioctl install
$ # check out modified version of sock-shop-istio app 
$ kubectl apply -f 1-sock-shop-install/1-sock-shop-complete-demo-istio.yaml -nsock-shop
$ kubectl apply -f <(istioctl kube-inject -f 1-sock-shop-install/2-sockshop-gateway.yaml) -n sock-shop
$ kubectl apply -f <(istioctl kube-inject -f 1-sock-shop-install/3-virtual-services-all.yaml ) -n sock-shop
$ # If you want to create a LoadBalancer and make it publicly available
$ kubectl apply -f 1-sock-shop-install/frontend-load-balancer.yml 

```
To get public endpoint of application we need to find its external-ip:
```
$ kubectl get svc front-end-load-balancer
NAME                      TYPE           CLUSTER-IP     EXTERNAL-IP                                                              PORT(S)        AGE
front-end-load-balancer   LoadBalancer   172.20.99.29   {{ DNS NAME }}                                                           80:30081/TCP   38s
$ curl {{ DNS NAME }}
```

### Clean environment
```
$ terraform destroy
Error: error deleting S3 Bucket (butique-cluster-logs-vpc-016bf0a811bbe963a-flow-logs): BucketNotEmpty: The bucket you tried to delete is not empty
        status code: 409, request id: ***, host id: ***

# This is because we have data on s3 bucket - we need to clean it and destroy again

$ aws --profile {{your profile}} s3 rm s3://sock-shop-cluster-logs-vpc-056445edb0295f98e-flow-logs --recursive
$ terraform destroy
```
