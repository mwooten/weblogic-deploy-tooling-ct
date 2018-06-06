"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

from java.util import HashMap

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.create import CreateException
from oracle.weblogic.deploy.util import ScriptRunner

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_helper, testing_constants
from wlsdeploy.testing.define.test_def_settings import TestDefSettings
from wlsdeploy.testing.define.test_def_stage import TestDefStage

_class_name = 'CreateDomain'
_SETTINGS_0 = 'settings-0'


class CreateDomain(unittest.TestCase):
    def __init__(self, test_name, stage, test_def, logger):
        unittest.TestCase.__init__(self, test_name)
        self._test_name = test_name
        self._stage = stage
        self._test_def = test_def
        self._logger = logger

    def stepRunCreateDomainScript(self):
        _method_name = 'stepRunCreateDomainScript'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        settings_0 = self._test_def.get_settings(_SETTINGS_0)

        module_to_import = self._stage.get_module_to_import()

        if module_to_import is not None:
            self.__run_using_module_to_import(module_to_import, settings_0)
        else:
            script_path = self._stage.get_script_to_run()
            if script_path is not None:
                self.__run_using_script_to_run(script_path, settings_0)
            else:
                # Stage didn't contain a script_to_run or module_to_import field, so
                # fail stating that
                self.fail(testing_helper.format_message('WLSDPLY-09857',
                                                        self._stage.get_name(),
                                                        TestDefStage.SCRIPT_TO_RUN,
                                                        TestDefStage.MODULE_TO_IMPORT))

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

    def __run_using_script_to_run(self, script_path, settings):
        script_to_run = testing_helper.verify_file_exists(script_path, self._logger)

        env = _populate_env_map(settings)

        args = _populate_tool_args([], settings)

        script_runner = ScriptRunner(env, self._stage.get_name())
        exit_code = script_runner.executeScript(script_to_run, True, None, args)
        self.assertEqual(exit_code, 0, testing_helper.format_message('WLSDPLY-09835', script_to_run, exit_code))

    def __run_using_module_to_import(self, module_to_import, settings):
        tool_module = testing_helper.import_tool_module(module_to_import, self._logger)

        args = list()

        # args[0] is the file path for the tool_module
        args.append('%s/%s.py' % (testing_constants.TOOL_MODULES_PATH, module_to_import))

        # Use settings to populate all the other args
        args = _populate_tool_args(args, settings)

        try:
            exit_code = tool_module.main(args)
        except CreateException, ce:
            self.fail(testing_helper.format_message('WLSDPLY-09826',
                                                    self._test_name,
                                                    self._stage.get_module_name(),
                                                    self._stage.get_class_name(),
                                                    ce.getLocalizedMessage()))
        except SystemExit, se:
            exit_code = str(se)

        self.assertEqual(exit_code, None, testing_helper.format_message('WLSDPLY-09835',
                                                                        module_to_import, exit_code))


def _populate_env_map(settings):
    env = HashMap()

    if settings.is_field_set(TestDefSettings.JAVA_HOME):
        env.put(testing_constants.JAVA_HOME_ENVVAR, settings.get_java_home())

    if settings.is_field_set(TestDefSettings.WLST_PATH):
        env.put(testing_constants.WLST_PATH_ENVVAR, settings.get_wlst_path())

    return env


def _populate_tool_args(args, settings):

    args.append('-%s' % TestDefSettings.ORACLE_HOME)
    args.append('%s' % settings.get_oracle_home())
    args.append('-%s' % TestDefSettings.DOMAIN_PARENT)
    args.append('%s' % settings.get_domain_parent())

    # The metadata will have a default value for
    # TestDefSettings.DOMAIN_TYPE, which will
    # be picked up if no TestDefSettings.DOMAIN_TYPE
    # field was present in the test definition

    args.append('-%s' % TestDefSettings.DOMAIN_TYPE)
    args.append('%s' % settings.get_domain_type())

    if settings.is_field_set(TestDefSettings.MODEL_FILE):
        args.append('-%s' % TestDefSettings.MODEL_FILE)
        args.append('%s' % settings.get_model_file_name())

    if settings.is_field_set(TestDefSettings.ARCHIVE_FILE):
        args.append('-%s' % TestDefSettings.ARCHIVE_FILE)
        args.append('%s' % settings.get_archive_file_name())

    if settings.is_field_set(TestDefSettings.VARIABLE_FILE):
        args.append('-%s' % TestDefSettings.VARIABLE_FILE)
        args.append('%s' % settings.get_variable_file())

    if settings.is_field_set(TestDefSettings.JAVA_HOME):
        args.append('-%s' % TestDefSettings.JAVA_HOME)
        args.append('%s' % settings.get_java_home())

    if settings.is_field_set(TestDefSettings.WLST_PATH):
        args.append('-%s' % TestDefSettings.WLST_PATH)
        args.append('%s' % settings.get_wlst_path())

    if settings.is_field_set(TestDefSettings.USE_ENCRYPTION):
        args.append('%s' % TestDefSettings.USE_ENCRYPTION)

    return args
