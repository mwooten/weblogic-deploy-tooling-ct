"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.stages.system_test_it import SystemTestIT

_class_name = 'SingleApplicationTest'


class SingleApplicationTest(SystemTestIT):
    """

    """
    def __init__(self, step_name, stage, test_def, logger):
        SystemTestIT.__init__(self, step_name, stage, test_def, logger)

    def setUp(self):
        _method_name = 'setUp'
        SystemTestIT.setUp(self)
        self.populate_env_map(self._test_def)
        self._logger.finest('env={0}', str(self._env), class_name=self._class_name, method_name=_method_name)

    def populate_env_map(self, test_def):
        a2c_dev_testing_mode = test_def.get_env_var_value('A2C_DEV_TESTING_MODE_ENVVAR')
        if a2c_dev_testing_mode is not None:
            self._env.put(SystemTestIT.A2C_DEV_TESTING_MODE_ENVVAR, a2c_dev_testing_mode)

        build_dir = test_def.get_env_var_value('BUILD_DIR_ENVVAR')
        if build_dir is not None:
            self._env.put(SystemTestIT.BUILD_DIR_ENVVAR, build_dir)

        source_domain_name = test_def.get_env_var_value('SOURCE_DOMAIN_NAME_ENVVAR')
        if source_domain_name is not None:
            self._env.put(SystemTestIT.SOURCE_DOMAIN_NAME_ENVVAR, source_domain_name)

        supported_versions = test_def.get_env_var_value('SUPPORTED_VERSIONS_ENVVAR')
        if supported_versions is not None:
            self._env.put(SystemTestIT.SUPPORTED_VERSIONS_ENVVAR, supported_versions)

        target_domain_name = test_def.get_env_var_value('TARGET_DOMAIN_NAME_ENVVAR')
        if target_domain_name is not None:
            self._env.put(SystemTestIT.TARGET_DOMAIN_NAME_ENVVAR, target_domain_name)

        test_def_file = test_def.get_env_var_value('TEST_DEF_FILE_ENVVAR')
        if test_def_file is not None:
            self._env.put(SystemTestIT.TEST_DEF_FILE_ENVVAR, test_def_file)

        user_tests_to_run = test_def.get_env_var_value('USER_TESTS_TO_RUN_ENVVAR')
        if user_tests_to_run is not None:
            self._env.put(SystemTestIT.USER_TESTS_TO_RUN_ENVVAR, user_tests_to_run)

        wait_between_phases_secs = test_def.get_env_var_value('WAIT_BETWEEN_PHASES_SECS_ENVVAR')
        if wait_between_phases_secs is not None:
            self._env.put(SystemTestIT.WAIT_BETWEEN_PHASES_SECS_ENVVAR, wait_between_phases_secs)
