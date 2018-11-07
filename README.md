## Dockerfile Serverless Generator

### Description

This repository contains a Dockerfile serverless generator implement with `Python 3.6`, `AWS Lambda` and `CloudWatch` periodic trigger.

The purpose is to generate a new docker image whenever there are official new releases to **terraform** (automatically), **packer**, **ansible**, or other cloud management tools contained.

Dockerfile's repository can be found [here](https://github.com/ccurcanu/docker-cloud-tools) and is used by a [Docker automated build](https://hub.docker.com/r/ccurcanu/cloud-tools/) constructing an image with handy cloud management tools (i.e. ```terraform, packer, ansible```).  


### Deployment

It is done with terraform and the source code can be found in ```terraform``` directory.

Commands to be run in order to provision the cloud infrastructure:

```
# CWD into terraform directory and

# Initialize terraform project
terraform init

# Inspect what infrastructure will be provisioned
terraform plan

# Deploy the infrastructure
terraform apply

# Destory the infrastructure if it's not needed anymore
terraform destroy

```
