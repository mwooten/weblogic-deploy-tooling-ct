"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0

The WLS Deploy Tooling CT entry point for performing WDTCT tests.
"""
import os
import sys

from java.lang import IllegalArgumentException

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import FileUtils
from oracle.weblogic.deploy.util import WebLogicDeployToolingVersion

# java classes from weblogic-deploy-tooling-ct
from oracle.weblogic.deploy.testing import TestingConstants
from oracle.weblogic.deploy.testing import TestingException
from oracle.weblogic.deploy.testing import TestDefinitionException
from oracle.weblogic.deploy.testing import IntegrationTestException
from oracle.weblogic.deploy.testing import VerificationException
from oracle.weblogic.deploy.testing import SystemTestException

sys.path.append(os.path.dirname(os.path.realpath(sys.argv[0])))

# python classes from weblogic-deploy-tooling
from wlsdeploy.util import wlst_helper
from wlsdeploy.util.model_context import ModelContext
from wlsdeploy.util.weblogic_helper import WebLogicHelper
from wlsdeploy.util.cla_utils import CommandLineArgUtil

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.exception import exception_helper
from wlsdeploy.testing.logging.platform_logger import PlatformLogger
from wlsdeploy.testing.test_runner import TestRunner

_program_name = 'runTest'
_class_name = 'run_test'
__logger = PlatformLogger('wlsdeploy.testing', resource_bundle_name=TestingConstants.RESOURCE_BUNDLE_NAME)
__wls_helper = WebLogicHelper(__logger)

_TEST_TYPE_SWITCH = '-test_type'
_TEST_DEF_FILE_SWITCH = '-test_def_file'
_TEST_DEF_OVERRIDES_FILE_SWITCH = '-test_def_overrides_file'
_TEST_DEF_VERIFIER_NAME_SWITCH = '-test_def_verifier_name'
_TEST_DEF_METADATA_FILE_SWITCH = '-test_def_metadata_file'
_VERIFY_ONLY_SWITCH = '-verify_only'

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


def __verify_test_def_file_arg(run_test_args_map):
    """

    :param run_test_args_map:
    :return:
    """
    _method_name = '__verify_test_def_file_arg'

    test_def_file_name = None

    if _TEST_DEF_FILE_SWITCH in run_test_args_map:
        try:
            test_def_file_name = run_test_args_map[_TEST_DEF_FILE_SWITCH]
            run_test_args_map[_TEST_DEF_FILE_SWITCH] = \
                FileUtils.validateExistingFile(test_def_file_name)
        except IllegalArgumentException, iae:
            ex = exception_helper.create_verification_exception('WLSDPLY-20014',
                                                                _TEST_DEF_FILE_SWITCH,
                                                                iae.getLocalizedMessage(), error=iae)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

    if test_def_file_name is None:
        ex = exception_helper.create_verification_exception('WLSDPLY-20005',
                                                            _program_name,
                                                            _TEST_DEF_FILE_SWITCH)
        ex.setExitCode(CommandLineArgUtil.ARG_VALIDATION_ERROR_EXIT_CODE)
        __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    return


def __verify_test_def_overrides_file_arg(run_test_args_map):
    """

    :param run_test_args_map:
    :return:
    """
    _method_name = '__verify_test_def_overrides_file_arg'

    test_def_overrides_file = None

    if run_test_args_map[_TEST_DEF_OVERRIDES_FILE_SWITCH] is not None:
        try:
            test_def_overrides_file = run_test_args_map[_TEST_DEF_OVERRIDES_FILE_SWITCH]
            run_test_args_map[_TEST_DEF_OVERRIDES_FILE_SWITCH] = \
                FileUtils.validateExistingFile(test_def_overrides_file)
        except IllegalArgumentException, iae:
            ex = exception_helper.create_verification_exception('WLSDPLY-20014',
                                                                _TEST_DEF_OVERRIDES_FILE_SWITCH,
                                                                iae.getLocalizedMessage(), error=iae)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

    return


def __verify_test_def_metadata_file_arg(run_test_args_map):
    """

    :param run_test_args_map:
    :return:
    """
    _method_name = '__verify_test_def_metadata_file_arg'

    test_def_metadata_file = None

    if run_test_args_map[_TEST_DEF_METADATA_FILE_SWITCH] is not None:
        try:
            test_def_metadata_file = run_test_args_map[_TEST_DEF_METADATA_FILE_SWITCH]
            run_test_args_map[_TEST_DEF_METADATA_FILE_SWITCH] = \
                FileUtils.validateExistingFile(test_def_metadata_file)
        except IllegalArgumentException, iae:
            ex = exception_helper.create_verification_exception('WLSDPLY-20014',
                                                                _TEST_DEF_METADATA_FILE_SWITCH,
                                                                iae.getLocalizedMessage(), error=iae)
            __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
            raise ex

    return


def __process_run_test_args(run_test_args_map):
    _method_name = '__process_run_test_args'

    test_type = None

    if _TEST_TYPE_SWITCH in run_test_args_map:
        test_type = run_test_args_map[_TEST_TYPE_SWITCH]
        run_test_args_map[_TEST_TYPE_SWITCH] = test_type

    if test_type is None:
        ex = exception_helper.create_verification_exception('WLSDPLY-20005',
                                                            _program_name,
                                                            _TEST_TYPE_SWITCH)
        ex.setExitCode(CommandLineArgUtil.ARG_VALIDATION_ERROR_EXIT_CODE)
        __logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    __verify_test_def_file_arg(run_test_args_map)
    __verify_test_def_overrides_file_arg(run_test_args_map)
    __verify_test_def_metadata_file_arg(run_test_args_map)

    if _VERIFY_ONLY_SWITCH not in run_test_args_map:
        run_test_args_map[_VERIFY_ONLY_SWITCH] = False

    return


def __run_test(run_test_args_map):
    """

    :param run_test_args_map:
    :return:
    :raises TestingException:
    :raises TestDefinitionException:
    :raises IntegrationTestException:
    :raises SystemTestException:
    :raises VerificationException:
    """

    test_type = run_test_args_map[_TEST_TYPE_SWITCH]
    test_def_file = run_test_args_map[_TEST_DEF_FILE_SWITCH]
    test_def_overrides_file = run_test_args_map[_TEST_DEF_OVERRIDES_FILE_SWITCH]
    test_def_verifier_name = run_test_args_map[_TEST_DEF_VERIFIER_NAME_SWITCH]
    test_def_metadata_file = run_test_args_map[_TEST_DEF_METADATA_FILE_SWITCH]
    verify_only = run_test_args_map[_VERIFY_ONLY_SWITCH]
    test_runner = TestRunner(logger=__logger)
    test_runner.run_test(test_type, test_def_file, test_def_overrides_file,
                         test_def_verifier_name, test_def_metadata_file, verify_only)
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

    run_test_args_map = {
        _TEST_DEF_OVERRIDES_FILE_SWITCH: None,
        _TEST_DEF_VERIFIER_NAME_SWITCH: None,
        _TEST_DEF_METADATA_FILE_SWITCH: None
    }

    if _TEST_TYPE_SWITCH in args:
        index = sys.argv.index(_TEST_TYPE_SWITCH)
        value = sys.argv[index+1]
        run_test_args_map[_TEST_TYPE_SWITCH] = value
        sys.argv.remove(_TEST_TYPE_SWITCH)
        sys.argv.remove(value)

    if _TEST_DEF_FILE_SWITCH in args:
        index = sys.argv.index(_TEST_DEF_FILE_SWITCH)
        value = sys.argv[index+1]
        run_test_args_map[_TEST_DEF_FILE_SWITCH] = value
        sys.argv.remove(_TEST_DEF_FILE_SWITCH)
        sys.argv.remove(value)

    if _TEST_DEF_OVERRIDES_FILE_SWITCH in args:
        index = sys.argv.index(_TEST_DEF_OVERRIDES_FILE_SWITCH)
        value = sys.argv[index+1]
        run_test_args_map[_TEST_DEF_OVERRIDES_FILE_SWITCH] = value
        sys.argv.remove(_TEST_DEF_OVERRIDES_FILE_SWITCH)
        sys.argv.remove(value)

    if _TEST_DEF_VERIFIER_NAME_SWITCH in args:
        index = sys.argv.index(_TEST_DEF_VERIFIER_NAME_SWITCH)
        value = sys.argv[index+1]
        run_test_args_map[_TEST_DEF_VERIFIER_NAME_SWITCH] = value
        sys.argv.remove(_TEST_DEF_VERIFIER_NAME_SWITCH)
        sys.argv.remove(value)

    if _TEST_DEF_METADATA_FILE_SWITCH in args:
        index = sys.argv.index(_TEST_DEF_METADATA_FILE_SWITCH)
        value = sys.argv[index+1]
        run_test_args_map[_TEST_DEF_METADATA_FILE_SWITCH] = value
        sys.argv.remove(_TEST_DEF_METADATA_FILE_SWITCH)
        sys.argv.remove(value)

    if _VERIFY_ONLY_SWITCH in args:
        value = True
        run_test_args_map[_VERIFY_ONLY_SWITCH] = value
        sys.argv.remove(_VERIFY_ONLY_SWITCH)

    try:
        __process_args(args)
        __process_run_test_args(run_test_args_map)
    except VerificationException, ve:
        exit_code = ve.getExitCode()
        if exit_code != CommandLineArgUtil.HELP_EXIT_CODE:
            __logger.severe('WLSDPLY-20008', _program_name, ve.getLocalizedMessage(), error=ve,
                            class_name=_class_name, method_name=_method_name)
        sys.exit(exit_code)

    try:
        __run_test(run_test_args_map)

    except (TestingException, TestDefinitionException, VerificationException,
            IntegrationTestException, SystemTestException), e:
        __logger.severe('WLSDPLY-09812', _program_name,
                        e.getClass().getSimpleName(),
                        e.getLocalizedMessage(), error=e,
                        class_name=_class_name, method_name=_method_name)
        sys.exit(CommandLineArgUtil.PROG_ERROR_EXIT_CODE)

    return

if __name__ == "main":
    WebLogicDeployToolingVersion.logVersionInfo(_program_name)
    main(sys.argv)
