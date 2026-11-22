import com.google.inject.Key;
import org.eclipse.sisu.Parameters;
import java.util.Arrays;

public class AnnotationCompatibilityProbe {
    public static void main(String[] args) {
        System.out.println("java=" + System.getProperty("java.version"));
        System.out.println("Guice=" + Key.class.getProtectionDomain().getCodeSource().getLocation());
        System.out.println("Parameters annotations=" + Arrays.toString(Parameters.class.getAnnotations()));
        System.out.println("binding=" + Key.get(String.class, Parameters.class));
    }
}
