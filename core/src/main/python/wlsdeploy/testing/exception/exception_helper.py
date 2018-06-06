"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import sys
import traceback

import java.lang.Throwable as Throwable
from java.text import MessageFormat
from java.util import ResourceBundle

# java classes from weblogic-deploy-tooling
import oracle.weblogic.deploy.exception.PyAttributeErrorException as PyAttributeErrorException
import oracle.weblogic.deploy.exception.PyBaseException as PyBaseException
import oracle.weblogic.deploy.exception.PyIOErrorException as PyIOErrorException
import oracle.weblogic.deploy.exception.PyKeyErrorException as PyKeyErrorException
import oracle.weblogic.deploy.exception.PyTypeErrorException as PyTypeErrorException
import oracle.weblogic.deploy.exception.PyValueErrorException as PyValueErrorException

# java classes from weblogic-deploy-tooling-ct
import oracle.weblogic.deploy.testing.TestingConstants as TestingConstants
import oracle.weblogic.deploy.testing.VerificationException as VerificationException
import oracle.weblogic.deploy.testing.TestingException as TestingException
import oracle.weblogic.deploy.testing.TestDefinitionException as TestDefinitionException
import oracle.weblogic.deploy.testing.IntegrationTestException as IntegrationTestException
import oracle.weblogic.deploy.testing.SystemTestException as SystemTestException
import oracle.weblogic.deploy.testing.CompareModelsException as CompareModelsException

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.exception.expection_types import ExceptionType

_EXCEPTION_TYPE_MAP = {
    ExceptionType.INTEGRATION_TEST:      'create_integration_test_exception',
    ExceptionType.SYSTEM_TEST:           'create_system_test_exception',
    ExceptionType.TESTING:               'create_testing_exception',
    ExceptionType.TEST_DEF:              'create_test_definition_exception',
    ExceptionType.VERIFICATION:          'create_verification_exception',
    ExceptionType.COMPARE_MODELS:        'create_compare_models_exception'
}


def create_exception(exception_type, key, *args, **kwargs):
    """
    Create an exception of the specified type.
    :param exception_type: the exception type
    :param key: key to the message in resource bundler or the message itself
    :param args: list of parameters for the parameters or empty if none needed for the message
    :param kwargs: contains Throwable or instance if present
    :return: BundleAwareException: an exception of the specified type which is a subclass of BundleAwareException
    """
    if exception_type in _EXCEPTION_TYPE_MAP:
        method_name = _EXCEPTION_TYPE_MAP[exception_type]
    else:
        raise TypeError('Unknown exception type: ' + str(exception_type))

    return globals()[method_name](key, *args, **kwargs)


def get_message(key, *args):
    """
    Get the formatted message from the resource bundle.

    :param key: the message key
    :param args: the token values
    :return: the formatted message string
    """
    bundle = ResourceBundle.getBundle(TestingConstants.RESOURCE_BUNDLE_NAME)
    message = bundle.getString(key)
    if len(args) > 0:
        message = MessageFormat.format(message, list(args))

    return message


def create_compare_models_exception(key, *args, **kwargs):
    """
    Create a CompareModelsException from a message id, list of message parameters and Throwable error.
    :param key: key to the message in resource bundler or the message itself
    :param args: list of parameters for the parameters or empty if none needed for the message
    :param kwargs: contains Throwable or instance if present
    :return: CompareModelsException encapsulating the exception information
    """
    arg_list, error = _return_exception_params(*args, **kwargs)
    arg_len = len(arg_list)
    if error is not None:
        if isinstance(error, Throwable) is False:
            error = convert_error_to_exception()
        if arg_len > 0:
            ex = CompareModelsException(key, error, arg_list)
        else:
            ex = CompareModelsException(key, error)
    else:
        if arg_len > 0:
            ex = CompareModelsException(key, arg_list)
        else:
            ex = CompareModelsException(key)
    return ex


def create_verification_exception(key, *args, **kwargs):
    """
    Create a VerificationException from a message id, list of message parameters and Throwable error.
    :param key: key to the message in resource bundler or the message itself
    :param args: list of parameters for the parameters or empty if none needed for the message
    :param kwargs: contains Throwable or instance if present
    :return: VerificationException encapsulating the exception information
    """
    arg_list, error = _return_exception_params(*args, **kwargs)
    arg_len = len(arg_list)
    if error is not None:
        if isinstance(error, Throwable) is False:
            error = convert_error_to_exception()
        if arg_len > 0:
            ex = VerificationException(key, error, arg_list)
        else:
            ex = VerificationException(key, error)
    else:
        if arg_len > 0:
            ex = VerificationException(key, arg_list)
        else:
            ex = VerificationException(key)
    return ex


