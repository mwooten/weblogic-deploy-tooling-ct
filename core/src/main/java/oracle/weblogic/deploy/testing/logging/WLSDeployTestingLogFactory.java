/*
 * Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
 * The Universal Permissive License (UPL), Version 1.0
 */
package oracle.weblogic.deploy.testing.logging;

import java.util.HashMap;
import java.util.logging.Logger;

import oracle.weblogic.deploy.testing.TestingConstants;

/**
 * The java.util.logging log factory for the WLS Deploy tooling.
 */
public final class WLSDeployTestingLogFactory {
    private static final HashMap<String, PlatformLogger> LOGGERS = new HashMap<>();

    private static final String DEFAULT_RESOURCE_BUNDLE_NAME = TestingConstants.RESOURCE_BUNDLE_NAME;

    // Hide the default constructor.
    //
    private WLSDeployTestingLogFactory() {
        // No constructor for this utility class
    }

    /**
     * Get the logger using the specified logger name and resource bundle name.
     *
     * @param loggerName the logger name
     * @param resourceBundleName the resource bundle name
     * @return the logger
     */
    public static PlatformLogger getLogger(String loggerName, String resourceBundleName) {
        PlatformLogger myLogger = LOGGERS.get(loggerName);

        if (myLogger == null) {
            myLogger = initializeLogger(loggerName, resourceBundleName);
        }
        return myLogger;
    }

    /**
     * Get the logger using the logger name and using the default resource bundle for the WLS Deploy tooling.
     *
     * @param loggerName the logger name
     * @return the logger
     */
    public static PlatformLogger getLogger(String loggerName) {
        PlatformLogger myLogger = LOGGERS.get(loggerName);

        if (myLogger == null) {
            myLogger = initializeLogger(loggerName, DEFAULT_RESOURCE_BUNDLE_NAME);
        }
        return myLogger;
    }

    ////////////////////////////////////////////////////////////////////////////////
    // private helper methods                                                     //
    ////////////////////////////////////////////////////////////////////////////////

    private static synchronized PlatformLogger initializeLogger(String loggerName, String resourceBundleName) {
        // Make sure another thread didn't get here first and create it)
        PlatformLogger myLogger = LOGGERS.get(loggerName);
        if (myLogger == null) {
            myLogger = getComponentLogger(loggerName, resourceBundleName);
            LOGGERS.put(loggerName, myLogger);
        }
        return myLogger;
    }

    private static PlatformLogger getComponentLogger(String name, String resourceBundleName) {
        final Logger logger = Logger.getLogger(name, resourceBundleName);
        return new PlatformLogger(logger);
    }
}
