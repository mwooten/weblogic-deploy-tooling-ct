"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

import traceback
import unittest

import java.lang.System as JSystem
import java.lang.Thread as JThread
import java.util.logging.Level as JLevel
import java.util.logging.LogRecord as JLogRecord
import java.util.logging.Logger as JLogger
from oracle.weblogic.deploy.util import PyOrderedDict

from wlsdeploy.testing.common import testing_helper
from wlsdeploy.util import string_utils

_RESOURCE_ID = 'resource_id'
_ARGS = 'args'


class TestResults(object):
    """
    Class for logging and printing out test results

    """
    _class_name = 'TestResults'
    _ERRORS_COUNT = 'errors_count'
    _WARNINGS_COUNT = 'warnings_count'
    _INFOS_COUNT = 'infos_count'

    def __init__(self):
        self._test_result_dict = PyOrderedDict()

    def __str__(self):
        return self.__to_string()

    def set_test_result(self, test_result):
        self._test_result_dict[test_result.get_test_area()] = test_result

    def get_errors_count(self):
        """

        :return:
        """
        results_summary = self.__get_summary()
        return results_summary[TestResults._ERRORS_COUNT]

    def get_warnings_count(self):
        """

        :return:
        """
        results_summary = self.__get_summary()
        return results_summary[TestResults._WARNINGS_COUNT]

    def get_infos_count(self):
        """

        :return:
        """
        results_summary = self.__get_summary()
        return results_summary[TestResults._INFOS_COUNT]

    def log_results(self, logger):
        """

        :param logger:
        :return:
        """
        _method_name = 'log_results'

        if logger is not None:
            # Get counts for all the TestResult objects
            # in this TestResults object
            results_summary = self.__get_summary()

            jlogger = JLogger.getLogger(logger.get_name(), logger.resource_bundle_name)

            jlogger.setLevel(JLevel.INFO)

            # Determine what the severity level is going to be for the
            # summary log message. Needs to be set in accordance with
            # what the severest test message was.
            if results_summary[TestResults._INFOS_COUNT] > 0:
                jlogger.setLevel(JLevel.INFO)
            if results_summary[TestResults._WARNINGS_COUNT] > 0:
                jlogger.setLevel(JLevel.WARNING)
            if results_summary[TestResults._ERRORS_COUNT] > 0:
                jlogger.setLevel(JLevel.SEVERE)

            total_messages_count = \
                int(results_summary[TestResults._ERRORS_COUNT]) + int(results_summary[TestResults._WARNINGS_COUNT]) + \
                int(results_summary[TestResults._INFOS_COUNT])

            logger.log(jlogger.getLevel(),
                       'WLSDPLY-09810',
                       results_summary[TestResults._ERRORS_COUNT],
                       results_summary[TestResults._WARNINGS_COUNT],
                       results_summary[TestResults._INFOS_COUNT],
                       class_name=self._class_name, method_name=_method_name)

            if total_messages_count > 0:
                logger.log(jlogger.getLevel(), 'WLSDPLY-09811', total_messages_count,
                           class_name=self._class_name, method_name=_method_name)

            for test_result in self._test_result_dict.values():
                if test_result.get_infos_count() > 0:
                    jlogger.setLevel(JLevel.INFO)
                    self.__log_results_category_details(test_result.get_infos_messages(), _method_name, jlogger)

            for test_result in self._test_result_dict.values():
                if test_result.get_warnings_count() > 0:
                    jlogger.setLevel(JLevel.WARNING)
                    self.__log_results_category_details(test_result.get_warnings_messages(), _method_name, jlogger)

            for test_result in self._test_result_dict.values():
                if test_result.get_errors_count() > 0:
                    jlogger.setLevel(JLevel.SEVERE)
                    self.__log_results_category_details(test_result.get_errors_messages(), _method_name, jlogger)

            jlogger.setLevel(JLevel.INFO)

        return

    def __log_results_category_details(self, category_messages, method_name, jlogger):
        """

        :param category_messages:
        :param method_name:
        :param jlogger:
        :return:
        """

        for i in range(len(category_messages)):
            messages = category_messages[i]
            _log_category_message(jlogger, messages[_RESOURCE_ID], messages[_ARGS],
                                  class_name=self._class_name, method_name=method_name)

    def __get_summary(self):
        """

        :return:
        """

        results_summary = {
            TestResults._ERRORS_COUNT: 0,
            TestResults._WARNINGS_COUNT: 0,
            TestResults._INFOS_COUNT: 0
        }

        for test_result in self._test_result_dict.values():
            if test_result is not None:
                results_summary[TestResults._ERRORS_COUNT] += test_result.get_errors_count()
                results_summary[TestResults._WARNINGS_COUNT] += test_result.get_warnings_count()
                results_summary[TestResults._INFOS_COUNT] += test_result.get_infos_count()

        return results_summary

    def __to_string(self):
        """

        :return:
        """

        tmp = ''

        for test_result in self._test_result_dict.values():
            if test_result.get_errors_count() > 0 \
                    or test_result.get_warnings_count() > 0 \
                    or test_result.get_infos_count():
                tmp += str(test_result)
                tmp += ','

        if tmp[-1:] == ',':
            # Strip off trailing ','
            tmp = tmp[:-1]

        return '[%s]' % tmp