def create_test_definition_exception(key, *args, **kwargs):
    """
    Create a TestDefinitionException from a message id, list of message parameters and Throwable error.
    :param key: key to the message in resource bundler or the message itself
    :param args: list of parameters for the parameters or empty if none needed for the message
    :param kwargs: contains Throwable or instance if present
    :return: TestDefinitionException encapsulating the exception information
    """
    arg_list, error = _return_exception_params(*args, **kwargs)
    arg_len = len(arg_list)
    if error is not None:
        if isinstance(error, Throwable) is False:
            error = convert_error_to_exception()
        if arg_len > 0:
            ex = TestDefinitionException(key, error, arg_list)
        else:
            ex = TestDefinitionException(key, error)
    else:
        if arg_len > 0:
            ex = TestDefinitionException(key, arg_list)
        else:
            ex = TestDefinitionException(key)
    return ex


def create_integration_test_exception(key, *args, **kwargs):
    """
    Create a IntegrationTestException from a message id, list of message parameters and Throwable error.
    :param key: key to the message in resource bundler or the message itself
    :param args: list of parameters for the parameters or empty if none needed for the message
    :param kwargs: contains Throwable or instance if present
    :return: IntegrationTestException encapsulating the exception information
    """
    arg_list, error = _return_exception_params(*args, **kwargs)
    arg_len = len(arg_list)
    if error is not None:
        if isinstance(error, Throwable) is False:
            error = convert_error_to_exception()
        if arg_len > 0:
            ex = IntegrationTestException(key, error, arg_list)
        else:
            ex = IntegrationTestException(key, error)
    else:
        if arg_len > 0:
            ex = IntegrationTestException(key, arg_list)
        else:
            ex = IntegrationTestException(key)
    return ex


def create_system_test_exception(key, *args, **kwargs):
    """
    Create a SystemTestException from a message id, list of message parameters and Throwable error.
    :param key: key to the message in resource bundler or the message itself
    :param args: list of parameters for the parameters or empty if none needed for the message
    :param kwargs: contains Throwable or instance if present
    :return: SystemTestException encapsulating the exception information
    """
    arg_list, error = _return_exception_params(*args, **kwargs)
    arg_len = len(arg_list)
    if error is not None:
        if isinstance(error, Throwable) is False:
            error = convert_error_to_exception()
        if arg_len > 0:
            ex = SystemTestException(key, error, arg_list)
        else:
            ex = SystemTestException(key, error)
    else:
        if arg_len > 0:
            ex = SystemTestException(key, arg_list)
        else:
            ex = SystemTestException(key)
    return ex


def create_testing_exception(key, *args, **kwargs):
    """
    Create a TestingException from a message id, list of message parameters and Throwable error.
    :param key: key to the message in resource bundler or the message itself
    :param args: list of parameters for the parameters or empty if none needed for the message
    :param kwargs: contains Throwable or instance if present
    :return: TestingException encapsulating the exception information
    """
    arg_list, error = _return_exception_params(*args, **kwargs)
    arg_len = len(arg_list)
    if error is not None:
        if isinstance(error, Throwable) is False:
            error = convert_error_to_exception()
        if arg_len > 0:
            ex = TestingException(key, error, arg_list)
        else:
            ex = TestingException(key, error)
    else:
        if arg_len > 0:
            ex = TestingException(key, arg_list)
        else:
            ex = TestingException(key)
    return ex


def convert_error_to_exception():
    """
    Convert a Python built-in error to a proper bundle-aware Java exception
    :return: the bundle-aware Java exception
    """
    exc_type, exc_obj, exc_tb = sys.exc_info()
    ex_strings = traceback.format_exception(exc_type, exc_obj, exc_tb)
    exception_message = ex_strings[-1]
    for ex_string in ex_strings:
        exception_message += ex_string

    exception_type = str(exc_type)

    if exception_type.find("exceptions.IOError") == 0:
        custom_exception = PyIOErrorException(exception_message)
    elif exception_type.find("exceptions.KeyError") == 0:
        custom_exception = PyKeyErrorException(exception_message)
    elif exception_type.find("exceptions.ValueError") == 0:
        custom_exception = PyValueErrorException(exception_message)
    elif exception_type.find("exceptions.TypeError") == 0:
        custom_exception = PyTypeErrorException(exception_message)
    elif exception_type.find("exceptions.AttributeError") == 0:
        custom_exception = PyAttributeErrorException(exception_message)
    else:
        custom_exception = PyBaseException(exception_message)
    return custom_exception


def _return_exception_params(*args, **kwargs):
    """
    Get the exception parameters from the list
    :param args: input args
    :param kwargs: input names args
    :return: the args and error for the exception
    """
    arg_list = list(args)
    error = kwargs.pop('error', None)
    return arg_list, error
