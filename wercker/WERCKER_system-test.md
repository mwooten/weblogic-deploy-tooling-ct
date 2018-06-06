![Alt text](../images/oracle_wdt_200x90.jpg?raw=true "")
# Using Wercker to Orchestrate WDT-CT System Tests
This document provides details on the role that Wercker plays in the WDT-CT initiative. These details are intentionally tied to how the A2C system tests work, because that is the frame of reference for the initial system testing the WDT-CT will perform.
## Modularization of the ``wercker.yml`` File
The primary artifact for Wercker is the [wercker.yml](wercker.yml) file.
There is just one of these for the entire Wercker application, which is fine for operations, but not really good for designing in a modular way or avoiding merge conflict situations.
Breaking this monolithic file up into meaningfully-named ``.yml`` fragments that Maven can later assembles into a single file, seemed like a manageable way to address both of those concerns.

## Applications
Currently, the Wercker application is under a particular user's wercker account, but ideally we'd probably want it to be under an organization or team.

![Alt text](../images/wdt-ct-wercker-app.PNG?raw=true "")

### Environment Variables
placeholder-paragraph

<table style="width=60%">
 <col style="width=10%"/>
 <col style="width=50%"/>
 <tr>
   <th>Application ENV Variable</th>
   <th>Remarks</th>
 </tr>
</table>
<p/>

### How Will the WDT-CT Wercker Application be Triggered?
Current thinking is that a ``pull request`` in the ``oracle/weblogic-deploy-tooling`` repository, will be the trigger event for starting a WDT-CT system test.

## Workflows
The system test equivalent for a workflow is a ``test_def`` file. That file is essentially "the test" that you want to run.<p/>
For example, the ``single-application-test.json`` test_def file, is functionally equivalent to the  **singleApplicationTest.java** file, in the A2C system test project. But the ``SingleApplicationTest.java`` file extends the ``SystemTestSupport.java``, so the behavior in that is what the workflow needs to implement. 

### Environment Variables
Keeping with the notion that the ``SystemTestSupport.java`` file is the implementation for the workflow. The following table would be the workflow-level environment variables:<p/>

<table style="width=80%">
 <col style="width=20%"/>
 <col style="width=10%"/>
 <col style="width=10%"/>
 <col style="width=40%"/>
 <tr>
   <th>Workflow ENV Variable</th>
   <th>Req'd</th>
   <th>Default</th>
   <th>Description</th>
 </tr>
 <tr>
   <td style="align:left"><code>STDOUT_LOG_POLICY</code></td>
   <td style="align:left">No</td>
   <td style="align:left"><code>both</code></td>
   <td style="align:left"><p>Possible values:</p><ul><li><code>file</code></li><li><code>stdout</code></li><li><code>both</code></li></ul></td>
 </tr>
 <tr>
   <td style="align:left"><code>LOG_DIR</code></td>
   <td style="align:left">No</td>
   <td style="align:left"><code>$[A2C_HOME}/logs</code></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>LOG_PROPERTIES</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>A2C_HOME_PARENT_DIR</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>A2C_HOME</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>A2C_LOG_CONFIG</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>A2C_POST_CLASSPATH</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>JAVA_HOME</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>TEST_AUTOMATION_HOME</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>TEST_SUPPORT_HOME</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>OUTPUT_DIR</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>JAVA7_HOME</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>JAVA8_HOME</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>JAVA9_HOME</code></td>
   <td style="align:left">No</td>
   <td style="align:left">both</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>DOMAIN_PARENT_DIR</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">Base domain parent directory</td>
 </tr>
 <tr>
   <td style="align:left"><code>ANNOTATED_PROV</code></td>
   <td style="align:left">No</td>
   <td style="align:left"></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
</table>
<p/>

## Pipelines
The WDTT initiative equivalent for a pipeline is a ``stage``
<table style="width=100%">
 <col style="width=20%"/>
 <col style="width=80%"/>
 <tr>
   <th>Pipeline</th>
   <th>Description</th>
 </tr>
 <tr>
   <td style="align:left"><a href="compare-model-template.yml">compare-model</a></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><a href="create-domain-template.yml">create-domain</a></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><a href="deploy-apps-template.yml">deploy-apps-domain</a></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><a href="discover-domain-template.yml">discover-domain</a></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><a href="system-test-it-template.yml">system-test-it</a></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><a href="validate-model-template.yml">validate-model</a></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
</table>
<p/>

### Environment Variables
Keeping with the notion that the ``singleApplicationTest`` system test is an example of a _workflow pipeline_, the following table details what the pipeline-level environment variables would be:

<table style="width=80%">
 <col style="width=20%"/>
 <col style="width=10%"/>
 <col style="width=10%"/>
 <col style="width=40%"/>
 <tr>
   <th>Workflow Pipeline ENV Variable</th>
   <th>Required</th>
   <th>Default</th>
   <th>Description</th>
 </tr>
 <tr>
   <td style="align:left"><code>A2C_DEV_TESTING_MODE</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>BUILD_DIR</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">Maven project build directory</td>
 </tr>
 <tr>
   <td style="align:left"><code>SOURCE_DOMAIN_NAME</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>SUPPORTED_VERSIONS</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">List versions the tests supports</td>
 </tr>
 <tr>
   <td style="align:left"><code>TARGET_DOMAIN_NAME</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>TEST_DEF_FILE</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>USER_TESTS_TO_RUN</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
 <tr>
   <td style="align:left"><code>RCU_DB</code></td>
   <td style="align:left">No</td>
   <td style="align:left"></td>
   <td style="align:left">RCU Database connect string</td>
 </tr>
 <tr>
   <td style="align:left"><code>RCU_PREFIX</code></td>
   <td style="align:left">No</td>
   <td style="align:left"></td>
   <td style="align:left">RCU Prefix</td>
 </tr>
 <tr>
   <td style="align:left"><code>RCU_SYS_PWD</code></td>
   <td style="align:left">No</td>
   <td style="align:left"></td>
   <td style="align:left">RCU SYS password</td>
 </tr>
 <tr>
   <td style="align:left"><code>RCU_SCHEMA_PWD</code></td>
   <td style="align:left">No</td>
   <td style="align:left"></td>
   <td style="align:left">RCU Schema password</td>
 </tr>
 <tr>
   <td style="align:left"><code>WAIT_BETWEEN_PHASES_SECS</code></td>
   <td style="align:left">Yes</td>
   <td style="align:left"></td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
</table>
<p/>