def _log_category_message(jlogger, message, *args, **kwargs):
    method = kwargs.get('method_name', None)
    clazz = kwargs.get('class_name', None)
    record = JLogRecord(jlogger.getLevel(), message)
    record.setLoggerName(jlogger.getName())
    record.setMillis(JSystem.currentTimeMillis())
    record.setParameters(list(*args))
    record.setResourceBundle(jlogger.getResourceBundle())
    if clazz is not None:
        record.setSourceClassName(clazz)
    if method is not None:
        record.setSourceMethodName(method)
    record.setThreadID(int(JThread.currentThread().getId()))
    jlogger.log(record)
    return


class TestResult(unittest.TestResult):
    """
    Class for capturing test results
    """
    _TEST_AREA = 'test_area'
    _ERRORS = 'errors'
    _WARNINGS = 'warnings'
    _INFOS = 'infos'
    _COUNT = 'count'
    _MESSAGES = 'messages'

    def __init__(self, test_area):
        self._result = {
            TestResult._TEST_AREA: test_area,
            TestResult._ERRORS: {
                TestResult._COUNT: 0,
                TestResult._MESSAGES: []
            },
            TestResult._WARNINGS: {
                TestResult._COUNT: 0,
                TestResult._MESSAGES: []
            },
            TestResult._INFOS: {
                TestResult._COUNT: 0,
                TestResult._MESSAGES: []
            }
        }
        self.errors = []
        self.failures = []
        self.skipped = []
        self.expectedFailures = []
        self.unexpectedSuccesses = []
        self.shouldStop = False
        self.testsRun = 0
        self.buffer = False

    def __str__(self):
        tmp = '"test_area": "%s",' % self._result[TestResult._TEST_AREA]
        if self.get_errors_count() > 0:
            tmp += self.__to_string(TestResult._ERRORS)
        if self.get_warnings_count() > 0:
            tmp += self.__to_string(TestResult._WARNINGS)
        if self.get_infos_count() > 0:
            tmp += self.__to_string(TestResult._INFOS)

        if tmp[-1:] == ',':
            # Strip off trailing ','
            tmp = tmp[:-1]

        return "{%s}" % tmp

    def add_error(self, resource_id, *args):
        """

        :param resource_id:
        :param args:
        :return:
        """
        self._result[TestResult._ERRORS][TestResult._COUNT] += 1
        message = {_RESOURCE_ID: resource_id, _ARGS: args}
        self._result[TestResult._ERRORS][TestResult._MESSAGES].append(message)
        self.stop()
        return

    def add_warning(self, resource_id, *args):
        """

        :param resource_id:
        :param args:
        :return:
        """
        self._result[TestResult._WARNINGS][TestResult._COUNT] += 1
        message = {_RESOURCE_ID: resource_id, _ARGS: args}
        self._result[TestResult._WARNINGS][TestResult._MESSAGES].append(message)
        return

    def add_info(self, resource_id, *args):
        """

        :param resource_id:
        :param args:
        :return:
        """
        self._result[TestResult._INFOS][TestResult._COUNT] += 1
        message = {_RESOURCE_ID: resource_id, _ARGS: args}
        self._result[TestResult._INFOS][TestResult._MESSAGES].append(message)
        return

    def get_test_area(self):
        """

        :return:
        """
        return self._result[TestResult._TEST_AREA]

    def get_errors_count(self):
        """

        :return:
        """
        return self._result[TestResult._ERRORS][TestResult._COUNT]

    def get_errors_messages(self):
        """

        :return:
        """
        return self._result[TestResult._ERRORS][TestResult._MESSAGES]

    def get_warnings_count(self):
        """

        :return:
        """
        return self._result[TestResult._WARNINGS][TestResult._COUNT]

    def get_warnings_messages(self):
        """

        :return:
        """
        return self._result[TestResult._WARNINGS][TestResult._MESSAGES]

    def get_infos_count(self):
        """

        :return:
        """
        return self._result[TestResult._INFOS][TestResult._COUNT]

    def get_infos_messages(self):
        """

        :return:
        """
        return self._result[TestResult._INFOS][TestResult._MESSAGES]

    # override addError(test, err) method
    def addError(self, test, err):
        test_name_sections = string_utils.rsplit(test.id(), '.', 1)
        error_message = traceback.format_exception_only(err[0], err[1])[0]
        self.add_error('WLSDPLY-09826',
                       test_name_sections[1],
                       test_name_sections[0],
                       error_message[:-1])

    # override addFailure(test, err) method
    def addFailure(self, test, err):
        test_name_sections = string_utils.rsplit(test.id(), '.', 1)
        failure_message = traceback.format_exception_only(err[0], err[1])[0]
        self.add_error('WLSDPLY-09804',
                       test_name_sections[1],
                       test_name_sections[0],
                       failure_message[:-1])

    # override addSuccess(test, err) method
    def addSuccess(self, test):
        test_name_sections = string_utils.rsplit(test.id(), '.', 1)
        self.add_info('WLSDPLY-09803', test_name_sections[1], test_name_sections[0])

    def __to_string(self, category_name):
        tmp = ' "%s": {' % category_name
        tmp += '"count": %d, ' % self._result[category_name][TestResult._COUNT]
        tmp += '"messages": ['
        for message in self._result[category_name][TestResult._MESSAGES]:
            tmp += "{"
            tmp += '"%s": "%s",' % ('message', testing_helper.format_message(message[_RESOURCE_ID],
                                                                             list(message[_ARGS])))
            if tmp[-1:] == ',':
                # Strip off trailing ','
                tmp = tmp[:-1]
            tmp += "},"
        if tmp[-1:] == ',':
            # Strip off trailing ','
            tmp = tmp[:-1]
        # Concatenate closing ']}'
        tmp += "]},"

        return tmp
