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
  default = "" # Please fill this with proper access token
}

variable "dockerfile_github_repository" {
  default = "ccurcanu/docker-cloud-tools"
}
