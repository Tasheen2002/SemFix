"""Archive and disassemble the resolved POI and DSS compatibility evidence."""
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import tarfile

ROOT = Path(__file__).resolve().parents[1]
JAVAP = Path('C:/Program Files/Java/jdk-21.0.11/bin/javap.exe')

def main():
    candidates = list(csv.DictReader((ROOT / 'results/test_failure_candidates.csv').open(encoding='utf-8-sig', newline='')))
    for n in (103, 104):
        base = ROOT / f'logs/case{n}_evidence'
        inspections = []
        for phase in ('pre', 'breaking'):
            container = 'bump-' + candidates[n-1]['case_id'] + '-' + phase
            if n == 103:
                if phase == 'pre':
                    paths = ['/root/.m2/repository/org/apache/poi/poi/4.1.2/poi-4.1.2.jar']
                else:
                    events = '\n'.join(p.read_text(errors='replace') for p in (base / phase / 'runner-events').rglob('*.events'))
                    paths = sorted(set(re.findall(r'/root/[^"\s:]+\.jar', events)))
                    paths = [p for p in paths if any(s in p for s in ('/poi/poi/', '/poi/poi-ooxml/', '/poi/poi-scratchpad/', '/tika-parser-microsoft-module/'))]
            else:
                summary = json.loads((base / phase / 'archive_summary.json').read_text())
                paths = sorted(set().union(*(set(r['classpath'].split(':')) for r in summary['reports'])))
                paths = [p for p in paths if '/sd-dss/dss-pades' in p and p.endswith('.jar')]
            for path in paths:
                data = subprocess.check_output(['docker', 'cp', container + ':' + path, '-'])
                with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                    members = [m for m in archive if m.isfile()]
                    if len(members) != 1:
                        raise ValueError('Expected one JAR')
                    data = archive.extractfile(members[0]).read()
                destination = base / phase / Path(path).name
                with destination.open('xb') as output:
                    output.write(data)
                if '/poi/poi/' in path:
                    classes = ['org.apache.poi.extractor.POITextExtractor', 'org.apache.poi.hssf.model.InternalWorkbook']
                elif '/poi/poi-ooxml/' in path:
                    classes = ['org.apache.poi.ooxml.extractor.POIXMLTextExtractor']
                elif 'tika-parser-microsoft-module' in path:
                    classes = ['org.apache.tika.detect.microsoft.POIFSContainerDetector']
                elif '/dss-pades-pdfbox/' in path:
                    classes = ['eu.europa.esig.dss.pdf.pdfbox.PdfBoxSignatureService']
                elif '/dss-pades/' in path:
                    classes = ['eu.europa.esig.dss.pdf.AbstractPDFSignatureService']
                else:
                    classes = []
                record = {'phase': phase, 'resolved_path': path, 'sha256': hashlib.sha256(data).hexdigest(), 'disassemblies': []}
                for clazz in classes:
                    command = [str(JAVAP), '-classpath', str(destination), '-p', '-s', '-c', clazz]
                    result = subprocess.run(command, capture_output=True, text=True)
                    if result.returncode:
                        raise RuntimeError(result.stderr)
                    name = phase + '_' + destination.stem + '_' + clazz.rsplit('.', 1)[-1] + '_javap.txt'
                    with (base / name).open('x', encoding='utf-8') as output:
                        output.write(result.stdout)
                    record['disassemblies'].append({'class': clazz, 'file': name, 'command': command, 'exit_code': result.returncode})
                    lines = result.stdout.splitlines()
                    print(n, phase, destination.name, '\n'.join(line for line in lines if any(s in line for s in ('public abstract class', 'public interface', 'public class', 'WORKBOOK_DIR_ENTRY_NAMES', 'checkDocumentPermissions'))))
                inspections.append(record)
        with (base / 'resolved_jar_inspection.json').open('x', encoding='utf-8') as output:
            json.dump(inspections, output, indent=2)

if __name__ == '__main__':
    main()
