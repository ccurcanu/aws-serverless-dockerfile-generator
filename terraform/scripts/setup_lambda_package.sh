#!/usr/bin/env bash
#
#  Prepare the Lambda function deployment package by installing the dependencies
# relative to the function. Terraform will build the package zip and will deploy
# it to AWS.
##

TMP=/tmp/dockerfilegenerator

if [ -d $TMP ]; then
  rm -rf $TMP;
fi

mkdir $TMP
cp ../lambda_function.py $TMP
for mod in $(cat ../requirements.txt); do
  pip install $mod -t $TMP;
done;
