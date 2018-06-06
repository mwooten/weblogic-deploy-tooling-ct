@ECHO OFF
@rem **************************************************************************
@rem runTest.cmd
@rem
@rem Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
@rem The Universal Permissive License (UPL), Version 1.0
@rem
@rem     NAME
@rem       runTest.cmd - Script for running different types of test, on the components
@rem                     of the WLS Deploy tool
@rem                           
@rem
@rem     DESCRIPTION
@rem       This script uses WebLogic MBeans and WLST to run certified and user-defined
@rem       test types, on the components of the WLS Deploy tool.
@rem
@rem
@rem This script uses the following command-line arguments directly. The remaining
@rem arguments are passed down to the underlying python program:
@rem
@rem     - -oracle_home                 The directory of the existing Oracle Home to use when
@rem                                    running the underlying python program, not the one to
@rem                                    use when running the test. That Oracle Home
@rem                                    is specified inside the test definition file.
@rem
@rem                                    The Oracle Home directory must exist and it is the
@rem                                    caller^'s responsibility to verify that it does. This
@rem                                    argument is required.
@rem
@rem     - -test_type                   The type of test to run. This argument is required.
@rem                                    The currently supported types are:
@rem
@rem                                        smoke-test
@rem                                        integration-test
@rem                                        system-test
@rem
@rem     - -test_def_file               The JSON file containing the definition of the
@rem                                    test to run. This argument is required.
@rem
@rem     - -test_def_overrides_file     A properties file containing the properties to use for
@rem                                    variables specified in values, in the test_def_file.
@rem                                    This argument is required, if test_def_file contains
@rem                                    variable expressions (e.g. @@PROP:settings-0.domain_name@@,
@rem                                    @@PROP:test.home@@, etc). Otherwise, it is optional.
@rem
@rem     - -test_def_verifier_name      Optional name of the verification test to use when
@rem                                    verifying the test. Will use the default
@rem                                    built-in verification test, if not provided.
@rem
@rem     - -test_def_metadata_file      Optional name of the metadata file to use with the
@rem                                    test_def_file. If not provided, the metadata file
@rem                                    inside the installer's archive will be used. Passing it
@rem                                    as a command line option is more efficient and provides
@rem                                    a greater degree of flexibility. It removes the need to
@rem                                    recreate a new installer archive, every time you need to
@rem                                    make a change to the metadata.
@rem
@rem     - -wlst_path                   The path to the Oracle Home product directory where the
@rem                                    wlst.cmd script is located. This argument is only needed
@rem                                    for pre-12.2.1 upper stack products like SOA.
@rem
@rem                                      For example, with SOA 12.1.3, -wlst_path should be
@rem                                      specified as %ORACLE_HOME%\soa
@rem
@rem     - -verify_only                 Flag indicating to only perform test verification steps.
@rem                                    This argument is optional and has no value.
@rem
@rem This script uses the following environment variables:
@rem
@rem JAVA_HOME             - The location of the JDK to use when running the underlying 
@rem                         python program, not the one to use when running the integration
@rem                         test. That JDK is specified inside the test definition file.
@rem
@rem                         If provided, the caller must set the JAVA_HOME variable to the
@rem                         home directory of a valid Java 7 (or later) JDK.
@rem
@rem WLSDEPLOY_HOME        - The location of the WLS Deploy installation. If it is set,
@rem                         it will be honored, provided it is an existing directory. 
@rem                         Otherwise, the location will be calculated using the location
@rem                         of this script.
@rem                         
@rem WLSDEPLOY_PROPERTIES  - Extra system properties to pass to WLST. The caller can use
@rem                         this environment variable to add additional system properties
@rem                         to the the WLST environment.
@rem

SETLOCAL

SET WLSDEPLOY_PROGRAM_NAME=runTest
SET ENTRY_POINT_MODULE=run_test.py
SET SCRIPT_NAME=runTest.cmd
SET SCRIPT_PATH=%~dp0
FOR %%i IN ("%SCRIPT_PATH%") DO SET SCRIPT_PATH=%%~fsi
IF %SCRIPT_PATH:~-1%==\ SET SCRIPT_PATH=%SCRIPT_PATH:~0,-1%

IF NOT DEFINED WLSDEPLOY_HOME (
  SET WLSDEPLOY_HOME=%SCRIPT_PATH%\..
) ELSE (
  IF NOT EXIST "%WLSDEPLOY_HOME%" (
    ECHO Specified WLSDEPLOY_HOME of "%WLSDEPLOY_HOME%" does not exist >&2
    SET RETURN_CODE=2
    GOTO exit_script
  )
)
FOR %%i IN ("%WLSDEPLOY_HOME%") DO SET WLSDEPLOY_HOME=%%~fsi
IF %WLSDEPLOY_HOME:~-1%==\ SET WLSDEPLOY_HOME=%WLSDEPLOY_HOME:~0,-1%

