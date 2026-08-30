from pathlib import Path
import json, zipfile, tempfile

def write_evidence_bundle(path,analysis,passport,sbom,report_html):
    path=Path(path)
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('analysis.json',json.dumps(analysis,indent=2,ensure_ascii=False))
        z.writestr('runproof-passport.json',json.dumps(passport,indent=2,ensure_ascii=False))
        z.writestr('dependency-inventory.json',json.dumps(sbom,indent=2,ensure_ascii=False))
        z.writestr('runproof-report.html',report_html)
        z.writestr('README.txt','RunProof evidence bundle: analysis, signed passport, dependency inventory and human-readable report.')
    return path
