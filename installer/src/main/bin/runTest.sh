#!/bin/sh
# *****************************************************************************
# runTest.sh
#
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
# The Universal Permissive License (UPL), Version 1.0
#
#     NAME
#       runTest.sh - Script for running different types of test, on the components
#                    of the WLS Deploy tool
#
#     DESCRIPTION
#       This script uses WebLogic MBeans and WLST to run certified and user-defined
#       test types, on the components of the WLS Deploy tool.
#
#
# This script uses the following command-line arguments directly, the rest
# of the arguments are passed down to the underlying python program:
#
#     - -oracle_home                 The directory of the existing Oracle Home to use.
#                                    This directory must exist and it is the caller^'s
#                                    responsibility to verify that it does. This
#                                    argument is required.
#
#     - -test_type                   The type of test to run. This argument is required.
#                                    The currently supported types are:
#   
#                                        smoke-test   
#                                        integration-test   
#                                        system-test   
#   
#     - -test_def_file               The JSON file containing the definition of the
#                                    test to run. This argument is required.
#   
#     - -test_def_overrides_file     A properties file containing the properties to use for
#                                    variables specified in values, in the test_def_file.
#                                    This argument is required, if test_def_file contains
#                                    variable expressions (e.g. @@PROP:settings-0.domain_name@@,
#                                    @@PROP:test.home@@, etc). Otherwise, it is optional.
#   
#     - -test_def_verifier_name      Optional name of the verification test to use when
#                                    verifying the test. Will use the default
#                                    built-in verification test, if not provided.
#   
#     - -test_def_metadata_file      Optional name of the metadata file to use with the
#                                    test_def_file. If not provided, the metadata file
#                                    inside the installer's archive will be used. Passing it
#                                    as a command line option is more efficient and provides
#                                    a greater degree of flexibility. It removes the need to
#                                    recreate a new installer archive, every time you need to
#                                    make a change to the metadata.
#
#     - -wlst_path                   The path to the Oracle Home product directory under
#                                    which to find the wlst.sh script.  This is only
#                                    needed for pre-12.2.1 upper stack products like SOA.
#
#                                      For example, for SOA 12.1.3, -wlst_path should be
#                                      specified as $ORACLE_HOME/soa
#
#     - -verify_only                 Flag indicating to only perform test verification steps.
#                                    This argument is optional and has no value.
#
# This script uses the following variables:
#
# JAVA_HOME             - The location of the JDK to use.  The caller must set
#                         this variable to a valid Java 7 (or later) JDK.
#
# WLSDEPLOY_HOME        - The location of the WLS Deploy installation.
#                         If the caller sets this, the callers location will be
#                         honored provided it is an existing directory.
#                         Otherwise, the location will be calculated from the
#                         location of this script.
#
# WLSDEPLOY_PROPERTIES  - Extra system properties to pass to WLST.  The caller
#                         can use this environment variable to add additional
#                         system properties to the WLST environment.
#

usage() {
  echo ""
  echo "Usage: $1 [-help]"
  echo "          -oracle_home <oracle-home>"
  echo "          -test_type <test-type>"
  echo "          -test_def_file <test-def-file>"
  echo "          [-test_def_overrides_file <test-def-overrides-file>]"
  echo "          [-test_def_verifier_name <verification-test-name>]"
  echo "          [-test_def_metadata_file <test-def-metadata-file>]"
  echo "          [-java_home <java-home>]"
  echo "          [-wlst_path <wlst-path>]"
  echo "          [-verify_only]"
  echo ""
  echo "    where:"
  echo "        oracle-home                 - The existing Oracle Home directory for the domain"
  echo ""
  echo "        test-type                   - The type of test to run. The currently supported"
  echo "                                      types are:"
  echo ""
  echo "                                          smoke-test"
  echo "                                          integration-test"
  echo "                                          system-test"
  echo ""
  echo "        test-def-file               - The test definition file for the test to run."
  echo ""
  echo "        test-def-overrides-file     - A properties file containing the properties to use for"
  echo "                                      variables specified in values, in the test-def-file."
  echo ""
  echo "                                      NOTE: This argument is required, if test-def-file contains"
  echo '                                            variable expressions (e.g. @@PROP:settings-0.domain_name@@,'
  echo '                                            @@PROP:test.home@@, etc). Otherwise, it is optional.'
  echo ""
  echo "        test-def-verifier-name      - The name of the verification test to use when verifying the"
  echo "                                      test definition file. Defaults to the name of the default"
  echo "                                      built-in verification test, if not provided."
  echo ""
  echo "        test-def-metadata-file      - The name of the metadata file to use with the"
  echo "                                      test-def-file. If not provided, the metadata file"
  echo "                                      inside the installer's archive will be used."
  echo ""
  echo "        java-home                   - The Java Home to use with testing tool. Defaults to the"
  echo "                                      value of the JAVA_HOME environment variable, if not provided."
  echo ""
  echo "        wlst-path                   - The Oracle Home subdirectory of the wlst.sh"
  echo "                                      script to use (e.g., ^<ORACLE_HOME^>/soa)"
  echo ""
  echo "        verify-only                 - the flag indicating to only perform test verification steps."
  echo "                                      This argument is optional and has no value."
}

