import org.json.JSONObject;

class JsonStringProbe {
    public static void main(String[] args) throws Exception {
        JSONObject session = new JSONObject("{\"id\":1}");
        System.out.println(session.get("id").getClass().getName());
        System.out.println(session.getString("id"));
    }
}
