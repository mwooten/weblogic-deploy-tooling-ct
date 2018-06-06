"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

from java.util import HashMap

from wlsdeploy.testing import testing_helper
from wlsdeploy.testing.common import system_test_support, testing_helper
from wlsdeploy.testing.common.system_test_support import SystemTestSupport
from wlsdeploy.testing.define.test_def_settings import TestDefSettings
from wlsdeploy.testing.define.test_def_stage import TestDefStage
from wlsdeploy.testing.exception import exception_helper
from wlsdeploy.util import dictionary_utils


class SystemTestIT(unittest.TestCase):
    """

    """
    _class_name = 'SystemTestIT'
    _DEFAULT_WAIT_TIME_SECS = 3

    A2C_DEV_TESTING_MODE_ENVVAR = 'A2C_DEV_TESTING_MODE'
    BUILD_DIR_ENVVAR = 'BUILD_DIR'
    SOURCE_DOMAIN_NAME_ENVVAR = 'SOURCE_DOMAIN_NAME'
    SUPPORTED_VERSIONS_ENVVAR = 'SUPPORTED_VERSIONS'
    TARGET_DOMAIN_NAME_ENVVAR = 'TARGET_DOMAIN_NAME'
    TEST_DEF_FILE_ENVVAR = 'TEST_DEF_FILE'
    USER_TESTS_TO_RUN_ENVVAR = 'USER_TESTS_TO_RUN'
    WAIT_BETWEEN_PHASES_SECS_ENVVAR = 'WAIT_BETWEEN_PHASES_SECS'

    def __init__(self, step_name, stage, test_def, logger):
        self._step_name = step_name
        self._stage = stage
        self._test_def = test_def
        self._logger = logger
        self._env = HashMap()
        step_names_file_name = stage.get_field_value(TestDefStage.STEP_NAMES_FILE)
        self._step_names_map = SystemTestIT.StepNames(step_names_file_name, logger)
        test_name = self._step_names_map.get_step_name(step_name).get_test_name()
        unittest.TestCase.__init__(self, test_name)

    def __getattr__(self, test_method_name):
        return getattr(self, 'proxy_method')

    def proxy_method(self):
        _method_name = 'proxy_method'

        self._logger.entering(class_name=self._class_name, method_name=_method_name)

        wdtct_home = self._test_def.get_env_var_value('A2C_HOME_ENVVAR')
        if wdtct_home is not None:
            self._logger.info('wdtct_home={0}', wdtct_home,
                              class_name=self._class_name, method_name=_method_name)

        # self._step_name is actually a key into the step_names map. Use it
        # to get the step name object
        step_name = self._step_names_map.get_step_name(self._step_name)

        source_settings_id = step_name.get_source_image_id()
        target_settings_id = step_name.get_target_image_id()

        self.run_test(step_name.get_test_name(), self.__get_test_number(self._step_name),
                      source_settings_id, target_settings_id)

        self._logger.exiting(class_name=self._class_name, method_name=_method_name)

        return

    def setUp(self):
        # userTestsToRun = getAndValidateUserTestsToRun(getAndValidateSupportedVersions());
        #
        # a2cHome = getAndValidateAppToCloudHome();
        # testAutomationHome = getAndValidateTestAutomationHome();
        # testSupportHome = getAndValidateTestSupportHome();
        # this.logDir = getLogDirectory();
        # this.loggingPropertiesFile = getLoggingPropertiesFile();
        # this.loggingSupportJar = getCanonicalFile(MessageFormat.format(TEST_LOGGING_JAR_LOCATION_TEMPLATE,
        #                                                                testAutomationHome.getPath()));
        # systemTestStdoutLogPolicy = getAndValidateStdoutLogPolicy();
        #
        # domainParentDir = getAndValidateDomainParentDir();
        # sourceDomainName = getSourceDomainName();
        # targetDomainName = getTargetDomainName();
        # outputDir = getAndValidateOutputDirectory();
        # testFile = getAndValidateTestFile();
        #
        # waitSeconds = validateAndGetIntegerArg(WAIT_BETWEEN_PHASES_SECS_ENVVAR, true);
        self.populate_env_map(self._test_def)

    def run_test(self, test_name, test_number, source_settings_id, target_settings_id):
        _method_name = 'run_test'

        self._logger.entering(test_name, test_number, class_name=self._class_name, method_name=_method_name)

        self._logger.finer('source_settings_id={0}, target_settings_id={1}',
                           source_settings_id, target_settings_id,
                           class_name=self._class_name, method_name=_method_name)

        self._logger.info('WLSDPLY-09864',
                          self._step_name, self._stage.get_name(),
                          class_name=self._class_name, method_name=_method_name)

        source_settings = self._test_def.get_settings(source_settings_id)
        target_settings = self._test_def.get_settings(target_settings_id)

        self.assertEquals(source_settings.get_domain_type(),
                          target_settings.get_domain_type())

        self._logger.exiting(class_name=self._class_name, method_name=_method_name)

        return

    def populate_env_map(self, test_def):
        stdout_log_policy = test_def.get_env_var_value('STDOUT_LOG_POLICY_ENVVAR')
        if stdout_log_policy is not None:
            self._env.put(SystemTestSupport.STDOUT_LOG_POLICY_ENVVAR, stdout_log_policy)

        log_dir = test_def.get_env_var_value('LOG_DIR_ENVVAR')
        if log_dir is not None:
            self._env.put(SystemTestSupport.LOG_DIR_ENVVAR, log_dir)

        log_properties = test_def.get_env_var_value('LOG_PROPERTIES_ENVVAR')
        if log_properties is not None:
            self._env.put(SystemTestSupport.LOG_PROPERTIES_ENVVAR, log_properties)

        a2c_home = test_def.get_env_var_value('A2C_HOME_ENVVAR')
        if a2c_home is not None:
            self._env.put(SystemTestSupport.A2C_HOME_ENVVAR, a2c_home)

        a2c_log_config = test_def.get_env_var_value('A2C_LOG_CONFIG_ENVVAR')
        if a2c_log_config is not None:
            self._env.put(SystemTestSupport.A2C_LOG_CONFIG_ENVVAR, a2c_log_config)

        a2c_post_classpath = test_def.get_env_var_value('A2C_POST_CLASSPATH_ENVVAR')
        if a2c_post_classpath is not None:
            self._env.put(SystemTestSupport.A2C_POST_CLASSPATH_ENVVAR, a2c_post_classpath)

        java_home = test_def.get_env_var_value('JAVA_HOME_ENVVAR')
        if java_home is not None:
            self._env.put(SystemTestSupport.JAVA_HOME_ENVVAR, java_home)

        test_automation_home = test_def.get_env_var_value('TEST_AUTOMATION_HOME_ENVVAR')
        if test_automation_home is not None:
            self._env.put(SystemTestSupport.TEST_AUTOMATION_HOME_ENVVAR, test_automation_home)

        test_support_home = test_def.get_env_var_value('TEST_SUPPORT_HOME_ENVVAR')
        if test_support_home is not None:
            self._env.put(SystemTestSupport.TEST_SUPPORT_HOME_ENVVAR, test_support_home)

        output_dir = test_def.get_env_var_value('OUTPUT_DIR_ENVVAR')
        if output_dir is not None:
            self._env.put(SystemTestSupport.OUTPUT_DIR_ENVVAR, output_dir)

        java7_home = test_def.get_env_var_value('JAVA7_HOME_ENVVAR')
        if java7_home is not None:
            self._env.put(SystemTestSupport.JAVA7_HOME_ENVVAR, java7_home)

        java8_home = test_def.get_env_var_value('JAVA8_HOME_ENVVAR')
        if java8_home is not None:
            self._env.put(SystemTestSupport.JAVA8_HOME_ENVVAR, java8_home)

        java9_home = test_def.get_env_var_value('JAVA9_HOME_ENVVAR')
        if java9_home is not None:
            self._env.put(SystemTestSupport.JAVA9_HOME_ENVVAR, java9_home)

        domain_parent_dir = test_def.get_env_var_value('DOMAIN_PARENT_DIR_ENVVAR')
        if domain_parent_dir is not None:
            self._env.put(SystemTestSupport.DOMAIN_PARENT_DIR_ENVVAR, domain_parent_dir)

        annotated_prov = test_def.get_env_var_value('ANNOTATED_PROV')
        if annotated_prov is not None:
            self._env.put(SystemTestSupport.ANNOTATED_PROV, annotated_prov)

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

    def __get_build_dir(self):
        return self._test_def.get_env_var_value('BUILD_DIR_ENVVAR')

    def __get_supported_versions(self):
        return self._test_def.get_env_var_value('SUPPORTED_VERSIONS_ENVVAR')

    def __get_user_tests_to_run(self):
        return self._test_def.get_env_var_value('USER_TESTS_TO_RUN_ENVVAR')

    def __get_test_file(self):
        test_file = self._test_def.get_env_var_value('TEST_DEF_FILE_ENVVAR')
        return system_test_support.get_canonical_file(test_file)

    def __get_domain_parent_dir(self):
        domain_parent_dir = self._test_def.get_env_var_value('DOMAIN_PARENT_DIR_ENVVAR')
        return system_test_support.get_canonical_file(domain_parent_dir)

    def __get_source_domain_name(self):
        return self._test_def.get_env_var_value('SOURCE_DOMAIN_NAME_ENVVAR')

    def __get_target_domain_name(self):
        return self._test_def.get_env_var_value('TARGET_DOMAIN_NAME_ENVVAR')

    def __validate_and_get_integer_arg(self, env_var_alias, must_be_non_negative):
        result = SystemTestIT._DEFAULT_WAIT_TIME_SECS

        env_var_value = self._test_def.get_env_var_value(env_var_alias)
        if env_var_value is not None:
            result = int(env_var_value)

        if must_be_non_negative and result < 0:
            result = SystemTestIT._DEFAULT_WAIT_TIME_SECS
        return result

    def __get_test_number(self, step_name):
        return self._step_names_map.get_step_name_index(step_name)

    class StepNames(object):
        """

        """
        _class_name = 'StepNames'

        def __init__(self, step_names_file_name, logger):
            _method_name = '__init__'

            self._logger = logger
            self._logger.finer('step_names_file_name={0}',
                               step_names_file_name,
                               class_name=self._class_name, method_name=_method_name)
            file_dict = testing_helper.translate_file(step_names_file_name, self._logger)
            if TestDefStage.STEP_NAMES not in file_dict:
                ex = exception_helper.create_system_test_exception('WLSDPLY-09888',
                                                                   step_names_file_name)
                self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
                raise ex

            self._step_names_dict = file_dict[TestDefStage.STEP_NAMES]

        def get_step_name(self, step_name):
            _method_name = 'get_step_name'

            step_name_dict = dictionary_utils.get_dictionary_element(self._step_names_dict, step_name)

            if not step_name_dict:
                ex = exception_helper.create_system_test_exception('WLSDPLY-09889', step_name)
                self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
                raise ex

            return SystemTestIT.StepName(step_name, step_name_dict, self._logger)

        def get_step_name_index(self, step_name):
            retval = 0
            map_keys = self._step_names_dict.keys()
            for i in range(0, len(map_keys)):
                if map_keys[i] == step_name:
                    retval = i
                    break
            return retval

    class StepName(object):
        """

        """
        _class_name = 'StepName'

        TEST_NAME = 'test_name'
        SOURCE_IMAGE_ID = 'source_image_id'
        TARGET_IMAGE_ID = 'target_image_id'

        def __init__(self, step_name, step_name_dict, logger):
            self._step_name = step_name
            self._step_name_dict = step_name_dict
            self._logger = logger

        def get_test_name(self):
            return dictionary_utils.get_element(self._step_name_dict, SystemTestIT.StepName.TEST_NAME)

        def get_source_image_id(self):
            return dictionary_utils.get_element(self._step_name_dict, SystemTestIT.StepName.SOURCE_IMAGE_ID)

        def get_target_image_id(self):
            return dictionary_utils.get_element(self._step_name_dict, SystemTestIT.StepName.TARGET_IMAGE_ID)


def _populate_script_args(settings):
    args = list()

    args.append('-%s' % TestDefSettings.ORACLE_HOME)
    args.append('%s' % settings.get_oracle_home())

    args.append('-%s' % TestDefSettings.ORACLE_HOME)
    args.append('%s' % settings.get_oracle_home())
    args.append('-%s' % TestDefSettings.DOMAIN_TYPE)
    args.append('%s' % settings.get_domain_type())
    args.append('-%s' % TestDefSettings.ARCHIVE_FILE)
    args.append('%s' % settings.get_archive_file_name())

    if settings.is_field_set(TestDefSettings.DOMAIN_HOME):
        args.append('-%s' % TestDefSettings.DOMAIN_HOME)
        args.append('%s' % settings.get_domain_home())

    if settings.is_field_set(TestDefSettings.MODEL_FILE):
        args.append('-%s' % TestDefSettings.MODEL_FILE)
        args.append('%s' % settings.get_model_file_name())

    if settings.is_field_set(TestDefSettings.WLST_PATH):
        args.append('-%s' % TestDefSettings.WLST_PATH)
        args.append('%s' % settings.get_wlst_path())

    return args
