/* Core: helpers, wallet, state, navigation, dialogs, Wallet/Profile panels.
   NOTE: all balances and results are computed and stored on the device (localStorage).
   That is fine for this test/demo phase but must NEVER be used to secure real money. */
var APP_VER='1.1.0';
var IM={'7️⃣':'seven','💎':'gem','🔔':'bell','🍇':'grape','🍉':'melon','🍊':'orange','🍒':'cherry','🥭':'mango','🍎':'apple','🍋':'lemon','🍓':'straw','🐟':'fish','🍔':'burger','🍕':'pizza','🍗':'chicken'},NN={'🍉':'Watermelon','🥭':'Mango','7️⃣':'77','🍎':'Apple','🍋':'Lemon','🍓':'Strawberry','🐟':'Fish','🍔':'Burger','🍕':'Pizza','🍗':'Chicken','💎':'Diamond','🔔':'Bell','🍇':'Grapes','🍊':'Orange','🍒':'Cherry'};
function ic(e){var k=IM[e];return k?'<svg class="ic" aria-hidden="true"><use href="#i-'+k+'"/></svg>':e}
function histHTML(a){return a.map(function(e){return '<span class="hi" title="'+(NN[e]||'')+'">'+ic(e)+'</span>'}).join('')}

var $=function(s,r){return(r||document).querySelector(s)},$$=function(s,r){return[].slice.call((r||document).querySelectorAll(s))};
var wallet=5000,timers=[],cleanup=null,today={};
try{var sv=localStorage.getItem('la_w');if(sv!==null&&isFinite(+sv)&&+sv>=0)wallet=Math.round(+sv)}catch(e){}
function fmt(n){return n>=1000?(n/1000)+'K':String(n)}
function money(n){return n.toLocaleString('en-IN')}
function setW(n){wallet=Math.max(0,Math.round(n));$$('.bal').forEach(function(e){e.textContent=money(wallet)});try{localStorage.setItem('la_w',wallet)}catch(e){}}
function toast(t,kind){var e=$('#toast');e.textContent=t;e.className='toast '+(kind||'');e.style.display='block';clearTimeout(toast.t);toast.t=setTimeout(function(){e.style.display='none'},2200)}
function later(f,ms){var t=setTimeout(f,ms);timers.push(t);return t}
function every(f,ms){var t=setInterval(f,ms);timers.push(t);return t}
function stopAll(){timers.forEach(function(t){clearTimeout(t);clearInterval(t)});timers=[]}
var RNG=function(){return Math.random()};
function pickW(a){var s=0,i;a.forEach(function(x){s+=x.w});var r=RNG()*s;for(i=0;i<a.length;i++){r-=a[i].w;if(r<0)return a[i]}return a[0]}
function rnd(n){return Math.floor(RNG()*n)}
setW(wallet);

/* ---- state (saved to localStorage under sp_st), sound ---- */
var ST={n:0,b:0,w:0,tx:[],snd:1,id:''};
try{var parsed=JSON.parse(localStorage.getItem('sp_st')||'{}');if(parsed&&typeof parsed==='object')ST=Object.assign(ST,parsed)}catch(e){}
/* sanitise whatever came back from storage so corrupt or missing data can never crash the UI */
['n','b','w'].forEach(function(k){ST[k]=isFinite(+ST[k])?+ST[k]:0});
if(!Array.isArray(ST.tx))ST.tx=[];ST.tx=ST.tx.filter(function(x){return x&&typeof x==='object'&&isFinite(+x.a)});
if(!ST.h||typeof ST.h!=='object')ST.h={};ST.h.wheel=Array.isArray(ST.h.wheel)?ST.h.wheel:[];ST.h.greedy=Array.isArray(ST.h.greedy)?ST.h.greedy:[];
var tdk=new Date().toDateString();if(ST.tdk!==tdk){ST.tdk=tdk;ST.td={}}if(!ST.td||typeof ST.td!=='object')ST.td={};today=ST.td;
if(!/^\d{6}$/.test(String(ST.id)))ST.id=String(100000+rnd(900000));
function save(){try{localStorage.setItem('sp_st',JSON.stringify(ST))}catch(e){}}
function txn(k,g,a){ST.tx.unshift({k:k,g:g,a:a,t:Date.now(),b:wallet});ST.tx=ST.tx.slice(0,60);if(k=='Bet'){ST.b+=a;ST.n++}else if(k=='Win')ST.w+=a;else if(k=='Refund')ST.b-=a;save()}
var AC;function snd(f,d,t){if(!ST.snd)return;try{AC=AC||new(window.AudioContext||window.webkitAudioContext)();var o=AC.createOscillator(),g=AC.createGain();o.type=t||'sine';o.frequency.value=f;g.gain.value=.08;o.connect(g);g.connect(AC.destination);o.start();g.gain.exponentialRampToValueAtTime(.0001,AC.currentTime+d);o.stop(AC.currentTime+d)}catch(e){}}
$('.who small').textContent='Guest · ID '+ST.id;save();
function sbIcon(){var u=$('#sb use');u.setAttribute('href',ST.snd?'#u-sound':'#u-mute');$('#sb').setAttribute('aria-pressed',ST.snd?'false':'true');$('#sb').setAttribute('aria-label',ST.snd?'Sound on. Tap to mute':'Sound off. Tap to unmute')}
$('#sb').onclick=function(){ST.snd=ST.snd?0:1;save();sbIcon();snd(600,.1)};sbIcon();
window.onerror=function(){toast('Something went wrong. Please try again.','err')};

