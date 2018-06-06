"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
from wlsdeploy.util.enum import Enum

ExceptionType = Enum([
    'INTEGRATION_TEST',
    'SYSTEM_TEST',
    'TESTING',
    'TEST_DEF',
    'VERIFICATION',
    'COMPARE_MODELS'
])
