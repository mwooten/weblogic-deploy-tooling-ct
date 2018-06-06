"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import os
import sys

from java.io import File
from java.io import IOException

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import PyOrderedDict
from oracle.weblogic.deploy.util import StringUtils

# java classes from weblogic-deploy-tooling-ct
from oracle.weblogic.deploy.testing import TestingConstants

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_helper
from wlsdeploy.testing.exception import exception_helper
from wlsdeploy.testing.logging.platform_logger import PlatformLogger

_class_name = 'SystemTestSupport'
_logger = PlatformLogger('wlsdeploy.system_test', resource_bundle_name=TestingConstants.RESOURCE_BUNDLE_NAME)


class SystemTestSupport(object):
    """

    """
    WINDOWS = sys.platform.startswith('win')
    SHELL_SCRIPT_EXTENSION = (WINDOWS and ['cmd'] or ['sh'])[0]

    TEST_SEPARATOR = '[ \t]*,[ \t]*'
    BUILD_DIR = os.getcwd()

    BUILD_DIR_OPT = 'buildDir'
    TEST_FILE_OPT = 'testFile'
    USER_TESTS_TO_RUN_OPT = 'userTestsToRun'
    SUPPORTED_VERSIONS_OPT = 'supportedVersions'
    DOMAIN_PARENT_DIR_OPT = 'domainParentDir'

    STDOUT_LOG_POLICY_STDOUT_VALUE = 'stdout'
    STDOUT_LOG_POLICY_FILE_VALUE = 'file'
    STDOUT_LOG_POLICY_BOTH_VALUE = 'both'
    DEFAULT_STDOUT_LOG_POLICY = STDOUT_LOG_POLICY_BOTH_VALUE

    WDTCT_HOME_ENVVAR = 'WDTCT_HOME'

    STDOUT_LOG_POLICY_ENVVAR = 'STDOUT_LOG_POLICY'
    LOG_DIR_ENVVAR = 'WDTCT_TEST_LOG_DIRECTORY'
    LOG_PROPERTIES_ENVVAR = 'LOG_PROPERTIES'
    WDTCT_LOG_CONFIG_ENVVAR = 'WDTCT_LOG_CONFIG'
    WDTCT_POST_CLASSPATH_ENVVAR = 'WDTCT_POST_CLASSPATH'
    JAVA_HOME_ENVVAR = 'JAVA_HOME'
    TEST_AUTOMATION_HOME_ENVVAR = 'TEST_AUTOMATION_HOME'
    TEST_SUPPORT_HOME_ENVVAR = 'TEST_SUPPORT_HOME'
    OUTPUT_DIR_ENVVAR = 'OUTPUT_DIR'
    JAVA7_HOME_ENVVAR = 'JAVA7_HOME'
    JAVA8_HOME_ENVVAR = 'JAVA8_HOME'
    JAVA9_HOME_ENVVAR = 'JAVA9_HOME'
    DOMAIN_PARENT_DIR_ENVVAR = 'DOMAIN_PARENT_DIR'
    A2C_HOME_ENVVAR = 'A2C_HOME'
    A2C_LOG_CONFIG_ENVVAR = 'A2C_LOG_CONFIG'
    A2C_POST_CLASSPATH_ENVVAR = 'A2C_POST_CLASSPATH'

    SYSTEM_TEST_LOG_CONFIG_CLASS = 'oracle.jcs.lifecycle.test.logging.JCSLifecycleTestingLoggingConfig'
    SYSTEM_TEST_LOG_CONFIG = '-Djava.util.logging.config.class=%s' % SYSTEM_TEST_LOG_CONFIG_CLASS

    LOG_DIR_DEFAULT = 'logs'
    TEST_LOGGING_JAR_LOCATION_TEMPLATE = os.path.join('{0}', 'lib', 'jcslcm-test-support-lib.jar')

    ANNOTATED_PROV = 'ANNOTATED_PROV'

    DOMAIN_PARENT_DIR_DEFAULT = 'domains'
    TEST_AUTOMATION_HOME_DEFAULT = 'jcslcm-test-support'
    TEST_SUPPORT_HOME_DEFAULT = 'a2c-system-test-support'
    LOG_PROPERTIES_FILE_DEFAULT = os.path.join(TEST_SUPPORT_HOME_DEFAULT, 'etc', 'logging.properties')

    WLS = 'wls'
    JRF = 'jrf'
    RJRF = 'rjrf'

    WLS_TEST_TYPE = 'wls'
    RESTRICTED_JRF_TEST_TYPE = 'rjrf'
    JRF_TEST_TYPE = 'jrf'
    VALID_DOMAIN_TYPES = [
        WLS_TEST_TYPE,
        RESTRICTED_JRF_TEST_TYPE,
        JRF_TEST_TYPE
    ] 

    SOURCE_DOMAIN_VERSIONS = ['1036', '1211', '1212', '1213', '1221', '12211', '12212', '12213']
    TARGET_DOMAIN_VERSIONS = ['1213', '12212', '12213']
    ALL_DOMAIN_VERSIONS = list(SOURCE_DOMAIN_VERSIONS)

    SUPPORTED_VERSIONS_ALL = 'ALL'
    SUPPORTED_VERSIONS_DEFAULT = list(SOURCE_DOMAIN_VERSIONS)

    _JAVA7 = 'jdk7'
    _JAVA8 = 'jdk8'
    _JAVA9 = 'jdk9'

    ORACLE_HOME_ENV_VARIABLE_TEMPLATE = '{0}{1}_HOME'
    SOURCE_DOMAIN_DIR_TEMPLATE = 'test{0}-source'
    TARGET_DOMAIN_DIR_TEMPLATE = 'test{0}-target'
    OUTPUT_DIR_TEMPLATE = 'test{0}'
    TEST_LOG_DIR_TEMPLATE = 'test{0}'

    def __init__(self, args=None):
        self._args = args
        # Save OS environment variables into a Python dictionary
        self._env = os.environ
        self._oracle_homes = PyOrderedDict()
        self._java_homes = PyOrderedDict()
        self._required_versions = PyOrderedDict()

    def get_archive_file_name(self, path, domain_name):
        return get_canonical_path(path, '%s.zip' % domain_name)

    def get_overrides_file_name(self, domain_name):
        return '%s.json' % domain_name

    def get_build_dir(self):
        build_dir = None
        if SystemTestSupport.BUILD_DIR_OPT in self._args:
            build_dir = get_canonical_file(self._args[SystemTestSupport.BUILD_DIR_OPT])
        return build_dir

    def get_supported_versions(self):
        """
        Returns the value assigned to the -supported_versions command-line argument.

        This value is a comma-separated string of the WLS versions (without dots),
        which should be used during the test. None is returned, if -supported_versions
        was not supplied as a command-line argument.

        :return: A comma-separated string of the WLS versions (without dots)
                to use in the test, or None
        """
        supported_versions = None
        if SystemTestSupport.SUPPORTED_VERSIONS_OPT in self._args:
            supported_versions = self._args[SystemTestSupport.SUPPORTED_VERSIONS_OPT]
        return supported_versions

    def get_user_tests_to_run(self):
        user_tests = None
        if SystemTestSupport.USER_TESTS_TO_RUN_OPT in self._args:
            user_tests = self._args[SystemTestSupport.USER_TESTS_TO_RUN_OPT]
        return user_tests

    def get_test_file(self):
        test_file = None
        if SystemTestSupport.TEST_FILE_OPT in self._args:
            test_file = get_canonical_file(self._args[SystemTestSupport.TEST_FILE_OPT])
        return test_file

    def get_domain_parent_dir(self):
        domain_parent_dir = None
        if SystemTestSupport.DOMAIN_PARENT_DIR_OPT in self._args:
            domain_parent_dir = self.__get_domain_parent_dir(self._args[SystemTestSupport.DOMAIN_PARENT_DIR_OPT])
        return domain_parent_dir

    def get_app_to_cloud_home(self):
        a2c_home = None
        if SystemTestSupport.A2C_HOME_ENVVAR in self._env:
            a2c_home = self._env[SystemTestSupport.A2C_HOME_ENVVAR]
        return a2c_home

    def get_log_directory(self):
        log_directory = None
        if SystemTestSupport.LOG_DIR_ENVVAR in self._env:
            log_directory = self.__get_log_directory(self._env[SystemTestSupport.LOG_DIR_ENVVAR])
        return log_directory

    def get_logging_properties_file(self):
        logging_properties_file = None
        if SystemTestSupport.LOG_PROPERTIES_ENVVAR in self._env:
            logging_properties_file = \
                self.__get_logging_properties_file(self._env[SystemTestSupport.LOG_PROPERTIES_ENVVAR])
        return logging_properties_file

    def get_output_directory(self):
        output_directory = None
        if SystemTestSupport.OUTPUT_DIR_ENVVAR in self._env:
            output_directory = \
                get_canonical_file(self._env[SystemTestSupport.OUTPUT_DIR_ENVVAR])
        return output_directory

    def get_annotated_provisioning(self):
        annotated_provisioning = None
        if SystemTestSupport.ANNOTATED_PROV in self._env:
            annotated_provisioning = self._env[SystemTestSupport.ANNOTATED_PROV]
        return annotated_provisioning

    def get_and_validate_supported_versions(self):
        return self.__get_and_validate_supported_versions(self.get_supported_versions())

    def get_and_validate_test_automation_home(self):
        test_automation_home = None
        if SystemTestSupport.TEST_AUTOMATION_HOME_ENVVAR in self._env:
            test_automation_home = \
                self.__get_and_validate_test_automation_home(self._env[SystemTestSupport.TEST_AUTOMATION_HOME_ENVVAR])
        return test_automation_home

    def get_and_validate_test_support_home(self):
        test_support_home = None
        if SystemTestSupport.TEST_SUPPORT_HOME_ENVVAR in self._env:
            test_support_home = self.__get_and_validate_test_support_home(self._env[SystemTestSupport.TEST_SUPPORT_HOME_ENVVAR])
        return test_support_home

    def get_and_validate_stdout_log_policy(self):
        result = SystemTestSupport.DEFAULT_STDOUT_LOG_POLICY

        env_var_value = None

        if SystemTestSupport.STDOUT_LOG_POLICY_ENVVAR in self._env:
            env_var_value = self._env[SystemTestSupport.STDOUT_LOG_POLICY_ENVVAR]

        if env_var_value is not None:
            if SystemTestSupport.STDOUT_LOG_POLICY_BOTH_VALUE.lower() == env_var_value.lower():
                result = SystemTestSupport.STDOUT_LOG_POLICY_BOTH_VALUE
            elif SystemTestSupport.STDOUT_LOG_POLICY_FILE_VALUE.lower() == env_var_value.lower():
                result = SystemTestSupport.STDOUT_LOG_POLICY_FILE_VALUE
            elif SystemTestSupport.STDOUT_LOG_POLICY_STDOUT_VALUE.lower() == env_var_value.lower():
                result = SystemTestSupport.STDOUT_LOG_POLICY_STDOUT_VALUE

        return result

    def get_log_dir_for_test(self, log_base_dir, test_number):
        _method_name = 'get_log_dir_for_test'

        log_dir = get_canonical_path(log_base_dir,
                                      testing_helper.format_message(SystemTestSupport.TEST_LOG_DIR_TEMPLATE, test_number))
        if not log_dir.exists() and not log_dir.mkdirs():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09872', log_dir.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return log_dir

    def get_source_domain_parent_dir_for_test(self, domain_parent_dir, test_number):
        _method_name = 'get_source_domain_parent_dir_for_test'

        source_domain_parent_dir = get_canonical_path(domain_parent_dir,
                                                       testing_helper.format_message(SystemTestSupport.SOURCE_DOMAIN_DIR_TEMPLATE,
                                                                                    test_number))

        if not source_domain_parent_dir.exists() and not source_domain_parent_dir.mkdirs():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09873',
                                                               source_domain_parent_dir.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return source_domain_parent_dir

    def get_target_domain_parent_dir_for_test(self, domain_parent_dir, test_number):
        _method_name = 'get_target_domain_parent_dir_for_test'

        target_domain_parent_dir = get_canonical_path(domain_parent_dir,
                                                       testing_helper.format_message(SystemTestSupport.TARGET_DOMAIN_DIR_TEMPLATE,
                                                                                    test_number))

        if not target_domain_parent_dir.exists() and not target_domain_parent_dir.mkdirs():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09874',
                                                               target_domain_parent_dir.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return target_domain_parent_dir

    def get_output_dir_for_test(self, output_base_dir, test_number):
        _method_name = 'get_output_dir_for_test'

        output_dir = get_canonical_path(output_base_dir,
                                         testing_helper.format_message(SystemTestSupport.OUTPUT_DIR_TEMPLATE,
                                                                      test_number))
        if not output_dir.exists() and not output_dir.mkdirs():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09875',
                                                               output_dir.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return output_dir

    def get_and_validate_app_to_cloud_home(self):
        _method_name = 'get_and_validate_app_to_cloud_home'

        a2c_home = self.get_app_to_cloud_home()
        if not a2c_home.exists():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09876',
                                                               a2c_home.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex
        elif not a2c_home.isDirectory():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09877',
                                                               a2c_home.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return a2c_home

    def get_and_validate_output_directory(self):
        _method_name = 'get_and_validate_output_directory'

        output_dir = self.get_output_directory()
        if not output_dir.exists() and not output_dir.mkdirs():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09878',
                                                               output_dir.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex
        elif not output_dir.isDirectory():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09879',
                                                               output_dir.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return output_dir

    def get_and_validate_user_tests_to_run(self, supported_versions):
        return self.__get_and_validate_user_tests_to_run(supported_versions, self.get_user_tests_to_run());

    def does_wls_version_require_java9(self, version):
        # None yet
        return False

    def does_wls_version_require_java8(self, version):
        # 12.2.1 or higher requires Java 8
        return not _is_target_version_less_than_source_version('12.1.3', version)

    def does_wls_version_require_java7(self, version):
        _method_name = 'does_wls_version_require_java7'

        # 10.3.6 to 12.1.3 requires Java 7
        is_less_than_1221 = _is_target_version_less_than_source_version('12.2.1', version)
        is_less_than_1036 = _is_target_version_less_than_source_version('10.3.6', version)

        _logger.finer('{0} is less than 12.2.1: {1}', version, is_less_than_1221,
                       class_name=_class_name, method_name=_method_name)

        _logger.finer('{0} is less than 10.3.6: {1}', version, is_less_than_1036,
                       class_name=_class_name, method_name=_method_name)

        return is_less_than_1221 and is_less_than_1036

    def get_oracle_home_for_test(self, type, version):
        _method_name = 'get_oracle_home_for_test'

        _logger.entering(type, version, class_name=_class_name, method_name=_method_name)
        _logger.finer("oracle_homes contains keys: {0}", str(self._oracle_homes),
                       class_name=_class_name, method_name=_method_name)

        oracle_home = None
        key = 'jrf%s' % version
        if self._oracle_homes.__contains__(key):
            oracle_home = self._oracle_homes.get(key)

        if oracle_home is None:
            key = 'wls%s' % version
            if self._oracle_homes.__contains__(key):
                oracle_home = self._oracle_homes.get(key)

        _logger.exiting(class_name=_class_name, method_name=_method_name, result=oracle_home)

        return oracle_home

    def get_java_home_for_domain_creation(self, version):
        return self.get_java_home(version, True)

    def get_java_home_for_test(self, version):
        return self.get_java_home(version, False)

    def get_java_home(self, version, is_for_domain_creation):
        _method_name = 'get_java_home'

        _logger.entering(version, is_for_domain_creation, class_name=_class_name, method_name=_method_name)
        if version[-1] == '.':
            version = _get_dot_delimited_version(version)

        if self.does_wls_version_require_java9(version):
            java_home = self._java_homes.get(SystemTestSupport._JAVA9)
        elif self.does_wls_version_require_java8(version):
            java_home = self._java_homes.get(SystemTestSupport._JAVA8)
        elif self.does_wls_version_require_java7(version):
            java_home = self._java_homes.get(SystemTestSupport._JAVA7)
        else:
            # Cannot use Java 6 for running the test because AppToCloud
            # tools do not support it.
            if self._java_homes.__contains__(SystemTestSupport._JAVA8):
                java_home = self._java_homes.get(SystemTestSupport._JAVA8)
            elif self._java_homes.__contains__(SystemTestSupport._JAVA7):
                java_home = self._java_homes.get(SystemTestSupport._JAVA7)
            else:
                ex = exception_helper.create_system_test_exception('WLSDPLY-09866', version)
                _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                raise ex

        _logger.exiting(class_name=_class_name, method_name=_method_name, result=java_home)

        return java_home

    def get_automation_type_for_test(self, test_type):
        _method_name = 'get_automation_type_for_test'

        _logger.entering(test_type, class_name=_class_name, method_name=_method_name)

        automation_type = None

        if test_type == SystemTestSupport.JRF_TEST_TYPE:
            automation_type = SystemTestSupport.JRF
        elif test_type == SystemTestSupport.RESTRICTED_JRF_TEST_TYPE:
            automation_type = SystemTestSupport.RJRF
        elif test_type == SystemTestSupport.WLS_TEST_TYPE:
            automation_type = SystemTestSupport.WLS

        _logger.exiting(class_name=_class_name, method_name=_method_name, result=automation_type)
        return automation_type

    def validate_locations_for_webLogic_versions_required(self, env, versions_required):
        _method_name = 'validate_locations_for_webLogic_versions_required'

        for version, types in versions_required.iteritems():
            requires_jrf = self.__requires_jrf(types)
            jrf_variable_name = testing_helper.format_message(SystemTestSupport.ORACLE_HOME_ENV_VARIABLE_TEMPLATE,
                                                             'JRF', version)
            wls_variable_name = testing_helper.format_message(SystemTestSupport.ORACLE_HOME_ENV_VARIABLE_TEMPLATE,
                                                             'WLS', version)
            if jrf_variable_name in os.environ:
                oracle_home_to_validate = os.environ[jrf_variable_name]
                version_key = '%s%s' % (SystemTestSupport.JRF_TEST_TYPE, version)
            elif not requires_jrf and wls_variable_name in os.environ:
                oracle_home_to_validate = os.environ[wls_variable_name]
                version_key = '%s%s' % (SystemTestSupport.WLS_TEST_TYPE, version)
            else:
                if requires_jrf:
                    message_id = 'WLSDPLY-09880'
                else:
                    message_id = 'WLSDPLY-09881'

                ex = exception_helper.create_system_test_exception(message_id, version)
                _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                raise ex

            if not self._oracle_homes.__contains__(version_key):
                oracle_home = get_canonical_file(oracle_home_to_validate)

            if not oracle_home.exists():
                if requires_jrf:
                    message_id = 'WLSDPLY-09882'
                else:
                    message_id = 'WLSDPLY-09883'

                ex = exception_helper.create_system_test_exception(message_id,
                                                                   oracle_home.getPath(),
                                                                   version)
                _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                raise ex

            elif not oracle_home.isDirectory():
                if requires_jrf:
                    message_id = 'WLSDPLY-09884'
                else:
                    message_id = 'WLSDPLY-09885'

                ex = exception_helper.create_system_test_exception(message_id,
                                                                   oracle_home.getPath(),
                                                                   version)
                _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                raise ex

            self._oracle_homes[version_key] = oracle_home
            self.__validate_locations_for_java_versions_required(env, version)

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

    def __validate_locations_for_java_versions_required(self, env, version):
        _method_name = '__validate_locations_for_java_versions_required'

        _logger.entering(env, version, class_name=_class_name, method_name=_method_name)

        if version[-1] == '.':
            version = _get_dot_delimited_version(version)

        requires_java9 = self.does_wls_version_require_java9(version)
        requires_java8 = self.does_wls_version_require_java8(version)
        requires_java7 = self.does_wls_version_require_java7(version)

        java_home_name = None
        java_home_key = None
        validated = False

        if requires_java9:
            if self._java_homes.__contains__(SystemTestSupport._JAVA9):
                validated = True
            else:
                java_home_name = os.environ[SystemTestSupport.JAVA9_HOME_ENVVAR]
                java_home_key = SystemTestSupport._JAVA9
        elif requires_java8:
            if self._java_homes.__contains__(SystemTestSupport._JAVA8):
                validated = True
            else:
                java_home_name = os.environ[SystemTestSupport.JAVA8_HOME_ENVVAR]
                java_home_key = SystemTestSupport._JAVA8
        elif requires_java7:
            if self._java_homes.__contains__(SystemTestSupport._JAVA7):
                validated = True
            else:
                java_home_name = os.environ[SystemTestSupport.JAVA7_HOME_ENVVAR]
                java_home_key = SystemTestSupport._JAVA7
        else:
            ex = exception_helper.create_system_test_exception('WLSDPLY-09867', version)
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        if not validated:
            if StringUtils.isEmpty(java_home_name):
                ex = exception_helper.create_system_test_exception('WLSDPLY-09868', version)
                _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                raise ex

        java_home = get_canonical_file(java_home_name)
        if not java_home.exists():
            _logger.finer('WLSDPLY-09886', java_home_name,
                          class_name=_class_name, method_name=_method_name)
        elif not java_home.isDirectory():
            _logger.finer('WLSDPLY-09887', java_home_name,
                          class_name=_class_name, method_name=_method_name)

        self._java_homes[java_home_key] = java_home

    def __requires_jrf(self, types):
        return SystemTestSupport.JRF_TEST_TYPE in types or SystemTestSupport.RESTRICTED_JRF_TEST_TYPE in types

    def __get_and_validate_test_automation_home(self, option_value):
        _method_name = '__get_and_validate_test_automation_home'

        if StringUtils.isEmpty(option_value):
            test_automation_home = get_canonical_path(self.get_build_dir(),
                                                       SystemTestSupport.TEST_AUTOMATION_HOME_DEFAULT)
        else:
            test_automation_home = get_canonical_file(option_value)

        if not test_automation_home.exists():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09869',
                                                               'TEST_AUTOMATION_HOME',
                                                               test_automation_home.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex
        elif not test_automation_home.isDirectory():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09870',
                                                               'TEST_AUTOMATION_HOME',
                                                               test_automation_home.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return test_automation_home

    def __get_and_validate_test_support_home(self, option_value):
        _method_name = '__get_and_validate_test_support_home'

        if StringUtils.isEmpty(option_value):
            test_support_home = get_canonical_path(self.get_build_dir(),
                                                    SystemTestSupport.TEST_SUPPORT_HOME_DEFAULT)
        else:
            test_support_home = get_canonical_file(option_value)

        if not test_support_home.exists():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09869',
                                                               'TEST_SUPPORT_HOME',
                                                               test_support_home.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex
        elif not test_support_home.isDirectory():
            ex = exception_helper.create_system_test_exception('WLSDPLY-09870',
                                                               'TEST_SUPPORT_HOME',
                                                               test_support_home.getPath())
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return test_support_home

    def __get_and_validate_supported_versions(self, option_value):
        _method_name = '__get_and_validate_supported_versions'

        supported_versions = self.__get_supported_versions(option_value)
        non_matching_versions = [item for item in supported_versions
                                 if item not in SystemTestSupport.ALL_DOMAIN_VERSIONS]
        if non_matching_versions:
            ex = exception_helper.create_system_test_exception('WLSDPLY-09871',
                                                               ', '.join(non_matching_versions))
            _logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return supported_versions

    def __get_and_validate_user_tests_to_run(self, supported_versions, user_tests_to_run):
        _method_name = '__get_and_validate_user_tests_to_run'

        _logger.entering(supported_versions, class_name=_class_name, method_name=_method_name)
        user_specified_tests = ["wls1212:wls1213"]

        _logger.exiting(class_name=_class_name, method_name=_method_name, result=user_specified_tests)

        return user_specified_tests

    def __get_supported_versions(self, option_value):
        """
        Converts a string of comma-separated WLS versions into a Python list
        :param option_value: A comma-separated string of WLS versions (without the dots)
        :return: A Python list containing the supported WLS versions without the dots in them
        """
        if StringUtils.isEmpty(option_value) or option_value == SystemTestSupport.SUPPORTED_VERSIONS_ALL:
            supported_versions = SystemTestSupport.SUPPORTED_VERSIONS_DEFAULT
        else:
            supported_versions = [x.strip() for x in option_value.split(',') if x]

        return supported_versions

    def __get_log_directory(self, option_value):
        if StringUtils.isEmpty(option_value):
            log_dir = get_canonical_path(self.get_build_dir(),
                                          SystemTestSupport.LOG_DIR_DEFAULT)
        else:
            log_dir = get_canonical_file(option_value)
        return log_dir

    def __get_logging_properties_file(self, option_value):
        if StringUtils.isEmpty(option_value):
            logging_properties_file = get_canonical_path(self.get_build_dir(),
                                                          SystemTestSupport.LOG_PROPERTIES_FILE_DEFAULT)
        else:
            logging_properties_file = get_canonical_file(option_value)

        return logging_properties_file

    def __get_domain_parent_dir(self, option_value):
        if StringUtils.isEmpty(option_value):
            domain_parent_dir = get_canonical_path(self.get_build_dir(),
                                                    SystemTestSupport.DOMAIN_PARENT_DIR_DEFAULT)
        else:
            domain_parent_dir = get_canonical_file(option_value)

        return domain_parent_dir


def get_canonical_file(file_name):
    result = File(file_name)
    try:
        result = result.getCanonicalFile()
    except IOException:
        result = result.getAbsoluteFile()
    return result


def get_canonical_path(dir_path, file_name):
    result = File(dir_path, file_name)
    try:
        result = result.getCanonicalFile()
    except IOException:
        result = result.getAbsoluteFile()
    return result


def _is_target_version_less_than_source_version(source, target):
    return target < source


def _get_dot_delimited_version(compressed_version):
    result = ''
    result += compressed_version[0:2]
    for i in range(2, len(compressed_version)):
        result += '.'
        result += compressed_version[i]
    return result
