/* ---------- GreedyBaby ---------- */
function greedy(gb){
 var F=RULES.greedy.foods,POS=[0,1,2,5,8,7,6,3],bets=[0,0,0,0,0,0,0,0],busy=false,dead=false,t=15,rd=0,pend=null,tw=today.greedy||0,hist=ST.h.greedy.slice(0,8);
 var html='';for(var p=0;p<9;p++){var k=POS.indexOf(p);html+=k<0?'<div class="mid"><div><span class="e"><svg class="ic" aria-hidden="true"><use href="#i-bear"/></svg></span><b id="cd">15</b><small id="ph">Bet time</small></div></div>':'<button class="fd tier'+(F[k].m>=25?3:F[k].m>=10?2:1)+'" data-i="'+k+'" aria-label="Bet on '+NN[F[k].e]+', pays x'+F[k].m+'"><span class="e">'+ic(F[k].e)+'</span><span class="m">x'+F[k].m+'</span></button>'}
 gb.innerHTML='<div class="stat"><div><b id="tw">'+money(tw)+'</b><i>Today\'s win</i></div><div><b id="rd">1</b><i>Round</i></div></div><div class="tbar" aria-hidden="true"><i id="tbr"></i></div><div class="ring" id="ring">'+html+'</div><div class="msg" id="mg" role="status" aria-live="polite">Choose the wager, then choose food</div><div class="bsum"><span>Chip <b>₹<span id="cv">10</span></b></span><span>Total bet <b>₹<span id="tbt">0</span></b></span></div>'+chipsHTML()+'<div class="hist"><em>Results</em><span id="hs">'+histHTML(hist)+'</span></div>';
 var cv=chipPick(gb),fds=$$('.fd',gb),byI={},mid=$('.mid',gb);fds.forEach(function(b){byI[b.dataset.i]=b});
 function tot(){return bets.reduce(function(a,b){return a+b},0)}
 function msg(s,k){var m=$('#mg',gb);m.textContent=s;m.className='msg'+(k?' '+k:'')}
 fds.forEach(function(b){b.onclick=function(){var i=+b.dataset.i,v=cv();if(busy)return toast('Drawing in progress. Betting is closed.');if(wallet<v)return toast('Insufficient balance','err');setW(wallet-v);txn('Bet','GreedyBaby',v);snd(300,.05);bets[i]+=v;mark(i);$('#tbt',gb).textContent=money(tot())}});
 function mark(i){var b=byI[i],m=$('.my',b);if(!m){m=document.createElement('span');m.className='my';b.appendChild(m)}m.textContent=fmt(bets[i]);b.classList.add('has')}
 function round(){if(dead)return;busy=false;gb.classList.remove('busy');mid.classList.remove('win');t=15;rd++;bets=[0,0,0,0,0,0,0,0];fds.forEach(function(b){b.classList.remove('win','hl','has');var m=$('.my',b);if(m)m.remove()});$('#tbt',gb).textContent='0';$('#ph',gb).textContent='Bet time';$('#cd',gb).textContent=t+'s';$('#rd',gb).textContent=rd;msg('Place your bets');$('#tbr',gb).style.transform='scaleX(1)';
  var iv=every(function(){t--;$('#cd',gb).textContent=t+'s';$('#tbr',gb).style.transform='scaleX('+Math.max(0,t)/15+')';if(t<=0){clearInterval(iv);go()}},1000)}
 function go(){busy=true;gb.classList.add('busy');$('#ph',gb).textContent='Drawing';$('#cd',gb).textContent='...';var w=pickW(F.map(function(f,i){return {w:f.w,i:i}})).i,last=24+w;pend={w:w,bets:bets.slice()};bets=[0,0,0,0,0,0,0,0];/* the round now owns these bets: closing the game must not refund them */
  (function tick(c){fds.forEach(function(b){b.classList.remove('hl')});byI[c%8].classList.add('hl');if(c>=last)return settle();later(function(){tick(c+1)},c>last-10?70+(c-(last-10))*30:70)})(0)}
 function settle(){
  if(!pend)return;var p=pend;pend=null;var w=p.w,win=RULES.greedy.pay(w,p.bets);
  fds.forEach(function(b){b.classList.remove('hl')});byI[w].classList.add('win');mid.classList.add('win');
  hist.unshift(F[w].e);hist=hist.slice(0,8);ST.h.greedy=hist;$('#hs',gb).innerHTML=histHTML(hist);$('#cd',gb).innerHTML=ic(F[w].e);$('#ph',gb).textContent='Result';
  if(win){setW(wallet+win);txn('Win','GreedyBaby',win);snd(880,.3);tw+=win;today.greedy=tw;$('#tw',gb).textContent=money(tw);msg(NN[F[w].e]+' won! You got ₹'+money(win),'win')}
  else msg(NN[F[w].e]+' was the winner'+(p.bets.some(Boolean)?'. No win this round.':''),p.bets.some(Boolean)?'lose':'');
  save();if(!dead)later(round,3200)}
 cleanup=function(){dead=true;if(pend)settle();else{var s=tot();if(s){setW(wallet+s);txn('Refund','GreedyBaby',s);bets=[0,0,0,0,0,0,0,0]}}};
 round();
}
