#!/bin/sh
# *****************************************************************************
# compareModels.sh
#
# Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
# The Universal Permissive License (UPL), Version 1.0
#
#     NAME
#       compareModels.sh - Script for comparing two domain model files, which
#                          have already been run through the validate component 
#                          of the WLS Deploy Tool.
#
#     DESCRIPTION
#          This script runs a Python script in WebLogic WLST, which compares the
#          sections, folders and attributes of one domain model file, to another
#          domain model file. The first domain model file is referred to as the "expected"
#          domain model, while the latter is referred to as the "actual" domain model.
#
# This script uses the following command-line arguments directly. The remaining
# arguments are passed down to the underlying python program:
#
#        - -oracle_home                    The directory of the existing Oracle Home to use.
#                                          This directory must exist and it is the caller^'s
#                                          responsibility to verify that it does. This
#                                          argument is required.
#
#        - -expected_model_file            The .yaml/.json file to use for the "expected" domain
#                                          model. This argument is required.
#   
#        - -actual_model_file              The .yaml/.json file to use for the "actual" domain
#                                          model. This argument is required.
#   
#        - -expected_model_overrides_file  A properties file containing the properties to use for
#                                          variables specified in values, in expected_model_file.
#
#                                          NOTE: This argument is required, if expected_model_file contains
#                                                variable expressions (e.g. @@PROP:settings-0.domain_name@@,
#                                                @@PROP:test.home@@, etc). Otherwise, it is optional.
#
#        - -actual_model_overrides_file    A properties file containing the properties to use for
#                                          variables specified in values, in actual_model_file.
#
#                                          NOTE: This argument is required, if actual_model_file contains
#                                                variable expressions (e.g. @@PROP:settings-0.domain_name@@,
#                                                @@PROP:test.home@@, etc). Otherwise, it is optional.
#
#        - -compare_results_file           The file to write the comparison results to. Results
#                                          are always written to the compareModels.log log, so
#                                          this argument is optional.
#
#        - -wlst_path                      The path to the Oracle Home product directory under
#                                          which to find the wlst.sh script.  This is only
#                                          needed for pre-12.2.1 upper stack products like SOA.
#
#                                            For example, for SOA 12.1.3, -wlst_path should be
#                                            specified as $ORACLE_HOME/soa
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
  echo "          -expected_model_file <expected-model-file>"
  echo "          -actual_model_file <actual-model-file>"
  echo "          [-expected_model_overrides_file <expected-model-overrides-file>]"
  echo "          [-actual_model_overrides_file <actual-model-overrides-file>]"
  echo "          [-compare_results_file <compare-results-file>]"
  echo "          [-java_home <java-home>]"
  echo "          [-wlst_path <wlst-path>]"
  echo ""
  echo "    where:"
  echo "       oracle-home                    - The existing Oracle Home directory for the domain"
  echo ""
  echo "       expected-model-file            - The .yaml/.json file to use for the 'expected' domain"
  echo "                                        model."
  echo ""
  echo "       actual-model-file              - The .yaml/.json file to use for the 'actual'"
  echo "                                        model."
  echo ""
  echo "       expected-model-overrides-file  - A properties file containing the properties to use for"
  echo "                                        variables specified in values, in expected-model-file."
  echo ""
  echo "                                          NOTE: This argument is required, if expected-model-file contains"
  echo "                                                variable expressions (e.g. @@PROP:settings-0.domain_name@@,"
  echo "                                                @@PROP:test.home@@, etc). Otherwise, it is optional."
  echo ""
  echo "       actual-model-overrides-file    - A properties file containing the properties to use for"
  echo "                                        variables specified in values, in actual-model-file."
  echo ""
  echo "                                          NOTE: This argument is required, if actual-model-file contains"
  echo "                                                variable expressions (e.g. @@PROP:settings-0.domain_name@@,"
  echo "                                                @@PROP:test.home@@, etc). Otherwise, it is optional."
  echo ""
  echo "       compare-results-file           - The file to write the comparison results to. Results"
  echo "                                        are always written to the compareModels.log log."
  echo ""
  echo "       java-home                      - The Java Home to use with testing tool. Defaults to the"
  echo "                                        value of the JAVA_HOME environment variable, if not provided."
  echo ""
  echo "       wlst-path                      - The Oracle Home subdirectory of the wlst.sh"
  echo "                                        script to use (e.g., ^<ORACLE_HOME^>/soa)"
  echo ""
}

umask 27

WLSDEPLOY_PROGRAM_NAME="compareModels"; export WLSDEPLOY_PROGRAM_NAME
SCRIPT_NAME=compareModels.sh
ENTRY_POINT_MODULE=compare_models.py

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
        -expected_model_file)
        EXPECTED_MODEL_FILE="$2"
        shift
        ;;
        -actual_model_file)
        ACTUAL_MODEL_FILE="$2"
        shift
        ;;
        -compare_results_file)
        shift
        ;;
        -wlst_path)
        WLST_PATH_DIR="$2"
        shift
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

if [ "${EXPECTED_MODEL_FILE}" = "" ]; then
    echo "Required argument EXPECTED_MODEL_FILE not provided" >&2
    usage `basename $0`
    exit 99
elif [ ! -f ${EXPECTED_MODEL_FILE} ]; then
    echo "The specified EXPECTED_MODEL_FILE does not exist: ${EXPECTED_MODEL_FILE}" >&2
    exit 98
fi

if [ "${ACTUAL_MODEL_FILE}" = "" ]; then
    echo "Required argument ACTUAL_MODEL_FILE not provided" >&2
    usage `basename $0`
    exit 99
elif [ ! -f ${ACTUAL_MODEL_FILE} ]; then
    echo "The specified ACTUAL_MODEL_FILE does not exist: ${ACTUAL_MODEL_FILE}" >&2
    exit 98
fi

if [ "${COMPARE_RESULTS_FILE}" != "" ]; then
    COMPARE_RESULTS_FILE_DIR=$(dirname ${COMPARE_RESULT_FILE})
    if [ ! -w $COMPARE_RESULTS_FILE_DIR ]; then 
        echo "$COMPARE_RESULTS_FILE_DIR is not writable!"
        exit 97
    fi
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
elif [ ${RETURN_CODE} -eq 97 ]; then
  echo ""  
  echo "${SCRIPT_NAME} failed due to directory write permissions error" >&2
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
