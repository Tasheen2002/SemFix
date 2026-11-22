import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.Statement;
public class H2PrecisionProbe {
    public static void main(String[] args) throws Exception {
        Class.forName("org.h2.Driver");
        try (Connection connection = DriverManager.getConnection("jdbc:h2:mem:case114_precision");
             Statement statement = connection.createStatement()) {
            System.out.println("database=" + connection.getMetaData().getDatabaseProductVersion());
            System.out.println("sql=" + args[0]);
            statement.execute(args[0]);
            System.out.println("CREATE TABLE accepted");
        }
    }
}