umask 27

WLSDEPLOY_PROGRAM_NAME="runTest"; export WLSDEPLOY_PROGRAM_NAME
SCRIPT_NAME=runTest.sh
ENTRY_POINT_MODULE=run_test.py

if [ -z "${DOMAIN_TYPE}" ]; then
    DOMAIN_TYPE="WLS"
fi

if [ "${WLSDEPLOY_HOME}" = "" ]; then
    BASEDIR="$( cd "$( dirname $0 )" && pwd )"
    WLSDEPLOY_HOME=`cd "${BASEDIR}/.." ; pwd`
    export WLSDEPLOY_HOME
elif [ ! -d ${WLSDEPLOY_HOME} ]; then
    echo "Specified WLSDEPLOY_HOME of ${WLSDEPLOY_HOME} does not exist" >&2
    exit 2
fi

WLSDEPLOY_INSTALL_JARS=\
${WLSDEPLOY_HOME}/lib/weblogic-deploy-core.jar:\
${WLSDEPLOY_HOME}/lib/weblogic-deploy-tooling-ct-core.jar

#
# Make sure that the JAVA_HOME environment variable is set to point to a
# JDK 7 or higher JVM (and that it isn't OpenJDK).
#
if [ "${JAVA_HOME}" = "" ]; then
  echo "Please set the JAVA_HOME environment variable to point to a Java 7 installation" >&2
  exit 2
elif [ ! -d "${JAVA_HOME}" ]; then
  echo "Your JAVA_HOME environment variable to points to a non-existent directory: ${JAVA_HOME}" >&2
  exit 2
fi

if [ -x "${JAVA_HOME}/bin/java" ]; then
  JAVA_EXE=${JAVA_HOME}/bin/java
else
  echo "Java executable at ${JAVA_HOME}/bin/java either does not exist or is not executable" >&2
  exit 2
fi

JVM_OUTPUT=`${JAVA_EXE} -version 2>&1`
case "${JVM_OUTPUT}" in
  *OpenJDK*)
    echo "JAVA_HOME ${JAVA_HOME} contains OpenJDK, which is not supported" >&2
    exit 2
    ;;
esac

JVM_FULL_VERSION=`${JAVA_EXE} -fullversion 2>&1 | awk -F "\"" '{ print $2 }'`
JVM_VERSION=`echo ${JVM_FULL_VERSION} | awk -F "." '{ print $2 }'`

if [ ${JVM_VERSION} -lt 7 ]; then
  echo "You are using an unsupported JDK version ${JVM_FULL_VERSION}" >&2
  exit 2
else
  echo "JDK version is ${JVM_FULL_VERSION}"
fi

