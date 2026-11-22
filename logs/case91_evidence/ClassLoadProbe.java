class ClassLoadProbe {
    public static void main(String[] args) throws Exception {
        System.out.println(Class.forName(args[0], false, ClassLoader.getSystemClassLoader()).getName());
    }
}
