"""Remove only this batch's stopped containers after evidence validation."""
import csv,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def docker(*args): return subprocess.check_output(['docker',*args],text=True)
def inventory():
 return {k:set(docker(*args).splitlines()) for k,args in {'containers':['ps','-aq','--no-trunc'],'images':['image','ls','-q','--no-trunc'],'volumes':['volume','ls','-q']}.items()}
def main():
 assert json.loads((ROOT/'results/cases161_165_completion_check.json').read_text())['passed']
 old=json.loads((ROOT/'results/backups/before_cases161_165/docker_inventory.json').read_text())
 before=inventory(); targets={}
 for n in range(161, 166):
  for phase in ('pre','breaking'):
   m=json.loads((ROOT/f'logs/case{n}_evidence/{phase}/archive_summary.json').read_text())
   targets['bump-'+m['case_id']+'-'+phase]=m['image_id']
 for name,image in targets.items():
  info=json.loads(docker('inspect',name))[0]
  assert info['Image']==image and info['State']['Status']=='exited' and info['Id'] not in old['containers']
 removed=docker('rm',*targets).splitlines(); after=inventory()
 assert before['images']==after['images'] and before['volumes']==after['volumes']
 assert set(old['containers'])<=after['containers'] and set(old['images'])<=after['images'] and set(old['volumes'])<=after['volumes']
 report={'removed_containers':removed,'images_preserved':True,'volumes_preserved':True,'preexisting_resources_preserved':True}
 with (ROOT/'logs/cases161_165_container_cleanup.json').open('x') as f:json.dump(report,f,indent=2)
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
