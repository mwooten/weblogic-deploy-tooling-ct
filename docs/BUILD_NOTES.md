### Special Note About the ```$REPO_DIR/.mvn/maven.config``` File
The ``.zip`` file (e.g. installer) for WDT-CT, needs to contain the ``.py`` files for both ``oracle/weblogic-deploy-tooling`` and ``wercker/weblogic-deploy-tooling-ct``.<p/>
Normally, these ``.py`` files would be placed inside the ``$WDT_HOME/lib/weblogic-deploy-core.jar`` file, and the full path to that would be added to ``sys.path``. Doing that would normally make all the WDT ``.py`` files locatable, but this does not appear to be the case when using WLST. It appears that they must be placed in a directory on the filesystem in order for them to be successfully located, so the build process for ``wercker/weblogic-deploy-tooling-ct`` copies them from an existing local checkout of ``oracle/weblogic-deploy-tooling``, using a relative path specified in a Java System property named ``weblogic-deploy-tooling-project-dir``. That property is typically set in the ``$REPO_DIR/.mvn/maven.config`` file, like so:<p/>
&nbsp;&nbsp;&nbsp;``-Dweblogic-deploy-tooling-project-dir=../../../../github.com/repositories/weblogic-deploy-tooling``</p>

Note that it must be a relative path (not an absolute one), and that it must be relative to the ``$REPO_DIR/installer/src/assembly`` directory, which is where the ``zip.xml`` file is located. The ``$REPO_DIR/pom.xml`` file contains ``maven-enforcer-plugin`` enforcer rules to ensure the ``weblogic-deploy-tooling-project-dir`` Java System property has been set properly, and that it points to a directory containing a ``oracle/weblogic-deploy-tooling`` repo directory.<p/>

- Push does a build
- Pull Request does a system-test

Branch(es): system-test_0.11, release_0.11

Application:
   Name: weblogic-deploy-tooling-ct
   EnvironmentVariables:
      - "CONTAINER_REGISTRY_USERNAME": "mwooten"
      - "CONTAINER_REGISTRY_PASSWORD": "_qM-rZK2o89FS9sN6Rnf"
   Workflow:
      SerialPipelines:
         build:
            Trigger: "Pull request for any branch in oracle/weblogic-deploy-tooling GitHub repo"
            EnvironmentVariables:
               - "IMAGE_ID": "registry.gitlab.com/weblogic-deploy/store/build/maven"
               - "IMAGE_TAG": "3.5.2-jdk-8"
            Box: 
               - id: $IMAGE_ID
               - tag: $IMAGE_TAG
               Steps:
                  name: build-wdt-ct (wercker/maven)
                  name: install-wdt-ct (bash)

         [2] name: run-system-test <<< build [pipeline]
         env_vars: {
            "IMAGE_ID": "registry.gitlab.com/weblogic-deploy/store/sandbox/weblogic:12.1.3",
            "TEST_DEF": "testing/smoke_test/certified/create-smoke-test.json",
            "TEST_DEF_OVERRIDES_FILE": "testing/smoke_test/default-smoke-test-overrides.properties"
         }
         box: ${WERCKER_IMAGE_URI}
            Steps
               name: run-test (bash)
                  |

      Parallel Pipelines
         name: compare-topology-section
            Steps
               name: get-default-values

         name: compare-resources-section
            Steps
               name: get-default-values

         name: compare-app-deployments-section
            Steps
               name: get-default-values

