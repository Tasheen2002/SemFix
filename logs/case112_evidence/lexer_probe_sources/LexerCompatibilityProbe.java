import org.antlr.v4.runtime.atn.ATNDeserializer;
public class LexerCompatibilityProbe {
    public static void main(String[] args) throws Exception {
        System.out.println("runtime=" + ATNDeserializer.class.getProtectionDomain().getCodeSource().getLocation());
        System.out.println("method=" + ATNDeserializer.class.getMethod("deserialize", char[].class));
        System.out.println("initialized=" + Class.forName(args[0]));
    }
}
