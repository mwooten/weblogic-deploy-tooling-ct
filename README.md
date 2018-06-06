![Alt text](images/oracle_wdt_200x90.jpg?raw=true "")
# Oracle WebLogic Server Deploy Tooling - Continuous Testing (CT)
This README.md serves as temporary documentation for the WebLogic Deploy Tooling-Continuous Testing (WDT-CT) project. It is targeted at developers, and covers all the topics you need to be aware of when building and installing it, plus how to run the smoke tests that are included in the WDT-CT installer ``.zip`` file.

## What is the WDT-CT?
The WDT-CT is essentially an extension of the WDT, which provides the functionality for creating and running different types of tests (e.g. smoke, system, integration, regression, what-if, etc.) on the WDT components (create, discover, deploy).<p/>
As implied by its name, the WDT-CT is an approach for doing continuous testing on the components of the WDT.<p/>

### How it Differs from the A2C System Tester
The WDT-CT differs from the system tests subsystem for testing the A2C components, in several ways:<p/>
1. It is mostly written in Python as opposed to Java, and runs on the Python/Jython interpreter used for running WLST scripts. 
2. It only uses Maven to create the WDT-CT installer ``.zip`` file.
3. It uses metadata models (metamodels) to define the test definition types (e.g. smoke, system, integration, etc.). These metamodels govern the settings and stages (e.g. discrete actions) used for a given test definition type.
4. It uses Wercker to orchestrate the steps for a test. How it does this will be described in detail, later in this document.

placeholder-paragraph
### How it is Similar to the A2C System Tester
The WDT-CT provides a ``system-test`` test definition type for creating A2C-style system tests, like ``singleApplicationTest``. The key difference is that there is no need for a Java or Python class named ``singleApplicationTest``, because the test definition file contains all the data (or pointers to it) needed to run the test. This includes ENVVAR aliases, source and target domain settings, as well as ``@@PROP:xxx@@`` expressions for substitution variables defined in an overrides ``.properties`` file.<p/>
The similarities are in what happens when a test is run using the ``singleApplicationTest[.json|.yml]`` test definition file:
1. placeholder-item
2. placeholder-item
3. placeholder-item

placeholder-paragraph

## Source Repository
The source code and test definition files used in the WDT-CT project, are in the following private GitHub  repository:

&nbsp;&nbsp;&nbsp;https://github.com/wercker/weblogic-deploy-tooling-ct

If you don't have access to it, please send an e-mail to [Derek Sharpe](mailto:derek.sharpe@oracle.com) requesting access.

## Build-Time Dependencies
As mentioned earlier, the WDT-CT is an extension of the WDT. 

``com.oracle.weblogic.lifecycle:weblogic-deploy-core`` is the Maven identifier for WDT, so at build-time, WDT-CT uses ``com.oracle.weblogic.lifecycle:weblogic-deploy-core:[0.10)`` in the applicable ``<dependency>`` elements of it's ``pom.xml`` files. This works fine for compiling the Java code, but assembling the installer zip requires that the actual ``.py`` files from that Maven identifier, be included as part of the zip. This means that the WDT-CT installer ``.zip`` file contains everything needed to install and run the WDT-CT, as well as the WDT.

Doing a ``mvn clean install`` inside the WDT-CT's project directory, should result in the following installer ``.zip`` file being generated:<p/>
&nbsp;&nbsp;&nbsp;```$REPO_DIR/installer/target/weblogic-deploy-tooling-ct-installer.zip```<p/>
Again, that installer ``.zip`` file includes all the files you'd find in the WDT installer ``.zip``, plus the ones for the WDT-CT.

## Run-Time Dependencies
The ``weblogic-deploy-tooling-ct-installer.zip`` contains the ``weblogic-deploy-core.jar`` and ``weblogic-deploy-tooling-ct-core.jar`` files, in the ``lib`` directory. Both are added to the ``CLASSPATH`` environment variable used when running WLST, so it is able to resolve all run-time references to Java classes and resources inside those two ``.jar`` files. The ``.py`` files are not in those two ``.jar`` files, so WLST must read them from the ``$INSTALL_DIR/lib/python`` directory.  

See ["Special Note About the $REPO_DIR/.mvn/config"](docs/BUILD_NOTES.md) for specifics.

## Building the ``weblogic-deploy-tooling-ct.zip`` Installer
You need to have Apache Maven 3.3+ installed in order to build the installer ``.zip`` for the WDT-CT. Afterwards, just open a command prompt, change directory to where you did the ``git checkout`` to, and type in the following:<p/>

&nbsp;&nbsp;&nbsp;``mvn clean install``<p/>

