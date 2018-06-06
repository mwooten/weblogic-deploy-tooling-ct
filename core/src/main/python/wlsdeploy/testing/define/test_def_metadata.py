"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import PyOrderedDict

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_constants, testing_helper
from wlsdeploy.testing.exception import exception_helper

_class_name = 'TestDefMetadata'


class TestDefMetadata(object):
    """

    """
    REQUIRED = 'required'
    DATA_TYPE = 'data_type'
    EOR_FIELDS = 'eor_fields'
    DEFAULT_VALUE = 'default_value'
    POSSIBLE_VALUES = 'possible_values'

    SETTINGS_ID_WILDCARD = '${settings_id}*'
    STAGE_NAME_WILDCARD = '${stage_name}*'

    def __init__(self, test_def_file_name, test_def_metadata_file, logger):
        """

        :param test_def_file_name:
        :param test_def_metadata_file:
        :param logger:
        """
        _method_name = '__init__'

        self._test_def_file_name = test_def_file_name
        self._logger = logger

        # test_def_metadata_file will be a string object, if the
        # -test_def_metadata_file command line parameter was
        # not provided. In that case, we need to use the metadata
        # file inside the installer archive.
        use_archive = isinstance(test_def_metadata_file, str)

        if use_archive:
            self._logger.info('WLSDPLY-09850', test_def_metadata_file, class_name=_class_name, method_name=_method_name)
        else:
            self._logger.info('WLSDPLY-09851', test_def_metadata_file, class_name=_class_name, method_name=_method_name)

        self._test_def_metadata_dict = _load_test_def_metadata(test_def_metadata_file, self._logger, use_archive)
        self._logger.finer('self._test_def_metadata_dict={0}', str(self._test_def_metadata_dict),
                           class_name=_class_name, method_name=_method_name)
        self._test_def_metadata_index = self.__populate_test_def_metadata_index(self._test_def_metadata_dict,
                                                                                [], PyOrderedDict())
        self._logger.finer('self._test_def_metadata_index={0}', str(self._test_def_metadata_index),
                           class_name=_class_name, method_name=_method_name)

    def get_required_fields(self):
        """

        :return:
        """
        required_fields = PyOrderedDict()
        iterators = [self._test_def_metadata_dict.iteritems()]
        while iterators:
            current_iterator = iterators.pop()
            for field_name, field_value in current_iterator:
                if TestDefMetadata.REQUIRED in field_value:
                    if TestDefMetadata.EOR_FIELDS not in field_value \
                            and field_value[TestDefMetadata.REQUIRED] == 'true':
                        metadata_paths = self._test_def_metadata_index[field_name]
                        self.__get_required_field_metadata_paths(field_name, metadata_paths)
                        required_fields[field_name] = metadata_paths
                else:
                    iterators.append(current_iterator)
                    iterators.append(field_value.iteritems())

        return required_fields

    def get_optional_fields(self):
        """

        :return:
        """
        optional_fields = PyOrderedDict()
        iterators = [self._test_def_metadata_dict.iteritems()]
        while iterators:
            current_iterator = iterators.pop()
            for field_name, field_value in current_iterator:
                if TestDefMetadata.REQUIRED in field_value:
                    if TestDefMetadata.EOR_FIELDS not in field_value \
                            and field_value[TestDefMetadata.REQUIRED] == 'false':
                        optional_fields[field_name] = self._test_def_metadata_index[field_name]
                else:
                    iterators.append(current_iterator)
                    iterators.append(field_value.iteritems())

        return optional_fields

    def get_eor_fields(self, metadata_path=None):
        """

        :return:
        """
        eor_fields = {}
        temp_dict = PyOrderedDict()
        iterators = [self._test_def_metadata_dict.iteritems()]
        while iterators:
            current_iterator = iterators.pop()
            for field_name, field_value in current_iterator:
                if TestDefMetadata.REQUIRED in field_value:
                    if TestDefMetadata.EOR_FIELDS in field_value:
                        temp_dict[field_name] = self._test_def_metadata_index[field_name]
                else:
                    iterators.append(current_iterator)
                    iterators.append(field_value.iteritems())

        if temp_dict:
            for key, value in temp_dict.iteritems():
                for metadata_path_token in value:
                    if metadata_path_token not in eor_fields:
                        eor_fields[metadata_path_token] = [key]
                    else:
                        eor_fields[metadata_path_token].append(key)

        if metadata_path is not None and metadata_path in eor_fields:
            eor_fields = {metadata_path: eor_fields[metadata_path]}

        return eor_fields

    def get_wildcard_fields(self):
        """

        :return:
        """
        wildcard_fields = PyOrderedDict()
        iterators = [self._test_def_metadata_dict.iteritems()]
        while iterators:
            current_iterator = iterators.pop()
            for field_name, field_value in current_iterator:
                if TestDefMetadata.REQUIRED not in field_value:
                    if '${' in field_name:
                        wildcard_fields[field_name] = self._test_def_metadata_index[field_name]

                    iterators.append(current_iterator)
                    iterators.append(field_value.iteritems())

        return wildcard_fields

    def get_default_value(self, metadata_path):
        """
        Returns the value assigned to the default_value dictionary element, of
        the metadata field specified in metadata_path.

        A value of None is returned, if the metadata field has no default_value
        dictionary element.

        :param metadata_path:
            A forward-slash delimited string of the path to a metadata field
        :type metadata_path: str
        :return:
            None or the value assigned to the default_value dictionary element, of a metadata field
        :raises: VerificationException:
            if metadata_path is malformed
        """
        default_value = None
        path_tokens = _get_path_tokens(metadata_path)
        if path_tokens:
            field_value = self.__get_metadata_field_value(path_tokens)
            if field_value is not None and TestDefMetadata.DEFAULT_VALUE in field_value:
                default_value = field_value[TestDefMetadata.DEFAULT_VALUE]
        return default_value

    def get_data_type(self, metadata_path):
        """
        Returns the value assigned to the data_type dictionary element, of the
        metadata field specified in metadata_path.

        :param metadata_path:
        :return:
        """
        data_type = None
        path_tokens = _get_path_tokens(metadata_path)
        if path_tokens:
            field_value = self.__get_metadata_field_value(path_tokens)
            if field_value is not None:
                data_type = field_value[TestDefMetadata.DATA_TYPE]
        return data_type

    def get_possible_values(self, metadata_path):
        """

        :param metadata_path:
        :return:
        """
        possible_values = []
        path_tokens = _get_path_tokens(metadata_path)
        if path_tokens:
            field_value = self.__get_metadata_field_value(path_tokens)
            if field_value is not None and TestDefMetadata.POSSIBLE_VALUES in field_value:
                possible_values = field_value[TestDefMetadata.POSSIBLE_VALUES]
        return possible_values

    def is_possible_value(self, value, metadata_path):
        """

        :param value:
        :param metadata_path:
        :return:
        """
        return value in self.get_possible_values(metadata_path)

    def is_valid_field(self, metadata_path):
        """

        :param metadata_path:
        :return:
        """
        field_value = None
        path_tokens = _get_path_tokens(metadata_path)
        if path_tokens:
            field_value = self.__get_metadata_field_value(path_tokens)
        return field_value is not None

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

    def __get_all_fields(self):
        all_fields = PyOrderedDict()
        iterators = [self._test_def_metadata_dict.iteritems()]
        while iterators:
            current_iterator = iterators.pop()
            for field_name, field_value in current_iterator:
                if TestDefMetadata.REQUIRED in field_value:
                    all_fields[field_name] = self._test_def_metadata_index[field_name]
                else:
                    iterators.append(current_iterator)
                    iterators.append(field_value.iteritems())

        return all_fields

    def __get_required_field_metadata_paths(self, field_name, metadata_paths):
        for metadata_path in metadata_paths:
            path_tokens = _get_path_tokens('%s/%s' % (metadata_path, field_name))
            field_value = self.__get_metadata_field_value(path_tokens)
            if field_value[TestDefMetadata.REQUIRED] == 'false':
                metadata_paths.remove(metadata_path)
        return

    def __get_metadata_field_value(self, path_tokens):
        field_name = path_tokens.pop()
        field_value = None

        if field_name is not None:
            test_def_metadata_dict_node = self._test_def_metadata_dict

            if path_tokens:
                for path_token in path_tokens:
                    if path_token in test_def_metadata_dict_node:
                        test_def_metadata_dict_node = test_def_metadata_dict_node[path_token]
                    else:
                        break

            if field_name in test_def_metadata_dict_node:
                field_value = test_def_metadata_dict_node[field_name]

        return field_value

    def __populate_test_def_metadata_index(self, test_def_metadata_dict, path_tokens, test_def_metadata_index):
        """

        :param test_def_metadata_dict:
        :param path_tokens:
        :param test_def_metadata_index:
        :return:
        """
        _method_name = '_populate_test_def_metadata_index'

        predefined_wildcards = [TestDefMetadata.SETTINGS_ID_WILDCARD, TestDefMetadata.STAGE_NAME_WILDCARD]

        for field_name, field_value in test_def_metadata_dict.iteritems():
            if isinstance(field_value, dict):
                if TestDefMetadata.EOR_FIELDS in field_value:
                    if field_name in field_value[TestDefMetadata.EOR_FIELDS]:
                        ex = exception_helper.create_test_definition_exception('WLSDPLY-09832',
                                                                               self._test_def_file_name,
                                                                               field_name)
                        self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                        raise ex

                if TestDefMetadata.REQUIRED in field_value:
                    field_name_path = [path_tokens[i] for i in range(len(path_tokens))]
                    if [x for x in predefined_wildcards if field_name == x]:
                        ex = exception_helper.create_test_definition_exception('WLSDPLY-09834')
                        self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                        raise ex

                    elif '${' in field_name:
                        ex = exception_helper.create_test_definition_exception('WLSDPLY-09833',
                                                                               field_name,
                                                                               ', '.join(predefined_wildcards))
                        self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                        raise ex

                    elif field_name in test_def_metadata_index:
                        test_def_metadata_index[field_name].append(_as_metadata_path(field_name_path))
                        self._logger.finest('1 field_name={0}, test_def_metadata_index[field_name]={1}',
                                            field_name, str(test_def_metadata_index[field_name]),
                                            class_name=_class_name, method_name=_method_name)
                    else:
                        test_def_metadata_index[field_name] = [_as_metadata_path(field_name_path)]
                        self._logger.finest('2 field_name={0}, test_def_metadata_index[field_name]={1}',
                                            field_name, str(test_def_metadata_index[field_name]),
                                            class_name=_class_name, method_name=_method_name)
                else:
                    field_name_path = [path_tokens[i] for i in range(len(path_tokens))]
                    test_def_metadata_index[field_name] = [_as_metadata_path(field_name_path)]

                    if '${' in field_name:
                        if [x for x in predefined_wildcards if field_name == x]:
                            new_path_tokens = field_name_path
                            new_path_tokens.append(field_name)
                        else:
                            ex = exception_helper.create_test_definition_exception('WLSDPLY-09833',
                                                                                   field_name,
                                                                                   ', '.join(predefined_wildcards))
                            self._logger.throwing(ex, class_name=_class_name, method_name=_method_name)
                            raise ex
                    else:
                        if test_def_metadata_index[field_name]:
                            new_path_tokens = field_name_path
                            new_path_tokens.append(field_name)
                        else:
                            new_path_tokens = [field_name]

                    test_def_metadata_dict = field_value
                    self.__populate_test_def_metadata_index(test_def_metadata_dict, new_path_tokens,
                                                            test_def_metadata_index)

        return test_def_metadata_index


def _load_test_def_metadata(test_def_metadata_file, logger, use_archive=True):
    if use_archive:
        metadata_file_path = '%s/%s' % (testing_constants.METADATA_DIR, test_def_metadata_file)
        metadata_file = testing_helper.extract_file(metadata_file_path, logger)
    else:
        metadata_file = test_def_metadata_file

    return testing_helper.translate_file(metadata_file, logger)


def _as_metadata_path(path_tokens):
    return '%s' % '/'.join(path_tokens)


def _get_path_tokens(metadata_path):
    """
    Returns a Python list containing path elements of metadata_path.

    :param metadata_path: String containing the name of a metadata 
                          field, or a forward-slash delimited path 
                          to a metadata field
    :return: A Python list containing path elements in metadata_path
    :raises VerificationException: if metadata_path is malformed
    """

    # Split metadata_path on '/'
    path_tokens = metadata_path.split('/')
    # Remove any blank list items caused by the user entering
    # extraneous '/' characters.
    while '' in path_tokens:
        del path_tokens[path_tokens.index('')]

    # Raise an exception if path_tokens is empty
    if not path_tokens:
        ex = exception_helper.create_verification_exception('WLSDPLY-09828', metadata_path)
        raise ex

    return path_tokens
