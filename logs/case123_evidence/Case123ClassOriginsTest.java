import java.net.URL;
import java.util.Enumeration;
import org.junit.jupiter.api.Test;
public class Case123ClassOriginsTest {
    @Test public void origins() throws Exception {
        ClassLoader loader = Case123ClassOriginsTest.class.getClassLoader();
        String[] resources = {
            "com/fasterxml/jackson/databind/ObjectMapper.class",
            "com/fasterxml/jackson/core/JsonFactory.class",
            "com/fasterxml/jackson/annotation/JsonProperty.class",
            "com/fasterxml/jackson/annotation/JsonKey.class"
        };
        for (String path : resources) {
            Enumeration<URL> urls = loader.getResources(path);
            boolean found = false;
            while (urls.hasMoreElements()) {
                found = true;
                System.out.println("CASE123_RESOURCE " + path + "=" + urls.nextElement());
            }
            if (!found) System.out.println("CASE123_RESOURCE " + path + "=ABSENT");
        }
    }
}
