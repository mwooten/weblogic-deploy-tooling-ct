"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

from java.util import HashMap
from oracle.weblogic.deploy.util import ScriptRunner

import wlsdeploy.testing.common.testing_helper as testing_helper
from wlsdeploy.testing.define.test_def_settings import TestDefSettings

_class_name = 'ShutdownAdminServer'
_SETTINGS_1 = 'settings-1'


class ShutdownAdminServer(unittest.TestCase):

    def __init__(self, test_name, stage, test_def, logger):
        unittest.TestCase.__init__(self, test_name)
        self._test_name = test_name
        self._stage = stage
        self._test_def = test_def
        self._logger = logger

    def stepShutdownAdminServer(self):
        _method_name = 'stepShutdownAdminServer'

        settings_1 = self._test_def.get_settings(_SETTINGS_1)

        can_proceed = (settings_1.is_field_set(TestDefSettings.ADMIN_SERVER_NAME),
                       settings_1.is_field_set(TestDefSettings.DOMAIN_HOME),
                       settings_1.is_field_set(TestDefSettings.DOMAIN_NAME))

        if 0 in can_proceed:
            needed_fields = [TestDefSettings.ADMIN_SERVER_NAME, TestDefSettings.DOMAIN_HOME,
                             TestDefSettings.DOMAIN_NAME]

            missing_fields = [needed_fields[i] for i, x in enumerate(can_proceed) if x == 0]
            self.fail(testing_helper.format_message('WLSDPLY-09854', settings_1.get_id(),
                                                   ', '.join(missing_fields)))

        admin_server_name = settings_1.get_admin_server_name()
        domain_name = settings_1.get_domain_name()
        domain_home = settings_1.get_domain_home()

        script_runner = ScriptRunner(HashMap(), admin_server_name)
        script_to_run = testing_helper.verify_file_exists('%s/%s' % (domain_home, self._stage.get_script_to_run()),
                                                         self._logger)

        admin_user = settings_1.get_admin_user()
        admin_url = settings_1.get_admin_url()

        args = list()

        args.append('%s' % admin_user)
        args.append('%s' % settings_1.get_admin_pass())
        args.append('%s' % admin_url)

        self._logger.info('WLSDPLY-09846', admin_server_name, domain_name, admin_url, admin_user,
                          class_name=_class_name, method_name=_method_name)

        exit_code = script_runner.executeScript(script_to_run, True, None, args)
        self.assertEqual(exit_code, 0, testing_helper.format_message('WLSDPLY-09835', script_to_run, exit_code))

        self._logger.info('WLSDPLY-09847', admin_server_name, domain_name,
                          class_name=_class_name, method_name=_method_name)

        return
