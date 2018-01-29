terraform {
  backend "s3" {
    bucket = "tctfstate"
    key    = "state.tf"
    region = "us-east-1"
  }
}
