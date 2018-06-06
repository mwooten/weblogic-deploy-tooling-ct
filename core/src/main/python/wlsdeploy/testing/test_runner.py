"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_constants, testing_helper
from wlsdeploy.testing.define.test_def import TestDef
from wlsdeploy.testing.define.test_def_stage import TestDefStage
from wlsdeploy.testing.exception import exception_helper
from wlsdeploy.testing.stage_runner import StageRunner
from wlsdeploy.testing.test_results import TestResult
from wlsdeploy.testing.test_results import TestResults


class TestRunner(object):
    """

    """
    _class_name = 'TestRunner'

    def __init__(self, logger):
        self._logger = logger
        self._stage_modules_cache = {}

    def run_test(self, test_type, test_def_file, test_def_overrides_file, test_def_verifier_name=None,
                 test_def_metadata_file=None, verify_only=False):
        """
        Runs the test specified in the given '''test_def''' object.

        :param test_type:
        :param test_def_file: A file object created from a JSON/YAML test definition file name
        :param test_def_overrides_file: A file object created from a test definition overrides properties file
        :param test_def_verifier_name: The name of the verification test to use when
                                       verifying the test definition file
        :param test_def_metadata_file: A file object created from a JSON/YAML test definition metadata file
        :param verify_only: A flag indicating to only perform test verification steps
        :return: TestResults object created when running the test
        :raises TestingException: if a TestingException is raised while running the test
        :raises TestDefinitionException: if test_def Is missing a metadata file field
        :raises SystemTestException: if a SystemTestException is raised while running the test
        :raises IntegrationTestException: if a IntegrationTestException is raised while running the test
        """

        _method_name = 'run_test'

        self._logger.entering(test_type, class_name=self._class_name, method_name=_method_name)

        test_results = TestResults()
        stage_runner = StageRunner(self._logger)

        test_def = TestDef(test_def_file, self._logger, test_def_overrides_file, test_def_metadata_file)

        test_def_type = test_def.get_type()

        self._logger.finer('test_def_type={0}', test_def_type,
                           class_name=self._class_name, method_name=_method_name)

        if test_def_type not in testing_constants.SUPPORTED_TEST_DEF_TYPES:
            ex = \
                exception_helper.create_test_definition_exception('WLSDPLY-09823',
                                                                  test_def_file.getAbsolutePath(),
                                                                  test_def_type,
                                                                  ', '.join(testing_constants.SUPPORTED_TEST_DEF_TYPES))
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        if verify_only:
            self._logger.info('WLSDPLY-09865', test_def.get_name(), test_def.get_def_file_name(),
                              class_name=self._class_name, method_name=_method_name)
        else:
            self._logger.info('WLSDPLY-09800', test_def.get_name(), test_def.get_def_file_name(),
                              class_name=self._class_name, method_name=_method_name)

        test_verifier = TestRunner.TestDefVerifier(test_type, self._logger, stage_runner)

        if test_def_metadata_file is not None:
            metadata_file_verifier = TestRunner.TestDefMetadataVerifier(test_type,
                                                                        self._logger, stage_runner)
            test_result = metadata_file_verifier.verify_test_def_metadata(test_def_metadata_file)
            test_results.set_test_result(test_result)

        if test_results.get_errors_count() > 0:
            ex = \
                exception_helper.create_verification_exception('WLSDPLY-09802',
                                                               test_def_metadata_file)
            self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
            raise ex

        test_result = test_verifier.verify_test_def(test_def, verifier_name=test_def_verifier_name)

        if test_result.get_errors_count() > 0:
            test_results.set_test_result(test_result)

        if test_results.get_errors_count() is 0 and verify_only is False:
            for stage in test_def.get_stages():
                test_result = stage_runner.run_stage(stage, test_def)
                test_results.set_test_result(test_result)
                if test_results.get_errors_count() > 0:
                    if stage.continue_when_fail() == 'true':
                        self._logger.warning('WLSDPLY-09849', stage.get_name(), TestDefStage.CONTINUE_WHEN_FAIL,
                                             class_name=self._class_name, method_name=_method_name)
                    else:
                        break

        log_policy = test_def.get_stdout_log_policy()

        if log_policy == testing_constants.STDOUT_LOG_POLICY_FILE:
            test_results.log_results(self._logger)
        elif log_policy == testing_constants.STDOUT_LOG_POLICY_STDOUT:
            test_results.print_details()
        elif log_policy == testing_constants.STDOUT_LOG_POLICY_BOTH:
            test_results.log_results(self._logger)
            test_results.print_details()

        self._logger.exiting(class_name=self._class_name, method_name=_method_name)

        return test_results

    class TestDefVerifier(object):
        """

        """
        _class_name = 'TestDefVerifier'

        def __init__(self, test_type, logger, stage_runner):
            self._test_type = test_type
            self._logger = logger
            self._stage_runner = stage_runner

            # A TestDefVerifier can be asked to use several different verification
            # tests, so we use a cache to store the loaded ones in.
            self._stage_modules_cache = {}

        def verify_test_def(self, test_def, verifier_name=None, stage_name=None):
            """
            Uses the verification test associated with verifier_name, to verify that
            test_def conforms to the metadata for it's test definition type.

            testing_constants.DEFAULT_TEST_DEF_VERIFIER_TEST is used, if the
            verifier_name parameter is not provided.

            The string resulting from concatenating 'certified_' to the test type
            is used, if the stage_name parameter is not provided.

            :param test_def: The TestDef object to verify
            :param verifier_name: The name of the verification test to use.
            :param stage_name: The name of the verification test stage to use
            :return: A TestResult object containing the results of the verification test
            :raises VerificationException: if one is thrown while running the verification test stage's steps
            """
            _method_name = 'verify_test'

            self._logger.entering(class_name=self._class_name, method_name=_method_name)

            if verifier_name is not None:
                # TODO: Use verifier_name to search for the verification test
                # in verification_test
                verify_test_def_file_path = None
            else:
                verify_test_def_file_path = \
                    '%s/%s/%s' % (testing_constants.VERIFICATION_TEST_DIR,
                                  testing_constants.CERTIFIED_DIR,
                                  testing_constants.DEFAULT_TEST_DEF_VERIFIER_TEST)
            if stage_name is None:
                stage_name = 'certified_%s' % self._test_type

            verify_test_def_file = testing_helper.extract_file(verify_test_def_file_path, self._logger)
            verify_test_def = TestDef(verify_test_def_file, self._logger)

            stage = verify_test_def.get_stage(stage_name)

            if stage is None:
                ex = \
                    exception_helper.create_verification_exception('WLSDPLY-09815',
                                                                   stage_name,
                                                                   verify_test_def.get_def_file_name())
                self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
                raise ex

            stage_module = self._stage_runner.get_stage_module(stage)
            stage_class = getattr(stage_module, stage.get_class_name())

            suite = unittest.TestSuite()

            test_result = TestResult(stage_name)

            for step_name in stage.get_step_names():
                suite.addTest(stage_class(step_name, stage, test_def, test_result, self._logger))

            if stage_name not in self._stage_modules_cache:
                self._stage_modules_cache[stage_name] = stage_module

            suite.run(test_result)

            self._logger.exiting(class_name=self._class_name, method_name=_method_name)

            return test_result

    class TestDefMetadataVerifier(object):
        """

        """
        _class_name = 'TestDefMetadataVerifier'

        def __init__(self, test_type, logger, stage_runner):
            self._test_type = test_type
            self._logger = logger
            self._stage_runner = stage_runner

        def verify_test_def_metadata(self, metadata_file_name):
            """

            :param metadata_file_name: File name for the test definition metadata file
            :return: A TestResult object containing the results of the verification test
            :raises VerificationException: if one is thrown while running the verification test stage's steps
            """
            _method_name = 'verify_test_def_metadata'

            self._logger.entering(class_name=self._class_name, method_name=_method_name)

            self._logger.info('WLSDPLY-09859', metadata_file_name,
                              class_name=self._class_name, method_name=_method_name)

            test_def_metadata_file = testing_helper.verify_file_exists(metadata_file_name, self._logger)
            test_def_metadata_dict = testing_helper.translate_file(test_def_metadata_file, self._logger)

            verify_test_def_file_path = \
                '%s/%s/%s' % (testing_constants.VERIFICATION_TEST_DIR,
                              testing_constants.CERTIFIED_DIR,
                              testing_constants.DEFAULT_TEST_DEF_METADATA_VERIFIER_TEST)

            stage_name = testing_constants.METADATA_FILE_VERIFICATION_STAGE_NAME

            verify_test_def_file = testing_helper.extract_file(verify_test_def_file_path, self._logger)
            verify_test_def = TestDef(verify_test_def_file, self._logger)

            stage = verify_test_def.get_stage(stage_name)

            if stage is None:
                ex = \
                    exception_helper.create_verification_exception('WLSDPLY-09815',
                                                                   stage_name,
                                                                   verify_test_def.get_def_file_name())
                self._logger.throwing(ex, class_name=self._class_name, method_name=_method_name)
                raise ex

            stage_module = self._stage_runner.get_stage_module(stage)
            stage_class = getattr(stage_module, stage.get_class_name())

            suite = unittest.TestSuite()

            test_result = TestResult(stage_name)

            for step_name in stage.get_step_names():
                suite.addTest(stage_class(step_name, test_def_metadata_file, test_def_metadata_dict,
                                          stage, test_result, self._logger))

            suite.run(test_result)

            self._logger.exiting(class_name=self._class_name, method_name=_method_name)

            return test_result
