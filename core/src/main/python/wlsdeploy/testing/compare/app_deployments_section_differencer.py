"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

import re

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common.model_constants import APP_DEPLOYMENTS
from wlsdeploy.testing.compare.model_file_types import ModelFileType
from wlsdeploy.testing.compare.model_section_differencer import ModelSectionDifferencer

_DEPLOYABLE_LIBRARY_PATTERN = re.compile(r'appDeployments:/Library/([a-z-]+)(#[0-9.]+)(@[0-9._-]+)(/.+)')


class AppDeploymentsSectionDifferencer(ModelSectionDifferencer):
    """
    Class for comparing the appDeployments section in two model files

    """
    _class_name = 'AppDeploymentsSectionDifferencer'

    def __init__(self, logger=None):
        self._logger = logger
        ModelSectionDifferencer.__init__(self, self._class_name, self._logger)
        self._excludes_dict = None

    def compare_sections(self, expected_section_folder_dict, actual_section_folder_dict, item_paths, comparison_result):
        _method_name = 'compare_sections'

        self._logger.info('WLSDPLY-09916', APP_DEPLOYMENTS, ModelFileType.EXPECTED, ModelFileType.ACTUAL,
                          class_name=self._class_name, method_name=_method_name)

        self._excludes_dict = ModelSectionDifferencer._load_model_section_excludes(self, APP_DEPLOYMENTS)

        ModelSectionDifferencer._compare_sections(self, APP_DEPLOYMENTS, expected_section_folder_dict,
                                                  actual_section_folder_dict, item_paths, comparison_result)

    def _handle_expected_item_path(self, item_path, node_value, item_paths):
        _method_name = '_handle_expected_item_path'

        exclude_flag = False

        expected_excludes_dict = self._excludes_dict.get(ModelFileType.EXPECTED)

        for regex_pattern in expected_excludes_dict.keys():
            if re.match(regex_pattern, item_path):
                self._logger.finest('1 regex_pattern={0}', regex_pattern,
                                    class_name=self._class_name, method_name=_method_name)
                exclude_flag = True
                break

        if exclude_flag:
            item_paths[item_path] = [node_value, None, node_value]
        else:
            item_paths[item_path] = [node_value, None, None]

        return

    def _handle_actual_item_path(self, item_path, node_value, item_paths):
        _method_name = '_handle_actual_item_path'

        item_value = []

        if item_path in item_paths:
            # item_path is in actual and expected models. Whether
            # or not they have matching values, will be determined
            # in the __match_item_path_values() method
            item_value = item_paths.get(item_path)
            item_value[ModelSectionDifferencer.ItemValueTypes.ACTUAL] = node_value
            item_value[ModelSectionDifferencer.ItemValueTypes.DEFAULT] = None
        else:
            # Deployable libraries use versioning scheme, so use a regex pattern
            # to try to match item_path that way
            m = _DEPLOYABLE_LIBRARY_PATTERN.match(item_path)
            if m:
                #
                # Found a match, so create a list of all the relevant possible item
                # paths, which might match an existing item_path in item_paths
                #
                #   m.group(1) is the library name (e.g. jax-rs)
                #   m.group(2) is the major version (e.g. #2.0)
                #   m.group(3) is the minor version (e.g. @2.22.4.0)
                #   m.group(4) is the attribute name (e.g. /@ModuleType)
                #
                possible_item_paths = [
                    '%s%s%s' % ('appDeployments:/Library/', m.group(1), m.group(4)),
                    '%s%s%s%s' % ('appDeployments:/Library/', m.group(1), m.group(2), m.group(4)),
                    '%s%s%s%s%s' % ('appDeployments:/Library/', m.group(1), m.group(2), m.group(3), m.group(4)),
                ]
                for possible_item_path in possible_item_paths:
                    if possible_item_path in item_paths:
                        # Found an existing item_path in item_paths, which matches
                        # the current possible_item_path value
                        item_path = possible_item_path
                        self._logger.finest('possible_item_path={0}', item_path,
                                            class_name=self._class_name, method_name=_method_name)
                        # Get item_value for item_path
                        item_value = item_paths.get(item_path)
                        # Update the ModelSectionDifferencer.ItemValueTypes.ACTUAL
                        # list index with value assigned to node_value
                        item_value[ModelSectionDifferencer.ItemValueTypes.ACTUAL] = node_value
                        # Set ModelSectionDifferencer.ItemValueTypes.DEFAULT list
                        # index to None, to signal that we aren't using a default value
                        item_value[ModelSectionDifferencer.ItemValueTypes.DEFAULT] = None
            else:
                # item_path is only in the actual model. This is the case
                # when it is for a WLST attribute with a default value, or
                # WLST generates automagically. Either way, use the value
                # from the actual model, as the value for both actual and
                # default in the item paths collections.
                exclude_flag = False

                actual_excludes_dict = self._excludes_dict.get(ModelFileType.ACTUAL)

                for regex_pattern in actual_excludes_dict.keys():
                    if re.match(regex_pattern, item_path):
                        self._logger.finest('2 regex_pattern={0}', regex_pattern,
                                            class_name=self._class_name, method_name=_method_name)
                        exclude_flag = True
                        break

                if exclude_flag:
                    item_value = [None, node_value, node_value]
                else:
                    item_value = [None, node_value, None]

        item_paths[item_path] = item_value

        self._logger.finer('item_path={0}: [{1}, {2}, {3}]',
                           item_path,
                           item_value[ModelSectionDifferencer.ItemValueTypes.EXPECTED],
                           item_value[ModelSectionDifferencer.ItemValueTypes.ACTUAL],
                           item_value[ModelSectionDifferencer.ItemValueTypes.DEFAULT],
                           class_name=self._class_name, method_name=_method_name)

        return
