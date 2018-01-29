import boto3
from subprocess import call

ec2 = boto3.resource('ec2')
compact_filter = [{'Name':'tag:Compact','Values':['True']}]


class resource_import_group:

    def __init__(self, resource_list, resource_type):
        self.resource_list = resource_list
        self.resource_type = resource_type

    def resource_template(self):
        self.resource_templates = []
        x = 1
        for resource in self.resource_list:
            self.resource_templates.append('resource "{}" "{}" {{}}'.format(self.resource_type, x))
            x += 1
        print(self.resource_templates)
        return self.resource_templates

    def terraform_import(resource_type, resources):
        x = 0
        for resource in resources:
            call(['terraform', 'import',"{}.{}".format(resource_type,x),"{}", resource.id])
            x += 1

    def write_templates(self):
        path = './{}.tf'.format(self.resource_type)
        with open(path,'w+') as template_file:
            for resource in self.resource_templates:
                template_file.write('{}\n'.format(resource))
    
    def import_resources(self):
        self.resource_template()
        self.write_templates()

vpcs = resource_import_group(list(ec2.vpcs.filter(Filters=compact_filter)), "aws_vpc")
vpcs.import_resources()

subnets = resource_import_group(list(ec2.subnets.filter(Filters=compact_filter)), "aws_subnet")
subnets.import_resources()

instances = resource_import_group(list(ec2.instances.filter(Filters=compact_filter)), "aws_instance")
instances.resource_template()
