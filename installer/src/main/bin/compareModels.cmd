@ECHO OFF

@rem **************************************************************************
@rem compareModels.cmd
@rem
@rem Copyright (c) 2017, 2018, Oracle and/or its affiliates. All rights reserved.
@rem The Universal Permissive License (UPL), Version 1.0
@rem
@rem     NAME
@rem       compareModels.cmd - Script for comparing two domain model files, which
@rem                           have already been run through the validate component 
@rem                           of the WLS Deploy Tool.
@rem
@rem     DESCRIPTION
@rem       This script runs a Python script in WebLogic WLST, which compares the
@rem       sections, folders and attributes of one domain model file, to another
@rem       domain model file. The first domain model file is referred to as the "expected"
@rem       domain model, while the latter is referred to as the "actual" domain model.
@rem
@rem This script uses the following command-line arguments directly. The remaining
@rem arguments are passed down to the underlying python program:
@rem
@rem     - -oracle_home                    The directory of the existing Oracle Home to use when
@rem                                       running the underlying python program.
@rem
@rem                                       The Oracle Home directory must exist and it is the
@rem                                       caller^'s responsibility to verify that it does. This
@rem                                       argument is required.
@rem
@rem     - -expected_model_file            The .yaml/.json file to use for the "expected" domain
@rem                                       model. This argument is required.
@rem
@rem     - -actual_model_file              The .yaml/.json file to use for the "actual" domain
@rem                                       model. This argument is required.
@rem
@rem     - -expected_model_overrides_file  A properties file containing the properties to use for
@rem                                       variables specified in values, in expected_model_file.
@rem
@rem                                       NOTE: This argument is required, if expected_model_file contains
@rem                                             variable expressions (e.g. @@PROP:settings-0.domain_name@@,
@rem                                             @@PROP:test.home@@, etc). Otherwise, it is optional.
@rem
@rem     - -actual_model_overrides_file    A properties file containing the properties to use for
@rem                                       variables specified in values, in actual_model_file.
@rem
@rem                                       NOTE: This argument is required, if expected_model_file contains
@rem                                             variable expressions (e.g. @@PROP:settings-0.domain_name@@,
@rem                                             @@PROP:test.home@@, etc). Otherwise, it is optional.
@rem
@rem     - -compare_results_file           The file to write the comparison results to. Results
@rem                                       are always written to the compareModels.log log, so
@rem                                       this argument is optional.
@rem
@rem     - -wlst_path                      The path to the Oracle Home product directory where the
@rem                                       wlst.cmd script is located. This argument is only needed
@rem                                       for pre-12.2.1 upper stack products like SOA.
@rem
@rem                                         For example, with SOA 12.1.3, -wlst_path should be
@rem                                         specified as %ORACLE_HOME%\soa
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

SET WLSDEPLOY_PROGRAM_NAME=compareModels
SET ENTRY_POINT_MODULE=compare_models.py
SET SCRIPT_NAME=compareModels.cmd
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
SET EXPECTED_MODEL_FILE=
SET ACTUAL_MODEL_FILE=
SET COMPARE_RESULTS_FILE=
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
IF "%1" == "-expected_model_file" (
  SET EXPECTED_MODEL_FILE=%2
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-actual_model_file" (
  SET ACTUAL_MODEL_FILE=%2
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-compare_results_file" (
  SET COMPARE_RESULTS_FILE=%2
  SHIFT
  GOTO arg_continue
)
IF "%1" == "-wlst_path" (
  SHIFT
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
IF "%EXPECTED_MODEL_FILE%" == "" (
  ECHO Required argument EXPECTED_MODEL_FILE not provided >&2
  SET RETURN_CODE=99
  GOTO usage
)
IF "%ACTUAL_MODEL_FILE%" == "" (
  ECHO Required argument ACTUAL_MODEL_FILE not provided >&2
  SET RETURN_CODE=99
  GOTO usage
)
IF NOT "%COMPARE_RESULTS_FILE%" == "" (
  FOR %%F in (%COMPARE_RESULTS_FILE%) do set dirname=%%~dpF
  copy /Y NUL "%dirname%\.writable" > NUL 2>&1 && set WRITEOK=1
  IF NOT DEFINED WRITEOK (
    SET RETURN_CODE=97
    GOTO set_return_code
  )
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

:set_return_code
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
IF "%RETURN_CODE%" == "97" (
  ECHO.
  ECHO %SCRIPT_NAME% failed due to directory write permissions error >&2
  ECHO Directory portion of %COMPARE_RESULTS_FILE% is not writable >&2
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
ECHO              -expected_model_file ^<expected-model-file^>
ECHO              -actual_model_file ^<actual-model-file^>
ECHO              [-expected_model_overrides_file ^<expected-model-overrides-file^>]
ECHO              [-actual_model_overrides_file ^<actual-model-overrides-file^>]
ECHO              [-compare_results_file ^<compare-results-file^>]
ECHO              [-java_home ^<java-home^>]
ECHO              [-wlst_path ^<wlst-path^>]
ECHO.
ECHO     where:
ECHO         oracle-home                    - The existing Oracle Home directory for the domain
ECHO.
ECHO         expected-model-file            - The .yaml/.json file to use for the "expected" domain
ECHO                                          model.
ECHO.
ECHO         actual-model-file              - The .yaml/.json file to use for the "actual" domain
ECHO                                          model.
ECHO.
ECHO         expected-model-overrides-file  - A properties file containing the properties to use for
ECHO                                          variables specified in values, in expected-model-file.
ECHO.
ECHO                                          NOTE: This argument is required, if expected-model-file contains
ECHO                                                variable expressions (e.g. @@PROP:settings-0.domain_name@@,
ECHO                                                @@PROP:test.home@@, etc). Otherwise, it is optional.
ECHO.
ECHO         actual-model-overrides-file    - A properties file containing the properties to use for
ECHO                                          variables specified in values, in actual-model-file.
ECHO.
ECHO                                          NOTE: This argument is required, if expected-model-file contains
ECHO                                                variable expressions (e.g. @@PROP:settings-0.domain_name@@,
ECHO                                                @@PROP:test.home@@, etc). Otherwise, it is optional.
ECHO.
ECHO         compare-results-file           - The file to write the comparison results to. Results
ECHO                                          are always written to the compareModels.log log.
ECHO.
ECHO         java-home                      - the Java Home to use with testing tool. Defaults to the
ECHO                                          value of the JAVA_HOME environment variable, if not provided.
ECHO.
ECHO         wlst-path                      - the Oracle Home subdirectory of the wlst.cmd
ECHO                                          script to use (e.g., ^<ORACLE_HOME^>\soa)
ECHO.

:exit_script
IF DEFINED USE_CMD_EXIT (
  EXIT %RETURN_CODE%
) ELSE (
  EXIT /B %RETURN_CODE%
)

ENDLOCAL