This should result in the ``$REPO_DIR/installer/target/weblogic-deploy-tooling-ct-installer.zip`` file being generated. 

## Installing the WDT-CT
To install the WDT-CT, you just need to unzip the ``weblogic-deploy-tooling-ct-installer.zip`` file into a directory, **_on a host where Oracle WebLogic Server is already installed_**. This host can be a local machine, local VM, docker image or an OCI compute instance.<p/>
WDT-CT runs on the Python/Jython interpreter that comes with that Oracle WebLogic Server install, so the WDT-CT will need to be told the values of the following environment variables, from that:<p/>
<table style="width=80%">
 <col style="width=20%"/>
 <col style="width=60%"/>
 <tr>
   <th>OS Env Variable</th>
   <th>Remarks</th>
 </tr>
 <tr>
   <td style="align:left">ORACLE_HOME</td>
   <td style="align:left">If the host is a docker image, you can use a <code>docker inspect</code> command to get the value from the docker images <code>.Config.Env</code> area. There is a <code>get-docker-config-info.sh</code> shell script in the <a href="https://gitlab.com/weblogic-deploy/weblogic-deploy-tooling-docker/blob/master/installer/src/main/get-docker-config-info.sh">weblogic-deploy-tooling-docker</a> project, which contains a function to get the value of <code>ORACLE_HOME</code> from this <code>.Config.Env</code> area.</td>
 </tr>
 <tr>
   <td style="align:left">JAVA_HOME</td>
   <td style="align:left">If the host is a docker image, you can use a <code>docker inspect</code> command to get the value from the docker images <code>.Config.Env</code> area. There is a <code>get-docker-config-info.sh</code> shell script in the <a href="https://gitlab.com/weblogic-deploy/weblogic-deploy-tooling-docker/blob/master/installer/src/main/get-docker-config-info.sh">weblogic-deploy-tooling-docker</a> project, which contains a function to get the value of <code>JAVA_HOME</code> from this <code>.Config.Env</code> area.</td>
 </tr>
</table>
<p/>


## So What Exactly Does the WDT-CT Do?
The WDT-CT is used to perform an aspect of DevOps referred to as <i>continuous testing</i>. Continuous testing is an activity that plays a key role in achieving continuous integration, which is another aspect of DevOps.<p/>
As the name implies, continuous testing is an activity that involves performing tests on a code base, to ensure it is ready to be used to create a release...at anytime...not just at the end of a sprint.<p/>
The test being performed are generally triggered by an event in the code repository, like a <code>push</code> or <code>pull request</code>. When this occurs, a web hook configured in the repository triggers some type of technology that can manage the execution of the test, and report the test results.<p/>
The following table presents the technologies used to implement the WDT-CT, and the role each plays:<p/>
<table style="width=80%">
 <col style="width=20%"/>
 <col style="width=60%"/>
 <tr>
   <th>Technology</th>
   <th>Remarks</th>
 </tr>
 <tr>
   <td style="align:left">Docker</td>
   <td style="align:left"><p>The Oracle WebLogic Server installs that are used when running a test, are containers created from docker images. These docker containers provide the execution environment for the tests.<p/>
   <p>They are built and managed by members of the WDT development team, and stored in a private container registry on GitLab.</p>
 </tr>
 <tr>
   <td style="align:left">Git Hub</td>
   <td style="align:left"><p>For the WDT-CT, the code repository is <code>oracle/weblogic-deploy-tooling</code> at GitHub. It has a web hook that triggers a Wercker application whenever a <code>pull request</code> occurs, and the pipelines of this application orchestrate the running of the test.</p>
 </tr>
 <tr>
   <td style="align:left">Wercker</td>
   <td style="align:left"><p>The GitHub web hooks trigger Wercker pipelines, which have steps to:</p>
   <ol>
   <li><p>Perform a Maven build on the WDT.</p></li>
   <li><p>Perform a Maven build on the WDT-CT.</p></li>
   <li><p>Run a <code>docker build</code> to install the WDT-CT into one or more docker images.</p></li>
   <li><p>Invoke the <code>$WDTCT_HOME/bin/runTest.sh</code> shell script, passing in information about the test to run.</p></li>
   </ol></td>
 </tr>
 <tr>
   <td style="align:left">Hudson</td>
   <td style="align:left">placeholder-paragraph</td>
 </tr>
</table>
<p/>

