"""Exercise the new landing-page → standalone 3D room → landing-page route."""
import json,subprocess,sys,os
from pathlib import Path
root=Path(__file__).resolve().parent.parent
base=(sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:4173/dist').rstrip('/')
remote=base.startswith('https://')
out=root/'artifacts/qa/combined';out.mkdir(parents=True,exist_ok=True)
def run(*args):
 p=subprocess.run(['agent-browser','--session',os.environ.get('CYG_QA_SESSION','cyg-combined-preview'),'--json',*args],capture_output=True,text=True)
 assert p.returncode==0,p.stderr+p.stdout
 r=json.loads(p.stdout);assert r.get('success'),r
 return r.get('data',{})
def ev(js):return run('eval',js).get('result')
run('set','viewport','1440','1000');run('open',base+'/')
run('wait','--fn','window.__introDone===true')
assert ev('location.href')==base+'/'
assert ev('document.body.dataset.version')=='11'
assert not ev("performance.getEntriesByType('resource').some(r=>r.name.endsWith('.glb')||r.name.includes('/three/'))")
assert ev("getComputedStyle(document.body).backgroundColor==='rgb(19, 11, 19)'&&getComputedStyle(document.querySelector('.event')).color==='rgb(66, 40, 34)'&&getComputedStyle(document.querySelector('.closing')).backgroundColor==='rgb(19, 11, 19)'&&getComputedStyle(document.querySelector('.site-header')).backgroundColor==='rgb(13, 9, 14)'")
run('find','role','link','click','--name','進入 3D 展場','--exact')
run('wait','--fn','window.__cafe?.ready===true')
assert ev('location.pathname')==('/cyg-4th/cafe/' if remote else '/dist/cafe/')
model=ev('window.__cafe.snapshot()');assert model['modelBytes']==1861616 and model['meshes']==54
run('click','[data-view="interior"]');ev('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
assert ev('window.__cafe.snapshot().view')=='interior'
run('screenshot',str(out/('remote-cafe.png' if remote else 'cafe.png')))
run('find','role','link','click','--name','← 返回活動頁','--exact');run('wait','--fn','window.__introDone===true')
assert ev('location.href')==base+'/'
run('set','viewport','320','800');run('reload');run('wait','--fn','window.__introDone===true')
assert ev('innerWidth===document.documentElement.scrollWidth')
run('find','role','link','click','--name','3D 展場','--exact');run('wait','--fn','window.__cafe?.ready===true')
assert ev('innerWidth===document.documentElement.scrollWidth')
run('find','role','link','click','--name','← 返回活動頁','--exact');run('wait','--fn','window.__introDone===true')
run('find','role','link','click','--name','回到設計總覽 ↗','--exact');run('wait','--fn',"document.querySelectorAll('article').length===11")
assert ev('location.href')==base+'/designs/'
assert ev('innerWidth===document.documentElement.scrollWidth')
run('find','role','link','click','--name','緋夜劇場','--exact');run('wait','--fn','window.__introDone===true')
assert ev('location.href')==base+'/versions/02-crimson-theatre/'
run('find','role','link','click','--name','回到設計總覽 ↗','--exact');run('wait','--fn',"document.querySelectorAll('article').length===11")
run('find','role','link','click','--name','前往活動首頁 · 緋幕手帖 ↗','--exact');run('wait','--fn','window.__introDone===true')
assert ev('location.href')==base+'/'
run('open',base+'/versions/11-theatre-scrapbook/?from=legacy#event');run('wait','--fn','window.__introDone===true')
assert ev('location.href')==base+'/?from=legacy#event'
run('find','role','link','click','--name','3D 展場','--exact');run('wait','--fn','window.__cafe?.ready===true')
run('find','role','link','click','--name','所有設計版本','--exact');run('wait','--fn',"document.querySelectorAll('article').length===11")
assert ev('location.href')==base+'/designs/'
errors=run('errors');assert not errors.get('errors'),errors
report={'status':'PASS','base':base,'styles':{'header':'02 crimson theatre','body':'theatre palette with paper collage','footer':'02 dark theatre'},'homepage':'11-theatre-scrapbook','collectionPath':'/designs/','legacyRedirectPreservesQueryAndHash':True,'collectionToExistingVersionAndBack':True,'cafeToCollection':True,'existingVersions':10,'totalVersions':11,'modelBytes':model['modelBytes'],'modelMeshes':model['meshes'],'landingDefers3DResources':True,'desktopInvitationTo3D':True,'mobileNavigationTo3D':True,'returnToActivity':True,'allVersionsAccessible':True,'pageErrors':errors.get('errors',[]),'notRun':['實體手機效能','使用者美術驗收']}
path=out/'remote-qa.json' if remote else root/'docs/combined-preview-qa.json'
path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
