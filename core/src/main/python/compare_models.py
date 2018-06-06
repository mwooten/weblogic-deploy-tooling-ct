"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0

The entry point for WDT Tester component that compares domain models
"""
import os
import sys

from java.lang import IllegalArgumentException
from oracle.weblogic.deploy.util import FileUtils
from oracle.weblogic.deploy.testing import VerificationException
from oracle.weblogic.deploy.util import TranslateException
from oracle.weblogic.deploy.util import WebLogicDeployToolingVersion

# java classes from weblogic-deploy-tooling-ct
from oracle.weblogic.deploy.testing import CompareModelsException
from oracle.weblogic.deploy.testing import TestingConstants

sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))

# python classes from weblogic-deploy-tooling
from wlsdeploy.util import wlst_helper
from wlsdeploy.util.model_context import ModelContext
from wlsdeploy.util.weblogic_helper import WebLogicHelper
from wlsdeploy.util.cla_utils import CommandLineArgUtil
from wlsdeploy.util.model_translator import FileToPython

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.exception import exception_helper
from wlsdeploy.testing.logging.platform_logger import PlatformLogger
from wlsdeploy.testing.compare.model_comparer import ModelComparer
from wlsdeploy.testing.common import testing_common

_program_name = 'compareModels'
_class_name = 'compare_models'
__logger = PlatformLogger('wlsdeploy.compare_models', resource_bundle_name=TestingConstants.RESOURCE_BUNDLE_NAME)
__wls_helper = WebLogicHelper(__logger)

_EXPECTED_MODEL_FILE_SWITCH = '-expected_model_file'
_ACTUAL_MODEL_FILE_SWITCH = '-actual_model_file'
_EXPECTED_MODEL_OVERRIDES_FILE_SWITCH = '-expected_model_overrides_file'
_ACTUAL_MODEL_OVERRIDES_FILE_SWITCH = '-actual_model_overrides_file'
_COMPARE_RESULT_FILE_SWITCH = '-compare_results_file'

__required_arguments = [
    CommandLineArgUtil.ORACLE_HOME_SWITCH,
]

__optional_arguments = [
    CommandLineArgUtil.JAVA_HOME_SWITCH,
]


def __process_args(args):
    """
    Process the command-line arguments and prompt the user for any missing information

    :param (list) args:
        the command-line arguments list
    :raises CLAException:
        if an error occurs while validating and processing the command-line arguments
    """
    cla_util = CommandLineArgUtil(_program_name, __required_arguments, __optional_arguments)
    required_arg_map, optional_arg_map = cla_util.process_args(args)

    __verify_required_args_present(required_arg_map)
    __process_java_home_arg(optional_arg_map)

    combined_arg_map = optional_arg_map.copy()
    combined_arg_map.update(required_arg_map)

    return ModelContext(_program_name, combined_arg_map)


def __verify_required_args_present(required_arg_map):
    """
    Verify that the required args are present.

    :param (dict) required_arg_map:
        the required arguments map
    :raises CLAException: if one or more of the required arguments are missing
    """
    _method_name = '__verify_required_args_present'

    for req_arg in __required_arguments:
        if req_arg not in required_arg_map:
            ex = exception_helper.create_verification_exception('WLSDPLY-20005', _program_name, req_arg)
            ex.setExitCode(CommandLineArgUtil.USAGE_ERROR_EXIT_CODE)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex
    return


def __process_java_home_arg(optional_arg_map):
    """
    Verify that java_home is set.  If not, set it.
    :param optional_arg_map: the optional arguments map
    :raises CLAException: if the java home argument is not valid
    """
    _method_name = '__process_java_home_arg'

    if CommandLineArgUtil.JAVA_HOME_SWITCH not in optional_arg_map:
        java_home_name = os.environ.get('JAVA_HOME')
        try:
            java_home = FileUtils.validateExistingDirectory(java_home_name)
        except IllegalArgumentException, iae:
            ex = exception_helper.create_verification_exception('WLSDPLY-12400', _program_name, java_home_name,
                                                                iae.getLocalizedMessage(), error=iae)
            ex.setExitCode(CommandLineArgUtil.ARG_VALIDATION_ERROR_EXIT_CODE)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex
        optional_arg_map[CommandLineArgUtil.JAVA_HOME_SWITCH] = java_home.getAbsolutePath()
    return


def __verify_expected_model_file_arg(compare_models_args_map):
    """

    :param compare_models_args_map:
    :return:
    """
    _method_name = '__verify_expected_model_file_arg'

    expected_model_file_name = None

    if _EXPECTED_MODEL_FILE_SWITCH in compare_models_args_map:
        try:
            expected_model_file_name = compare_models_args_map[_EXPECTED_MODEL_FILE_SWITCH]
            compare_models_args_map[_EXPECTED_MODEL_FILE_SWITCH] = \
                FileUtils.validateExistingFile(expected_model_file_name)
        except IllegalArgumentException, iae:
            ex = exception_helper.create_verification_exception('WLSDPLY-20014',
                                                                _EXPECTED_MODEL_FILE_SWITCH,
                                                                iae.getLocalizedMessage(), error=iae)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

    if expected_model_file_name is None:
        ex = exception_helper.create_verification_exception('WLSDPLY-20005',
                                                            _program_name,
                                                            _EXPECTED_MODEL_FILE_SWITCH)
        ex.setExitCode(CommandLineArgUtil.ARG_VALIDATION_ERROR_EXIT_CODE)
        __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    return


def __verify_actual_model_file_arg(compare_models_args_map):
    """

    :param compare_models_args_map:
    :return:
    """
    _method_name = '__verify_actual_model_file_arg'

    actual_model_file_name = None

    if _ACTUAL_MODEL_FILE_SWITCH in compare_models_args_map:
        try:
            actual_model_file_name = compare_models_args_map[_ACTUAL_MODEL_FILE_SWITCH]
            compare_models_args_map[_ACTUAL_MODEL_FILE_SWITCH] = \
                FileUtils.validateExistingFile(actual_model_file_name)
        except IllegalArgumentException, iae:
            ex = exception_helper.create_verification_exception('WLSDPLY-20014',
                                                                _ACTUAL_MODEL_FILE_SWITCH,
                                                                iae.getLocalizedMessage(), error=iae)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

    if actual_model_file_name is None:
        ex = exception_helper.create_verification_exception('WLSDPLY-20005',
                                                            _program_name,
                                                            _ACTUAL_MODEL_FILE_SWITCH)
        ex.setExitCode(CommandLineArgUtil.ARG_VALIDATION_ERROR_EXIT_CODE)
        __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    return


def __verify_expected_model_overrides_file_arg(compare_models_args_map):
    """

    :param compare_models_args_map:
    :return:
    """
    _method_name = '__verify_expected_models_overrides_file_arg'

    expected_models_overrides_file = None

    if compare_models_args_map[_EXPECTED_MODEL_OVERRIDES_FILE_SWITCH] is not None:
        try:
            expected_model_overrides_file = compare_models_args_map[_EXPECTED_MODEL_OVERRIDES_FILE_SWITCH]
            compare_models_args_map[_EXPECTED_MODEL_OVERRIDES_FILE_SWITCH] = \
                FileUtils.validateExistingFile(expected_model_overrides_file)
        except IllegalArgumentException, iae:
            ex = exception_helper.create_verification_exception('WLSDPLY-20014',
                                                                _EXPECTED_MODEL_OVERRIDES_FILE_SWITCH,
                                                                iae.getLocalizedMessage(), error=iae)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

    return


def __verify_actual_model_overrides_file_arg(compare_models_args_map):
    """

    :param compare_models_args_map:
    :return:
    """
    _method_name = '__verify_actual_models_overrides_file_arg'

    actual_models_overrides_file = None

    if compare_models_args_map[_ACTUAL_MODEL_OVERRIDES_FILE_SWITCH] is not None:
        try:
            actual_model_overrides_file = compare_models_args_map[_ACTUAL_MODEL_OVERRIDES_FILE_SWITCH]
            compare_models_args_map[_ACTUAL_MODEL_OVERRIDES_FILE_SWITCH] = \
                FileUtils.validateExistingFile(actual_model_overrides_file)
        except IllegalArgumentException, iae:
            ex = exception_helper.create_verification_exception('WLSDPLY-20014',
                                                                _ACTUAL_MODEL_OVERRIDES_FILE_SWITCH,
                                                                iae.getLocalizedMessage(), error=iae)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

    return


def __process_compare_models_args(compare_models_args_map):
    __verify_expected_model_file_arg(compare_models_args_map)
    __verify_actual_model_file_arg(compare_models_args_map)
    __verify_expected_model_overrides_file_arg(compare_models_args_map)
    __verify_actual_model_overrides_file_arg(compare_models_args_map)

    return


def __compare_models(compare_models_args_map):
    """

    :param compare_models_args_map:
    :return:
    :raises CompareModelsException:
    :raises VerificationException:
    """
    _method_name = '__compare_models'

    expected_model_file = None

    try:
        expected_model_file = compare_models_args_map[_EXPECTED_MODEL_FILE_SWITCH]
        expected_model_dict = FileToPython(expected_model_file.getAbsolutePath(), True).parse()
    except TranslateException, te:
        __logger.severe('WLSDPLY-20009', _program_name, expected_model_file.getAbsolutePath(), te.getLocalizedMessage(),
                        error=te, class_name=_class_name, method_name=_method_name)
        ex = exception_helper.create_verification_exception(te.getLocalizedMessage(), error=te)
        __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    actual_model_file = None

    try:
        actual_model_file = compare_models_args_map[_ACTUAL_MODEL_FILE_SWITCH]
        actual_model_dict = FileToPython(actual_model_file.getAbsolutePath(), True).parse()
    except TranslateException, te:
        __logger.severe('WLSDPLY-20009', _program_name, actual_model_file.getAbsolutePath(), te.getLocalizedMessage(),
                        error=te, class_name=_class_name, method_name=_method_name)
        ex = exception_helper.create_verification_exception(te.getLocalizedMessage(), error=te)
        __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    expected_model_overrides_file = compare_models_args_map[_EXPECTED_MODEL_OVERRIDES_FILE_SWITCH]

    if expected_model_overrides_file is not None:
        __logger.info('WLSDPLY-09924', expected_model_overrides_file, "expected",
                      class_name=_class_name, method_name=_method_name)
        testing_common.apply_substitution_variables_file(expected_model_overrides_file, expected_model_dict, __logger)

    actual_model_overrides_file = compare_models_args_map[_ACTUAL_MODEL_OVERRIDES_FILE_SWITCH]

    if actual_model_overrides_file is not None:
        __logger.info('WLSDPLY-09924', actual_model_overrides_file, "actual",
                      class_name=_class_name, method_name=_method_name)
        testing_common.apply_substitution_variables_file(actual_model_overrides_file, actual_model_dict, __logger)

    if expected_model_dict is not None and actual_model_dict is not None:
        model_comparer = ModelComparer(logger=__logger)

        comparison_results = model_comparer.compare_models(expected_model_dict,
                                                           actual_model_dict)
        comparison_results.log_results(__logger)

        compare_results_file = compare_models_args_map[_COMPARE_RESULT_FILE_SWITCH]

        if compare_results_file is not None:
            model_comparer.write_compare_results(compare_results_file)

    return


def main(args):
    """
    The entry point for run test program

    :param args:
    :return:
    """
    _method_name = 'main'

    wlst_helper.silence()

    __logger.entering(args[0], class_name=_class_name, method_name=_method_name)

    for index, arg in enumerate(args):
        __logger.finer('sys.argv[{0}] = {1}', str(index), arg, class_name=_class_name, method_name=_method_name)

    compare_models_args_map = {
        _EXPECTED_MODEL_FILE_SWITCH: None,
        _ACTUAL_MODEL_FILE_SWITCH: None,
        _EXPECTED_MODEL_OVERRIDES_FILE_SWITCH: None,
        _ACTUAL_MODEL_OVERRIDES_FILE_SWITCH: None,
        _COMPARE_RESULT_FILE_SWITCH: None
    }

    if _EXPECTED_MODEL_FILE_SWITCH in args:
        index = sys.argv.index(_EXPECTED_MODEL_FILE_SWITCH)
        value = sys.argv[index+1]
        compare_models_args_map[_EXPECTED_MODEL_FILE_SWITCH] = value
        sys.argv.remove(_EXPECTED_MODEL_FILE_SWITCH)
        sys.argv.remove(value)

    if _ACTUAL_MODEL_FILE_SWITCH in args:
        index = sys.argv.index(_ACTUAL_MODEL_FILE_SWITCH)
        value = sys.argv[index+1]
        compare_models_args_map[_ACTUAL_MODEL_FILE_SWITCH] = value
        sys.argv.remove(_ACTUAL_MODEL_FILE_SWITCH)
        sys.argv.remove(value)

    if _EXPECTED_MODEL_OVERRIDES_FILE_SWITCH in args:
        index = sys.argv.index(_EXPECTED_MODEL_OVERRIDES_FILE_SWITCH)
        value = sys.argv[index+1]
        compare_models_args_map[_EXPECTED_MODEL_OVERRIDES_FILE_SWITCH] = value
        sys.argv.remove(_EXPECTED_MODEL_OVERRIDES_FILE_SWITCH)
        sys.argv.remove(value)

    if _ACTUAL_MODEL_OVERRIDES_FILE_SWITCH in args:
        index = sys.argv.index(_ACTUAL_MODEL_OVERRIDES_FILE_SWITCH)
        value = sys.argv[index+1]
        compare_models_args_map[_ACTUAL_MODEL_OVERRIDES_FILE_SWITCH] = value
        sys.argv.remove(_ACTUAL_MODEL_OVERRIDES_FILE_SWITCH)
        sys.argv.remove(value)

    if _COMPARE_RESULT_FILE_SWITCH in args:
        index = sys.argv.index(_COMPARE_RESULT_FILE_SWITCH)
        value = sys.argv[index+1]
        compare_models_args_map[_COMPARE_RESULT_FILE_SWITCH] = value
        sys.argv.remove(_COMPARE_RESULT_FILE_SWITCH)
        sys.argv.remove(value)

    try:
        __process_args(args)
        __process_compare_models_args(compare_models_args_map)
    except VerificationException, ve:
        exit_code = ve.getExitCode()
        if exit_code != CommandLineArgUtil.HELP_EXIT_CODE:
            __logger.severe('WLSDPLY-20008', _program_name, ve.getLocalizedMessage(), error=ve,
                            class_name=_class_name, method_name=_method_name)
        sys.exit(exit_code)

    try:
        __compare_models(compare_models_args_map)

    except (CompareModelsException, VerificationException), e:
        __logger.severe('WLSDPLY-09812', _program_name,
                        e.getClass().getSimpleName(),
                        e.getLocalizedMessage(), error=e,
                        class_name=_class_name, method_name=_method_name)
        sys.exit(CommandLineArgUtil.PROG_ERROR_EXIT_CODE)

    return

if __name__ == "main":
    WebLogicDeployToolingVersion.logVersionInfo(_program_name)
    main(sys.argv)
