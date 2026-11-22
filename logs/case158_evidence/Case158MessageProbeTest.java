import org.junit.Test;
import org.apache.http.client.HttpResponseException;
import org.apache.http.HttpResponse;
import com.github.sardine.impl.SardineException;
public class Case158MessageProbeTest {
    @Test public void messageAndOrigins() {
        System.out.println("CASE158_ORIGIN httpclient=" + HttpResponseException.class.getProtectionDomain().getCodeSource().getLocation());
        System.out.println("CASE158_ORIGIN httpcore=" + HttpResponse.class.getProtectionDomain().getCodeSource().getLocation());
        System.out.println("CASE158_PARENT " + new HttpResponseException(400, "m").getMessage());
        System.out.println("CASE158_CLIENT " + new SardineException("m", 400, "response phrase").getMessage());
    }
}
