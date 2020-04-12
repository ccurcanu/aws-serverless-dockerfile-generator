#!/usr/bin/env bash -x

TMP=/tmp/dockerfilegenerator

if [ -d $TMP ]; then rm -rf $TMP; fi
mkdir $TMP
cp ../lambda_function.py $TMP
cp -r ../dockerfilegenerator $TMP
pip install -r ../requirements.txt --system -t $TMP