## Running a WDT-CT Test
Once the WDT-CT is installed, you can execute a &quot;smoke test&quot; to ensure it is ready to be used, from a Wercker pipeline step. You'll find the smoke tests in the following directory:<p/>
&nbsp;&nbsp;&nbsp;``$WDTCT_HOME/testing/smoke_tests/certified``<p/>
The default overrides file for all the smoke tests is in the directory above that:<p/>
&nbsp;&nbsp;&nbsp;``$WDTCT_HOME/testing/smoke_tests/default-smoke-test-overrides.properties``<p/>
Edit the values assigned to entries in that file, to match where Oracle WebLogic Server and the JDK are installed. The OOTB smoke test test definition files use this properties file, so pay careful attention to where you say things are. Once you've finished editing and saving the file, you should be ready to run a smoke test.<p/>
<table style="border:0;width=50%">
<tr>
  <td style="width:10%;valign:top;">IMPORTANT:<p/></td>
  <td style="width:40%"><p>Remember to change the paths for the model, archive or variable files cited in the <code>$WDTCT_HOME/testing/smoke_tests/default-smoke-test-overrides.properties</code> file. Those files are not in the WDT installer <code>.zip</code> file, but are referenced in that overrides file.</td>
</tr>
</table>

Let's start by opening a terminal and running a smoke test using the ``create-smoke-test.json`` test definition file:<p/>

```
$ WDTCT_HOME=<path to where you unzipped the installer.zip>
$ cd $WDTCT_HOME
$ bin/runTest.sh -test_type system-test -test_def_file testing/smoke_test/certified/create-smoke-test.json -test_def_overrides_file testing/smoke_test/default-smoke-test-overrides.properties -oracle_home <path to where Oracle WebLogic Server is installed>
```
The smoke test will send output to the terminal, and create log files in the ``$WDTCT_HOME/logs`` directory. 

### The ``$WDTCT_HOME/bin/runTest[.cmd|.sh]`` Script
The ``$WDTCT_HOME/bin/runTest[.cmd|.sh]`` script is the executable used to run a WDT-CT test. It supports the following command-line options:
<table style="width=60%">
 <col style="width=10%"/>
 <col style="width=50%"/>
 <tr>
   <th>Command-Line Option</th>
   <th>Remarks</th>
 </tr>
 <tr>
   <td style="align:left"><code>-oracle_home</code></td>
    <p>This is the directory where Oracle WebLogic Server has been installed. It is a required option.</p>
 </tr>
 <tr>
   <td style="align:left"><code>-test_type</code></td>
    <p>This identifies the "type" of test to run. Specify one of the following as the option value:<p/>
    <ul>
    <li><code>smoke-test</code></li>
    <li><code>system-test</code></li>
    <li><code>integration-test</code></li>
    </ul>
    <p>This is a required option.</p>
    <p><b>NOTE:</b> This WIP release is only implementing the functionality associated with the <code>smoke-test</code> and <code>system-test</code> choices.</p>
 </tr>
 <tr>
   <td style="align:left"><code>-test_def_file</code></td>
    <p>This is the path to the test definition file to use for the test. It is a required option.</p>
 </tr>
 <tr>
   <td style="align:left"><code>-test_def_overrides_file</code></td>
    <p>This is the path to a <code>.properties</code> file that contains property names used in <code>test_def_file</code>. It is only required if <code>test_def_file</code> contains <code>@@PROP:xxx@@</code> expressions.</p>
 </tr>
 <tr>
   <td style="align:left"><code>-test_def_verifier_name</code></td>
    <p>This is the name of a test definition file verifier to use. A verifier ensures that <code>test_def_file</code> conforms to the test definition metadata file associated with it. If not present, a built-in verifier will be is used.</p>
    <p><b>NOTE:</b> This WIP release will only be using the built-in verifier.</p>
 </tr>
 <tr>
   <td style="align:left"><code>-test_def_metadata_file</code></td>
    <p>This is the path to a test definition metadata file to associate with the <code>test_def_file</code> file. If not present, the test definition metadata file inside <code>$WDTCT_HOME/lib/weblogic-deploy-tooling-ct-core.jar</code> file will be used.</p>
 </tr>
 <tr>
   <td style="align:left"><code>-verify_only</code></td>
    <p>Flag indicating to only perform the test definition verification step(s). If not present, the verification and test steps will be performed.</p>
 </tr>
</table>
<p/>

### The Test Definition File (``test_def``)
placeholder-paragraph

### The Test Definition Metadata File (``test_def_metadata``)
placeholder-paragraph

### The Test Definition Overrides File (``test_def_overrides``)
placeholder-paragraph

### The Test Orchestration File (``wercker.yml``)
placeholder-paragraph

//TODO: Continue working on this README.md, after we get more of the Wercker pieces in place and able to run a smoke test.
