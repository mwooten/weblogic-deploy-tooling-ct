"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_common, testing_helper
from wlsdeploy.testing.compare.model_comparer import ModelComparer

_class_name = 'CompareModels'
_SETTINGS_0 = 'settings-0'
_SETTINGS_1 = 'settings-1'


class CompareModels(unittest.TestCase):
    """

    """
    MODEL_FILES = 'model_files'
    VARIABLE_FILES = 'variable_files'
    ARCHIVE_FILES = 'archive_files'
    COMPARISON_RESULTS_FILE = 'comparison_results_file'

    def __init__(self, test_name, stage, test_def, logger):
        unittest.TestCase.__init__(self, test_name)
        self._test_name = test_name
        self._stage = stage
        self._test_def = test_def
        self._logger = logger

    def stepCompareModels(self):
        _method_name = 'stepCompareModels'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        model_files = self._stage.get_field_value(CompareModels.MODEL_FILES)
        variable_files = self._stage.get_field_value(CompareModels.VARIABLE_FILES)
        archive_files = self._stage.get_field_value(CompareModels.ARCHIVE_FILES)
        compare_results_file = self._stage.get_field_value(CompareModels.COMPARISON_RESULTS_FILE)

        self._logger.info('WLSDPLY-09841', self._stage.get_class_name(), 'four',
                          class_name=_class_name, method_name=_method_name)

        self._logger.info('WLSDPLY-09842',
                          '%s="%s"; %s="%s"; %s="%s"; %s="%s";' % (
                              CompareModels.MODEL_FILES, str(model_files),
                              CompareModels.VARIABLE_FILES, str(variable_files),
                              CompareModels.ARCHIVE_FILES, str(archive_files),
                              CompareModels.COMPARISON_RESULTS_FILE, compare_results_file
                          ),
                          self._test_def.get_def_file_name(),
                          class_name=_class_name, method_name=_method_name)

        expected_settings = self._test_def.get_settings(_SETTINGS_0)
        actual_settings = self._test_def.get_settings(_SETTINGS_1)

        expected_model_file = expected_settings.get_model_file()
        actual_model_file = actual_settings.get_model_file()

        self._logger.info('WLSDPLY-09909', expected_model_file.getAbsolutePath(), actual_model_file.getAbsolutePath(),
                          class_name=_class_name, method_name=_method_name)

        expected_model_dict, actual_model_dict = _load_models(expected_model_file, actual_model_file, self._logger)

        for i in range(len(variable_files)):
            variable_file_name = self._test_def.get_field_value(variable_files[i])
            if i == 0:
                self._logger.info('WLSDPLY-09924', variable_file_name, "expected",
                                  class_name=_class_name, method_name=_method_name)
                testing_common.apply_substitution_variables_file(variable_file_name, expected_model_dict, self._logger)
            elif i == 1:
                self._logger.info('WLSDPLY-09924', variable_file_name, "actual",
                                  class_name=_class_name, method_name=_method_name)
                testing_common.apply_substitution_variables_file(variable_file_name, actual_model_dict, self._logger)

        model_comparator = ModelComparer(self._logger)
        comparison_results = model_comparator.compare_models(expected_model_dict, actual_model_dict)
        comparison_results.log_results(self._logger)
        self.assertEqual(comparison_results.get_errors_count(), 0)

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################


def _load_models(expected_model_file, actual_model_file, logger):
    expected_model_dict = testing_helper.translate_file(expected_model_file, logger)
    actual_model_dict = testing_helper.translate_file(actual_model_file, logger)
    return expected_model_dict, actual_model_dict
