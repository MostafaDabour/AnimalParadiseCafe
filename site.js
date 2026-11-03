(function(){
  // Always land at the top of a new page.
  try{ if('scrollRestoration' in history) history.scrollRestoration='manual'; }catch(e){}
  if(!location.hash) window.scrollTo(0,0);

  // Open now status, Vineland time. Open 4:00 to 24:00 every day.
  try{
    var h=+new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',hour:'numeric',hour12:false}).format(new Date())%24;
    var open=h>=4;
    document.querySelectorAll('[data-open]').forEach(function(el){
      el.textContent=open?'Open now · until 12AM':'Closed now · opens at 4AM';
      el.classList.toggle('is-open',open);
    });
  }catch(e){}

  // Mobile menu
  var btn=document.getElementById('menuBtn'),nav=document.getElementById('nav');
  if(btn&&nav){btn.addEventListener('click',function(){var o=nav.classList.toggle('open');btn.setAttribute('aria-expanded',o);btn.textContent=o?'Close':'Menu';});}

  // Menu board filter
  var tabs=document.querySelectorAll('.tab');
  tabs.forEach(function(t){t.addEventListener('click',function(){
    var f=t.getAttribute('data-filter');
    tabs.forEach(function(x){var on=x===t;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on);});
    document.querySelectorAll('.mb').forEach(function(s){s.hidden=!(f==='all'||s.getAttribute('data-cat')===f);});
  });});

  // Order popup: branded hand-off to Clover checkout (Clover blocks being framed)
  var om=document.getElementById('orderModal'),lastFocus=null;
  function openOM(e){ if(!om) return; if(e){e.preventDefault();} lastFocus=document.activeElement; om.hidden=false; document.body.classList.add('om-open'); var p=om.querySelector('.om-panel'); p&&p.focus(); try{ if(window.fbq) fbq('track','InitiateCheckout'); }catch(x){} }
  function closeOM(){ if(!om||om.hidden) return; om.hidden=true; if(location.hash==='#order'){ try{ history.replaceState(null,'',location.pathname+location.search); }catch(x){} } document.body.classList.remove('om-open'); if(lastFocus&&lastFocus.focus) lastFocus.focus(); }
  document.addEventListener('click',function(e){
    var t=e.target.closest&&e.target.closest('[data-order]'); if(t&&!om.contains(t)){ openOM(e); return; }
    if(e.target.closest&&e.target.closest('[data-close]')) closeOM();
  });
  if(location.hash==='#order') setTimeout(function(){openOM();},300);
  window.addEventListener('hashchange',function(){ if(location.hash==='#order') openOM(); });
  document.addEventListener('click',function(e){
    if(om&&!om.hidden&&e.target.closest&&e.target.closest('.om-panel a[target]')) setTimeout(closeOM,150);
  });
  document.addEventListener('keydown',function(e){
    if(!om||om.hidden) return;
    if(e.key==='Escape'){ closeOM(); return; }
    if(e.key==='Tab'){ var f=om.querySelectorAll('a,button'); if(!f.length) return; var a=f[0],z=f[f.length-1];
      if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus();} else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus();} }
  });

  // Bowl builder
  var b=document.getElementById('builder');
  if(!b) return;
  var SW={'Açaí':'#4B1D66','Pitaya':'#E0337E','Mango':'#FFB01F','Passion fruit':'#F28C28','Coconut':'#EFE6D8','Banana':'#F4D96B'};
  var LINK={single:'https://animal-cafe.cloveronline.com/menu/build-your-own-bowl-EFH18GTNEDRMT',split:'https://animal-cafe.cloveronline.com/menu/build-your-split-base-bowl-CQRF8J3VPT8GC'};
  var type='single',bases=['Açaí'];
  var fmt=function(n){return '$'+n.toFixed(2);};
  function checked(name){return Array.prototype.map.call(b.querySelectorAll('input[name="'+name+'"]:checked'),function(i){return i.value;});}
  function render(){
    var max=type==='split'?2:1;
    while(bases.length>max) bases.shift();
    b.querySelectorAll('.base-pick').forEach(function(p){p.setAttribute('aria-pressed',bases.indexOf(p.dataset.base)>-1);});
    document.getElementById('baseHint').textContent=type==='split'?'Choose 2':'Choose 1';
    var fruit=checked('fruit'),crunch=checked('crunch'),drizzle=checked('drizzle'),extra=checked('extra');
    var start=type==='split'?11.99:10.49;
    var xf=Math.max(0,fruit.length-2),xd=Math.max(0,drizzle.length-1);
    var total=start+xf*1.25+crunch.length*.75+xd*.5+extra.length*.75;
    var L=[[ (type==='split'?'Split base: ':'Base: ')+(bases.join(' + ')||'pick one'), fmt(start)],['Granola','included']];
    L.push(['Fruit: '+(fruit.join(', ')||'pick up to 2'), xf?('+'+fmt(xf*1.25)):'included']);
    if(crunch.length) L.push(['Crunch: '+crunch.join(', '),'+'+fmt(crunch.length*.75)]);
    L.push(['Drizzle: '+(drizzle.join(', ')||'pick 1'), xd?('+'+fmt(xd*.5)):'included']);
    if(extra.length) L.push(['Extras: '+extra.join(', '),'+'+fmt(extra.length*.75)]);
    var ul=document.getElementById('bLines');ul.innerHTML='';
    L.forEach(function(r){var li=document.createElement('li');var a=document.createElement('span');a.textContent=r[0];var c=document.createElement('span');c.textContent=r[1];li.appendChild(a);li.appendChild(c);ul.appendChild(li);});
    document.getElementById('bTotal').textContent=fmt(total);
    document.getElementById('bOrder').href=LINK[type];
    var viz=document.getElementById('bowlViz').children;
    viz[0].style.background=SW[bases[0]]||'#4B1D66';
    viz[1].style.background=SW[bases[1]||bases[0]]||'#4B1D66';
  }
  b.querySelectorAll('.seg-btn').forEach(function(s){s.addEventListener('click',function(){
    type=s.dataset.type;b.querySelectorAll('.seg-btn').forEach(function(x){var on=x===s;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on);});render();});});
  b.querySelectorAll('.base-pick').forEach(function(p){p.addEventListener('click',function(){
    var n=p.dataset.base,i=bases.indexOf(n);
    if(i>-1){ if(bases.length>1) bases.splice(i,1); } else { bases.push(n); }
    render();});});
  b.addEventListener('change',render);
  render();
})();