/* ---- dialogs ---- */
var modalOpener=null;
function modalOpen(){return !$('#modal').hidden}
function openModal(o){var m=$('#modal');modalOpener=document.activeElement;$('#modal-t').textContent=o.title;$('#modal-b').innerHTML=o.html||'';var f=$('#modal-f');f.innerHTML='';
 (o.buttons||[]).forEach(function(b){var e=document.createElement('button');e.className='btn '+(b.cls||'');e.textContent=b.label;if(b.id)e.id=b.id;e.onclick=function(){closeModal();if(b.fn)b.fn()};f.appendChild(e)});
 f.style.display=(o.buttons||[]).length?'':'none';m.hidden=false;var box=$('.modal-box',m);box.scrollTop=0;$('#modal-b').scrollTop=0;
 var first=$('#modal-f .btn')||$('#modal-x');(first||box).focus()}
function closeModal(){var m=$('#modal');if(m.hidden)return;m.hidden=true;try{if(modalOpener&&modalOpener.focus)modalOpener.focus()}catch(e){}modalOpener=null}
$('#modal-x').onclick=closeModal;
$('#modal').onclick=function(e){if(e.target===this)closeModal()};
document.addEventListener('keydown',function(e){if(!modalOpen())return;if(e.key==='Escape'){closeModal();return}
 if(e.key==='Tab'){var f=$$('#modal button').filter(function(b){return b.offsetParent!==null});if(!f.length)return;var a=f[0],z=f[f.length-1];if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}}});
function confirmBox(o,ok){openModal({title:o.title,html:'<p class="mp">'+o.msg+'</p>',buttons:[{label:o.cancel||'Cancel',cls:'ghost'},{label:o.ok||'OK',cls:o.danger?'danger':'',id:'modal-ok',fn:ok}]})}

/* ---- Android back button support: each opened game/panel pushes one history entry ---- */
var pushed=0,skipPops=0;
function pushView(){try{history.pushState({sp:1},'');pushed++}catch(e){}}
function popView(){if(pushed>0){pushed--;skipPops++;try{history.back()}catch(e){skipPops--}}}
window.addEventListener('popstate',function(){
 if(skipPops>0){skipPops--;return}
 if(pushed>0)pushed--;
 if(modalOpen()){closeModal();try{history.pushState({sp:1},'');pushed++}catch(e){}return}
 if($('#gv').classList.contains('on'))closeGame(true);
 else if($('#pv').classList.contains('on'))panel('home',true)});

/* ---- navigation ---- */
$('#add').onclick=function(){addCredit()};
$('#claim').onclick=function(){addCredit()};
function addCredit(){setW(wallet+1000);txn('Test credit','Wallet',1000);toast('Added ₹1,000 test balance','ok');if($('#pv').classList.contains('on')&&$('#pt').textContent==='Wallet')panel('wallet',false,true)}
$$('.g').forEach(function(c){c.onclick=function(){open(c.dataset.g)}});
$$('[data-soon]').forEach(function(b){b.onclick=function(){toast('Coming soon')}});
function closeGame(fromPop){stopAll();if(cleanup)cleanup();cleanup=null;$('#gv').classList.remove('on');$('#homeV').style.display='';if(!fromPop)popView()}
$('#close').onclick=function(){closeGame()};
var LOGO={slot:'lucky777',wheel:'super77pro',greedy:'greedybaby'};
function open(g){if($('#gv').classList.contains('on'))return;stopAll();closeModal();$('#gl').src='assets/'+LOGO[g]+'.webp';$('#gv').className='game on g-'+g;$('#gv').dataset.g=g;$('#homeV').style.display='none';pushView();var gb=$('#gb');gb.innerHTML='';gb.scrollTop=0;({slot:slot,wheel:wheel,greedy:greedy})[g](gb)}
$('#info').onclick=function(){var g=$('#gv').dataset.g;if(typeof helpFor==='function')helpFor(g)};

