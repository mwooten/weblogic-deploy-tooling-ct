"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

# python classes from weblogic-deploy-tooling
from wlsdeploy.util import dictionary_utils

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_constants

_class_name = 'TestDefStage'


class TestDefStage(object):
    """

    """

    CONTINUE_WHEN_FAIL = 'continue_when_fail'
    STEP_NAMES = 'step_names'
    STEP_NAMES_FILE = 'step_names_file'
    SCRIPT_TO_RUN = 'script_to_run'
    MODULE_TO_IMPORT = 'module_to_import'

    MODULE_NAME = 'module_name'
    CLASS_NAME = 'class_name'

    def __init__(self, stage_name, stage_dict, test_def_metadata, logger):
        self._name = stage_name
        self._stage_dict = stage_dict
        self._logger = logger
        self._test_def_metadata = test_def_metadata
        self._module_name = None
        self._class_name = None

    def get_name(self):
        return self._name

    def get_step_names(self):
        return dictionary_utils.get_dictionary_element(self._stage_dict, TestDefStage.STEP_NAMES)

    def get_script_to_run(self):
        return dictionary_utils.get_element(self._stage_dict, TestDefStage.SCRIPT_TO_RUN)

    def get_module_to_import(self):
        return dictionary_utils.get_element(self._stage_dict, TestDefStage.MODULE_TO_IMPORT)

    def get_module_name(self):
        return self._module_name

    def set_module_name(self, module_name):
        self._module_name = module_name

    def get_class_name(self):
        return self._class_name

    def set_class_name(self, class_name):
        self._class_name = class_name

    def get_field_value(self, metadata_path, field_name=None, default=None):
        """
        Finds and returns the value assigned to the field that metadata_path points to. The assumption
        is that metadata_path contains the field name (as the right-most slash-delimited value), if
        field_name argument isn't supplied.

        :param metadata_path: A forward slash-delimited string that identifies where field_name
        is located, in the test definition data bag.
        :param field_name: An optional string containing the field name to find the value for.
        :param default: An optional default value to return, if one could not be found.
        :return: The value assigned to field_name in this test definition object, based on the
        specified metadata_path, or None.
        """
        path_tokens = metadata_path.split('/')

        if field_name is None:
            field_name = path_tokens.pop()

        field_value = None

        if field_name is not None:
            def_dict_node = self._stage_dict

            if path_tokens:
                for path_token in path_tokens:
                    if path_token in def_dict_node:
                        def_dict_node = def_dict_node[path_token]
                    else:
                        break

            if field_name in def_dict_node:
                field_value = def_dict_node[field_name]

        if field_value is None:
            metadata_path = '%s/%s/%s' % (testing_constants.STAGES, self._name, metadata_path)
            field_value = self._test_def_metadata.get_default_value(metadata_path)

        if default is not None and field_value is None:
            field_value = default

        return field_value

    def continue_when_fail(self):
        response = dictionary_utils.get_dictionary_element(self._stage_dict, TestDefStage.CONTINUE_WHEN_FAIL)
        if response is None:
            response = self._test_def_metadata.get_default_value(TestDefStage.CONTINUE_WHEN_FAIL)
        return response
