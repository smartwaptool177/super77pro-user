/* Game rules: single source of truth for payouts. Tested for RTP in the test suite. */
var RULES={
 slot:{sym:[{s:'7️⃣',m:200,w:1},{s:'💎',m:100,w:2},{s:'🔔',m:60,w:3},{s:'🍇',m:40,w:4},{s:'🍉',m:32,w:5},{s:'🍊',m:26,w:6},{s:'🍒',m:18,w:7}],
  lines:[[1,1,1],[0,0,0],[2,2,2],[0,1,2],[2,1,0]],
  pay:function(g,bet){var win=0,hit=[],wl=[];this.lines.forEach(function(L,i){var a=g[0][L[0]],b=g[1][L[1]],c=g[2][L[2]];if(a.s==b.s&&b.s==c.s){win+=a.m*bet/5;hit.push([0,L[0]],[1,L[1]],[2,L[2]]);wl.push(i)}});return{win:win,hit:hit,wl:wl}}},
 wheel:{seg:['🍉','🥭','🍉','🥭','🍉','🥭','🍉','🥭','7️⃣'],box:[{k:'🍉',m:2},{k:'7️⃣',m:8},{k:'🥭',m:2}],
  pay:function(r,bets){var s=0;this.box.forEach(function(b,i){if(b.k==r)s+=bets[i]*b.m});return s}},
 greedy:{foods:[{e:'🍎',m:5,w:90},{e:'🍋',m:5,w:90},{e:'🍓',m:5,w:90},{e:'🥭',m:5,w:90},{e:'🐟',m:10,w:45},{e:'🍔',m:15,w:30},{e:'🍕',m:25,w:18},{e:'🍗',m:45,w:10}],
  pay:function(w,bets){return bets[w]*this.foods[w].m}}
};
