"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_helper, testing_constants
from wlsdeploy.testing.define.test_def_stage import TestDefStage
from wlsdeploy.testing.exception import exception_helper
from wlsdeploy.testing.test_results import TestResult

_class_name = 'StageRunner'


class StageRunner(object):
    """

    """
    def __init__(self, logger):
        self._logger = logger
        self._stage_modules_cache = {}
        self._stages_map = _load_stages_map(self._logger)

    def run_stage(self, stage, test_def):
        """
        Runs the given '''stage''' which is associated with the given '''test_def''' object.

        If this is a test definition for a testing_constants.SYSTEM_TEST, then the
        stage will have the following parameters:

            TestDefStage.STEP_NAMES_FILE
                The name of the JSON file that contains the step names for the stage.

            TestDefStage.STEP_NAMES
                A Python list containing the step (or test method) name of a stage. A stage
                is actually a class that extends unittest.TestCase, so step names are essentially
                the names of the methods in that class.

        :param stage: A TestDefStage object associated with the test definition file
        :param test_def: A TestDef object that contains the stages for the test
        :return: TestResult object created when running the stage
        :raises TestingException: if a TestingException is raised while running the test
        :raises SystemTestException: if a SystemTestException is raised while running the test
        :raises IntegrationTestException: if a IntegrationTestException is raised while running the test
        """
        _method_name = 'run_stage'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        if stage is None:
            ex = exception_helper.create_testing_exception('WLSDPLY-09862')
            self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        stage_module = self.get_stage_module(stage)
        test_result = self.__run_stage(stage_module, stage, test_def)

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

        return test_result

    def get_stage_module(self, stage):
        """
        Returns the Python module associated with the given stage.

        Getting a stage's module is not generally something that needs to be exposed, but
        the verification test type is an exception. For example, a TestDefVerifier needs to
        create and run a verification test, in order to verify that a TestDef is conformant
        with the test config metadata for it. Like all other test types, the steps in this
        verification test are defined in a stage module, but here the TestDefVerifier needs to
        run the stage steps on the TestDef, not asks a StageRunner to do it. Making this
        a public method allows that use case to be supported.

        The module and class name parameters are set on the passed in stage object, using
        information from the stages map that was created when the stages map JSON file was
        loaded.

        :param stage: A TestDefStage object
        :return: The Python module associated with a given stage
        :raises: TestingException: if there is problem obtaining the stage's Python module
        """
        _method_name = 'get_stage_module'

        if stage is None:
            ex = exception_helper.create_testing_exception('WLSDPLY-09862')
            self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        stage_name = stage.get_name()

        if stage_name not in self._stages_map:
            ex = exception_helper.create_testing_exception('WLSDPLY-09806', stage_name)
            self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        module_name = self._stages_map[stage_name][TestDefStage.MODULE_NAME]
        class_name = self._stages_map[stage_name][TestDefStage.CLASS_NAME]

        self._logger.finer('module_name={0}, class_name={1}', module_name, class_name,
                           class_name=_class_name, method_name=_method_name)

        if stage_name in self._stage_modules_cache:
            self._logger.fine('WLSDPLY-09817', stage_name, class_name=_class_name, method_name=_method_name)
            stage_module = self._stage_modules_cache[stage_name]
        else:
            self._logger.fine('WLSDPLY-09818', stage_name, class_name=_class_name, method_name=_method_name)
            stage_module = testing_helper.import_stage_module(module_name, self._logger)

        stage.set_module_name(module_name)
        stage.set_class_name(class_name)

        return stage_module

    def __run_stage(self, stage_module, stage, test_def):
        stage_name = stage.get_name()
        class_name = stage.get_class_name()

        stage_class = getattr(stage_module, class_name)

        suite = unittest.TestSuite()

        step_names = stage.get_step_names()

        test_result = TestResult(stage_name)

        if step_names:
            for step_name in step_names:
                suite.addTest(stage_class(step_name, stage, test_def, self._logger))

        if stage_name not in self._stage_modules_cache:
            self._stage_modules_cache[stage_name] = stage_module

        suite.run(test_result)

        return test_result


def _load_stages_map(logger):
    """
    Loads the JSON file that maps stage names to a Python module and class names.

    The map key is the stage name, which is passed to or used in several method calls.

    :return: A Python dictionary representation of the stages map
    :raises: TestingException: if the JSON file is malformed or there is problem loading the file
    """

    json_file_path = '%s/%s' % (testing_constants.TESTDEFS_DIR, testing_constants.CERTIFIED_STAGES_MAP_FILE)
    json_file = testing_helper.extract_file(json_file_path, logger)

    certified_stages = testing_helper.translate_file(json_file, logger)
    if testing_constants.STAGES not in certified_stages:
        ex = exception_helper.create_testing_exception('WLSDPLY-09805', json_file_path)
        raise ex

    stages_map = certified_stages[testing_constants.STAGES]

    json_file_path = '%s/%s' % (testing_constants.TESTDEFS_DIR, testing_constants.USER_DEFINED_STAGES_MAP_FILE)
    json_file = testing_helper.extract_file(json_file_path, logger)

    user_defined_stages = testing_helper.translate_file(json_file, logger)
    if testing_constants.STAGES not in user_defined_stages:
        ex = exception_helper.create_testing_exception('WLSDPLY-09805', json_file_path)
        raise ex

    stages_map.update(user_defined_stages[testing_constants.STAGES])

    return stages_map
