
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
});
