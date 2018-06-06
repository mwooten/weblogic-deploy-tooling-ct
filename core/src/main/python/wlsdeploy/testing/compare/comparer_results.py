"""
Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
The Universal Permissive License (UPL), Version 1.0
"""

import java.lang.System as JSystem
import java.lang.Thread as JThread
import java.util.logging.Level as JLevel
import java.util.logging.LogRecord as JLogRecord
import java.util.logging.Logger as JLogger
from oracle.weblogic.deploy.util import PyOrderedDict

import wlsdeploy.testing.common.testing_helper as testing_helper

_RESOURCE_ID = 'resource_id'
_ARGS = 'args'


class ComparerResults(object):
    """
    Class for collecting and printing out comparator results

    """
    _class_name = 'ComparerResults'
    _ERRORS_COUNT = 'errors_count'
    _WARNINGS_COUNT = 'warnings_count'
    _INFOS_COUNT = 'infos_count'

    def __init__(self):
        self._comparison_result_dict = PyOrderedDict()

    def __str__(self):
        return self.__to_string()

    def set_comparison_result(self, comparison_result):
        self._comparison_result_dict[comparison_result.get_comparison_area()] = comparison_result

    def get_errors_count(self):
        """

        :return:
        """
        results_summary = self.__get_summary()
        return results_summary[ComparerResults._ERRORS_COUNT]

    def get_warnings_count(self):
        """

        :return:
        """
        results_summary = self.__get_summary()
        return results_summary[ComparerResults._WARNINGS_COUNT]

    def get_infos_count(self):
        """

        :return:
        """
        results_summary = self.__get_summary()
        return results_summary[ComparerResults._INFOS_COUNT]

    def write_to_file(self, file_path):
        pass

    def log_results(self, logger):
        """

        :param logger:
        :return:
        """
        _method_name = 'log_results'

        if logger is not None:
            # Get counts for all the ComparerResult objects
            # in this ComparerResults object
            results_summary = self.__get_summary()

            jlogger = JLogger.getLogger(logger.get_name(), logger.resource_bundle_name)

            jlogger.setLevel(JLevel.INFO)

            # Determine what the severity level is going to be for the
            # summary log message. Needs to be set in accordance with
            # what the severest test message was.
            if results_summary[ComparerResults._INFOS_COUNT] > 0:
                jlogger.setLevel(JLevel.INFO)
            if results_summary[ComparerResults._WARNINGS_COUNT] > 0:
                jlogger.setLevel(JLevel.WARNING)
            if results_summary[ComparerResults._ERRORS_COUNT] > 0:
                jlogger.setLevel(JLevel.SEVERE)

            total_messages_count = \
                int(results_summary[ComparerResults._ERRORS_COUNT]) + \
                int(results_summary[ComparerResults._WARNINGS_COUNT]) + \
                int(results_summary[ComparerResults._INFOS_COUNT])

            logger.log(jlogger.getLevel(),
                       'WLSDPLY-09901',
                       results_summary[ComparerResults._ERRORS_COUNT],
                       results_summary[ComparerResults._WARNINGS_COUNT],
                       results_summary[ComparerResults._INFOS_COUNT],
                       class_name=self._class_name, method_name=_method_name)

            if total_messages_count > 0:
                logger.log(jlogger.getLevel(), 'WLSDPLY-09811', total_messages_count,
                           class_name=self._class_name, method_name=_method_name)

            for comparison_result in self._comparison_result_dict.values():
                if comparison_result.get_infos_count() > 0:
                    jlogger.setLevel(JLevel.INFO)
                    self.__log_results_category_details(comparison_result.get_infos_messages(), _method_name, jlogger)

            for comparison_result in self._comparison_result_dict.values():
                if comparison_result.get_warnings_count() > 0:
                    jlogger.setLevel(JLevel.WARNING)
                    self.__log_results_category_details(comparison_result.get_warnings_messages(), _method_name, jlogger)

            for comparison_result in self._comparison_result_dict.values():
                if comparison_result.get_errors_count() > 0:
                    jlogger.setLevel(JLevel.SEVERE)
                    self.__log_results_category_details(comparison_result.get_errors_messages(), _method_name, jlogger)

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
            ComparerResults._ERRORS_COUNT: 0,
            ComparerResults._WARNINGS_COUNT: 0,
            ComparerResults._INFOS_COUNT: 0
        }

        for comparison_result in self._comparison_result_dict.values():
            if comparison_result is not None:
                results_summary[ComparerResults._ERRORS_COUNT] += comparison_result.get_errors_count()
                results_summary[ComparerResults._WARNINGS_COUNT] += comparison_result.get_warnings_count()
                results_summary[ComparerResults._INFOS_COUNT] += comparison_result.get_infos_count()

        return results_summary

    def __to_string(self):
        """

        :return:
        """

        tmp = ''

        for comparison_result in self._comparison_result_dict.values():
            if comparison_result.get_errors_count() > 0 \
                    or comparison_result.get_warnings_count() > 0 \
                    or comparison_result.get_infos_count():
                tmp += str(comparison_result)
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


