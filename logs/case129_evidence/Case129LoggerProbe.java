import org.apache.logging.log4j.LogManager;

public class Case129LoggerProbe {
    public static void main(String[] args) {
        System.out.println(LogManager.getContext(false).getClass().getName());
    }
}
