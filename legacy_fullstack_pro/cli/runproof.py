#!/usr/bin/env python3
from pathlib import Path
import argparse, sys, json
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from core.engine import analyze_project
from core.passport import verify_passport
from core.evidence import write_evidence_bundle

DEV_SECRET='runproof-local-cli-secret'

def print_summary(a):
    print('='*64);print('RUNPROOF — Software Reproducibility Verifier');print('='*64)
    print('Project      :',a['scan']['project_name']);print('Type         :',a['detection']['type']);print('Runtime      :',a['runtime'].get('version') or 'Not found')
    print('-'*64)
    for k,v in a['score']['checks'].items():print(f"{k.replace('_',' ').title():24} {v['status'].upper()}")
    print('-'*64);print('Readiness    :',a['score']['score'],'/ 100 —',a['score']['status'])
    if a.get('verification'):
        v=a['verification'];print('Verification :',v.get('status'));print('Verified     :',v.get('verified',False))
        if v.get('hash_a'):print('Build A hash :',v['hash_a'][:24]+'...');print('Build B hash :',v['hash_b'][:24]+'...')
    if a['issues']:
        print('\nRunProof Doctor:')
        for i in a['issues']:print(f"[{i['severity'].upper()}] {i['title']}\n  Fix: {i['fix']}")

def main():
    ap=argparse.ArgumentParser(prog='runproof');sub=ap.add_subparsers(dest='cmd',required=True)
    for name in ['check','verify','report','evidence']:
        p=sub.add_parser(name);p.add_argument('project');p.add_argument('--execution',choices=['static','trusted'],default='static');p.add_argument('--timeout',type=int,default=60)
    pv=sub.add_parser('passport-verify');pv.add_argument('passport')
    args=ap.parse_args()
    if args.cmd=='passport-verify':
        p=json.loads(Path(args.passport).read_text());print('VALID' if verify_passport(p,DEV_SECRET) else 'INVALID');return
    a,p,s,r=analyze_project(args.project,args.execution,args.timeout,args.cmd in ('verify','evidence'),DEV_SECRET);print_summary(a)
    if args.cmd=='report':Path('runproof-report.html').write_text(r,encoding='utf-8');Path('runproof-passport.json').write_text(json.dumps(p,indent=2),encoding='utf-8');print('Generated runproof-report.html and runproof-passport.json')
    if args.cmd=='evidence':write_evidence_bundle('runproof-evidence.zip',a,p,s,r);print('Generated runproof-evidence.zip')
if __name__=='__main__':main()
