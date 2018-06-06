"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

# python classes from weblogic-deploy-tooling
from wlsdeploy.testing.common import testing_constants, testing_helper
from wlsdeploy.util import dictionary_utils

_class_name = 'TestDefSettings'


class TestDefSettings(object):
    """

    """
    SETTINGS_ID = 'settings_id'
    ADMIN_URL = 'admin_url'
    ADMIN_SERVER_NAME = 'admin_server_name'
    ADMIN_PASS = 'admin_pass'
    ADMIN_USER = 'admin_user'
    ARCHIVE_FILE = 'archive_file'
    DOMAIN_HOME = 'domain_home'
    DOMAIN_NAME = 'domain_name'
    DOMAIN_PARENT = 'domain_parent'
    DOMAIN_TYPE = 'domain_type'
    DOMAIN_VERSION = 'domain_version'
    ENCRYPTION_PASSPHRASE = 'encryption_passphrase'
    JAVA_HOME = 'java_home'
    MODEL_FILE = 'model_file'
    ORACLE_HOME = 'oracle_home'
    PREV_MODEL_FILE = 'prev_model_file'
    RCU_DB = 'rcu_db'
    RCU_PREFIX = 'rcu_prefix'
    RUN_RCU = 'run_rcu'
    RCU_SCHEMA_PASS = 'rcu_schema_pass'
    RCU_SYS_PASS = 'rcu_sys_pass'
    USE_ENCRYPTION = 'use_encryption'
    VARIABLE_FILE = 'variable_file'
    WLST_PATH = 'wlst_path'
    WLST_VERSION = 'wlst_version'

    def __init__(self, settings_id, settings_id_dict, test_def_metadata, logger):
        self._settings_id = settings_id
        self._settings_id_dict = settings_id_dict
        self._test_def_metadata = test_def_metadata
        self._logger = logger

        self._model_file = None
        self._variable_file = None
        self._archive_file = None
        self._prev_model_file = None

    def get_id(self):
        return self._settings_id

    def get_rcu_db(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.RCU_DB)

    def get_rcu_prefix(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.RCU_PREFIX)

    def get_run_rcu(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.RUN_RCU)

    def get_rcu_schema_pass(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.RCU_SCHEMA_PASS)

    def get_rcu_sys_pass(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.RCU_SYS_PASS)

    def get_use_encryption(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.USE_ENCRYPTION)

    def get_wlst_version(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.WLST_VERSION)

    def get_wlst_path(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.WLST_PATH)

    def get_java_home(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.JAVA_HOME)

    def get_oracle_home(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.ORACLE_HOME)

    def get_domain_home(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.DOMAIN_HOME)

    def get_domain_name(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.DOMAIN_NAME)

    def get_domain_parent(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.DOMAIN_PARENT)

    def get_domain_type(self):
        domain_type = dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.DOMAIN_TYPE)
        if domain_type is None:
            metadata_path = self.__create_metadata_path(TestDefSettings.DOMAIN_TYPE)
            domain_type = self._test_def_metadata.get_default_value(metadata_path)
        return domain_type

    def get_domain_version(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.DOMAIN_VERSION)

    def get_admin_server_name(self):
        admin_server_name = dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.ADMIN_SERVER_NAME)
        if admin_server_name is None:
            metadata_path = self.__create_metadata_path(TestDefSettings.ADMIN_SERVER_NAME)
            admin_server_name = self._test_def_metadata.get_default_value(metadata_path)
        return admin_server_name

    def get_admin_url(self):
        admin_url = dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.ADMIN_URL)
        if admin_url is None:
            metadata_path = self.__create_metadata_path(TestDefSettings.ADMIN_URL)
            admin_url = self._test_def_metadata.get_default_value(metadata_path)
        return admin_url

    def get_admin_user(self):
        admin_user = dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.ADMIN_USER)
        if admin_user is None:
            metadata_path = self.__create_metadata_path(TestDefSettings.ADMIN_USER)
            admin_user = self._test_def_metadata.get_default_value(metadata_path)
        return admin_user

    def get_admin_pass(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.ADMIN_PASS)

    def get_model_file_name(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.MODEL_FILE)

    def get_model_file(self):
        if self._model_file is None:
            model_file_name = self.get_model_file_name()
            self._model_file = testing_helper.verify_file_exists(model_file_name, self._logger)
            
        return self._model_file

    def get_variable_file_name(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.VARIABLE_FILE)

    def get_variable_file(self):
        if self._variable_file is None:
            variable_file_name = dictionary_utils.get_element(self._settings_id_dict,
                                                              TestDefSettings.VARIABLE_FILE)
            self._variable_file = testing_helper.verify_file_exists(variable_file_name, self._logger)

        return self._variable_file

    def get_archive_file_name(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.ARCHIVE_FILE)

    def get_archive_file(self):
        if self._archive_file is None:
            archive_file_name = self.get_archive_file_name()
            self._archive_file = testing_helper.verify_file_exists(archive_file_name, self._logger)

        return self._archive_file

    def get_prev_model_file_name(self):
        return dictionary_utils.get_element(self._settings_id_dict, TestDefSettings.PREV_MODEL_FILE)

    def get_prev_model_file(self):
        if self._prev_model_file is None:
            prev_model_file_name = self.get_prev_model_file_name()
            self._prev_model_file = testing_helper.verify_file_exists(prev_model_file_name, self._logger)

        return self._prev_model_file

    def is_field_set(self, field_name):
        value = dictionary_utils.get_element(self._settings_id_dict, field_name)
        return value is not None

    def __create_metadata_path(self, field_name):
        return '%s/%s/%s' % (testing_constants.SETTINGS, self.get_id(), field_name)
