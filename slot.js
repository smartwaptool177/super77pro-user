/* ---------- Lucky777 ---------- */
function slot(gb){
 var SY=RULES.slot.sym,LN=RULES.slot.lines,BETS=[5,10,50,100,500,1000],bi=1,busy=false,auto=false,dead=false,tw=today.slot||0,pend=null,g=[[],[],[]];
 var LC=['#ffd84d','#4de1ff','#ff7ad9','#7dff7a','#ff9a4d'];
 var bulbs='';for(var k=0;k<14;k++)bulbs+='<i style="--d:'+(k%2)+'"></i>';
 gb.innerHTML='<div class="stat"><div><b id="tw">'+money(tw)+'</b><i>Today\'s win</i></div><div><b id="lw">0</b><i>Last win</i></div></div>'+
  '<div class="cab"><div class="mq"><div class="bulbs" aria-hidden="true">'+bulbs+'</div><b>LUCKY <span>777</span></b></div>'+
  '<div class="rw"><div class="reels">'+[0,1,2].map(function(){return '<div class="reel"><div class="cell"></div><div class="cell"></div><div class="cell"></div></div>'}).join('')+'</div>'+
  '<svg class="plov" id="plov" viewBox="0 0 3 3" preserveAspectRatio="none" aria-hidden="true"></svg></div>'+
  '<div class="plines" aria-label="Paylines"><em>Paylines</em>'+LN.map(function(L,i){return '<span class="pln" data-i="'+i+'" style="--lc:'+LC[i]+'">'+(i+1)+'</span>'}).join('')+'<button class="lnk" id="ptb" aria-label="Open paytable"><svg class="ui"><use href="#u-info"/></svg>Paytable</button></div></div>'+
  '<div class="msg" id="mg" role="status" aria-live="polite">Press spin to play</div>'+
  '<div class="betbar" id="bb"><button class="rbtn" id="bm" aria-label="Decrease bet"><svg class="ui"><use href="#u-minus"/></svg></button><div class="betv"><i>Total bet</i><b>₹<span id="tb">'+money(BETS[bi])+'</span></b><small>₹<span id="lb">'+money(BETS[bi]/5)+'</span> on each of 5 lines</small></div><button class="rbtn" id="bp" aria-label="Increase bet"><svg class="ui"><use href="#u-plus"/></svg></button></div>'+
  '<div class="row"><button class="btn auto" id="au" aria-pressed="false"><svg class="ui"><use href="#u-auto"/></svg>AUTO</button><button class="btn big spin" id="sp">SPIN</button></div>';
 var reels=$$('.reel',gb),ov=$('#plov',gb);
 function cells(c){return $$('.cell',reels[c])}
 function show(c){cells(c).forEach(function(e,r){e.innerHTML=ic(g[c][r]?g[c][r].s:SY[Math.floor(Math.random()*7)].s)})}
 function upd(){$('#tb',gb).textContent=money(BETS[bi]);$('#lb',gb).textContent=money(BETS[bi]/5);$('#bm',gb).classList.toggle('off',bi==0);$('#bp',gb).classList.toggle('off',bi==BETS.length-1)}
 function lock(on){['bm','bp','sp'].forEach(function(i){$('#'+i,gb).disabled=on});gb.classList.toggle('busy',on);$('#sp',gb).textContent=on?'SPINNING':'SPIN'}
 function msg(t,k){var m=$('#mg',gb);m.textContent=t;m.className='msg'+(k?' '+k:'')}
 function clearWin(){$$('.cell',gb).forEach(function(e){e.classList.remove('w')});$$('.pln',gb).forEach(function(e){e.classList.remove('on')});ov.innerHTML='';reels.forEach(function(r){r.classList.remove('land')})}
 function setAuto(v){auto=v;var a=$('#au',gb);a.classList.toggle('on',v);a.setAttribute('aria-pressed',v?'true':'false')}
 $('#bm',gb).onclick=function(){if(!busy){bi=Math.max(0,bi-1);upd()}};
 $('#bp',gb).onclick=function(){if(!busy){bi=Math.min(BETS.length-1,bi+1);upd()}};
 $('#au',gb).onclick=function(){setAuto(!auto);if(auto&&!busy)spin()};
 $('#sp',gb).onclick=function(){spin()};
 $('#ptb',gb).onclick=function(){helpFor('slot')};
 function spin(){
  var bet=BETS[bi];if(busy||dead)return;
  if(wallet<bet){setAuto(false);msg('Insufficient balance. Lower your bet or add test balance in Wallet.','err');var b=$('#bb',gb);b.classList.remove('shake');void b.offsetWidth;b.classList.add('shake');return}
  busy=true;lock(true);setW(wallet-bet);txn('Bet','Lucky777',bet);snd(300,.08);msg('Good luck!');$('#lw',gb).textContent='0';clearWin();
  var fin=[0,1,2].map(function(){return [pickW(SY),pickW(SY),pickW(SY)]}),done=0;pend={fin:fin,bet:bet};
  [0,1,2].forEach(function(c){reels[c].classList.add('spin');var iv=every(function(){g[c]=[];show(c)},70);
   later(function(){clearInterval(iv);reels[c].classList.remove('spin');reels[c].classList.add('land');g[c]=fin[c];show(c);snd(220+c*40,.05);if(++done==3)settle()},700+c*450)});
 }
 function settle(){
  if(!pend)return;var p=pend;pend=null;g=p.fin;[0,1,2].forEach(show);
  var r=RULES.slot.pay(g,p.bet),win=r.win;
  r.hit.forEach(function(h){cells(h[0])[h[1]].classList.add('w')});
  ov.innerHTML=r.wl.map(function(i){return '<polyline points="'+LN[i].map(function(row,c){return (c+.5)+','+(row+.5)}).join(' ')+'" style="stroke:'+LC[i]+'"/>'}).join('');
  r.wl.forEach(function(i){$('.pln[data-i="'+i+'"]',gb).classList.add('on')});
  if(win){setW(wallet+win);txn('Win','Lucky777',win);snd(880,.3);tw+=win;today.slot=tw;save();$('#tw',gb).textContent=money(tw);$('#lw',gb).textContent=money(win);msg('You won ₹'+money(win)+'!','win')}
  else{msg('No win. Try again.','lose')}
  busy=false;lock(false);if(auto&&!dead)later(spin,1100)}
 [0,1,2].forEach(function(c){g[c]=[pickW(SY),pickW(SY),pickW(SY)];show(c)});upd();
 cleanup=function(){dead=true;setAuto(false);settle()};
}