#
# Check to see if no args were given and print the usage message
#
if [[ $# = 0 ]]; then
  usage `basename $0`
  exit 0
fi

SCRIPT_ARGS="$*"

#
# Find the args required to determine the WLST script to run
#

while [[ $# > 1 ]]; do
    key="$1"
    case $key in
        -help)
        usage `basename $0`
        exit 0
        ;;
        -java_home)
        JAVA_HOME="$2"
        shift
        ;;
        -oracle_home)
        ORACLE_HOME="$2"
        shift
        ;;
        -test_type)
        TEST_TYPE="$2"
        shift
        ;;
        -test_def_file)
        TEST_DEF_FILE="$2"
        shift
        ;;
        -test_def_overrides_file)
        shift
        ;;
        -test_def_verifier_name)
        shift
        ;;
        -test_def_metadata_file)
        shift
        ;;
        -wlst_path)
        WLST_PATH_DIR="$2"
        shift
        ;;
        -verify_only)
        ;;
        *)
        # unknown option
        ;;
    esac
    shift # past arg or value
done

#
# Check for values of required arguments for this script to continue.
# The underlying WLST script has other required arguments.
#
if [ "${ORACLE_HOME}" = "" ]; then
    echo "Required argument ORACLE_HOME not provided" >&2
    usage `basename $0`
    exit 99
elif [ ! -d ${ORACLE_HOME} ]; then
    echo "The specified ORACLE_HOME does not exist: ${ORACLE_HOME}" >&2
    exit 98
fi

if [ "${TEST_TYPE}" = "" ]; then
    echo "Required argument TEST_TYPE not provided" >&2
    usage `basename $0`
    exit 99
fi

if [ "${TEST_DEF_FILE}" = "" ]; then
    echo "Required argument TEST_DEF_FILE not provided" >&2
    usage `basename $0`
    exit 99
elif [ ! -f ${TEST_DEF_FILE} ]; then
    echo "The specified TEST_DEF_FILE does not exist: ${TEST_DEF_FILE}" >&2
    exit 98
fi

#
# If the WLST_PATH_DIR is specified, validate that it contains the wlst.sh script
#
if [ "${WLST_PATH_DIR}" != "" ]; then
    if [ ! -d ${WLST_PATH_DIR} ]; then
        echo "WLST_PATH_DIR specified does not exist: ${WLST_PATH_DIR}" >&2
        exit 98
    fi
    WLST=${WLST_PATH_DIR}/common/bin/wlst.sh
    if [ ! -x "${WLST}" ]; then
        echo "WLST executable ${WLST} not found under specified WLST_PATH_DIR: ${WLST_PATH_DIR}" >&2
        exit 98
    fi
    CLASSPATH=${WLSDEPLOY_INSTALL_JARS}; export CLASSPATH
    WLST_EXT_CLASSPATH=${WLSDEPLOY_INSTALL_JARS}; export WLST_EXT_CLASSPATH
else
    #
    # Find the location for wlst.sh
    #
    WLST=""
    USE_JRF_WLST=FALSE
    if [ "${DOMAIN_TYPE}" = "WLS" ]; then
        USE_JRF_WLST=FALSE
    elif [ "${DOMAIN_TYPE}" = "RestrictedJRF" ]; then
        USE_JRF_WLST=TRUE
    elif [ "${DOMAIN_TYPE}" = "JRF" ]; then
        USE_JRF_WLST=TRUE
    else
        echo "Domain type ${DOMAIN_TYPE} not recognized by shell script...assuming JRF is required"
    fi

    if [ "${USE_JRF_WLST}" = "TRUE" ]; then
        if [ -x ${ORACLE_HOME}/oracle_common/common/bin/wlst.sh ]; then
            WLST=${ORACLE_HOME}/oracle_common/common/bin/wlst.sh
            CLASSPATH=${WLSDEPLOY_INSTALL_JARS}; export CLASSPATH
            WLST_EXT_CLASSPATH=${WLSDEPLOY_INSTALL_JARS}; export WLST_EXT_CLASSPATH
        fi
    else
        if [ -x ${ORACLE_HOME}/wlserver_10.3/common/bin/wlst.sh ]; then
            WLST=${ORACLE_HOME}/wlserver_10.3/common/bin/wlst.sh
            CLASSPATH=${WLSDEPLOY_INSTALL_JARS}; export CLASSPATH
        elif [ -x ${ORACLE_HOME}/wlserver_12.1/common/bin/wlst.sh ]; then
            WLST=${ORACLE_HOME}/wlserver_12.1/common/bin/wlst.sh
            CLASSPATH=${WLSDEPLOY_INSTALL_JARS}; export CLASSPATH
        elif [ -x ${ORACLE_HOME}/wlserver/common/bin/wlst.sh -a -f ${ORACLE_HOME}/wlserver/.product.properties ]; then
            WLST=${ORACLE_HOME}/wlserver/common/bin/wlst.sh
            CLASSPATH=${WLSDEPLOY_INSTALL_JARS}; export CLASSPATH
        else
            WLST=${ORACLE_HOME}/oracle_common/common/bin/wlst.sh
            WLST_EXT_CLASSPATH=${WLSDEPLOY_INSTALL_JARS}; export WLST_EXT_CLASSPATH
        fi
    fi

    if [ "${WLST}" = "" ]; then
        echo "Unable to determine WLS version in ${ORACLE_HOME} to determine WLST shell script to call" >&2
        exit 98
    fi
