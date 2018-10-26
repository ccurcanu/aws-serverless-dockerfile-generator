variable "region" {
  default = "eu-west-2"
}

variable "enable_periodic_trigger" {
  default = true
}

variable "internal_store_s3_bucket_name" {
  default = "ccurcanu-dockerfilegenerator-prod"
}


variable "github_access_token" {
  default = "ee91125b9b75ac5247ba795e8d3296b5f6d1f682" # this is not a valid token
}

variable "dockerfile_github_repository" {
  default = "ccurcanu/docker-cloud-tools"
}
