# AWS Trash Compactor
A tool for creating and recycling disposable VPCs in AWS, using Terraform, Lambda and CloudWatch.

## Getting Started
This tool requires the Terraform state to be stored in an S3 bucket.  Create an S3 bucket, and configure the Terraform (./backend.tf) with the path of your state file, as well as the name and region of the S3 Bucket.  

Configure the Provider file (./provider.tf), so that Terraform has access to your AWS account.  If this tool is running on an EC2 Instance it is reccomended that you assign that instance an IAM role that allows it full access to EC2, VPC, Lambda, S3 and Cloudwatch services.  Otherwise, configure a shared credentials file which houses the access and secret key for a provide with the necccessary permissions.

### Prerequisites

Terraform
AWS CLI
AWS IAM Role or User with VPC, EC2, S3, Lambda and Cloudwatch priilleges.  


### Installing

A step by step series of examples that tell you have to get a development env running

## Deployment

Add additional notes about how to deploy this on a live system


## Authors
Dan Budris(https://github.com/danbudris)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
