/*
 * Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
 * The Universal Permissive License (UPL), Version 1.0
 */
package oracle.weblogic.deploy.testing.logging;

import java.util.logging.ConsoleHandler;
import java.util.logging.LogRecord;

/**
 * The WLS Deploy Testing Console Handler that prevents stack traces from being output to the console.
 */
public class WLSDeployTestingLoggingConsoleHandler extends ConsoleHandler {

    /**
     * The default constructor.
     */
    public WLSDeployTestingLoggingConsoleHandler() {
        // nothing to do
    }

    @Override
    public void publish(LogRecord record) {
        LogRecord myRecord = cloneRecordWithoutException(record);
        super.publish(myRecord);
    }

    private static LogRecord cloneRecordWithoutException(LogRecord record) {
        LogRecord newRecord = new LogRecord(record.getLevel(), record.getMessage());

        newRecord.setLoggerName(record.getLoggerName());
        newRecord.setMillis(record.getMillis());
        newRecord.setParameters(record.getParameters());
        newRecord.setResourceBundle(record.getResourceBundle());
        newRecord.setResourceBundleName(record.getResourceBundleName());
        newRecord.setSequenceNumber(record.getSequenceNumber());
        newRecord.setSourceClassName(record.getSourceClassName());
        newRecord.setSourceMethodName(record.getSourceMethodName());
        newRecord.setThreadID(record.getThreadID());
        // Skip thrown
        return newRecord;
    }
}
