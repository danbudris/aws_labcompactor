# AWS Lab Trash Compactor
A tool for creating, recycling and running garbage collection in disposable VPCs on AWS using Terraform and Python

## Getting Started
This tool requires the Terraform state to be stored in an S3 bucket.  Create an S3 bucket, and configure the Terraform (./backend.tf) with the path of your state file, as well as the name and region of the S3 Bucket.  

Configure the Provider file (./provider.tf), so that Terraform has access to an AWS account.  If this tool is running on an EC2 Instance it is reccomended that you assign that instance an IAM role that allows it full access to EC2, VPC, Lambda, S3 and Cloudwatch services.  Otherwise, configure a shared credentials file which houses the access and secret key for a provide with the necccessary permissions.

### Prerequisites

Terraform
Python 3+
AWS CLI
AWS IAM Role or User with VPC and EC2 access

### Installing

A step by step series of examples that tell you have to get a development env running

## Deployment

Add additional notes about how to deploy this on a live system

## Example
Run 'terraform plan' in the project director to launch the initial VPC setup, which contains both VPCS and 3 subnets.
Run './src/compactor.py' in the project directory to delete any VPCs, Subnets, or Instances tagged Compact: True in your aws account.

## Authors
Dan Budris(https://github.com/danbudris)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
