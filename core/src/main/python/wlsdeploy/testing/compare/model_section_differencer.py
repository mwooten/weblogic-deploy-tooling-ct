"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import PyOrderedDict

# python classes from weblogic-deploy-tooling
from wlsdeploy.util.enum import Enum

# java classes from weblogic-deploy-tooling-ct
from oracle.weblogic.deploy.testing import TestingConstants

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_helper, testing_constants
from wlsdeploy.testing.compare.model_file_types import ModelFileType
from wlsdeploy.testing.logging.platform_logger import PlatformLogger

_logger = PlatformLogger('wlsdeploy.testing', resource_bundle_name=TestingConstants.RESOURCE_BUNDLE_NAME)


class ModelSectionDifferencer(object):
    """
    """
    _class_name = 'ModelSectionDifferencer'
    ItemValueTypes = Enum(['EXPECTED', 'ACTUAL', 'DEFAULT'])

    def __init__(self, name, logger=None):
        self.name = name
        if logger is None:
            self._logger = _logger
        else:
            self._logger = logger

        self._excludes_dict = PyOrderedDict()

    ############################################
    #
    # Protected methods exposed to subclasses
    #
    ###########################################

    def _compare_sections(self, section_name, expected_section_dict, actual_section_dict, item_paths, comparison_result):
        _method_name = '__compare_sections'

        self._logger.info('WLSDPLY-09917', ModelFileType.EXPECTED, section_name,
                          class_name=self._class_name, method_name=_method_name)

        function_name = '_handle_expected_item_path'
        function = getattr(self, function_name)
        path_tokens, iterators_count = [], 0
        iterators = [expected_section_dict.iteritems()]

        while iterators:
            current_iterator = iterators.pop()
            for node_name, node_value in current_iterator:
                if not isinstance(node_value, dict):
                    item_path = '%s:/%s%s%s' % (section_name,
                                                '/'.join(path_tokens),
                                                (path_tokens and ['/'] or [''])[0],
                                                '@%s' % node_name)

                    self._logger.finer('item_path = {0}: [{1}, None, None]', item_path, node_value,
                                       class_name=self._class_name, method_name=_method_name)

                    function(item_path, node_value, item_paths)

                else:
                    self._logger.finer('node_name={0}', node_name,
                                       class_name=self._class_name, method_name=_method_name)

                    diff = cmp(iterators_count, len(iterators))
                    iterators_count = len(iterators)

                    self._logger.finer('iterators_count={0}', iterators_count,
                                       class_name=self._class_name, method_name=_method_name)

                    if diff == -1:
                        # increased
                        path_tokens.append(node_name)
                    elif diff == 1:
                        # deceased
                        path_tokens = path_tokens[0:iterators_count]+[node_name]
                    else:
                        # remained the same
                        if path_tokens:
                            path_tokens.pop()
                        path_tokens.append(node_name)

                    self._logger.finer('path_tokens={0}', str(path_tokens),
                                       class_name=self._class_name, method_name=_method_name)

                    iterators.append(current_iterator)
                    iterators.append(node_value.iteritems())

                    break

        self._logger.info('WLSDPLY-09917', ModelFileType.ACTUAL, section_name,
                          class_name=self._class_name, method_name=_method_name)

        function_name = '_handle_actual_item_path'
        function = getattr(self, function_name)
        path_tokens, iterators_count = [], 0
        iterators = [actual_section_dict.iteritems()]

        while iterators:
            current_iterator = iterators.pop()
            for node_name, node_value in current_iterator:
                if not isinstance(node_value, dict):
                    item_path = '%s:/%s%s%s' % (section_name,
                                                '/'.join(path_tokens),
                                                (path_tokens and ['/'] or [''])[0],
                                                '@%s' % node_name)

                    function(item_path, node_value, item_paths)

                else:
                    self._logger.finer('node_name={0}', node_name,
                                       class_name=self._class_name, method_name=_method_name)

                    diff = cmp(iterators_count, len(iterators))
                    iterators_count = len(iterators)

                    self._logger.finer('iterators_count={0}', iterators_count,
                                       class_name=self._class_name, method_name=_method_name)
                    if diff == -1:
                        # increased
                        path_tokens.append(node_name)
                    elif diff == 1:
                        # deceased
                        path_tokens = path_tokens[0:iterators_count]+[node_name]
                    else:
                        # remained the same
                        if path_tokens:
                            path_tokens.pop()
                        path_tokens.append(node_name)

                    self._logger.finer('path_tokens={0}', str(path_tokens),
                                       class_name=self._class_name, method_name=_method_name)

                    iterators.append(current_iterator)
                    iterators.append(node_value.iteritems())

                    break

        return comparison_result

    def _load_model_section_excludes(self, section_name):
        """
        Reads a JSON file containing information regarding which
        item paths should be excluded, when comparing a given
        model section.

        The JSON representation of the information looks like
        the following:

        ...
           "expected": {
              "domainInfo:/@AdminUserName": {
                 "node_name": "AdminUserName",
                 "reason": "This is a pseudo model section, so model generated by discover will not contain attributes from it"
              },
              "domainInfo:/@AdminPassword": {
                 "node_name": "AdminPassword",
                 "reason": "This is a pseudo model section, so model generated by discover will not contain attributes from it"
              },
          ...

        The lookup keys are the item path fields, which are siblings of the item value
        type node (e.g. "expected", "actual"). If the specified item path is present,
        then it will be excluded from the item paths for the model, of the item value
        type node it appears under. For example, if the "domainInfo:/@AdminUserName"
        item path is in the expected model, then "domainInfo:/@AdminUserName" will be
        excluded from the item paths collection. The item paths collection is used during
        the compare and match process.

        :param section_name: The name of the model section that the excludes
                             applies to
        :return: A Python dictionary contain excludes information
        :raises TestingException, if file cannot be translated into a python dictionary
        """
        _method_name = '_load_model_section_excludes'

        file_path = '%s/%s-excludes.json' % (testing_constants.EXCLUDES_DIR, section_name)
        j_file = testing_helper.extract_file(file_path, self._logger)
        self._logger.finer('WLSDPLY-09912', j_file.getAbsolutePath(), section_name,
                     class_name=self._class_name, method_name=_method_name)
        excludes_dict = testing_helper.translate_file(j_file, self._logger)

        return excludes_dict

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

