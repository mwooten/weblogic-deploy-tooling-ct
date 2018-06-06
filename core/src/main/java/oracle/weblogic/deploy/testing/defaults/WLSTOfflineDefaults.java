package oracle.weblogic.deploy.testing.defaults;

import java.util.List;

public interface WLSTOfflineDefaults {
    String getFolderName();
    boolean matches(String attributeName, Object expectedValue, Object actualValue);
    boolean isDefaultValue(String attributeName, Object value);
    void setAttributeDefaults(String attributeName, Class<?> type, List<String> defaultValues);
}
