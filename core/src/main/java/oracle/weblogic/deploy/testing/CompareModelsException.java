/*
 * Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
 * The Universal Permissive License (UPL), Version 1.0
 */
package oracle.weblogic.deploy.testing;

import oracle.weblogic.deploy.exception.BundleAwareException;

/**
 * The exception used by the compare models components.
 */
public class CompareModelsException extends BundleAwareException {
    private static final long serialVersionUID = 1L;

    /**
     * Constructs a default exception.
     */
    public CompareModelsException() {
        // default constructor
    }

    /**
     * Constructs a new exception with the specified message id.
     *
     * @param messageID the message ID
     */
    public CompareModelsException(String messageID) {
        super(messageID);
    }

    /**
     * Constructs a new exception with the specified message id and parameters.
     *
     * @param messageID the message ID
     * @param params    the parameters to use to fill in the message tokens
     */
    public CompareModelsException(String messageID, Object... params) {
        super(messageID, params);
    }

    /**
     * Constructs a new exception with the specified message id and cause.
     *
     * @param messageID the message ID
     * @param cause     the exception that triggered the creation of this exception
     */
    public CompareModelsException(String messageID, Throwable cause) {
        super(messageID, cause);
    }

    /**
     * Constructs a new exception with passed message id, cause, and parameters.
     *
     * @param messageID the message ID
     * @param cause     the exception that triggered the creation of this exception
     * @param params    the parameters to use to fill in the message tokens
     */
    public CompareModelsException(String messageID, Throwable cause, Object... params) {
        super(messageID, cause, params);
    }

    /**
     * Constructs a new exception with the specified cause.
     *
     * @param cause the exception that triggered the creation of this exception
     */
    public CompareModelsException(Throwable cause) {
        super(cause);
    }

    /**
     * {@inheritDoc}
     */
    @Override
    public String getBundleName() { return TestingConstants.RESOURCE_BUNDLE_NAME; }
}
