"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_helper, testing_constants
from wlsdeploy.testing.define.test_def import TestDef
from wlsdeploy.testing.define.test_def_metadata import TestDefMetadata
from wlsdeploy.testing.define.test_def_settings import TestDefSettings
from wlsdeploy.testing.define.test_def_stage import TestDefStage

_class_name = 'VerifyTestDefMetadataFile'
_MANAGED_FIELD_DEF_FIELDS = [
    TestDef.METADATA_FILE,
    TestDef.TYPE,
    TestDef.NAME,
    TestDef.DESCRIPTION,
    TestDef.OVERRIDES_FILE,
    testing_constants.LOGS_DIR,
    testing_constants.LOG_FILE,
    testing_constants.STDOUT_LOG_POLICY,
    TestDefSettings.ARCHIVE_FILE,
    TestDefSettings.ADMIN_PASS,
    TestDefSettings.ADMIN_SERVER_NAME,
    TestDefSettings.ADMIN_URL,
    TestDefSettings.ADMIN_USER,
    TestDefSettings.DOMAIN_HOME,
    TestDefSettings.DOMAIN_NAME,
    TestDefSettings.DOMAIN_PARENT,
    TestDefSettings.DOMAIN_TYPE,
    TestDefSettings.DOMAIN_VERSION,
    TestDefSettings.ENCRYPTION_PASSPHRASE,
    TestDefSettings.JAVA_HOME,
    TestDefSettings.MODEL_FILE,
    TestDefSettings.RCU_DB,
    TestDefSettings.RCU_PREFIX,
    TestDefSettings.RUN_RCU,
    TestDefSettings.RCU_SCHEMA_PASS,
    TestDefSettings.RCU_SYS_PASS,
    TestDefSettings.USE_ENCRYPTION,
    TestDefSettings.VARIABLE_FILE,
    TestDefSettings.WLST_PATH,
    TestDefSettings.WLST_VERSION,
    TestDefStage.CONTINUE_WHEN_FAIL,
    TestDefStage.STEP_NAMES,
    TestDefStage.STEP_NAMES_FILE,
    TestDefStage.SCRIPT_TO_RUN,
    TestDefStage.MODULE_TO_IMPORT
]


class VerifyTestDefMetadataFile(unittest.TestCase):
    """
    Stage module for verifying a test definition metadata file
    """
    def __init__(self, test_name, test_def_metadata_file, test_def_metadata_dict, stage, test_result, logger):
        """

        :param test_name:
        :param test_def_metadata_file:
        :param test_def_metadata_dict:
        :param stage:
        :param test_result:
        :param logger:
        """
        unittest.TestCase.__init__(self, test_name)
        self._stage = stage
        self._test_def_metadata_file = test_def_metadata_file
        self._test_def_metadata_dict = test_def_metadata_dict
        self._test_result = test_result
        self._logger = logger

    def verifyRequiredFieldsArePresent(self):
        _method_name = 'verifyRequiredFieldsArePresent'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        test_def_metadata_file_path = self._test_def_metadata_file.getAbsolutePath()

        self.assertEqual(TestDef.METADATA_FILE in self._test_def_metadata_dict,
                         True, testing_helper.format_message('WLSDPLY-09843',
                                                             test_def_metadata_file_path,
                                                             TestDef.METADATA_FILE))

        self.assertEqual(TestDef.TYPE in self._test_def_metadata_dict,
                         True, testing_helper.format_message('WLSDPLY-09843',
                                                             test_def_metadata_file_path,
                                                             TestDef.TYPE))

        self.assertEqual(TestDef.NAME in self._test_def_metadata_dict,
                         True, testing_helper.format_message('WLSDPLY-09843',
                                                             test_def_metadata_file_path,
                                                             TestDef.NAME))

        iterators = [self._test_def_metadata_dict.iteritems()]
        while iterators:
            current_iterator = iterators.pop()
            for field_name, field_value in current_iterator:
                if isinstance(field_value, dict):
                    if field_name in _MANAGED_FIELD_DEF_FIELDS:
                        self.__validate_field_definition(field_name, field_value.keys(), test_def_metadata_file_path)
                    iterators.append(current_iterator)
                    iterators.append(field_value.iteritems())

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

    def __validate_field_definition(self, field_name, field_def_fields, test_def_metadata_file_path):
        self.assertEqual(TestDefMetadata.REQUIRED in field_def_fields,
                         True, testing_helper.format_message('WLSDPLY-09844',
                                                             field_name,
                                                             test_def_metadata_file_path,
                                                             TestDefMetadata.REQUIRED))

        self.assertEqual(TestDefMetadata.DATA_TYPE in field_def_fields,
                         True, testing_helper.format_message('WLSDPLY-09844',
                                                             field_name,
                                                             test_def_metadata_file_path,
                                                             TestDefMetadata.DATA_TYPE))
