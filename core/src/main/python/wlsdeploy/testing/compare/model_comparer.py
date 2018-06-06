"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import PyOrderedDict

# java classes from weblogic-deploy-tooling-ct
from oracle.weblogic.deploy.testing import TestingConstants

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.logging.platform_logger import PlatformLogger
from wlsdeploy.testing.common.model_constants import APP_DEPLOYMENTS
from wlsdeploy.testing.common.model_constants import DOMAIN_INFO
from wlsdeploy.testing.common.model_constants import RESOURCES
from wlsdeploy.testing.common.model_constants import TOPOLOGY
from wlsdeploy.testing.compare.model_file_types import ModelFileType
from wlsdeploy.testing.compare.comparer_results import ComparerResults, ComparerResult
from wlsdeploy.testing.compare.model_section_differencer import ModelSectionDifferencer
from wlsdeploy.testing.compare.domain_info_section_differencer import DomainInfoSectionDifferencer
from wlsdeploy.testing.compare.topology_section_differencer import TopologySectionDifferencer
from wlsdeploy.testing.compare.resources_section_differencer import ResourcesSectionDifferencer
from wlsdeploy.testing.compare.app_deployments_section_differencer import AppDeploymentsSectionDifferencer

_class_name = 'ModelComparer'


class ModelComparer(object):
    """
    Class for comparing values in two model dictionaries
    """

    def __init__(self, logger=None):
        if logger is None:
            self._logger = \
                PlatformLogger('wlsdeploy.compare_models', resource_bundle_name=TestingConstants.RESOURCE_BUNDLE_NAME)
        else:
            self._logger = logger

        self._comparator_results = ComparerResults()

    def compare_models(self, expected_model_dict, actual_model_dict):
        """
        Compares the values in two domain model file.

        This is a two-way comparison that includes:

            1. Determining if actual_model_dict contains all the model folders
               and attributes found in expected_model_dict. (ONLY_IN_EXPECTED)

            2. Determining it expected_model_dict contains all the model folders
               and attributes found in actual_model_dict. (ONLY_IN_ACTUAL)

            3. Comparing the values of folder, folder instance or attribute names,
               when a folder, folder instance or attribute name appears in both
               expected_model_dict and actual_model_dict. (IN_BOTH)
               when they have matching .

        NOTE:  Normally, we'd use the aliases API and .json files in the
               oracle/weblogic-deploy-tooling project to help out here. But
               doing that is a form of "using the thing being tested, to
               test the thing being", which is of course,  not a reliable test.

        A "differencer" class/object is used to store the differences, and a "results"
        class/object is used to store the results of the comparison, when the "IN_BOTH"
        occurs.

        :param expected_model_dict: The model dict for the "expected" side of the comparison
        :param actual_model_dict: The model dict for the "actual" side of the comparison
        :return: A ComparerResults object containing a set of ComparerResult objects
        :raises TestingException: if an unrecoverable exception occurs during the comparison
        """
        _method_name = 'compare_models'

        item_paths = PyOrderedDict()

        domain_info_differencer = DomainInfoSectionDifferencer(self._logger)
        comparison_result = self.__compare_model_sections(DOMAIN_INFO, expected_model_dict, actual_model_dict,
                                                          item_paths, domain_info_differencer)
        self._comparator_results.set_comparison_result(comparison_result)

        topology_differencer = TopologySectionDifferencer(self._logger)
        comparison_result = self.__compare_model_sections(TOPOLOGY, expected_model_dict, actual_model_dict,
                                                          item_paths, topology_differencer)
        self._comparator_results.set_comparison_result(comparison_result)

        resources_differencer = ResourcesSectionDifferencer(self._logger)
        comparison_result = self.__compare_model_sections(RESOURCES, expected_model_dict, actual_model_dict,
                                                          item_paths, resources_differencer)
        self._comparator_results.set_comparison_result(comparison_result)

        app_deployments_differencer = AppDeploymentsSectionDifferencer(self._logger)
        comparison_result = self.__compare_model_sections(APP_DEPLOYMENTS, expected_model_dict, actual_model_dict,
                                                          item_paths, app_deployments_differencer)
        self._comparator_results.set_comparison_result(comparison_result)

        self._logger.finer('item_paths={0}', str(item_paths),
                           class_name=_class_name, method_name=_method_name)

        _match_item_path_values(item_paths, comparison_result)

        return self._comparator_results

    def write_compare_results(self, file_path):
        """

        :param file_path:
        :return:
        """
        self._comparator_results.write_to_file(file_path)

    ####################################################################################
    #
    # Private methods, private inner classes and static methods only, beyond here please
    #
    ####################################################################################

    def __compare_model_sections(self, section_name, expected_model_section_dict, actual_model_section_dict,
                                 item_paths, differencer):
        """

        :param section_name:
        :param expected_model_section_dict:
        :param actual_model_section_dict:
        :param item_paths:
        :param differencer:
        :return:
        """
        _method_name = '__compare_model_sections'

        self._logger.entering(section_name, class_name=_class_name, method_name=_method_name)

        comparison_result = ComparerResult(section_name)

        if section_name in expected_model_section_dict:
            if section_name not in actual_model_section_dict:
                comparison_result.add_warning('WLSDPLY-09911', ModelFileType.EXPECTED,
                                              section_name, ModelFileType.ACTUAL)
            else:
                differencer.compare_sections(expected_model_section_dict[section_name],
                                             actual_model_section_dict[section_name], item_paths, comparison_result)

        self._logger.exiting(class_name=_class_name, method_name=_method_name)

        return comparison_result


def _match_item_path_values(item_paths, comparison_result):
    """

    :param item_paths:
    :param comparison_result:
    :return:
    """
    for item_path, item_value in item_paths.iteritems():
        if item_value[ModelSectionDifferencer.ItemValueTypes.ACTUAL] is None:
            if item_value[ModelSectionDifferencer.ItemValueTypes.DEFAULT] is None:
                # item_path is only in expected, so report this as an
                # ERROR severity level comparison result
                comparison_result.add_error('WLSDPLY-09915', ModelFileType.EXPECTED,
                                            item_path, ModelFileType.ACTUAL)
            else:
                comparison_result.add_warning('WLSDPLY-09915', ModelFileType.EXPECTED,
                                              item_path, ModelFileType.ACTUAL)

        elif item_value[ModelSectionDifferencer.ItemValueTypes.EXPECTED] is None:
            if item_value[ModelSectionDifferencer.ItemValueTypes.DEFAULT] is None:
                # item_path is only in actual, so report this as a
                # WARNING severity level comparison result
                comparison_result.add_warning('WLSDPLY-09915', ModelFileType.ACTUAL,
                                              item_path, ModelFileType.EXPECTED)
            else:
                comparison_result.add_warning('WLSDPLY-09915', ModelFileType.ACTUAL,
                                              item_path, ModelFileType.EXPECTED)

    return
