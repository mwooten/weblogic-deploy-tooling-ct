"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""
import imp
import os.path
import sys

from java.io import IOException
from java.lang import IllegalArgumentException
from java.text import MessageFormat
from java.util import ResourceBundle

# java classes from weblogic-deploy-tooling
from oracle.weblogic.deploy.util import FileUtils
from oracle.weblogic.deploy.util import TranslateException

# java classes from weblogic-deploy-tooling-ct
import oracle.weblogic.deploy.testing.TestingConstants as TestingConstants

# python classes from weblogic-deploy-tooling-ct
from wlsdeploy.testing.common import testing_constants
from wlsdeploy.testing.exception import exception_helper
from wlsdeploy.util.model_translator import FileToPython

_class_name = 'testing_helper'


def format_message(key, *args):
    bundle = ResourceBundle.getBundle(TestingConstants.RESOURCE_BUNDLE_NAME)
    message = bundle.getString(key)
    if len(args) > 0:
        message = MessageFormat.format(message, list(args))
        #message = MessageFormat.format(message, args)

    return message


def import_stage_module(module_name, logger):
    return __import_module(testing_constants.STAGE_MODULES_PATH, module_name, logger)


def import_tool_module(module_name, logger):
    return __import_module(testing_constants.TOOL_MODULES_PATH, module_name, logger)


def __import_module(modules_path, module_name, logger):
    """

    :param modules_path:
    :param module_name:
    :param logger: A PlatformLogger instance that will be used for logging
                   any exceptions that are thrown
    :return:
    """
    _method_name = 'import_module'

    fp = None

    try:
        fp, pathname, description = imp.find_module(module_name, [modules_path])
    except ImportError:
        if fp is not None:
            fp.close()
        exctype, value = sys.exc_info()[:2]
        ex = exception_helper.create_testing_exception('WLSDPLY-09822', module_name, str(value))
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    try:
        _module = imp.load_module(module_name, fp, pathname, description)
        fp.close()
    except Exception:
        if fp is not None:
            fp.close()
        exctype, value = sys.exc_info()[:2]
        ex = exception_helper.create_testing_exception('WLSDPLY-09822', module_name, str(value))
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    return _module


def verify_directory_exists(directory_name, logger):
    """

    :param directory_name:
    :param logger: A PlatformLogger instance that will be used for logging
                   any exceptions that are thrown
    :return:
    """
    _method_name = 'verify_directory_exists'

    try:
        j_file = FileUtils.validateExistingDirectory(directory_name)
    except IllegalArgumentException, iae:
        ex = exception_helper.create_testing_exception('WLSDPLY-09809',
                                                       directory_name,
                                                       iae.getLocalizedMessage(), error=iae)
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    return j_file


def verify_file_exists(file_name, logger):
    """

    :param file_name:
    :param logger: A PlatformLogger instance that will be used for logging
                   any exceptions that are thrown
    :return:
    """
    _method_name = 'verify_file_exists'

    try:
        j_file = FileUtils.validateExistingFile(file_name)
    except IllegalArgumentException, iae:
        ex = exception_helper.create_testing_exception('WLSDPLY-09808',
                                                       file_name,
                                                       iae.getLocalizedMessage(), error=iae)
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    return j_file


def translate_file(from_file, logger):
    """
    Returns a Python dictionary representation of the from_file argument.

    If from_file is a string, the assumption taken is that it's the name
    of a JSON file. In that case, the verify_file_exists(file_name) method
    will be called on it, first. That method returns a Jython File object,
    which is what this translate_file(from_file) method works with.

    :param from_file: A File
    :param logger: A PlatformLogger instance that will be used for logging
                   any exceptions that are thrown
    :return: A Python dictionary representation of the from_file argument
    :raises: TestingException: if a TranslateException is caught during the translation
    """
    _method_name = 'translate_file'

    try:
        if isinstance(from_file, str):
            from_file = verify_file_exists(from_file, logger)

        from_file_dict = FileToPython(from_file.getAbsolutePath(), True).parse()
    except TranslateException, te:
        ex = exception_helper.create_testing_exception('WLSDPLY-09807',
                                                       from_file.getAbsolutePath(),
                                                       te.getLocalizedMessage(), error=te)
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    return from_file_dict


def extract_file(from_file_path, logger):
    """

    :param from_file_path:
    :param logger: A PlatformLogger instance that will be used for logging
                   any exceptions that are thrown
    :return:
    """
    _method_name = 'extract_file'

    from_file_name = os.path.basename(from_file_path)

    json_inputstream = FileUtils.getResourceAsStream(from_file_path)
    if json_inputstream is None:
        ex = exception_helper.create_testing_exception('WLSDPLY-09824', from_file_path)
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    try:
        j_file = FileUtils.writeInputStreamToFile(json_inputstream, from_file_name)
    except IOException, ioe:
        ex = exception_helper.create_testing_exception('WLSDPLY-09825', from_file_name,
                                                       ioe.getLocalizedMessage(), error=ioe)
        logger.throwing(ex, class_name=_class_name, method_name=_method_name)
        raise ex

    return j_file


def get_resource_as_stream(file_path):
    return FileUtils.getResourceAsStream(file_path)