/* ---- shared betting chips ---- */
var CHIPS=[[5,'#7a4fd0'],[10,'#17a2b8'],[50,'#1fa855'],[100,'#2a6fd4'],[500,'#e8761a'],[1000,'#d8322f']];
function chipsHTML(){return '<div class="chips" role="radiogroup" aria-label="Chip value">'+CHIPS.map(function(c,i){return '<button class="chip'+(i==1?' sel':'')+'" data-v="'+c[0]+'" style="--c:'+c[1]+'" role="radio" aria-checked="'+(i==1)+'" aria-label="Chip '+c[0]+'"><span>'+fmt(c[0])+'</span></button>'}).join('')+'</div>'}
function chipPick(root){var v=10;$$('.chip',root).forEach(function(b){b.onclick=function(){$$('.chip',root).forEach(function(x){x.classList.remove('sel');x.setAttribute('aria-checked','false')});b.classList.add('sel');b.setAttribute('aria-checked','true');v=+b.dataset.v;var l=$('#cv',root);if(l)l.textContent=money(v)}});return function(){return v}}

/* ---- game rules dialogs (generated from RULES so they always match the real payouts) ---- */
var LINE_NAMES=['Middle','Top','Bottom','Diagonal ↘','Diagonal ↗'];
function lineSVG(L){var p=L.map(function(r,c){return (12+c*18)+','+(7+r*12)}).join(' ');return '<svg class="mini" viewBox="0 0 60 40" aria-hidden="true">'+[0,1,2].map(function(c){return [0,1,2].map(function(r){return '<rect x="'+(c*18+4)+'" y="'+(r*12+2)+'" width="16" height="10" rx="2" class="'+(L[c]===r?'on':'')+'"/>'}).join('')}).join('')+'<polyline points="'+p+'"/></svg>'}
function helpFor(g){var R=RULES[g],h='',t='';
 if(g==='slot'){t='Lucky777 paytable';
  h='<p class="mp">Match <b>3 identical symbols</b> on any payline. Your total bet is split evenly across <b>5 paylines</b>, and each line pays its multiplier × line bet (total bet ÷ 5).</p><div class="pt-grid">'+R.sym.map(function(s){return '<div>'+ic(s.s)+'<b>×'+s.m+'</b></div>'}).join('')+'</div><h4>Paylines</h4><div class="pl-grid">'+R.lines.map(function(L,i){return '<div>'+lineSVG(L)+'<small>'+(i+1)+'. '+LINE_NAMES[i]+'</small></div>'}).join('')+'</div><p class="mp">Example: a bet of ₹10 puts ₹2 on each line. Three 77 symbols on one line pays 200 × ₹2 = ₹400.</p>'}
 else if(g==='wheel'){t='Super77Pro rules';var cnt={};R.seg.forEach(function(s){cnt[s]=(cnt[s]||0)+1});
  h='<p class="mp">Place chips on one or more boxes during the betting time. When the timer ends the wheel spins and the section under the pointer wins.</p><div class="pt-grid three">'+R.box.map(function(b){return '<div>'+ic(b.k)+'<b>×'+b.m+'</b><small>'+cnt[b.k]+' of '+R.seg.length+' sections</small></div>'}).join('')+'</div><p class="mp">A winning box pays your chips on it × the multiplier. Bets stay open only while the timer runs.</p>'}
 else{t='GreedyBaby rules';
  h='<p class="mp">Place chips on any of the 8 foods during the betting time. When the timer ends the light runs around the board and stops on the winner.</p><div class="pt-grid">'+R.foods.map(function(f){return '<div>'+ic(f.e)+'<b>×'+f.m+'</b><small>'+NN[f.e]+'</small></div>'}).join('')+'</div><p class="mp">A winning food pays your chips on it × its multiplier. Rarer foods pay more.</p>'}
 openModal({title:t,html:h+'<p class="mp fine">Test mode: coins are virtual.</p>',buttons:[{label:'Got it'}]})}

