import json,os,random,sys,time
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
URL='file://'+ROOT+'/www/index.html'
OUT=os.environ.get('OUT',os.path.join(ROOT,'tests','out'));os.makedirs(OUT,exist_ok=True)
R=[];ERR=[]
def ok(area,name,cond,detail=''):R.append((area,name,bool(cond),str(detail)))
FAST="(()=>{const si=window.setInterval,st=window.setTimeout;window.setInterval=(f,d)=>si(f,d/15);window.setTimeout=(f,d)=>st(f,d/15)})()"
def until(pg,js,t=8):
    e=time.time()+t
    while time.time()<e:
        if pg.evaluate(js):return True
        pg.wait_for_timeout(30)
    return False
def newpage(b,vw=360,vh=640,fresh=True):
    ctx=b.new_context(viewport={'width':vw,'height':vh},is_mobile=True,has_touch=True);ctx.add_init_script(FAST)
    pg=ctx.new_page();pg.on('pageerror',lambda e:ERR.append(str(e)));pg.on('console',lambda m:m.type=='error' and ERR.append(m.text))
    pg.on('dialog',lambda d:d.accept());pg.goto(URL);pg.wait_for_timeout(150);return pg
W=lambda pg:pg.evaluate('wallet')
def setrng(pg,v):pg.evaluate("v=>{RNG=()=>v}",v)
def seq(pg,vals):pg.evaluate("q=>{var i=0;RNG=()=>q[i++%q.length]}",vals)
with sync_playwright() as p:
    b=p.chromium.launch();pg=newpage(b)
    SY=pg.evaluate('RULES.slot.sym');LN=pg.evaluate('RULES.slot.lines');WH=pg.evaluate('RULES.wheel');GF=pg.evaluate('RULES.greedy.foods')
    # ---------------- MATH ----------------
    TW=sum(s['w'] for s in SY);rtp=sum(s['m']*(s['w']/TW)**3 for s in SY)
    ok('Slot math','exact RTP between 93% and 96%',0.93<=rtp<=0.96,f'{rtp*100:.2f}%')
    mc=pg.evaluate("(()=>{var T=0,N=1000000,b=10;RNG=()=>Math.random();for(var i=0;i<N;i++){var g=[0,1,2].map(()=>[pickW(RULES.slot.sym),pickW(RULES.slot.sym),pickW(RULES.slot.sym)]);T+=RULES.slot.pay(g,b).win}return T/(N*b)})()")
    ok('Slot math','simulated RTP (1,000,000 spins) within 5 points of exact',abs(mc-rtp)<0.05,f'{mc*100:.2f}%')
    def ref(g,bet):
        w=0
        for L in LN:
            a,bb,c=g[0][L[0]],g[1][L[1]],g[2][L[2]]
            if a==bb==c:w+=SY[a]['m']*bet/5
        return w
    rng=random.Random(7);bad=0
    for _ in range(3000):
        gi=[[rng.randrange(7) for _ in range(3)] for _ in range(3)];bet=rng.choice([5,10,50,100,500,1000])
        if rng.random()<.3:gi=[[gi[0][0]]*3]*3 if False else [[2,2,2],[2,2,2],[2,2,2]]
        got=pg.evaluate("([g,b])=>RULES.slot.pay(g.map(c=>c.map(i=>RULES.slot.sym[i])),b).win",[gi,bet])
        if abs(got-ref(gi,bet))>1e-9:bad+=1
    ok('Slot math','pay() equals independent reference on 3,000 random grids',bad==0,f'{bad} mismatches')
    ok('Slot math','all-77 grid pays 200 x bet on 5 lines',pg.evaluate("RULES.slot.pay([0,1,2].map(()=>[0,1,2].map(()=>RULES.slot.sym[0])),10).win")==2000)
    N=len(WH['seg']);cnt={}
    for s in WH['seg']:cnt[s]=cnt.get(s,0)+1
    for k,box in zip(['melon','77','mango'],WH['box']):
        r_=cnt[box['k']]/N*box['m'];ok('Wheel math',f'{k} box RTP = {r_*100:.1f}% (<=100%)',r_<=1.0001,f'{cnt[box["k"]]}/{N} x{box["m"]}')
    ok('Wheel math','all 3 boxes have the same RTP',len({round(cnt[x["k"]]/N*x["m"],6) for x in WH['box']})==1)
    for sym,exp in [('🍉',[20,0,0]),('7️⃣',[0,80,0]),('🥭',[0,0,20])]:
        got=pg.evaluate("([s,b])=>RULES.wheel.pay(s,b)",[sym,[10,10,10]]);ok('Wheel math',f'pay {sym} with 10/10/10 = {sum(exp)}',got==sum(exp),got)
    ok('Wheel math','77 x8 on 100 pays 800',pg.evaluate("RULES.wheel.pay('7️⃣',[0,100,0])")==800)
    T=sum(f['w'] for f in GF)
    for f in GF:
        r_=f['w']/T*f['m'];ok('GreedyBaby math',f'{f["e"]} x{f["m"]} RTP {r_*100:.1f}% (<=100%)',r_<=1.0,'')
    fr=pg.evaluate("(()=>{var c=[0,0,0,0,0,0,0,0],N=600000;RNG=()=>Math.random();for(var i=0;i<N;i++){var w=pickW(RULES.greedy.foods.map((f,i)=>({w:f.w,i:i}))).i;c[w]++}return c.map(x=>x/N)})()")
    ok('GreedyBaby math','sampled frequencies match weights (±0.6 pt)',all(abs(fr[i]-GF[i]['w']/T)<0.006 for i in range(8)),[round(x,3) for x in fr])
    ok('GreedyBaby math','pay = bet x multiplier for all 8 foods',all(pg.evaluate("([i,b])=>RULES.greedy.pay(i,b)",[i,[0]*i+[10]+[0]*(7-i)])==10*GF[i]['m'] for i in range(8)))
    pg.context.close()
    # ---------------- SLOT UI ----------------
    pg=newpage(b);pg.click('[data-g=slot]');pg.wait_for_timeout(100)
    for _ in range(10):pg.click('#bm')
    ok('Slot UI','BET − stops at 5',pg.inner_text('#tb')=='5');
    for _ in range(10):pg.click('#bp')
    ok('Slot UI','BET + stops at 1,000',pg.inner_text('#tb')=='1,000')
    seen=[pg.inner_text('#tb')]
    for _ in range(5):pg.click('#bm');seen.append(pg.inner_text('#tb'))
    ok('Slot UI','bet steps 1,000 > 500 > 100 > 50 > 10 > 5',seen==['1,000','500','100','50','10','5'],seen)
    pg.click('#bp')
    def rfor(sym_i):
        c=sum(s['w'] for s in SY[:sym_i])+SY[sym_i]['w']/2;return c/TW
    scen=[[[0]*3]*3,[[6,6,6],[0,1,2],[3,4,5]]]
    rng=random.Random(11)
    for _ in range(10):scen.append([[rng.randrange(7) for _ in range(3)] for _ in range(3)])
    scen.append([[2,5,6],[2,3,6],[2,4,6]]) # no win
    for gi in scen:
        gi=[list(c) for c in gi];bet=10;w0=W(pg);seq(pg,[rfor(gi[c][r]) for c in range(3) for r in range(3)])
        pg.click('#sp');done=until(pg,"!document.querySelector('#mg').textContent==false&&!busyCheck()") if False else until(pg,"/won|No win/.test(document.querySelector('#mg').textContent)",4)
        exp=-bet+ref(gi,bet);ok('Slot UI',f'spin grid {gi} -> wallet change {exp:+.0f}',done and W(pg)-w0==exp,f'got {W(pg)-w0}');pg.wait_for_timeout(60)
        until(pg,"document.querySelector('#sp')&&true",1)
    ok('Slot UI','reels show 3x3 SVG symbols',pg.locator('.reel .cell svg').count()==9)
    setrng(pg,0.5);pg.evaluate('setW(3)');w0=W(pg);pg.click('#sp');pg.wait_for_timeout(100)
    ok('Slot UI','insufficient balance blocks spin',W(pg)==w0 and 'Insufficient' in pg.inner_text('#mg'))
    pg.evaluate('setW(100000)');pg.evaluate("RNG=()=>Math.random()");pg.click('#au');pg.wait_for_timeout(1800);n=pg.evaluate('ST.n')
    ok('Slot UI','AUTO spins repeatedly',n>=4,f'{n} bets');pg.evaluate("setW(5)");pg.wait_for_timeout(1500)
    ok('Slot UI','AUTO stops by itself when balance too low',not pg.evaluate("document.querySelector('#au').classList.contains('on')"))
    pg.evaluate('setW(1000)');pg.evaluate("for(var i=0;i<5;i++)document.querySelector('#bm').click()");pg.evaluate("RNG=()=>0");w0=W(pg)
    # disable auto first
    pg.click('#sp') if False else None
    pg.click('#close');pg.wait_for_timeout(100)
    pg.click('[data-g=slot]');seq(pg,[0]*9);w0=W(pg);bet=int(pg.inner_text('#tb').replace(',',''));pg.click('#sp');pg.wait_for_timeout(30);pg.click('#close');pg.wait_for_timeout(100)
    ok('Slot UI','closing mid-spin still settles the result (77 grid)',W(pg)==w0-bet+200*bet,f'{W(pg)-w0} bet {bet}')
    pg.context.close()
    # ---------------- WHEEL UI ----------------
    def idx_for(sym):return [i for i,s in enumerate(WH['seg']) if s==sym][0]
    for name,sym,mult in [('watermelon','🍉',[2,0,0]),('77','7️⃣',[0,8,0]),('mango','🥭',[0,0,2])]:
        pg=newpage(b);pg.click('[data-g=wheel]');setrng(pg,(idx_for(sym)+.5)/N);pg.click('.chip[data-v="10"]')
        w0=W(pg)
        for i in range(3):pg.click(f'.bx[data-i="{i}"]')
        ok('Wheel UI',f'{name}: 3 bets of 10 deduct 30',W(pg)==w0-30)
        ok('Wheel UI',f'{name}: box labels show 10',pg.locator('.bx .t').all_inner_texts()==['10','10','10'])
        pg.click('.bx[data-i="0"]') if False else None
        started=until(pg,"document.querySelector('#mg').textContent=='Spinning...'",5)
        w1=W(pg);pg.click('.bx[data-i="1"]');ok('Wheel UI',f'{name}: betting blocked while spinning',W(pg)==w1)
        until(pg,"/Result/.test(document.querySelector('#mg').textContent)",5)
        exp=sum(10*m for m in mult)
        ok('Wheel UI',f'{name}: payout +{exp}',W(pg)-w0==-30+exp,W(pg)-w0)
        hist=pg.evaluate("document.querySelector('#hs svg use').getAttribute('href')")
        ok('Wheel UI',f'{name}: result history shows latest',hist=='#i-'+{'🍉':'melon','7️⃣':'seven','🥭':'mango'}[sym],hist)
        ok('Wheel UI',f'{name}: winning box highlighted',pg.locator('.bx.win').count()==1)
        if name=='watermelon':
            until(pg,"document.querySelector('#rd').textContent=='2'",6)
            ok('Wheel UI','next round starts: round 2, bets reset, timer back to 10',pg.locator('.bx .t').all_inner_texts()==['0','0','0'] and pg.inner_text('#cd')=='10',pg.inner_text('#cd'))
            vals=[]
            for _ in range(60):
                v=pg.inner_text('#cd');vals.append(v) if not vals or vals[-1]!=v else None;pg.wait_for_timeout(20)
            iv=[int(x) for x in vals];ok('Wheel UI','countdown ticks down one second at a time',len(iv)>=4 and all(iv[i]-iv[i+1]==1 for i in range(len(iv)-1) if iv[i]>0),vals)
            until(pg,"document.querySelector('#mg').textContent=='Place your bets'&&+document.querySelector('#cd').textContent>=8",6)
            pg.evaluate('setW(5)');w1=W(pg);pg.click('.bx[data-i="0"]');ok('Wheel UI','insufficient balance blocks bet',W(pg)==w1 and pg.inner_text('.bx[data-i="0"] .t')=='0')
            until(pg,"document.querySelector('#mg').textContent=='Place your bets'&&+document.querySelector('#cd').textContent>=8",6)
            pg.evaluate('setW(5000)');w1=W(pg);pg.click('.bx[data-i="0"]');pg.click('#close');pg.wait_for_timeout(80)
            ok('Wheel UI','closing during bet time refunds the bet',W(pg)==w1 and pg.evaluate("ST.tx[0].k")=='Refund',pg.evaluate("ST.tx[0].k"))
            pg.click('[data-g=wheel]');setrng(pg,(idx_for('🍉')+.5)/N);pg.click('.chip[data-v="10"]');w1=W(pg);pg.click('.bx[data-i="0"]')
            until(pg,"document.querySelector('#mg').textContent=='Spinning...'",5);pg.click('#close');pg.wait_for_timeout(80)
            ok('Wheel UI','closing mid-spin settles the result (win paid)',W(pg)==w1+10,W(pg)-w1)
        pg.context.close()
    # ---------------- GREEDY UI ----------------
    pg=newpage(b);pg.click('[data-g=greedy]');pg.click('.chip[data-v="10"]')
    def rmid(i):return (sum(f['w'] for f in GF[:i])+GF[i]['w']/2)/T
    icon={'🍎':'apple','🍋':'lemon','🍓':'straw','🥭':'mango','🐟':'fish','🍔':'burger','🍕':'pizza','🍗':'chicken'}
    for rnd_,i in enumerate(list(range(8))+[0]):
        until(pg,"document.querySelector('#ph').textContent=='Bet time'&&document.querySelector('#rd').textContent=='%d'"%(rnd_+1),8)
        setrng(pg,rmid(i));w0=W(pg)
        pg.evaluate("document.querySelectorAll('.fd').forEach(b=>b.click())")
        if rnd_==0:
            vals=[]
            for _ in range(14):
                v=pg.inner_text('#cd');vals.append(v) if not vals or vals[-1]!=v else None;pg.wait_for_timeout(15)
            ok('GreedyBaby UI','countdown ticks down',len(vals)>=3,vals)
        ok('GreedyBaby UI',f'round {rnd_+1}: 8 bets of 10 deduct 80',W(pg)==w0-80)
        until(pg,"document.querySelector('#ph').textContent=='Drawing'",8);w1=W(pg);pg.click('.fd[data-i="0"]');
        ok('GreedyBaby UI',f'round {rnd_+1}: betting blocked while drawing',W(pg)==w1) if rnd_<2 else None
        until(pg,"document.querySelector('#ph').textContent=='Result'",8)
        exp=10*GF[i]['m']
        ok('GreedyBaby UI',f'round {rnd_+1}: winner {GF[i]["e"]} x{GF[i]["m"]} pays {exp}',W(pg)-w0==-80+exp,W(pg)-w0)
        ok('GreedyBaby UI',f'round {rnd_+1}: history newest first',pg.evaluate("document.querySelector('#hs svg use').getAttribute('href')")=='#i-'+icon[GF[i]['e']])
    ok('GreedyBaby UI','history capped at 8 items',pg.locator('#hs svg').count()==8,pg.locator('#hs svg').count())
    until(pg,"document.querySelector('#ph').textContent=='Bet time'",8);pg.evaluate('setW(5)');w0=W(pg);pg.click('.fd[data-i="3"]')
    ok('GreedyBaby UI','insufficient balance blocks bet',W(pg)==w0)
    pg.evaluate('setW(5000)');w0=W(pg);pg.click('.fd[data-i="3"]');pg.click('#close');pg.wait_for_timeout(80)
    ok('GreedyBaby UI','closing during bet time refunds',W(pg)==w0)
    pg.click('[data-g=greedy]');pg.click('.chip[data-v="10"]');setrng(pg,rmid(4));w0=W(pg);pg.click('.fd[data-i="4"]')
    until(pg,"document.querySelector('#ph').textContent=='Drawing'",8);pg.click('#close');pg.wait_for_timeout(80)
    ok('GreedyBaby UI','closing mid-draw settles (fish x10 pays 100)',W(pg)==w0-10+100,W(pg)-w0)
    pg.context.close()
    # ---------------- WALLET / PERSISTENCE ----------------
    pg=newpage(b);pg.click('#add');ok('Wallet','+ adds test balance ₹1,000',W(pg)==6000)
    pg.click('[data-g=slot]');seq(pg,[0]*9);pg.click('#sp');until(pg,"/won/.test(document.querySelector('#mg').textContent)",4)
    pg.click('#close');pg.click('[data-g=wheel]');setrng(pg,(idx_for('🥭')+.5)/N);pg.click('.chip[data-v="50"]');pg.click('.bx[data-i="2"]');pg.click('.bx[data-i="0"]')
    until(pg,"/Result/.test(document.querySelector('#mg').textContent)",8);pg.click('#close')
    st=pg.evaluate('({b:ST.b,w:ST.w,n:ST.n,tx:ST.tx.length,wal:wallet,tw:today})')
    ok('Wallet','balance = 5000 + credits − wagered + won',st['wal']==5000+1000-st['b']+st['w'],st)
    ok('Wallet','bets placed counter',st['n']==3,st['n'])
    pg.reload();pg.wait_for_timeout(150)
    ok('Wallet','balance saved after reload',W(pg)==st['wal'])
    st2=pg.evaluate('({tx:ST.tx.length,b:ST.b,w:ST.w,tw:today})');ok('Wallet','history and totals saved after reload',st2['tx']==st['tx'] and st2['b']==st['b'] and st2['w']==st['w'],st2)
    pg.click('.nav [data-t=wallet]');ok('Wallet','history rows shown',pg.locator('.tx li').count()==st['tx'])
    pg.click('#pc');pg.click('[data-g=slot]');ok('Wallet','Today\'s win saved after reload (slot)',pg.inner_text('#tw')==f"{st['tw']['slot']:,}",pg.inner_text('#tw'))
    pg.click('#close');pg.click('[data-g=wheel]');ok('Wallet','wheel history saved after reload',pg.locator('#hs svg').count()==1);pg.click('#close')
    # ---------------- NAV / SOUND ----------------
    for t in ['wallet','profile','games','home']:
        pg.click(f'.nav [data-t={t}]');pg.wait_for_timeout(60)
        ok('Navigation',f'tab {t}: exactly one active',pg.locator('.nav .on').count()==1 and pg.evaluate(f"document.querySelector('.nav .on').dataset.t")==t)
        ok('Navigation',f'tab {t}: panel state',pg.evaluate("document.querySelector('#pv').classList.contains('on')")==(t in('wallet','profile')))
    pg.click('[data-g=slot]');s0=pg.evaluate('ST.snd');pg.click('#sb');ok('Sound','header button toggles sound',pg.evaluate('ST.snd')!=s0);pg.click('#sb');pg.click('#close')
    pg.click('.nav [data-t=profile]');pg.click('#sn');ok('Sound','profile toggle off',pg.evaluate('ST.snd')==0);pg.reload();pg.wait_for_timeout(120);ok('Sound','setting saved after reload',pg.evaluate('ST.snd')==0)
    pg.click('.nav [data-t=profile]');pg.click('#sn');pg.click('#rs');pg.click('#modal-ok');pg.wait_for_timeout(80)
    ok('Profile','reset test data restores ₹5,000 and clears history',W(pg)==5000 and pg.evaluate('ST.tx.length')==0 and pg.evaluate('ST.n')==0)
    pg.click('.nav [data-t=wallet]');ok('Wallet','empty state message',pg.locator('.empty').count()>=1 and 'No transactions' in pg.inner_text('#pb'))
    pg.context.close()
    # ---------------- REGRESSIONS + NEW BEHAVIOUR ----------------
    # R1: closing during the result pause must NOT refund bets that were already settled (bug in v1.0)
    for g_,bet_,rng_ in [('wheel','.bx[data-i="1"]',0.99),('greedy','.fd[data-i="0"]',0.99)]:
        pg=newpage(b);pg.click(f'[data-g={g_}]');setrng(pg,rng_);pg.click('.chip[data-v="100"]');pg.click(bet_)
        until(pg,"/Result|winner|won/.test(document.querySelector('#mg').textContent)",8);w1=W(pg);nt=pg.evaluate('ST.tx.length')
        pg.click('#close');pg.wait_for_timeout(100)
        ok('Regression',f'{g_}: closing during the result pause does not refund settled bets',W(pg)==w1 and pg.evaluate('ST.tx.length')==nt and pg.evaluate("ST.tx[0].k")!='Refund',f'{w1}->{W(pg)}')
        pg.context.close()
    # R2: one bet + immediate close in bet window still refunds exactly once
    pg=newpage(b);pg.click('[data-g=wheel]');pg.click('.chip[data-v="50"]');w0=W(pg);pg.click('.bx[data-i="0"]');pg.click('.bx[data-i="0"]');pg.click('#close');pg.wait_for_timeout(80)
    ok('Regression','wheel: two bets then close refunds exactly the two bets once',W(pg)==w0 and pg.evaluate("ST.tx.filter(x=>x.k=='Refund').length")==1)
    pg.context.close()
    # Slot: busy state + no double deduction + winning line display
    pg=newpage(b);pg.click('[data-g=slot]');setrng(pg,0.5);w0=W(pg)
    pg.evaluate("document.querySelector('#sp').click();document.querySelector('#sp').click();document.querySelector('#sp').click()")
    ok('Slot UI','triple tap on SPIN deducts the bet only once',W(pg)==w0-10,W(pg)-w0)
    ok('Slot UI','SPIN and bet buttons are disabled while spinning',pg.evaluate("['sp','bm','bp'].every(i=>document.getElementById(i).disabled)"))
    until(pg,"/won|No win/.test(document.querySelector('#mg').textContent)",5)
    ok('Slot UI','controls re-enabled after the spin',pg.evaluate("['sp','bm','bp'].every(i=>!document.getElementById(i).disabled)"))
    gi=[[0,1,2],[3,1,4],[5,1,6]] # middle row: 3 diamonds (index 1) on line 1 only
    seq(pg,[rfor(gi[c][r]) for c in range(3) for r in range(3)]);pg.click('#sp');until(pg,"/won|No win/.test(document.querySelector('#mg').textContent)",5)
    ok('Slot UI','winning payline is lit and drawn (1 line)',pg.locator('.pln.on').count()==1 and pg.locator('#plov polyline').count()==1,pg.locator('.pln.on').count())
    ok('Slot UI','winning cells highlighted (3)',pg.locator('.cell.w').count()==3)
    pg.click('#ptb');ok('Dialog','paytable dialog opens with 7 symbols and 5 payline diagrams',pg.locator('#modal:not([hidden])').count()==1 and pg.locator('.pt-grid > div').count()==7 and pg.locator('.pl-grid > div').count()==5)
    pg.keyboard.press('Escape');ok('Dialog','Escape closes the dialog',pg.locator('#modal[hidden]').count()==1)
    pg.click('#info');pg.click('#modal-x');ok('Dialog','info button + X close work',pg.locator('#modal[hidden]').count()==1)
    pg.context.close()
    # Wheel: final rotation agrees with reported segment (visual == logic)
    for sym in ['🍉','🥭','7️⃣']:
        pg=newpage(b);pg.click('[data-g=wheel]');ix=idx_for(sym);setrng(pg,(ix+.5)/N);until(pg,"document.querySelector('#mg').textContent=='Spinning...'",5)
        until(pg,"/Result/.test(document.querySelector('#mg').textContent)",6)
        rot=pg.evaluate("parseFloat(document.querySelector('#wh').style.transform.replace(/[^0-9.-]/g,''))");seg=round((((-rot)%360)+360)%360/(360/N))%N
        ok('Wheel UI',f'{sym}: wheel stops with the winning section under the pointer',seg==ix,f'seg {seg} vs {ix}')
        ok('Wheel UI',f'{sym}: highlighted wedge is the reported one',pg.evaluate(f"document.querySelector('#wg{ix}').classList.contains('wn')") and pg.locator('.wg.wn').count()==1)
        pg.context.close()
    # Wheel/greedy total-bet readout
    pg=newpage(b);pg.click('[data-g=wheel]');pg.click('.chip[data-v="50"]');pg.click('.bx[data-i="0"]');pg.click('.bx[data-i="2"]');pg.click('.bx[data-i="2"]')
    ok('Wheel UI','total bet readout = 150 and chip readout = 50',pg.inner_text('#tbt')=='150' and pg.inner_text('#cv')=='50')
    pg.context.close()
    pg=newpage(b);pg.click('[data-g=greedy]');pg.click('.chip[data-v="100"]');pg.click('.fd[data-i="1"]');pg.click('.fd[data-i="6"]')
    ok('GreedyBaby UI','total bet readout = 200',pg.inner_text('#tbt')=='200');pg.context.close()
    # Profile: reset needs confirmation; Cancel keeps data
    pg=newpage(b);pg.click('#add');pg.click('.nav [data-t=profile]');pg.click('#rs');ok('Profile','reset asks for confirmation (dialog shown)',pg.locator('#modal:not([hidden])').count()==1)
    pg.click('#modal-f .btn.ghost');ok('Profile','Cancel keeps balance and history',W(pg)==6000 and pg.evaluate('ST.tx.length')==1)
    pg.click('#rs');pg.click('#modal-ok');ok('Profile','Confirm resets and shows success toast',W(pg)==5000 and 'reset' in pg.inner_text('#toast').lower())
    pg.context.close()
    # Android back button (history) closes game / panel
    pg=newpage(b);pg.click('[data-g=slot]');pg.go_back();pg.wait_for_timeout(120)
    ok('Navigation','browser/Android back closes an open game',not pg.evaluate("document.getElementById('gv').classList.contains('on')"))
    pg.click('.nav [data-t=wallet]');pg.go_back();pg.wait_for_timeout(120)
    ok('Navigation','back closes the Wallet panel and Home tab is active',not pg.evaluate("document.getElementById('pv').classList.contains('on')") and pg.evaluate("document.querySelector('.nav .on').dataset.t")=='home')
    pg.click('[data-g=wheel]');pg.click('#close');pg.wait_for_timeout(120);pg.click('[data-g=greedy]');pg.wait_for_timeout(60)
    ok('Navigation','open/close/open quickly keeps the new game open (no stale back event)',pg.evaluate("document.getElementById('gv').classList.contains('on')"))
    pg.context.close()
    # Rapid screen switching never leaves two things active
    pg=newpage(b);bad_=0
    for t in ['wallet','profile','home','games','wallet','home','profile','games']*3:
        pg.click(f'.nav [data-t={t}]')
        if pg.locator('.nav .on').count()!=1:bad_+=1
    pg.click('[data-g=slot]');pg.click('#close');pg.click('[data-g=greedy]');pg.click('#close')
    ok('Navigation','24 rapid tab switches + game open/close: always exactly one active tab',bad_==0 and pg.locator('.game.on').count()==0,bad_)
    pg.context.close()
    # Missing / corrupt local data
    ctx=b.new_context(viewport={'width':360,'height':640},is_mobile=True,has_touch=True)
    ctx.add_init_script("localStorage.setItem('sp_st','{\"tx\":5,\"h\":7,\"n\":\"x\",\"b\":null,\"id\":42}');localStorage.setItem('la_w','abc')")
    pg=ctx.new_page();errs0=len(ERR);pg.on('pageerror',lambda e:ERR.append(str(e)));pg.goto(URL);pg.wait_for_timeout(150)
    pg.click('.nav [data-t=wallet]');pg.click('#pc');pg.click('.nav [data-t=profile]');pg.click('#pc');pg.click('[data-g=wheel]');pg.click('#close')
    ok('Robustness','corrupt saved data does not crash: balance falls back to 5000, panels and games still open',W(pg)==5000 and len(ERR)==errs0 and pg.evaluate("Array.isArray(ST.tx)&&/^[0-9]{6}$/.test(ST.id)"),ERR[errs0:errs0+2])
    ctx.close()
    ctx=b.new_context(viewport={'width':360,'height':640},is_mobile=True,has_touch=True);ctx.add_init_script("localStorage.setItem('la_w','-50')")
    pg=ctx.new_page();pg.goto(URL);pg.wait_for_timeout(100);ok('Robustness','negative saved balance is rejected',W(pg)==5000);ctx.close()
    # Touch-target sizes and reduced motion at 360 wide
    pg=newpage(b,360,740);pg.click('[data-g=wheel]')
    mins=pg.evaluate("[...document.querySelectorAll('.chip,#close,#sb,#info,.bx')].map(e=>{var r=e.getBoundingClientRect();return Math.min(r.width,r.height)})")
    ok('Accessibility','chips, header buttons and bet boxes are at least 40px touch targets',min(mins)>=40,min(mins))
    ok('Accessibility','game status message is a polite live region',pg.evaluate("document.getElementById('mg').getAttribute('aria-live')")=='polite')
    pg.context.close()
    # ---------------- LAYOUT ----------------
    sizes=[(320,568),(360,640),(375,667),(390,844),(412,915),(430,932),(768,1024),(640,360)]
    for vw,vh in sizes:
        pg=newpage(b,vw,vh);bad=[]
        def chk(label):
            r=pg.evaluate("""()=>{var bad=[],vw=innerWidth;document.querySelectorAll('.chip,.btn,.bx,.fd,.g,.nav button,.reel,.wheel,.x,.stat div,.ban,.tx li,.hist,.mid,.cab,.betbar,.bsum>span,.ring,.bal2,.prof,.setrow,.ez button,.wal,.hb').forEach(e=>{var r=e.getBoundingClientRect();if(r.width&&(r.left<-1||r.right>vw+1))bad.push(e.className+':'+Math.round(r.left)+'-'+Math.round(r.right))});return {bad:bad,sx:document.documentElement.scrollWidth>vw}}""")
            if r['bad'] or r['sx']:bad.append((label,r))
        chk('home')
        if (vw,vh) in [(360,640),(320,568),(390,844),(430,932),(768,1024),(640,360)]:pg.screenshot(path=f'{OUT}/L_home_{vw}.png')
        for g in ['slot','wheel','greedy']:
            pg.click(f'[data-g={g}]');pg.wait_for_timeout(150);chk(g)
            if (vw,vh) in [(360,640),(320,568),(390,844),(430,932),(768,1024),(640,360)]:pg.screenshot(path=f'{OUT}/L_{g}_{vw}.png')
            if g!='slot':
                # chips visible + reachable
                el=pg.evaluate("(()=>{var c=document.querySelector('.chips');c.scrollIntoView({block:'nearest'});var r=c.getBoundingClientRect();return r.top>=-1&&r.bottom<=innerHeight+2})()")
                if not el:bad.append((g,'chips not reachable by scrolling'))
            pg.click('#close')
        for t in ['wallet','profile']:
            pg.click(f'.nav [data-t={t}]');chk(t);pg.click('#pc')
        ok('Layout',f'{vw}x{vh}: nothing cut off, no sideways scroll (home, 3 games, wallet, profile)',not bad,bad[:2]);pg.context.close()
    ok('Errors','no JavaScript errors in the whole run',not ERR,ERR[:3])
    b.close()
tot=len(R);ps=sum(1 for r in R if r[2])
print(f'{ps}/{tot} passed')
for a,n,c,d in R:
    if not c:print('FAIL',a,'|',n,'|',d)
json.dump(R,open(OUT+'/results.json','w'))
