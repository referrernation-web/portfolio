# v31: the contact form sends from inside the game. FormSubmit's AJAX endpoint + fetch, so "Send message" no longer
# opens FormSubmit's thank-you page in a new tab; the visitor's email becomes Reply-To; _honey drops bots.
import io
p='index.html'; s=io.open(p,encoding='utf-8').read()
def rep(old,new,count=1):
    global s
    assert s.count(old)==count,('MISSING/AMBIGUOUS',old[:90],s.count(old))
    s=s.replace(old,new)
rep('<form class="form" action="https://formsubmit.co/markedcel06@gmail.com" method="POST" target="_blank"><input type="hidden" name="_subject" value="Mark&#39;s World contact">',
    '<form class="form" id="cform" action="https://formsubmit.co/ajax/markedcel06@gmail.com" method="POST"><input type="hidden" name="_subject" value="Mark&#39;s World contact"><input type="hidden" name="_template" value="table"><input type="hidden" name="_captcha" value="false"><input type="text" name="_honey" tabindex="-1" autocomplete="off" style="position:absolute;left:-9999px">')
rep("document.getElementById('dial').onclick=function(){grabFocus();cycleTime()};",
    "document.getElementById('dial').onclick=function(){grabFocus();cycleTime()};\n"
    "document.getElementById('cform').onsubmit=function(e){e.preventDefault();var f=this,b=f.querySelector('button');b.disabled=true;b.textContent='Sending\u2026';"
    "fetch(f.action,{method:'POST',headers:{'Accept':'application/json'},body:new FormData(f)}).then(function(r){return r.json()}).then(function(j){"
    "if(j&&/true/.test(String(j.success))){b.textContent='Sent \u2713 \u2014 I reply within a day';f.querySelectorAll('input:not([type=hidden]),textarea').forEach(function(i){i.value=''});toast('Message sent \u2014 salamat!')}"
    "else throw new Error(j&&j.message||'FormSubmit error')}).catch(function(err){b.disabled=false;b.textContent='Send message';toast('Not sent: '+err.message+' \u2014 email markedcel06@gmail.com')})});")
io.open(p,'w',encoding='utf-8').write(s); print('patch34 applied')