class ComparerResult(object):
    """
    Class for capturing model value comparison results
    """
    _COMPARISON_AREA = 'comparison_area'
    _ERRORS = 'errors'
    _WARNINGS = 'warnings'
    _INFOS = 'infos'
    _COUNT = 'count'
    _MESSAGES = 'messages'

    def __init__(self, comparison_area):
        self._result = {
            ComparerResult._COMPARISON_AREA: comparison_area,
            ComparerResult._ERRORS: {
                ComparerResult._COUNT: 0,
                ComparerResult._MESSAGES: []
            },
            ComparerResult._WARNINGS: {
                ComparerResult._COUNT: 0,
                ComparerResult._MESSAGES: []
            },
            ComparerResult._INFOS: {
                ComparerResult._COUNT: 0,
                ComparerResult._MESSAGES: []
            }
        }

    def __str__(self):
        tmp = '"comparison_area": "%s",' % self._result[ComparerResult._COMPARISON_AREA]
        if self.get_errors_count() > 0:
            tmp += self.__to_string(ComparerResult._ERRORS)
        if self.get_warnings_count() > 0:
            tmp += self.__to_string(ComparerResult._WARNINGS)
        if self.get_infos_count() > 0:
            tmp += self.__to_string(ComparerResult._INFOS)

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
        self._result[ComparerResult._ERRORS][ComparerResult._COUNT] += 1
        message = {_RESOURCE_ID: resource_id, _ARGS: args}
        self._result[ComparerResult._ERRORS][ComparerResult._MESSAGES].append(message)
        return

    def add_warning(self, resource_id, *args):
        """

        :param resource_id:
        :param args:
        :return:
        """
        self._result[ComparerResult._WARNINGS][ComparerResult._COUNT] += 1
        message = {_RESOURCE_ID: resource_id, _ARGS: args}
        self._result[ComparerResult._WARNINGS][ComparerResult._MESSAGES].append(message)
        return

    def add_info(self, resource_id, *args):
        """

        :param resource_id:
        :param args:
        :return:
        """
        self._result[ComparerResult._INFOS][ComparerResult._COUNT] += 1
        message = {_RESOURCE_ID: resource_id, _ARGS: args}
        self._result[ComparerResult._INFOS][ComparerResult._MESSAGES].append(message)
        return

    def get_comparison_area(self):
        """

        :return:
        """
        return self._result[ComparerResult._COMPARISON_AREA]

    def get_errors_count(self):
        """

        :return:
        """
        return self._result[ComparerResult._ERRORS][ComparerResult._COUNT]

    def get_errors_messages(self):
        """

        :return:
        """
        return self._result[ComparerResult._ERRORS][ComparerResult._MESSAGES]

    def get_warnings_count(self):
        """

        :return:
        """
        return self._result[ComparerResult._WARNINGS][ComparerResult._COUNT]

    def get_warnings_messages(self):
        """

        :return:
        """
        return self._result[ComparerResult._WARNINGS][ComparerResult._MESSAGES]

    def get_infos_count(self):
        """

        :return:
        """
        return self._result[ComparerResult._INFOS][ComparerResult._COUNT]

    def get_infos_messages(self):
        """

        :return:
        """
        return self._result[ComparerResult._INFOS][ComparerResult._MESSAGES]

    def __to_string(self, category_name):
        tmp = ' "%s": {' % category_name
        tmp += '"count": %d, ' % self._result[category_name][ComparerResult._COUNT]
        tmp += '"messages": ['
        for message in self._result[category_name][ComparerResult._MESSAGES]:
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
