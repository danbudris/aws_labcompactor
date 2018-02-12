import boto3
from subprocess import call
import os
import re

# Set the tag key/pair value of the resources to be compacted
tag = "Compact"
value = "True"
ec2 = boto3.resource('ec2')
compact_filter = [{'Name':'tag:{}'.format(tag),'Values':['{}'.format(value)]}]

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
# Set up the low-level client connection to lambda
awslambda = boto3.client('lambda')

def get_lambda_tags(func_arn):
    """Get the tags of a lambda, given the ARN of a function"""
    response = awslambda.list_tags(
        Resource=func_arn
    )
    return response['Tags']

def get_all_lambda_tags():
    """Get all lambdas and their tags as a list of dictionaries"""
    functions = awslambda.list_functions()
    function_arns = [i['FunctionArn'] for i in functions['Functions']]
    function_names = [i['FunctionName'] for i in functions['Functions']]
    function_tags = [{i: get_lambda_tags(i)} for i in function_arns]
    return function_tags


def get_lambda_tags_by_key(search_key, search_value):
    """Given a tag key and value returns a dictionary of matches and misses"""
    function_tags = get_all_lambda_tags()
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


def main():
    vpcs = resource_import_group(list(ec2.vpcs.filter(Filters=compact_filter)), "aws_vpc")
    vpcs.compact()
    
    subnets = resource_import_group(list(ec2.subnets.filter(Filters=compact_filter)), "aws_subnet")
    subnets.compact()
    
    instances = resource_import_group(list(ec2.instances.filter(Filters=compact_filter)), "aws_instance")
    instances.compact()

    lambdas = resource_import_group((get_lambda_tags_by_key('Compact','True')['matches']),"aws_lambda_function")
    lambdas.compact()

    # Run TF apply; this will destroy all resources that have been imported
    call(['terraform','apply','-auto-approve'])

if __name__ == "__main__":
    main()