/* ---- Wallet / Profile panels ---- */
var KIND={'Bet':{l:'Bet placed',c:'t-bet',s:'−',i:'u-down'},'Win':{l:'Win',c:'t-win',s:'+',i:'u-up'},'Refund':{l:'Refund',c:'t-ref',s:'+',i:'u-reset'},'Test credit':{l:'Test credit',c:'t-credit',s:'+',i:'u-plus'}};
function statsHTML(){var net=ST.w-ST.b;return '<div class="stat4"><div><b>'+ST.n+'</b><i>Bets placed</i></div><div><b>₹'+money(ST.b)+'</b><i>Wagered</i></div><div><b>₹'+money(ST.w)+'</b><i>Won</i></div><div><b class="'+(net>=0?'pos':'neg')+'">'+(net>=0?'+':'−')+'₹'+money(Math.abs(net))+'</b><i>Net result</i></div></div>'}
function txRow(x){var d=new Date(x.t),k=KIND[x.k]||{l:x.k,c:'t-ref',s:'+',i:'u-plus'},td=new Date().toDateString()===d.toDateString()?'':d.toLocaleDateString([],{day:'numeric',month:'short'})+' · ';
 return '<li class="'+k.c+'"><span class="ti"><svg class="ui"><use href="#'+k.i+'"/></svg></span><div><b>'+k.l+'</b><small>'+x.g+' · '+td+d.toLocaleTimeString([],{hour:'2-digit',minute:'2-digit'})+'</small></div><span class="amt '+(k.s=='−'?'neg':'pos')+'">'+k.s+'₹'+money(x.a)+'<small>Bal ₹'+money(+x.b||0)+'</small></span></li>'}
function panel(t,fromPop,keep){var p=$('#pv'),b=$('#pb'),was=p.classList.contains('on');
 $$('.nav button').forEach(function(x){var on=x.dataset.t==t;x.classList.toggle('on',on);if(on)x.setAttribute('aria-current','page');else x.removeAttribute('aria-current')});
 if(t=='home'||t=='games'){p.classList.remove('on');if(was&&!fromPop)popView();if(t=='games')$('.gm').scrollIntoView({behavior:'smooth',block:'start'});else $('.hs').scrollTo({top:0,behavior:'smooth'});return}
 if(!was)pushView();p.classList.add('on');$('#pt').textContent=t=='wallet'?'Wallet':'Profile';if(!keep)b.scrollTop=0;
 if(t=='wallet'){var h=ST.tx.map(txRow).join('');
  b.innerHTML='<div class="bal2"><span>Virtual test balance</span><b class="bal bigbal">'+money(wallet)+'</b><small><svg class="ui"><use href="#u-lock"/></svg>Test coins only. Not real money and cannot be withdrawn.</small></div>'+statsHTML()+'<button class="btn big" id="ad"><svg class="ui"><use href="#u-plus"/></svg>Add ₹1,000 test balance</button><h3 class="sec">Transaction history</h3>'+(h?'<ul class="tx">'+h+'</ul>':'<p class="empty">No transactions yet. Play a game to see your history here.</p>');
  $('#ad').onclick=function(){addCredit()}}
 else{b.innerHTML='<div class="prof"><img class="av" src="assets/logo-192.png" alt="" width="56" height="56"><div><b>Guest player</b><small>Player ID '+ST.id+'</small></div><span class="tag">Test account</span></div>'+statsHTML()+
  '<h3 class="sec">Preferences</h3><div class="setrow"><div><b>Sound effects</b><small>Bet clicks and win chimes</small></div><button class="sw'+(ST.snd?' on':'')+'" id="sn" role="switch" aria-checked="'+(ST.snd?'true':'false')+'" aria-label="Sound effects: '+(ST.snd?'On':'Off')+'"><i></i><span>'+(ST.snd?'On':'Off')+'</span></button></div>'+
  '<h3 class="sec">Data</h3><div class="setrow"><div><b>Reset test data</b><small>Restores your balance to ₹5,000 and clears history, totals and results.</small></div><button class="btn danger sm" id="rs"><svg class="ui"><use href="#u-reset"/></svg>Reset</button></div>'+
  '<h3 class="sec">About</h3><div class="about"><p><b>Super77Pro</b> · version '+APP_VER+'</p><p>Test mode: balances and game results are generated and stored on this device only. Real deposits and withdrawals are not available.</p></div>';
  $('#sn').onclick=function(){ST.snd=ST.snd?0:1;save();sbIcon();panel('profile',false,true)};
  $('#rs').onclick=function(){confirmBox({title:'Reset test data?',msg:'This sets your balance back to ₹5,000 and permanently clears your transaction history, totals and recent results.',ok:'Reset data',danger:true},function(){
   ST.n=ST.b=ST.w=0;ST.tx=[];ST.td={};today=ST.td;ST.h={wheel:[],greedy:[]};save();setW(5000);panel('profile',false,true);toast('Test data reset. Balance is ₹5,000.','ok')})}}}
$$('.nav button').forEach(function(b){b.onclick=function(){panel(b.dataset.t)}});
$('#pc').onclick=function(){panel('home')};
