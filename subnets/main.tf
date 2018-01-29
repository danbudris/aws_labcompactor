variable "vpc_id" {}
variable "cidr" {}

resource "aws_subnet" "main1" {
  vpc_id     = "${var.vpc_id}"
  cidr_block = "${cidrsubnet(var.cidr, 8, 2)}"

  tags {
    Name = "lab_az1"
  }
}

resource "aws_subnet" "main2" {
  vpc_id     = "${var.vpc_id}"
  cidr_block = "${cidrsubnet(var.cidr, 8, 3)}"

  tags {
    Name = "lab_az2"
  }
}

resource "aws_subnet" "main3" {
  vpc_id     = "${var.vpc_id}"
  cidr_block = "${cidrsubnet(var.cidr, 8, 4)}"

  tags {
    Name = "lab_az3"
  }
}

resource "aws_subnet" "external" {
  vpc_id = "${var.vpc_id}"
  cidr_block = "${cidrsubnet(var.cidr, 10, 1)}"

  tags {
    Name = "lab_external"
  }
}
