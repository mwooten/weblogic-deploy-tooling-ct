"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import os

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import VariableException

# python classes from weblogic-deploy-tooling
from wlsdeploy.util import dictionary_utils
from wlsdeploy.util import variables

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_constants, testing_helper
from wlsdeploy.testing.define.test_def_metadata import TestDefMetadata
from wlsdeploy.testing.define.test_def_settings import TestDefSettings
from wlsdeploy.testing.define.test_def_stage import TestDefStage
from wlsdeploy.testing.exception import exception_helper

_class_name = 'TestDef'


class TestDef(object):
    """
    """
    COPYRIGHT = 'copyright'
    LICENSE = 'license'
    TYPE = 'type'
    NAME = 'name'
    DESCRIPTION = 'description'
    METADATA_FILE = 'metadata_file'
    OVERRIDES_FILE = 'overrides_file'

    def __init__(self, test_def_file, logger, test_def_overrides_file=None,
                 test_def_metadata_file=None):
        _method_name = '__init__'

        self._logger = logger

        self._test_def_file = test_def_file

        self._test_def_dict = testing_helper.translate_file(test_def_file, self._logger)
        self._logger.finer('self._test_def_dict={0}', str(self._test_def_dict),
                           class_name=_class_name, method_name=_method_name)

        # The best practice is for all test metadata files to make
        # metadata_file a required field, which can be overridden by
        # specifying the -test_def_metadata_file argument, on the
        # command line.

        metadata_file = dictionary_utils.get_element(self._test_def_dict, TestDef.METADATA_FILE)

        if test_def_metadata_file is not None:
            # This means the -test_def_metadata_file argument was
            # specified on the command line. Use that to override
            # whatever was assigned to the metadata_file field, in
            # the test definition file.
            metadata_file = test_def_metadata_file

        if metadata_file is None:
            # There was no -test_def_metadata_file argument, and there
            # either is no metadata_file test-wide parameter in the test
            # definition, or it's value was None. In either case, this is
            # an error, because the metadata is needed from this point
            # forward.
            #
            # NOTE: You can't just hard-code a static (or default) value
            # here, because the python classes in this define package are
            # used for all types of test (not just integration ones) as well
            # as ones like regression, which we haven't even begun to look
            # at yet.
            #  .
            ex = exception_helper.create_test_definition_exception('WLSDPLY-09827',
                                                                   test_def_file.getAbsolutePath(),
                                                                   TestDef.METADATA_FILE)
            self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        # This next line could potentially raise a TestDefinitionException.
        # If it does, it means an error happened processing the metadata file.
        # We treat this as an "unrecoverable error", and just let it bubble up

        self._test_def_metadata = TestDefMetadata(self.get_def_file_name(),
                                                  metadata_file,
                                                  self._logger)

        overrides_file_name = dictionary_utils.get_element(self._test_def_dict, TestDef.OVERRIDES_FILE)

        if test_def_overrides_file is not None:
            overrides_file_name = test_def_overrides_file

        if overrides_file_name is not None:
            _apply_overrides_file(overrides_file_name, self._test_def_dict, self._logger)

        self._env_vars_dict = self.__get_env_vars_dict()

        settings_dict = self.__get_settings_dict()
        if settings_dict is not None:
            self._settings = TestDef.SettingsIterator(settings_dict, self._test_def_metadata, self._logger)

        stages_dict = self.__get_stages_dict()
        if stages_dict is not None:
            self._stages = TestDef.StagesIterator(stages_dict, self._test_def_metadata, self._logger)

    def get_def_file_name(self):
        return self._test_def_file.getAbsolutePath()

    def get_metadata(self):
        return self._test_def_metadata

    def get_metadata_file(self):
        return dictionary_utils.get_element(self._test_def_dict, TestDef.METADATA_FILE)

    def get_copyright(self):
        return dictionary_utils.get_element(self._test_def_dict, TestDef.COPYRIGHT)

    def get_license(self):
        return dictionary_utils.get_element(self._test_def_dict, TestDef.LICENSE)

    def get_type(self):
        return dictionary_utils.get_element(self._test_def_dict, TestDef.TYPE)

    def get_name(self):
        return dictionary_utils.get_element(self._test_def_dict, TestDef.NAME)

    def get_description(self):
        return dictionary_utils.get_element(self._test_def_dict, TestDef.DESCRIPTION)

    def get_settings_ids(self):
        return self._settings.get_settings_ids()

    def get_settings(self, settings_id):
        _method_name = 'get_settings'

        if settings_id not in self.get_settings_ids():
            ex = exception_helper.create_test_definition_exception('WLSDPLY-09816',
                                                                   settings_id,
                                                                   self.get_def_file_name())
            self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

        return self._settings.get_settings(settings_id)

    def get_stages(self):
        return self._stages

    def get_stage_names(self):
        return self._stages.get_stage_names()

    def get_stage(self, name):
        return self._stages.get_stage(name)

    def get_logs_dir(self):
        logs_dir = dictionary_utils.get_element(self._test_def_dict, testing_constants.LOGS_DIR)
        if logs_dir is None:
            logs_dir = self._test_def_metadata.get_default_value(testing_constants.LOGS_DIR)

        return logs_dir

    def get_log_file(self):
        log_file = dictionary_utils.get_element(self._test_def_dict, testing_constants.LOG_FILE)
        if log_file is None:
            log_file = self._test_def_metadata.get_default_value(testing_constants.LOG_FILE)
        return log_file

    def get_log_properties(self):
        log_properties = dictionary_utils.get_element(self._test_def_dict, testing_constants.LOG_PROPERTIES)
        if log_properties is None:
            log_properties = self._test_def_metadata.get_default_value(testing_constants.LOG_PROPERTIES)
        return log_properties

    def get_stdout_log_policy(self):
        stdout_log_policy = dictionary_utils.get_element(self._test_def_dict, testing_constants.STDOUT_LOG_POLICY)
        if stdout_log_policy is None:
            stdout_log_policy = self._test_def_metadata.get_default_value(testing_constants.STDOUT_LOG_POLICY)
        return stdout_log_policy

    def get_field_value(self, metadata_path, field_name=None):
        """
        Finds and returns the value assigned to the field that metadata_path points to. The assumption
        is that metadata_path contains the field name (as the right-most slash-delimited value), if
        field_name argument isn't supplied.

        :param metadata_path: A forward slash-delimited string that identifies where field_name
        is located, in the test definition data bag.
        :param field_name: An optional string containing the field name to find the value for.
        :return: The value assigned to field_name in this test definition object, based on the
        specified metadata_path, or None.
        """
        path_tokens = metadata_path.split('/')

        if field_name is None:
            field_name = path_tokens.pop()

        field_value = None

        if field_name is not None:
            def_dict_node = self._test_def_dict

            if path_tokens:
                for path_token in path_tokens:
                    if path_token in def_dict_node:
                        def_dict_node = def_dict_node[path_token]
                    else:
                        break

            if field_name in def_dict_node:
                field_value = def_dict_node[field_name]

        return field_value

    def contains_metadata_path(self, metadata_path):
        _method_name = 'contains_metadata_path'

        response = False

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        path_tokens = metadata_path.split('/')
        if path_tokens:
            def_dict_node = self._test_def_dict

            for path_token in path_tokens:
                if path_token in def_dict_node:
                    def_dict_node = def_dict_node[path_token]
                    response = True
                else:
                    response = False
                    break

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

        return response

    def get_env_var_value(self, env_var_alias):
        env_var_value = None
        env_var_name = dictionary_utils.get_element(self._env_vars_dict, env_var_alias)
        if env_var_name is None:
            metadata_path = '%s/%s' % (testing_constants.ENV_VARS, env_var_alias)
            env_var_name = self._test_def_metadata.get_default_value(metadata_path)

        if env_var_name is not None and env_var_name in os.environ:
            env_var_value = os.environ[env_var_name]
        return env_var_value

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

    def __get_env_vars_dict(self):
        return dictionary_utils.get_dictionary_element(self._test_def_dict, testing_constants.ENV_VARS)

    def __get_settings_dict(self):
        return dictionary_utils.get_dictionary_element(self._test_def_dict, testing_constants.SETTINGS)

    def __get_stages_dict(self):
        return dictionary_utils.get_dictionary_element(self._test_def_dict, testing_constants.STAGES)

    class SettingsIterator(object):
        def __init__(self, settings_dict, test_def_metadata, logger):
            self._settings_dict = settings_dict
            self._test_def_metadata = test_def_metadata
            self._logger = logger
            self._iterator_position = 0

        def __iter__(self):
            return self

        def next(self):
            if self._iterator_position < len(self._settings_dict):
                settings_id = self._settings_dict.keys()[self._iterator_position]
                test_def_settings = self.__create_test_def_settings(settings_id)
                self._iterator_position += 1
            else:
                self._iterator_position = 0
                raise StopIteration

            return test_def_settings

        def get_settings_ids(self):
            return self._settings_dict.keys()

        def get_settings(self, settings_id):
            return self.__create_test_def_settings(settings_id)

        def __create_test_def_settings(self, settings_id):
            return TestDefSettings(settings_id, self._settings_dict[settings_id],
                                   self._test_def_metadata, self._logger)

    class StagesIterator(object):
        def __init__(self, stages_dict, test_def_metadata, logger):
            self._stages_dict = stages_dict
            self._test_def_metadata = test_def_metadata
            self._logger = logger
            self._iterator_position = 0

        def __iter__(self):
            return self

        def next(self):
            if self._iterator_position < len(self._stages_dict):
                name = self._stages_dict.keys()[self._iterator_position]
                test_def_stage = self.__create_test_def_stage(name)
                self._iterator_position += 1
            else:
                self._iterator_position = 0
                raise StopIteration

            return test_def_stage

        def get_stage_names(self):
            return self._stages_dict.keys()

        def get_stage(self, name):
            return self.__create_test_def_stage(name)

        def __create_test_def_stage(self, name):
            test_def_stage = None
            if name in self._stages_dict:
                test_def_stage = TestDefStage(name, self._stages_dict[name],
                                              self._test_def_metadata, self._logger)
            return test_def_stage


def _apply_overrides_file(overrides_file_name, test_def_dict, logger):
    _method_name = '_apply_overrides_file'

    try:
        variable_map = variables.load_variables(overrides_file_name)
        variables.substitute(test_def_dict, variable_map)
    except VariableException, ve:
        ex = exception_helper.create_testing_exception('WLSDPLY-09814',
                                                       overrides_file_name,
                                                       ve.getLocalizedMessage(), error=ve)
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex
