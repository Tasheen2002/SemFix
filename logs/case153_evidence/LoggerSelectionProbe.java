import org.slf4j.LoggerFactory;

public class LoggerSelectionProbe {
    public static void main(String[] args) {
        System.out.println("factory=" + LoggerFactory.getILoggerFactory().getClass().getName());
        System.out.println("logger=" + LoggerFactory.getLogger("bump-diagnostic").getClass().getName());
    }
}