SET WLSDEPLOY_INSTALL_JARS=^
%WLSDEPLOY_HOME%\lib\weblogic-deploy-core.jar;^
%WLSDEPLOY_HOME%\lib\weblogic-deploy-tooling-ct-core.jar

@rem
@rem Check to see if no args were given and print the usage message
@rem
IF "%~1" == "" (
  SET RETURN_CODE=0
  GOTO usage
)

@rem
@rem Find the args required to determine the WLST script to run
@rem

SET ORACLE_HOME=
SET TEST_TYPE=
SET TEST_DEF_FILE=
SET WLST_PATH_DIR=
SET MIN_JDK_VERSION=7

:arg_loop
IF "%1" == "-help" (
  SET RETURN_CODE=0
  GOTO usage
)
IF "%1" == "-java_home" (
  SET JAVA_HOME=%2
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-oracle_home" (
  SET ORACLE_HOME=%2
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-test_type" (
  SET TEST_TYPE=%2
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-test_def_file" (
  SET TEST_DEF_FILE=%2
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-test_def_overrides_file" (
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-test_def_verifier_name" (
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-test_def_metadata_file" (
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-wlst_path" (
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-verify_only" (
  GOTO arg_continue
)
@REM If none of the above, unknown argument so skip it
:arg_continue
SHIFT
IF NOT "%~1" == "" (
  GOTO arg_loop
)

