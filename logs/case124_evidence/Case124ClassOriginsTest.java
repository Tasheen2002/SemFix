import java.net.URL;
import java.util.Enumeration;
import org.junit.Test;
public class Case124ClassOriginsTest {
    @Test public void origins() throws Exception {
        ClassLoader loader = Case124ClassOriginsTest.class.getClassLoader();
        String[] resources = {
            "javax/xml/bind/JAXBException.class",
            "jakarta/xml/bind/JAXBException.class"
        };
        for (String path : resources) {
            Enumeration<URL> urls = loader.getResources(path);
            boolean found = false;
            while (urls.hasMoreElements()) {
                found = true;
                System.out.println("CASE124_RESOURCE " + path + "=" + urls.nextElement());
            }
            if (!found) System.out.println("CASE124_RESOURCE " + path + "=ABSENT");
        }
    }
}
