package oracle.weblogic.deploy.testing.defaults;

import java.io.IOException;
import java.io.InputStream;
import java.text.MessageFormat;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Properties;
import java.util.regex.Pattern;

import oracle.weblogic.deploy.testing.logging.WLSDeployTestingLogFactory;
import oracle.weblogic.deploy.testing.logging.PlatformLogger;
import oracle.weblogic.deploy.util.StringUtils;

public class WLSTOfflineDefaultsFactory {
    private static final String CLASS = WLSTOfflineDefaultsFactory.class.getName();
    private static PlatformLogger logger =
            WLSDeployTestingLogFactory.getLogger("wlsdeploy.system_test");

    private static final String PACKAGE_PATH = "defaults";
    private static final String TOPOLOGY_PROPERTIES = PACKAGE_PATH + "/topology-excludes.yml";
    private static final String RESOURCES_PROPERTIES = PACKAGE_PATH + "/resources-excludes.yml";
    private static final String APPDEPLOYMENTS_PROPERTIES = PACKAGE_PATH + "/appDeployments-excludes.yml";
    private static final WLSTOfflineDefaults EMPTY_DEFAULTS = new WLSTOfflineDefaultsImpl("empty");
    private static final String FOLDER_SEPARATOR = ".";
    private static final Pattern TYPE_PATTERN = Pattern.compile("^\\{[a-zA-Z]+\\}[.].+");

    private static Map<String, WLSTOfflineDefaults> defaults = new HashMap<String, WLSTOfflineDefaults>();
    private static WLSTOfflineDefaultsFactory factory = null;

    private WLSTOfflineDefaultsFactory() {
        loadDefaults();
        // hide the default constructor
    }

    public static synchronized WLSTOfflineDefaultsFactory getDefaultsFactory() {
        if (factory  == null) {
            factory = new WLSTOfflineDefaultsFactory();
        }
        return factory;
    }

    public WLSTOfflineDefaults getFolderDefaults(String folderName) {
        final String METHOD = "getFolderDefaults";

        logger.entering(CLASS, METHOD, folderName);
        logDefaults();

        WLSTOfflineDefaults result = defaults.get(folderName);
        if (result == null) {
            result = EMPTY_DEFAULTS;
        }
        logger.exiting(CLASS, METHOD, result);
        return result;
    }

    private static void loadDefaults() {
        Properties topologyProperties = loadDefaultProperties(TOPOLOGY_PROPERTIES);
        Properties resourcesProperties = loadDefaultProperties(RESOURCES_PROPERTIES);
        Properties appDeploymentsProperties = loadDefaultProperties(APPDEPLOYMENTS_PROPERTIES);

        convertPropertiesFileFormat("topology", topologyProperties);
        convertPropertiesFileFormat("resources", resourcesProperties);
        convertPropertiesFileFormat("appDeployments", appDeploymentsProperties);
    }

    private static Properties loadDefaultProperties(String fileName) {
        final String METHOD = "loadDefaultProperties";

        logger.entering(CLASS, METHOD, fileName);
        Properties result = new Properties();
        InputStream inputStream = null;
        try {
            inputStream = WLSTOfflineDefaultsFactory.class.getClassLoader().getResourceAsStream(fileName);
            if (inputStream == null) {
                String message = MessageFormat.format("Failed to get InputStream for property file {0}", fileName);
                throw new IllegalStateException(message);
            }
            result.load(inputStream);
        } catch (IOException ioe) {
            String message = MessageFormat.format("Failed to load property file {0}: {1}", fileName, ioe.getMessage());
            throw new IllegalStateException(message, ioe);
        } finally {
            if (inputStream != null) {
                try { inputStream.close(); } catch (IOException ignore) { }
            }
        }
        logger.exiting(CLASS, METHOD, result);
        return result;
    }

