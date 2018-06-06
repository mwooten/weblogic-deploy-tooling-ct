"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

import wlstModule as wlst

import wlsdeploy.testing.common.testing_helper as testing_helper
from wlsdeploy.testing.define.test_def_settings import TestDefSettings

_class_name = 'StartAdminServer'
_SETTINGS_1 = 'settings-1'
_DEFAULT_TIMEOUT = 30000


class StartAdminServer(unittest.TestCase):
    JVM_ARGS = 'jvmArgs'
    TIMEOUT = 'timeout'

    def __init__(self, test_name, stage, test_def, logger):
        unittest.TestCase.__init__(self, test_name)
        self._test_name = test_name
        self._stage = stage
        self._test_def = test_def
        self._logger = logger

    def stepStartAdminServer(self):
        _method_name = 'stepStartAdminServer'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        settings_1 = self._test_def.get_settings(_SETTINGS_1)

        can_proceed = (settings_1.is_field_set(TestDefSettings.ADMIN_URL),
                       settings_1.is_field_set(TestDefSettings.ADMIN_SERVER_NAME),
                       settings_1.is_field_set(TestDefSettings.ADMIN_USER),
                       settings_1.is_field_set(TestDefSettings.ADMIN_PASS),
                       settings_1.is_field_set(TestDefSettings.DOMAIN_HOME),
                       settings_1.is_field_set(TestDefSettings.DOMAIN_NAME))

        needed_fields = [TestDefSettings.ADMIN_URL, TestDefSettings.ADMIN_SERVER_NAME,
                         TestDefSettings.ADMIN_USER, TestDefSettings.ADMIN_PASS,
                         TestDefSettings.DOMAIN_HOME, TestDefSettings.DOMAIN_NAME]

        missing_fields = [needed_fields[i] for i, x in enumerate(can_proceed) if x == 0]

        if missing_fields:
            self.fail(testing_helper.format_message('WLSDPLY-09853', settings_1.get_id(),
                                                   ', '.join(missing_fields)))

        admin_url = settings_1.get_admin_url()
        domain_home = settings_1.get_domain_home()
        domain_name = settings_1.get_domain_name()
        admin_server_name = settings_1.get_admin_server_name()
        admin_user = settings_1.get_admin_user()
        admin_pass = settings_1.get_admin_pass()

        jvm_args = self._stage.get_field_value(StartAdminServer.JVM_ARGS)
        timeout_value = self._stage.get_field_value(StartAdminServer.TIMEOUT, default=_DEFAULT_TIMEOUT)

        stdout_log = '%s/%s.out' % (self._test_def.get_logs_dir(), admin_server_name)

        self._logger.info('WLSDPLY-09838', admin_server_name, domain_name, admin_url, admin_user,
                          class_name=_class_name, method_name=_method_name)
        self._logger.info('WLSDPLY-09839', admin_server_name, stdout_log,
                          class_name=_class_name, method_name=_method_name)

        self._logger.info('WLSDPLY-09841', self._stage.get_class_name(), 'two',
                          class_name=_class_name, method_name=_method_name)
        self._logger.info('WLSDPLY-09842',
                          '%s="%s"; %s=%d' % (StartAdminServer.JVM_ARGS, jvm_args, StartAdminServer.TIMEOUT, timeout_value),
                          self._test_def.get_def_file_name(),
                          class_name=_class_name, method_name=_method_name)

        wlst_wls_id = wlst.startServer(adminServerName=admin_server_name, username=admin_user, password=admin_pass,
                                       domainName=domain_name, domainDir=domain_home, serverLog=stdout_log,
                                       timeout=timeout_value, jvmArgs=jvm_args)

        self._logger.info('WLSDPLY-09840', wlst_wls_id, class_name=_class_name, method_name=_method_name)

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

        return
