Dockerfile Serverless Generator (for cloud-tools Docker image)
==============================================================


.. contents:: **Table of Contents**
    :backlinks: none


Description
-----------

This repository contains code for a AWS Lambda function which generates a
dockerfile that will automatically trigger a docker image rebuild for an image
that contains handy cloud tools with latest versions.

The function is triggered by CloudWatch Periodic trigger at each 5 minutes and
checks if the  tools in the docker image have updates and regenerates the
dockerfile if needed.


Cloud Tools Docker image
------------------------

The image is based on Ubuntu 18.04 containing almost everything that you need
in order to do development in certain cloud environments.

Tools that are automatically updated are:
 * Hashicorp Terraform, and Packer
 * Golang Go (Coming soon)


Others includes:
 * Golang Go
 * OCI environment setup
 * Ansible
 * Build tools
 * Nice shell colouring
 * Others

Dockerfile's repository can be found `<https://github.com/ccurcanu/docker-cloud-tools>`_
and is used by a docker automated build here `<https://hub.docker.com/r/ccurcanu/cloud-tools>`_.


Deployment
----------

You have to use terraform and the source code can be found in ```terraform```
folder.

Commands to be run in order to provision the cloud infrastructure:


.. code-block:: bash

    $ terraform init     # Initialize tf project
    $ terraform plan     # setup internal tf state
    $ terraform apply    # Deploy the infrastructure
    $ terraform destroy  # only if you want to destory the infra and cleanup
