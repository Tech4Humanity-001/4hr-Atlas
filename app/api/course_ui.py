from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router=APIRouter(tags=["course-ui"])

@router.get("/course/{subtopic_id}",response_class=HTMLResponse)
def course_ui(subtopic_id:str):
    sid=subtopic_id.upper()
    return HTMLResponse(f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Atlas Course {sid}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:900px;margin:0 auto;padding:32px;line-height:1.55}}
.card{{border:1px solid #ddd;border-radius:12px;padding:24px;margin:16px 0}}
button{{padding:10px 16px;border-radius:8px;border:1px solid #888;background:white;cursor:pointer;margin:4px}}
button:hover{{background:#eee}} .muted{{color:#666}} .choice{{display:block;width:100%;text-align:left}}
</style></head><body>
<div id="app"><p>Loading course…</p></div>
<script>
const SID="{sid}", LEARNER="browser";
const app=document.getElementById("app");
async function getCourse(){{const r=await fetch("/api/v1/courses/"+SID); if(!r.ok) throw Error(await r.text()); return r.json();}}
function esc(s){{return String(s).replace(/[&<>"]/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}}[c]));}}
async function start(){{const c=await getCourse(); app.innerHTML=
  '<div class="card"><h1>'+esc(c.title)+'</h1><p>'+esc(c.intro)+'</p><h2>Lesson</h2><p>'+esc(c.lesson)+'</p><button id="complete">Complete lesson</button></div><div id="assessment"></div><div id="result"></div>';
  document.getElementById("complete").onclick=async()=>{{await fetch("/api/v1/courses/"+SID+"/lesson/complete",{{method:"POST",headers:{{"content-type":"application/json"}},body:JSON.stringify({{learner_id:LEARNER}})}}); begin();}};
}}
async function begin(){{const r=await fetch("/api/v1/courses/"+SID+"/assessment/start",{{method:"POST",headers:{{"content-type":"application/json"}},body:JSON.stringify({{learner_id:LEARNER}})}}); const x=await r.json(); showQuestion(x.questions[0],1,x.question_count);}}
function showQuestion(q,n,total){{const box=document.getElementById("assessment"); box.innerHTML='<div class="card"><p class="muted">Question '+n+' of '+total+'</p><h2>'+esc(q.prompt)+'</h2>'+q.choices.map(c=>'<button class="choice" data-a="'+esc(c)+'">'+esc(c)+'</button>').join("")+'<p id="feedback"></p></div>'; document.querySelectorAll(".choice").forEach(b=>b.onclick=()=>answer(q,b.dataset.a,n,total));}}
async function answer(q,a,n,total){{document.querySelectorAll(".choice").forEach(b=>b.disabled=true); const r=await fetch("/api/v1/courses/"+SID+"/assessment/answer",{{method:"POST",headers:{{"content-type":"application/json"}},body:JSON.stringify({{learner_id:LEARNER,question_id:q.id,answer:a}})}}); const x=await r.json(); document.getElementById("feedback").textContent=(x.correct?"Correct. ":"Not quite. ")+x.explanation; setTimeout(()=>x.next_question?showQuestion(x.next_question,n+1,total):showResult(x),700);}}
function showResult(x){{document.getElementById("result").innerHTML='<div class="card"><h2>Result</h2><p>Score: '+x.score+'%</p><p>Mastery: '+(x.mastery?"Yes":"Not yet")+'</p>'+(x.credential_id?'<p>Credential: <b>'+esc(x.credential_id)+'</b></p>':'')+'</div>';}}
start().catch(e=>app.innerHTML='<div class="card"><h1>Course unavailable</h1><p>'+esc(e.message)+'</p></div>');
</script></body></html>""")
