resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags {
    Name    = "lab_main"
  }
}

output "vpc_id" {
    value = "${aws_vpc.main.id}"
}

output "vpc_cidr" {
  value = "${aws_vpc.main.cidr_block}"
}
