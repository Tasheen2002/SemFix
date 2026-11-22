import java.io.File;
import java.nio.file.*;
import org.codehaus.plexus.components.io.resources.PlexusIoFileResource;
import org.codehaus.plexus.components.io.attributes.FileAttributes;
public class DirectoryProbe extends PlexusIoFileResource {
  DirectoryProbe(File file) throws Exception { super(file, file.getName(), FileAttributes.uncached(file)); }
  public static void main(String[] args) throws Exception {
    Path root=Files.createTempDirectory("symlink-probe");
    Path target=Files.createDirectory(root.resolve("target"));
    File link=Files.createSymbolicLink(root.resolve("link"),target).toFile();
    DirectoryProbe resource=new DirectoryProbe(link);
    System.out.println("File.isDirectory="+link.isDirectory()+" resource.isDirectory="+resource.isDirectory()+" resource.isSymbolicLink="+resource.isSymbolicLink());
  }
}
