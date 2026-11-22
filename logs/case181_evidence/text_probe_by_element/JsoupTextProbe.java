import java.io.File;
import org.jsoup.Jsoup;
public class JsoupTextProbe {
    public static void main(String[] arguments) throws Exception {
        var document = Jsoup.parse(new File(arguments[0]), "UTF-8");
        for (String name : new String[]{"html", "body", "div", "h1", "span"}) {
            System.out.println(name + "=" + document.selectFirst(name).select("*").text());
        }
    }
}
