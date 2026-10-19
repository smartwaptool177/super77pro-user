"""Static project checks: broken file references, JS syntax, JSON validity, Capacitor webDir, size budget.
Run: python3 tests/check_project.py [project-folder]"""
import json,os,re,subprocess,sys
root=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
bad=[];n=0
def chk(c,m):
    global n;n+=1
    if not c:bad.append(m)
html=open(root+'/www/index.html',encoding='utf8').read()
for ref in re.findall(r'(?:src|href)="([^"#][^"]*)"',html):
    if ref.startswith(('http','data:')):continue
    chk(os.path.exists(os.path.join(root,'www',ref)),'index.html -> missing '+ref)
for f in ['css/style.css','css/games.css']:
    for u in re.findall(r'url\(([^)]+)\)',open(f'{root}/www/{f}',encoding='utf8').read()):
        chk(os.path.exists(os.path.join(root,'www','css',u.strip('"\''))),f+' -> missing '+u)
for js in re.findall(r'src="(js/[^"]+)"',html):
    r=subprocess.run(['node','--check',f'{root}/www/{js}'],capture_output=True,text=True);chk(r.returncode==0,js+' syntax: '+r.stderr[:200])
# every asset is referenced somewhere in www (html/css/js)
blob=html+''.join(open(f'{root}/www/{d}/{f}',encoding='utf8').read() for d in ('css','js') for f in os.listdir(f'{root}/www/{d}'))
for a in os.listdir(root+'/www/assets'):chk(a in blob,'unreferenced asset www/assets/'+a)
# every use href="#id" resolves to a symbol in the sprite
sprite=open(root+'/www/js/sprite.js',encoding='utf8').read();ids=set(re.findall(r'id=\\"([\w-]+)\\"',sprite))
for u in set(re.findall(r'href="#([a-z]+-[\w-]*[\w])"',blob))|set(re.findall(r"#((?:i|u|n)-[\w-]*[\w])",blob)):chk(u in ids,'sprite id missing: '+u)
core=open(root+'/www/js/core.js',encoding='utf8').read();im=re.search(r'var IM=\{(.*?)\}',core).group(1)
for k in re.findall(r":'(\w+)'",im):chk('i-'+k in ids,'IM symbol missing from sprite: i-'+k)
for j in ['package.json','capacitor.config.json','database.rules.json']:
    try:json.load(open(f'{root}/{j}'));chk(True,'')
    except Exception as e:chk(False,j+' invalid JSON: '+str(e))
cap=json.load(open(root+'/capacitor.config.json'));chk(os.path.exists(os.path.join(root,cap['webDir'],'index.html')),'capacitor webDir has no index.html')
for a in ['icon-only.png','icon-foreground.png','splash.png','splash-dark.png']:chk(os.path.exists(f'{root}/assets/{a}'),'missing Android asset '+a)
sz=sum(os.path.getsize(os.path.join(d,f)) for d,_,fs in os.walk(root+'/www') for f in fs)
print(f'www bundle size: {sz/1024:.0f} KB')
print(f'{n-len(bad)}/{n} static checks passed')
for b in bad:print('FAIL',b)
sys.exit(1 if bad else 0)
