from pathlib import Path
import re
from .util import read_text

KEY=re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=')

def _keys(path):
    out=[]
    if not path.exists():return out
    for line in read_text(path).splitlines():
        m=KEY.match(line)
        if m:out.append(m.group(1))
    return sorted(set(out))

def check_environment(root):
    root=Path(root); required=_keys(root/'.env.example'); present=_keys(root/'.env')
    missing=[k for k in required if k not in present]
    return {'required_names':required,'present_names':present,'missing_names':missing,'has_env_file':(root/'.env').exists(),
            'note':'Values are never returned by RunProof; only variable names/status are reported.'}
