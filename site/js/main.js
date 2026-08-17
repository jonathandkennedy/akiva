
document.addEventListener('DOMContentLoaded',function(){
  var b=document.querySelector('.burger'),n=document.querySelector('nav.main');
  if(b&&n){b.addEventListener('click',function(){n.classList.toggle('open');b.classList.toggle('x');});
    n.querySelectorAll('a').forEach(function(a){a.addEventListener('click',function(){n.classList.remove('open');});});}
  document.querySelectorAll('.video-facade').forEach(function(v){
    v.addEventListener('click',function(){
      if(v.dataset.loaded)return;v.dataset.loaded='1';
      var f=document.createElement('iframe');
      f.src='https://player.vimeo.com/video/'+v.dataset.vid+'?autoplay=1';
      f.allow='autoplay; fullscreen; picture-in-picture';f.allowFullscreen=true;
      f.title=v.dataset.title||'Video';v.appendChild(f);
    });});
  // conversion tracking — no-ops if analytics isn't loaded
  function track(name,params){try{if(typeof gtag==='function'){gtag('event',name,params||{});}
    if(window.dataLayer){window.dataLayer.push(Object.assign({event:name},params||{}));}}catch(e){}}
  document.querySelectorAll('a[href^="tel:"]').forEach(function(a){
    a.addEventListener('click',function(){track('phone_call',{link_url:a.getAttribute('href')});});});
  document.querySelectorAll('a[href^="mailto:"]').forEach(function(a){
    a.addEventListener('click',function(){track('email_click',{});});});
  var cf=document.querySelector('.contact-form');
  if(cf){cf.addEventListener('submit',function(){track('generate_lead',{form:'contact'});});}
  // scroll reveals
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){
      if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}
    });},{threshold:.14,rootMargin:'0px 0px -6% 0px'});
    document.querySelectorAll('.reveal').forEach(function(el){io.observe(el);});
    // count-up stats
    var co=new IntersectionObserver(function(es){es.forEach(function(e){
      if(!e.isIntersecting)return;co.unobserve(e.target);
      var el=e.target,to=parseFloat(el.dataset.to||'0'),dec=parseInt(el.dataset.dec||'0',10),
          suf=el.dataset.suffix||'',t0=null,dur=1400;
      if(matchMedia('(prefers-reduced-motion: reduce)').matches){el.textContent=to.toFixed(dec)+suf;return;}
      requestAnimationFrame(function step(t){
        if(!t0)t0=t;var p=Math.min(1,(t-t0)/dur);p=1-Math.pow(1-p,3);
        el.textContent=(to*p).toFixed(dec)+suf;
        if(p<1)requestAnimationFrame(step);
      });
    });},{threshold:.5});
    document.querySelectorAll('.stat .num [data-to]').forEach(function(el){co.observe(el);});
  }else{
    document.querySelectorAll('.reveal').forEach(function(el){el.classList.add('in');});
  }
});