@rem
@rem Make sure that the JAVA_HOME environment variable is set to point to a
@rem JDK 7 or higher JVM (and that it isn't OpenJDK).
@rem
IF NOT DEFINED JAVA_HOME (
  ECHO Please set the JAVA_HOME environment variable to point to a Java 7 installation >&2
  SET RETURN_CODE=2
  GOTO exit_script
) ELSE (
  IF NOT EXIST "%JAVA_HOME%" (
    ECHO Your JAVA_HOME environment variable to points to a non-existent directory: %JAVA_HOME% >&2
    SET RETURN_CODE=2
    GOTO exit_script
  )
)
FOR %%i IN ("%JAVA_HOME%") DO SET JAVA_HOME=%%~fsi
IF %JAVA_HOME:~-1%==\ SET JAVA_HOME=%JAVA_HOME:~0,-1%

IF EXIST %JAVA_HOME%\bin\java.exe (
  FOR %%i IN ("%JAVA_HOME%\bin\java.exe") DO SET JAVA_EXE=%%~fsi
) ELSE (
  ECHO Java executable does not exist at %JAVA_HOME%\bin\java.exe does not exist >&2
  SET RETURN_CODE=2
  GOTO exit_script
)

FOR /F %%i IN ('%JAVA_EXE% -version 2^>^&1') DO (
  IF "%%i" == "OpenJDK" (
    ECHO JAVA_HOME %JAVA_HOME% contains OpenJDK^, which is not supported >&2
    SET RETURN_CODE=2
    GOTO exit_script
  )
)

@rem
@rem Check for values of required arguments for this script to continue.
@rem The underlying WLST script has other required arguments.
@rem
IF "%ORACLE_HOME%" == "" (
  ECHO Required argument ORACLE_HOME not provided >&2
  SET RETURN_CODE=99
  GOTO usage
)
IF "%TEST_TYPE%" == "" (
  ECHO Required argument TEST_TYPE not provided >&2
  SET RETURN_CODE=99
  GOTO usage
)
IF "%TEST_DEF_FILE%" == "" (
  ECHO Required argument TEST_DEF_FILE not provided >&2
  SET RETURN_CODE=99
  GOTO usage
)

@rem
@rem If the WLST_PATH_DIR is specified, validate that it contains the wlst.cmd script
@rem
IF DEFINED WLST_PATH_DIR (
  FOR %%i IN ("%WLST_PATH_DIR%") DO SET WLST_PATH_DIR=%%~fsi
  IF NOT EXIST "%WLST_PATH_DIR%" (
    ECHO WLST_PATH_DIR specified does not exist: %WLST_PATH_DIR% >&2
    SET RETURN_CODE=98
    GOTO exit_script
  )
  set "WLST=%WLST_PATH_DIR%\common\bin\wlst.cmd"
  IF NOT EXIST "%WLST%" (
    ECHO WLST executable %WLST% not found under specified WLST_PATH_DIR %WLST_PATH_DIR% >&2
    SET RETURN_CODE=98
    GOTO exit_script
  )
  SET CLASSPATH=%WLSDEPLOY_INSTALL_JARS%
  SET WLST_EXT_CLASSPATH=%WLSDEPLOY_INSTALL_JARS%
  GOTO found_wlst
)

@rem
@rem Find the location for wlst.cmd
@rem
SET WLST=
SET USE_JRF_WLST=FALSE
IF DEFINED DOMAIN_TYPE (
  IF "%DOMAIN_TYPE%" == "WLS" (
    SET USE_JRF_WLST=FALSE
    GOTO domain_type_recognized
  )
  IF "%DOMAIN_TYPE%" == "RestrictedJRF" (
    SET USE_JRF_WLST=TRUE
    GOTO domain_type_recognized
  )
  IF "%DOMAIN_TYPE%" == "JRF" (
    SET USE_JRF_WLST=TRUE
    GOTO domain_type_recognized
  )
  ECHO Domain type %DOMAIN_TYPE% not recognized by shell script...assuming JRF is required
  SET USE_JRF_WLST=TRUE
)

:domain_type_recognized
IF "%USE_JRF_WLST%" == "TRUE" (
    IF EXIST "%ORACLE_HOME%\oracle_common\common\bin\wlst.cmd" (
        SET WLST=%ORACLE_HOME%\oracle_common\common\bin\wlst.cmd
        SET CLASSPATH=%WLSDEPLOY_INSTALL_JARS%;%ORACLE_HOME%\wlserver\server\lib\wljmxclient.jar
        SET WLST_EXT_CLASSPATH=%WLSDEPLOY_INSTALL_JARS%
        GOTO found_wlst
    )
) ELSE (
    IF EXIST "%ORACLE_HOME%\wlserver_10.3\common\bin\wlst.cmd" (
        SET WLST=%ORACLE_HOME%\wlserver_10.3\common\bin\wlst.cmd
        SET CLASSPATH=%WLSDEPLOY_INSTALL_JARS%;%ORACLE_HOME%\wlserver_10.3\server\lib\wljmxclient.jar
        GOTO found_wlst
    )
    IF EXIST "%ORACLE_HOME%\wlserver_12.1\common\bin\wlst.cmd" (
        SET WLST=%ORACLE_HOME%\wlserver_12.1\common\bin\wlst.cmd
        SET CLASSPATH=%WLSDEPLOY_INSTALL_JARS%;;%ORACLE_HOME%\wlserver_12.1\server\lib\wljmxclient.jar

        GOTO found_wlst
    )
    IF EXIST "%ORACLE_HOME%\wlserver\common\bin\wlst.cmd" (
        IF EXIST "%ORACLE_HOME%\wlserver\.product.properties" (
            @rem WLS 12.1.2 or WLS 12.1.3
            SET WLST=%ORACLE_HOME%\wlserver\common\bin\wlst.cmd
            SET CLASSPATH=%WLSDEPLOY_INSTALL_JARS%;%ORACLE_HOME%\wlserver\server\lib\wljmxclient.jar
        ) ELSE (
            @rem WLS 12.2.1+
            SET WLST=%ORACLE_HOME%\oracle_common\common\bin\wlst.cmd
            SET WLST_EXT_CLASSPATH=%WLSDEPLOY_INSTALL_JARS%
        )
        GOTO found_wlst
    )
)

IF NOT EXIST "%WLST%" (
  ECHO Unable to locate wlst.cmd script in ORACLE_HOME %ORACLE_HOME% >&2
  SET RETURN_CODE=98
  GOTO exit_script
)
:found_wlst

SET LOG_CONFIG_CLASS=oracle.weblogic.deploy.logging.WLSDeployLoggingConfig
SET WLST_PROPERTIES=-Dcom.oracle.cie.script.throwException=true
SET "WLST_PROPERTIES=-Djava.util.logging.config.class=%LOG_CONFIG_CLASS% %WLST_PROPERTIES%"
SET "WLST_PROPERTIES=%WLST_PROPERTIES% %WLSDEPLOY_PROPERTIES%"
SET WLST_ARGS=-skipWLSModuleScanning

IF NOT DEFINED WLSDEPLOY_LOG_PROPERTIES (
  SET WLSDEPLOY_LOG_PROPERTIES=%WLSDEPLOY_HOME%\etc\logging.properties
)
IF NOT DEFINED WLSDEPLOY_LOG_DIRECTORY (
  SET WLSDEPLOY_LOG_DIRECTORY=%WLSDEPLOY_HOME%\logs
)

ECHO JAVA_HOME = %JAVA_HOME%
ECHO WLST_EXT_CLASSPATH = %WLST_EXT_CLASSPATH%
ECHO CLASSPATH = %CLASSPATH%
ECHO WLST_PROPERTIES = %WLST_PROPERTIES%
ECHO WLST_ARGS = %WLST_ARGS%

SET PY_SCRIPTS_PATH=%WLSDEPLOY_HOME%\lib\python
ECHO %WLST% %WLST_ARGS% %PY_SCRIPTS_PATH%\%ENTRY_POINT_MODULE% %*

"%WLST%" %WLST_ARGS% "%PY_SCRIPTS_PATH%\%ENTRY_POINT_MODULE%" %*

SET RETURN_CODE=%ERRORLEVEL%
IF "%RETURN_CODE%" == "100" (
  GOTO usage
)
IF "%RETURN_CODE%" == "99" (
  GOTO usage
)
IF "%RETURN_CODE%" == "98" (
  ECHO.
  ECHO %SCRIPT_NAME% failed due to a parameter validation error >&2
  GOTO exit_script
)
IF "%RETURN_CODE%" == "2" (
  ECHO.
  ECHO %SCRIPT_NAME% failed ^(exit code = %RETURN_CODE%^)
  GOTO exit_script
)
IF "%RETURN_CODE%" == "1" (
  ECHO.
  ECHO %SCRIPT_NAME% completed but with some issues ^(exit code = %RETURN_CODE%^) >&2
  GOTO exit_script
)
IF "%RETURN_CODE%" == "0" (
  ECHO.
  ECHO %SCRIPT_NAME% completed successfully ^(exit code = %RETURN_CODE%^)
  GOTO exit_script
)
@rem Unexpected return code so just print the message and exit...
ECHO.
ECHO %SCRIPT_NAME% failed ^(exit code = %RETURN_CODE%^) >&2
GOTO exit_script

:usage
ECHO.
ECHO Usage: %~nx0 [-help]
ECHO              -oracle_home ^<oracle-home^>
ECHO              -test_type ^<test-type^>
ECHO              -test_def_file ^<test-def-file^>
ECHO              [-test_def_overrides_file ^<test-def-overrides-file^>]
ECHO              [-test_def_verifier_name ^<verification-test-name^>]
ECHO              [-test_def_metadata_file ^<test-def-metadata-file^>]
ECHO              [-java_home ^<java-home^>]
ECHO              [-wlst_path ^<wlst-path^>]
ECHO              [-verify_only]
ECHO.
ECHO     where:
ECHO         oracle-home                 - The existing Oracle Home directory for the domain
ECHO.
ECHO         test-type                   - The type of test to run. The currently supported 
ECHO                                       types are:
ECHO.
ECHO                                           smoke-test
ECHO                                           integration-test
ECHO                                           system-test
ECHO.
ECHO         test-def-file               - The test definition file for the test to run.
ECHO.
ECHO         test-def-overrides-file     - A properties file containing the properties to use for
ECHO                                       variables specified in values, in the test-def-file.
ECHO.
ECHO                                       NOTE: This argument is required, if test-def-file contains
ECHO                                             variable expressions (e.g. @@PROP:settings-0.domain_name@@,
ECHO                                             @@PROP:test.home@@, etc). Otherwise, it is optional.
ECHO.
ECHO         test-def-verifier-name      - The name of the verification test to use when verifying the
ECHO                                       test definition file. Defaults to the name of the default
ECHO                                       built-in verification test, if not provided.
ECHO.
ECHO         test-def-metadata-file      - the name of the metadata file to use with the
ECHO                                       test-def-file. If not provided, the metadata file
ECHO                                       inside the installer's archive will be used.
ECHO.
ECHO         java-home                   - the Java Home to use with testing tool. Defaults to the
ECHO                                       value of the JAVA_HOME environment variable, if not provided.
ECHO.
ECHO         wlst-path                   - the Oracle Home subdirectory of the wlst.cmd
ECHO                                       script to use (e.g., ^<ORACLE_HOME^>\soa)
ECHO.
ECHO         verify-only                 - the flag indicating to only perform test verification steps.
ECHO                                       This argument is optional and has no value.

:exit_script
IF DEFINED USE_CMD_EXIT (
  EXIT %RETURN_CODE%
) ELSE (
  EXIT /B %RETURN_CODE%
)

ENDLOCAL
