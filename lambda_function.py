# -*- coding: utf-8 -*-

import dockerfilegenerator


def lambda_handler(event, context):
    return dockerfilegenerator.generator.lambda_handler()
