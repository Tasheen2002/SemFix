import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.Collection;
public class LoggerSelectionProbe {
    public static void main(String[] args) throws Exception {
        Class<?> capture = Class.forName("uk.org.lidalia.slf4jtest.TestLoggerFactory");
        capture.getMethod("clearAll").invoke(null);
        Logger logger = LoggerFactory.getLogger("case117-probe");
        logger.info("case117 diagnostic message");
        System.out.println("factory=" + LoggerFactory.getILoggerFactory().getClass().getName());
        System.out.println("logger=" + logger.getClass().getName());
        System.out.println("captured=" + ((Collection<?>) capture.getMethod("getAllLoggingEvents").invoke(null)).size());
    }
}
