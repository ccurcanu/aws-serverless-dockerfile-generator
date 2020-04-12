# -*- coding: utf-8 -*-

import os
import sys

sys.path.append(os.path.dirname(os.path.basename(__file__)))

import dockerfilegenerator.generator as generator


def lambda_handler(event, context):
    return generator.lambda_handler()
