import boto3
from subprocess import call
import os

ec2 = boto3.resource('ec2')
compact_filter = [{'Name':'tag:Compact','Values':['True']}]


class resource_import_group:
    def __init__(self, resource_list, resource_type):
        self.resource_list = resource_list
        self.resource_type = resource_type
        self.resource_templates = []
        self.path = './{}.tf'.format(self.resource_type)

    # create a tf templte for each object in the resource list
    def resource_template(self):
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

def main():
    vpcs = resource_import_group(list(ec2.vpcs.filter(Filters=compact_filter)), "aws_vpc")
    vpcs.compact()
    
    subnets = resource_import_group(list(ec2.subnets.filter(Filters=compact_filter)), "aws_subnet")
    subnets.compact()
    
    instances = resource_import_group(list(ec2.instances.filter(Filters=compact_filter)), "aws_instance")
    instances.compact()
    call(['terraform','apply','-auto-approve'])

if __name__ == "__main__":
    main()
