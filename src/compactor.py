import boto3
from subprocess import call
import os
import re
import argparse
import yaml

class resource_import_group:
    """Given a list of resources, and a Terraform resource type, this class can be used to import the resources and destroy them"""
    def __init__(self, resource_list, resource_type):
        self.resource_list = resource_list
        self.resource_type = resource_type
        self.resource_templates = []
        self.path = './{}.tf'.format(self.resource_type)

    # create a tf template for each object in the resource list
    def resource_template(self):
        """Generate a basic template to be used as a base for the TF import"""
        x = 0
        for resource in self.resource_list:
            self.resource_templates.append('resource "{}" "{}" {{}}'.format(self.resource_type, x))
            x += 1
        print(self.resource_templates)
        return self.resource_templates

    # write the templates to a file, so that imported resources can be bound to them
    def write_templates(self):
        with open(self.path,'w+') as template_file:
            for resource in self.resource_templates:
                template_file.write('{}\n'.format(resource))

    # import each resource from the resource list into terraform state, and bind it to a template
    def terraform_import(self):
        if (self.resource_type == "aws_lambda_function"):
            # AWS lambdas don't have a 'resource id', and are imported with their name
            x = 0
            for resource in self.resource_list:
                print(resource, x)
                call(['terraform', 'import', '{}.{}'.format(self.resource_type, x), resource])
                print('IT WORKED')
                x += 1
        else:
            x = 0
            for resource in self.resource_list:
                print(resource.id, resource, x)
                call(['terraform', 'import', '{}.{}'.format(self.resource_type, x), resource.id])
                print('IT WORKED')
                x += 1

    # remove the template .tf files that were created, so that when 'terraform apply' is run the imported resources do not match a template in a file and are destroyed
    def delete_self(self):
        os.remove(self.path)

    # refresh the tmeplate list, write the tempaltes to a file, import the resources, and delete the template files; this will mark all imported resources for destruction
    def compact(self):
        self.resource_template()
        self.write_templates()
        self.terraform_import()
        self.delete_self()

# Functions to obtain Lambda ARNs and tags
def get_lambda_tags(func_arn, connection):
    """Get the tags of a lambda, given the ARN of a function"""
    response = connection.list_tags(
        Resource=func_arn
    )
    return response['Tags']

def get_all_lambda_tags(connection):
    """Get all lambdas and their tags as a list of dictionaries"""
    functions = connection.list_functions()
    function_arns = [i['FunctionArn'] for i in functions['Functions']]
    function_names = [i['FunctionName'] for i in functions['Functions']]
    function_tags = [{i: get_lambda_tags(i, connection)} for i in function_arns]
    return function_tags


def get_lambda_tags_by_key(search_key, search_value, connection):
    """Given a tag key and value returns a dictionary of matches and misses"""
    function_tags = get_all_lambda_tags(connection)
    matches = []
    misses = []
    arn_seperator = r"function:(.+)"
    for item in function_tags:
        for key in item.keys():
            try:
                assert item[key][search_key] == search_value
                matches.append(re.search(arn_seperator, key).group(1))
            except (KeyError, AssertionError):
                misses.append(key)
                pass
    return {'matches': matches, 'misses':misses}

def main(aws_profile, aws_region, tag_key, tag_value):
    """Function to delete all VPC, Subnet, Ec2 Instance and Lambda resources with the given key/pair"""
    # Set up the session with the region and profile parameters
    session = boto3.session.Session(region_name="{}".format(aws_region), profile_name="{}".format(aws_profile))
    # Set up the resource level connection to EC2
    ec2 = session.resource('ec2')
    # Set up the low-level client connection to lambda
    # This will be passed to the lamabda search functions
    awslambda = session.client('lambda')

    # Set the tag key/pair value of the resources to be compacted
    tag = tag_key
    value = tag_value
    compact_filter = [{'Name': 'tag:{}'.format(tag), 'Values': ['{}'.format(value)]}]

    # Compact VPCS
    vpcs = resource_import_group(list(ec2.vpcs.filter(Filters=compact_filter)), "aws_vpc")
    vpcs.compact()

    # Compact Subnets
    subnets = resource_import_group(list(ec2.subnets.filter(Filters=compact_filter)), "aws_subnet")
    subnets.compact()

    # Compact Instances
    instances = resource_import_group(list(ec2.instances.filter(Filters=compact_filter)), "aws_instance")
    instances.compact()

    # Compact Lambdas
    lambdas = resource_import_group((get_lambda_tags_by_key('Compact','True',awslambda)['matches']),"aws_lambda_function")
    lambdas.compact()

    # Run TF apply; this will destroy all resources that have been imported
    call(['terraform','apply','-auto-approve'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("aws_profile")
    parser.add_argument("aws_region")
    parser.add_argument("tag_key")
    parser.add_argument("tag_value")
    args = parser.parse_args()
    main(args.aws_profile, args.aws_region, args.tag_key, args.tag_value)