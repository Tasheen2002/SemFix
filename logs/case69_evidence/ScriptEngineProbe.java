import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;

class ScriptEngineProbe {
    public static void main(String[] args) throws Exception {
        ScriptEngine engine = new ScriptEngineManager().getEngineByName("graal.js");
        System.out.println(engine.eval("1 + 1"));
    }
}
