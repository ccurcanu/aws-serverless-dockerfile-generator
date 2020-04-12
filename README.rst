Dockerfile Serverless Generator
===============================

.. image:: https://travis-ci.org/ccurcanu/aws-serverless-dockerfile-generator.svg?branch=master
    :target: https://travis-ci.org/ccurcanu/aws-serverless-dockerfile-generator

.. image:: https://codecov.io/gh/ccurcanu/aws-serverless-dockerfile-generator/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ccurcanu/aws-serverless-dockerfile-generator


-----


This repository contains code for a AWS Lambda function which generates a
dockerfile that will automatically trigger a docker image rebuild for an image
that contains handy cloud tools with latest versions.

The function is triggered by AWS CloudWatch Periodic trigger at each 5 minutes
and checks if the  tools in the docker image have updates and regenerates the
dockerfile if needed.


Generated docker image
------------------------

`The image <https://hub.docker.com/r/ccurcanu/cloud-tools>`_ is based on Ubuntu
18.04 and contains handy tools that you need in order to do development in
certain cloud environments.

Tools that are automatically updated are:
 * Hashicorp ```Terraform```, and ```Packer```
 * ```Golang Go``` (Coming soon)


Others includes:
 * Golang Go
 * OCI environment setup
 * Ansible
 * Build tools
 * Nice shell coloring
 * Others

Dockerfile's Github repository can be found `here <https://github.com/ccurcanu/docker-cloud-tools>`_
and is used by a docker automated build from `here <https://hub.docker.com/r/ccurcanu/cloud-tools>`_.


AWS Deployment
--------------

You have to use terraform and the source code can be found in ```terraform```
folder. Commands to be run in order to provision the cloud infrastructure:


.. code-block:: bash

    $ terraform init     # Initialize project
    $ terraform plan     # setup internal state
    $ terraform apply    # Deploy the infrastructure
    $ terraform destroy  # Only if you want to destroy the infra and cleanup