fi

LOG_CONFIG_CLASS=oracle.weblogic.deploy.logging.WLSDeployLoggingConfig
WLST_PROPERTIES=-Dcom.oracle.cie.script.throwException=true
WLST_PROPERTIES="-Djava.util.logging.config.class=${LOG_CONFIG_CLASS} ${WLST_PROPERTIES} ${WLSDEPLOY_PROPERTIES}"
WLST_ARGS=-skipWLSModuleScanning
export WLST_PROPERTIES

if [ "${WLSDEPLOY_LOG_PROPERTIES}" = "" ]; then
    WLSDEPLOY_LOG_PROPERTIES=${WLSDEPLOY_HOME}/etc/logging.properties; export WLSDEPLOY_LOG_PROPERTIES
fi

if [ "${WLSDEPLOY_LOG_DIRECTORY}" = "" ]; then
    WLSDEPLOY_LOG_DIRECTORY=${WLSDEPLOY_HOME}/logs; export WLSDEPLOY_LOG_DIRECTORY
fi

echo "JAVA_HOME = ${JAVA_HOME}"
echo "WLST_EXT_CLASSPATH = ${WLST_EXT_CLASSPATH}"
echo "CLASSPATH = ${CLASSPATH}"
echo "WLST_PROPERTIES = ${WLST_PROPERTIES}"
echo "WLST_ARGS = ${WLST_ARGS}"

PY_SCRIPTS_PATH=${WLSDEPLOY_HOME}/lib/python
echo "${WLST} ${WLST_ARGS} ${PY_SCRIPTS_PATH}/${ENTRY_POINT_MODULE} ${SCRIPT_ARGS}"

"${WLST}" "${WLST_ARGS}" "${PY_SCRIPTS_PATH}/${ENTRY_POINT_MODULE}" ${SCRIPT_ARGS}

RETURN_CODE=$?
if [ ${RETURN_CODE} -eq 100 ]; then
  usage `basename $0`
  RETURN_CODE=0
elif [ ${RETURN_CODE} -eq 99 ]; then
  usage `basename $0`
  echo ""
  echo "${SCRIPT_NAME} failed due to the usage error shown above" >&2
elif [ ${RETURN_CODE} -eq 98 ]; then
  echo ""
  echo "${SCRIPT_NAME} failed due to a parameter validation error" >&2
elif [ ${RETURN_CODE} -eq 2 ]; then
  echo ""
  echo "${SCRIPT_NAME} failed (exit code = ${RETURN_CODE})" >&2
elif [ ${RETURN_CODE} -eq 1 ]; then
  echo ""
  echo "${SCRIPT_NAME} completed but with some issues (exit code = ${RETURN_CODE})" >&2
elif [ ${RETURN_CODE} -eq 0 ]; then
  echo ""
  echo "${SCRIPT_NAME} completed successfully (exit code = ${RETURN_CODE})"
else
  # Unexpected return code so just print the message and exit...
  echo ""
  echo "${SCRIPT_NAME} failed (exit code = ${RETURN_CODE})" >&2
fi
exit ${RETURN_CODE}
