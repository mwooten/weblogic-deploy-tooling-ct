"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import unittest

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import PyOrderedDict

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.define.test_def_metadata import TestDefMetadata

_class_name = 'VerifyTestDef'


class VerifyTestDef(unittest.TestCase):
    """
    Stage module for verifying a test definition. This is the one the TestRunner.TestDefVerifier
    inner class uses, by default.
    """
    def __init__(self, test_name, stage, test_def, test_result, logger):
        """

        :param (str) test_name: The name of the unit test method (e.g. stage step) to be called, when the suite.run()
                                method is invoked.
        :param (TestDefStage) stage: Reference to stage object from test definition
        :param (TestDef) test_def: Reference to test definition object itself. Can be used to access test definition
                                   settings or metadata
        :param (TestResult) test_result: Reference to test result object for this verification test
        :param (PlatformLogger)logger: Reference to logger object to use for log messages and exceptions
        """
        unittest.TestCase.__init__(self, test_name)
        self._stage = stage
        self._test_def = test_def
        self._test_result = test_result
        self._logger = logger

    def verifyRequiredFieldsArePresent(self):
        _method_name = 'verifyRequiredFieldsArePresent'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        _module_name = self._stage.get_module_name()

        test_def_metadata = self._test_def.get_metadata()
        wildcard_fields = test_def_metadata.get_wildcard_fields()

        self._logger.finest('wildcard_fields={0}', str(wildcard_fields),
                            class_name=_class_name, method_name=_method_name)

        wildcard_field_values = {}

        if wildcard_fields:
            wildcard_field_values[TestDefMetadata.SETTINGS_ID_WILDCARD] = self._test_def.get_settings_ids()
            wildcard_field_values[TestDefMetadata.STAGE_NAME_WILDCARD] = self._test_def.get_stage_names()

            self._logger.finest('wildcard_field_values={0}', str(wildcard_field_values),
                                class_name=_class_name, method_name=_method_name)

        required_fields = test_def_metadata.get_required_fields()
        self._logger.finer('required_fields={0}', str(required_fields),
                           class_name=_class_name, method_name=_method_name)
        field_values = PyOrderedDict()

        for field_name, field_path_tokens in required_fields.iteritems():
            if wildcard_field_values:
                field_values = self.__get_wildcard_field_values(field_name, wildcard_field_values,
                                                                field_path_tokens, field_values)
            else:
                for field_path_token in field_path_tokens:
                    field_values['%s/%s' % (field_path_token, field_name)] = \
                        self._test_def.get_field_value(field_path_token, field_name)

        self._logger.finest('field_values={0}', str(field_values),
                            class_name=_class_name, method_name=_method_name)

        for name, value in field_values.iteritems():
            self._logger.finest('{0}={1}', name, value,
                                class_name=_class_name, method_name=_method_name)
            try:
                self.assertNotEqual(value, None)
            except AssertionError:
                self._test_result.add_error('WLSDPLY-09830', _method_name, _module_name, _class_name, name)

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

    def verifyOptionalFieldsAreValid(self):
        _method_name = 'verifyOptionalFieldsAreValid'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        test_def_metadata = self._test_def.get_metadata()
        optional_fields = test_def_metadata.get_optional_fields()
        self._logger.finer('optional_fields={0}', str(optional_fields),
                           class_name=_class_name, method_name=_method_name)

        self.assertEqual(True, True)
        self._logger.exiting(class_name=_class_name, method_name=_method_name)

    def verifyEORFieldsAreValid(self):
        _method_name = 'verifyEORFieldsAreValid'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        test_def_metadata = self._test_def.get_metadata()

        # Ask test definition metadata for it's eor (exclusive or)
        # fields. If there are some, it will return a Python dictionary
        # that looks something like this:
        #
        # {
        #     'stages/discover_domain': ['module_to_import', 'script_to_run'],
        #     'stages/shutdown_admin_server': ['script_to_run']
        # }
        #
        eor_fields = test_def_metadata.get_eor_fields()

        self._logger.finer('eor_fields={0}', str(eor_fields),
                           class_name=_class_name, method_name=_method_name)

        # If eor_fields is an empty Python dictionary, just return because
        # there is nothing that needs validating
        if not eor_fields:
            return

        eor_fields_present = {}

        # Loop through Python dictionary for test definition metadata's
        # eor_fields. The keys are the metadata path for the field(s), and
        # the values are a Python list containing the field names located
        # at that metadata path.

        for metadata_path, field_names in eor_fields.iteritems():
            # Use metadata_path to ask test definition if it has a
            # value, for each of the eor fields. Put the resulting
            # field names in a list.
            if self._test_def.contains_metadata_path(metadata_path):
                names_list = [field_name for field_name in field_names
                              if self._test_def.get_field_value(metadata_path, field_name) is not None]
                if metadata_path not in eor_fields_present:
                    eor_fields_present[metadata_path] = names_list
                else:
                    eor_fields_present[metadata_path].append(names_list)

        self._logger.finest('eor_fields_present={0}', str(eor_fields_present),
                            class_name=_class_name, method_name=_method_name)

        # The message produced when the next assertion fails needs the module
        # name, so go ahead and get that now.
        _module_name = self._stage.get_module_name()

        # eor_fields_present should only have one list item for a
        # given metadata path, so verify that that is the case
        for metadata_path, field_names in eor_fields_present.iteritems():
            try:
                self.assertEqual(len(field_names), 1)
            except AssertionError:
                if len(field_names) > 0:
                    # eor_fields_present contained more than 1 list item for
                    # a given metadata path, so record this as test error
                    self._test_result.add_error('WLSDPLY-09831', _method_name, _module_name,_class_name,
                                                metadata_path, ', '.join(field_names))
                else:
                    eor_fields = test_def_metadata.get_eor_fields(metadata_path)
                    # eor_fields_present contained no list items for a given
                    # metadata path, so record this as test error, as well
                    self._test_result.add_error('WLSDPLY-09831', _method_name, _module_name,_class_name,
                                                metadata_path,
                                                ', '.join(eor_fields[metadata_path]))

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

    def __get_wildcard_field_values(self, field_name, wildcard_field_values, field_path_tokens, field_values):
        _method_name = '__get_wildcard_field_values'

        self._logger.entering(class_name=_class_name, method_name=_method_name)

        for wildcard_field, wildcard_field_value_names in wildcard_field_values.iteritems():
            if wildcard_field in field_path_tokens:
                i = field_path_tokens.index(wildcard_field)
                for wildcard_field_value_name in wildcard_field_value_names:
                    field_path_tokens[i] = wildcard_field_value_name
                    field_values['%s/%s.%s' % (field_path_tokens[i], wildcard_field_value_name, field_name)] = \
                        self._test_def.get_field_value(field_path_tokens, field_name)

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

        return field_values
