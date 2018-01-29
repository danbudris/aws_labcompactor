module "vpcs" {
  source = "./vpcs"
}

module "subnets" {
  source = "./subnets"
  vpc_id = "${module.vpcs.vpc_id}"
  cidr   = "${module.vpcs.vpc_cidr}"
}
