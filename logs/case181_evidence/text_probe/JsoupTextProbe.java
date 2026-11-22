import java.io.File;
import org.jsoup.Jsoup;
public class JsoupTextProbe {
    public static void main(String[] arguments) throws Exception {
        var element = Jsoup.parse(new File(arguments[0]), "UTF-8").selectFirst("div");
        System.out.println(element.select("*").text());
    }
}
