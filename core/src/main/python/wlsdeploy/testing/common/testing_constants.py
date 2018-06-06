"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import sys
import os

SMOKE_TEST_DEF = 'smoke-test'
SYSTEM_TEST_DEF = 'system-test'
INTEGRATION_TEST_DEF = 'integration-test'
VERIFICATION_TEST_DEF = 'verification-test'

_CERTIFIED = 'certified'

_SMOKE_TEST = 'smoke_test'
_SYSTEM_TEST = 'system_test'
_INTEGRATION_TEST = 'integration_test'
_VERIFICATION_TEST = 'verification_test'

_STAGE_MODULES_RELATIVE_PATH = 'wlsdeploy/testing/stages'

SUPPORTED_TEST_DEF_TYPES = [
    SMOKE_TEST_DEF,
    '%s-%s' % (_CERTIFIED, SMOKE_TEST_DEF),
    SYSTEM_TEST_DEF,
    '%s-%s' % (_CERTIFIED, SYSTEM_TEST_DEF),
    INTEGRATION_TEST_DEF,
    '%s-%s' % (_CERTIFIED, INTEGRATION_TEST_DEF)
]

LOG_PROPERTIES = 'log_properties'
LOGS_DIR = 'logs_dir'
LOG_FILE = 'log_file'

STDOUT_LOG_POLICY = 'stdout_log_policy'

STDOUT_LOG_POLICY_STDOUT = 'stdout'
STDOUT_LOG_POLICY_FILE = 'file'
STDOUT_LOG_POLICY_BOTH = 'both'

LIFECYCLE_TEST_LOG_CONFIG_CLASS = 'oracle.jcs.lifecycle.test.logging.JCSLifecycleTestingLoggingConfig'
LIFECYCLE_TEST_LOG_CONFIG = '-Djava.util.logging.config.class=%s' % LIFECYCLE_TEST_LOG_CONFIG_CLASS

WEBLOGIC_DEPLOY_LOG_CONFIG_CLASS = 'oracle.weblogic.deploy.logging.WLSDeployLoggingConfig'
WEBLOGIC_DEPLOY_LOG_CONFIG = '-Djava.util.logging.config.class=%s' % WEBLOGIC_DEPLOY_LOG_CONFIG_CLASS

TEST_LOGGING_JAR_FILE = 'jcslcm-test-support-lib.jar'
TEST_LOGGING_JAR_LOCATION_TEMPLATE = '{0}%slib%s%s' % (os.path.extsep, os.path.extsep, TEST_LOGGING_JAR_FILE)

CERTIFIED_DIR = _CERTIFIED
USER_DEFINED_DIR = 'user_defined'

ENV_VARS = 'env_vars'
SETTINGS = 'settings'
STAGES = 'stages'
EOR_FIELDS = 'eor_fields'

CERTIFIED_STAGES_MAP_FILE = '%s_%s' % (CERTIFIED_DIR, 'stages.json')
USER_DEFINED_STAGES_MAP_FILE = '%s_%s' % (USER_DEFINED_DIR, 'stages.json')

DEFAULTS_DIR = 'defaults'
EXCLUDES_DIR = 'excludes'
TESTDEFS_DIR = 'testdefs'
METADATA_DIR = '%s/%s' % (TESTDEFS_DIR, 'metadata')
VERIFICATION_TEST_DIR = '%s/%s' % (TESTDEFS_DIR, _VERIFICATION_TEST)
SMOKE_TEST_DIR = '%s/%s' % (TESTDEFS_DIR, _SMOKE_TEST)
SYSTEM_TEST_DIR = '%s/%s' % (TESTDEFS_DIR, _SYSTEM_TEST)
INTEGRATION_TEST_DIR = '%s/%s' % (TESTDEFS_DIR, _INTEGRATION_TEST)

DEFAULT_TEST_DEF_VERIFIER_TEST = 'test-def-verification-test.json'
DEFAULT_TEST_DEF_METADATA_VERIFIER_TEST = 'test-def-metadata-verification-test.json'

STAGE_MODULES_PATH = '%s/%s' % (os.path.dirname(os.path.realpath(sys.argv[0])), _STAGE_MODULES_RELATIVE_PATH)
TOOL_MODULES_PATH = os.path.dirname(os.path.realpath(sys.argv[0]))

METADATA_FILE_VERIFICATION_STAGE_NAME = 'test_def_metadata_file_verification'

JAVA_HOME_ENVVAR = 'JAVA_HOME'
WLST_PATH_ENVVAR = 'WLST_PATH'