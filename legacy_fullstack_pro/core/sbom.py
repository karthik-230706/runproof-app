from datetime import datetime,timezone

def make_sbom(project_name,ptype,deps):
    return {'format':'RunProof Dependency Inventory','schema_version':'1.0','generated_at':datetime.now(timezone.utc).isoformat(),
            'project':{'name':project_name,'type':ptype},'component_count':deps.get('total',0),
            'components':[{'name':x.get('name'),'version':x.get('version'),'constraint':x.get('constraint'),'pinned':x.get('pinned'),'source':x.get('source')} for x in deps.get('components',[])]}