    private static void convertPropertiesFileFormat(String rootName, Properties data) {
        final String METHOD = "convertPropertiesFileFormat";

        logger.entering(CLASS, METHOD, rootName, data);
        if (data != null) {
            for (String key : data.stringPropertyNames()) {
                KeyStruct keyData = parseKey(rootName, key);
                List<String> defaultValuesList = parseValue(data.getProperty(key));

                WLSTOfflineDefaults defaultValues = defaults.get(keyData.folderName);
                if (defaultValues == null) {
                    defaultValues = new WLSTOfflineDefaultsImpl(keyData.folderName);
                    defaults.put(keyData.folderName, defaultValues);
                }
                defaultValues.setAttributeDefaults(keyData.attributeName, keyData.type, defaultValuesList);
            }
        }
        logger.exiting(CLASS, METHOD);
    }

    // The format of the property file key is:
    //
    //    [{<type>}.][<folder>.]<attributeName>
    //
    //    where:  type is String, Boolean, Integer, or Double.
    //                 If not present, the default is String.
    //
    //            folder is the dot separated path.
    //
    //            attributeName is the WLST Offline attribute name.
    //
    private static KeyStruct parseKey(String rootName, String key) {
        final String METHOD = "parseKey";

        logger.entering(CLASS, METHOD, rootName, key);
        KeyStruct result = new KeyStruct();

        String remainingKey = key;
        if (TYPE_PATTERN.matcher(key).matches()) {
            logger.finest("{0} includes type information", key);
            result.type = parseType(key.substring(1, key.indexOf('}')));
            remainingKey = key.substring(key.indexOf('.') + 1);
            logger.finest("{0} is type {1} and the remaining key is {2}", key,
                result.type.getSimpleName(), remainingKey);
        } else{
            logger.finest("{0} does not include type information", key);
        }

        int lastDotIndex = remainingKey.lastIndexOf('.');
        if (lastDotIndex >= 0 && lastDotIndex - 1 < remainingKey.length()) {
            result.folderName = rootName + FOLDER_SEPARATOR + remainingKey.substring(0, lastDotIndex);
            result.attributeName = remainingKey.substring(lastDotIndex + 1);
        } else if (lastDotIndex == -1){
            result.folderName = rootName;
            result.attributeName = remainingKey;
        } else {
            String message = MessageFormat.format("{0}.properties file contains invalid defaults property key: {1}",
                rootName, key);
            IllegalArgumentException iae = new IllegalArgumentException(message);
            logger.throwing(CLASS, METHOD, iae);
            throw iae;
        }
        logger.exiting(CLASS, METHOD, result);
        return result;
    }

    private static Class<?> parseType(String typeString) {
        final String METHOD = "parseType";

        logger.entering(CLASS, METHOD, typeString);
        Class<?> result;
        if (typeString.equalsIgnoreCase("int") || typeString.equalsIgnoreCase("Integer")) {
            result = Integer.class;
        } else if (typeString.equalsIgnoreCase("long") || typeString.equalsIgnoreCase("Long")) {
            result = Long.class;
        } else if (typeString.equalsIgnoreCase("boolean") || typeString.equalsIgnoreCase("Boolean")) {
            result = Boolean.class;
        } else if (typeString.equalsIgnoreCase("float") || typeString.equalsIgnoreCase("Float")) {
            result = Float.class;
        } else if (typeString.equalsIgnoreCase("double") || typeString.equalsIgnoreCase("Double")) {
            result = Double.class;
        } else {
            result = KeyStruct.DEFAULT_TYPE;
        }
        logger.exiting(CLASS, METHOD, result.getName());
        return result;
    }

    private static List<String> parseValue(String valueString) {
        final String METHOD = "parseValue";

        logger.entering(CLASS, METHOD, valueString);
        ArrayList<String> result = new ArrayList<String>();
        if (!StringUtils.isEmpty(valueString)) {
            String[] resultArray = valueString.split(",");
            for (String item : resultArray) {
                result.add(item.trim());
            }
        }
        logger.exiting(CLASS, METHOD, result);
        return result;
    }

    private void logDefaults() {
        if (logger.isFinestEnabled()) {
            logger.finest("factory defaults map has {0} entries", defaults.size());
            for (Map.Entry<String, WLSTOfflineDefaults> entry : defaults.entrySet()) {
                logger.finest("{0} = {1}", entry.getKey(), entry.getValue().getFolderName());
            }
        }
    }

    private static class KeyStruct {
        static final Class DEFAULT_TYPE = String.class;

        Class<?> type = DEFAULT_TYPE;
        String folderName;
        String attributeName;
    }
}
