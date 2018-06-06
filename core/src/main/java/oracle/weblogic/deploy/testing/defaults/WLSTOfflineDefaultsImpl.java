package oracle.weblogic.deploy.testing.defaults;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import oracle.weblogic.deploy.testing.logging.WLSDeployTestingLogFactory;
import oracle.weblogic.deploy.testing.logging.PlatformLogger;
import oracle.weblogic.deploy.util.StringUtils;

public class WLSTOfflineDefaultsImpl implements WLSTOfflineDefaults {
    private static final String CLASS = WLSTOfflineDefaultsImpl.class.getName();
    private static PlatformLogger logger =
        WLSDeployTestingLogFactory.getLogger("wlsdeploy.system_test");

    private String folderName;
    private Map<String, DefaultValueStruct> attributesDefaultValues;

    /* package */ WLSTOfflineDefaultsImpl(String folderName) {
        this.folderName = folderName;
        this.attributesDefaultValues = new HashMap<String, DefaultValueStruct>();
    }

    public String getFolderName() {
        return folderName;
    }

    public boolean matches(String attributeName, Object expectedValue, Object actualValue) {
        final String METHOD = "matches";

        logger.entering(CLASS, METHOD, attributeName, expectedValue, actualValue);
        logger.finest("expectedValue {0} is a {1}", expectedValue,
            (expectedValue != null ? expectedValue.getClass().getName() : "null"));
        logger.finest("actualValue {0} is a {1}", actualValue,
            (actualValue != null ? actualValue.getClass().getName() : "null"));

        boolean result;
        if (expectedValue == null) {
            if (actualValue == null) {
                result = true;
            } else {
                result = false;
            }
        } else if (expectedValue == actualValue || expectedValue.equals(actualValue) ||
            (actualValue != null && expectedValue.toString().equals(actualValue.toString()))) {
            result = true;
        } else if (isPossibleBooleanValue(expectedValue) &&
                   isPossibleBooleanValue(actualValue) &&
                   (getBooleanValue(expectedValue) == getBooleanValue(actualValue))) {
            result = true;
        } else {
            if (isDefaultValue(attributeName, expectedValue) && isDefaultValue(attributeName, actualValue)) {
                result = true;
            } else {
                result = false;
            }
        }
        logger.exiting(CLASS, METHOD, result);
        return result;
    }

    public boolean isDefaultValue(String attributeName, Object value) {
        final String METHOD = "isDefaultValue";

        logger.entering(CLASS, METHOD, attributeName, value);
        logDefaults();

        boolean result;
        DefaultValueStruct defaults = attributesDefaultValues.get(attributeName);
        if (defaults != null) {
            logger.finest("default = {0}", defaults);
            String valueString = null;
            if (value != null) {
                valueString = value.toString();
            }
            Class<?> type = defaults.type;
            List<String> defaultValues = defaults.values;

            result = isValidDefaultValue(type, valueString, defaultValues);
        } else if (value == null) {
            logger.finest("defaults is null and value is null");
            result = true;
        } else if (value.toString().length() == 0) {
            logger.finest("defaults is null and value is empty");
            result = true;
        } else {
            logger.finest("defaults is null, value = {0}", value);
            result = false;
        }
        logger.exiting(CLASS, METHOD, result);
        return result;
    }

    public void setAttributeDefaults(String attributeName, Class<?> type, List<String> defaultValues) {
        DefaultValueStruct value = new DefaultValueStruct();
        value.type = type;
        value.values = new ArrayList<String>(defaultValues);
        attributesDefaultValues.put(attributeName, value);
    }

    private boolean isValidDefaultValue(Class<?> type, String actualValue, List<String> values) {
        final String METHOD = "isActualValueValidDefault";

        logger.entering(CLASS, METHOD, type, actualValue, values);
        boolean result = false;

        if (StringUtils.isEmpty(actualValue)) {
            result = true;
        } else if (values.isEmpty()) {
            result = false;
        } else {
            if (type == Boolean.class) {
                boolean isDefault = false;
                boolean actualBoolean = getBooleanValue(actualValue);
                for (String value : values) {
                    boolean valueBoolean = getBooleanValue(value);
                    if (actualBoolean == valueBoolean) {
                        isDefault = true;
                        break;
                    }
                }
                result = isDefault;
            } else {
                result = values.contains(actualValue.toString());
            }
        }
        logger.exiting(CLASS, METHOD, result);
        return result;
    }

    private boolean getBooleanValue(Object value) {
        final String METHOD = "getBooleanValue";

        logger.entering(CLASS, METHOD, value);
        boolean result;
        if (value.toString().equalsIgnoreCase("true") || value.toString().equals("1")) {
            result = true;
        } else if (value.toString().equalsIgnoreCase("false") || value.toString().equals("0")) {
            result = false;
        } else {
            throw new IllegalArgumentException("Invalid boolean value: " + value.toString());
        }
        logger.exiting(CLASS, METHOD, result);
        return result;
    }

    private void logDefaults() {
        logger.finest("{0} default attribute map has {1} entries", folderName, attributesDefaultValues.size());
        for (Map.Entry<String, DefaultValueStruct> attributeDefault: attributesDefaultValues.entrySet()) {
            String key = attributeDefault.getKey();
            DefaultValueStruct value = attributeDefault.getValue();
            logger.finest("{0} is a {1} and set to [{2}]", key, value.type.getName(), value.values);
        }
    }

    private boolean isPossibleBooleanValue(Object value) {
        boolean result = false;
        if (value != null) {
            Class clazz = value.getClass();
            if (clazz == Boolean.class) {
                result = true;
            } else if (clazz == Integer.class) {
                int myValue = Integer.class.cast(value);
                if (myValue == 1 || myValue == 0) {
                    result = true;
                }
            } else if (clazz == String.class) {
                String myValue = String.class.cast(value);
                if (myValue.equalsIgnoreCase("true") || myValue.equalsIgnoreCase("false") ||
                    myValue.equals("1") || myValue.equals("0")) {
                    result = true;
                }
            }
        }
        return result;
    }

    class DefaultValueStruct {
        Class type;
        List<String> values = new ArrayList<String>();
    }
}
