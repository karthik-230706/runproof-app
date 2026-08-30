const app = document.getElementById("app");

const S = {
  route: location.hash.slice(1) || "landing",
  user: null,
  projectId: null,
  analysis: null,
  verification: null,
  passport: null,
  projectDetail: null,
  theme: localStorage.getItem("rp_theme") || "dark",
  beginner: localStorage.getItem("rp_beginner") !== "0"
};

document.documentElement.dataset.theme = S.theme;

const journeySteps = ["Project","Scan","Understand","Check","Doctor","Score","Verify","Passport"];

async function api(url, opt={}) {
  const init = {credentials:"include", ...opt};
  if (!(opt.body instanceof FormData)) {
    init.headers = {"Content-Type":"application/json", ...(opt.headers||{})};
  }
  const r = await fetch(url, init);
  const data = await r.json().catch(()=>({}));
  if (!r.ok) throw new Error(data.error || `Request failed (${r.status})`);
  return data;
}
async function apiForm(url, form) {
  const r = await fetch(url,{method:"POST",body:form,credentials:"include"});
  const data = await r.json().catch(()=>({}));
  if(!r.ok) throw new Error(data.error || "Request failed");
  return data;
}

function esc(v){return String(v??"").replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[m]));}
function val(id){return document.getElementById(id)?.value || "";}
function badge(text,kind="info"){return `<span class="badge ${kind}">${esc(text)}</span>`;}
function brand(){return `<div class="brand"><div class="shield logo-glow">R✓</div><div>RunProof<small>Build • Verify • Prove</small></div></div>`;}
function formatDate(v){try{return new Date(v).toLocaleString()}catch{return v||""}}
function maskPhone(p){if(!p)return ""; return p.length>8?p.slice(0,3)+" •••••• "+p.slice(-3):p;}
function toast(message){
  const t=document.createElement("div"); t.className="toast"; t.textContent=message;
  document.body.appendChild(t); setTimeout(()=>t.remove(),3000);
}
function closePopups(){document.querySelectorAll(".popup-layer,.command-layer").forEach(x=>x.remove());}
function go(route){
  closePopups(); S.route=route; location.hash=route; render(); window.scrollTo({top:0,behavior:"smooth"});
}
window.addEventListener("hashchange",()=>{S.route=location.hash.slice(1)||"landing";render();});
window.addEventListener("keydown",e=>{
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();openCommand();}
  if(e.key==="Escape")closePopups();
});

function greeting(){
  const h=new Date().getHours();
  if(h<12)return "Good morning";
  if(h<17)return "Good afternoon";
  return "Good evening";
}
function kindForScore(score){
  if(score===null||score===undefined)return "info";
  return score>=90?"good":score>=75?"warn":"bad";
}
function emptyState(icon,title,text,route="new",button="Start"){
  return `<div class="card empty"><div class="big">${icon}</div><h2>${esc(title)}</h2><p class="muted">${esc(text)}</p><button class="btn primary" onclick="go('${route}')">${esc(button)}</button></div>`;
}
function item(k,v){return `<div class="item"><small>${esc(k)}</small><b>${esc(v)}</b></div>`;}
function eventRow(icon,title,detail){
  return `<div class="event"><div class="eventicon">${icon}</div><div><b>${esc(String(title).replaceAll("_"," "))}</b><small>${esc(detail||"")}</small></div></div>`;
}
function projectRow(p){
  const status=p.last_status||"New";
  const kind=status.toLowerCase().includes("verified")?"good":kindForScore(p.last_score);
  return `<div class="proj proj-click" onclick="openProject(${p.id})"><b>${esc(p.name)}</b><span>#${p.id}</span><span>${p.last_score??"—"}</span><span>${badge(status,kind)}</span></div>`;
}
function stepbar(active){
  return `<div class="steps">${journeySteps.map((s,i)=>`<div class="step ${i<active?"done":i===active?"active":""}"><i class="bullet">${i<active?"✓":i+1}</i>${s}</div>${i<journeySteps.length-1?'<span class="muted">→</span>':""}`).join("")}</div>`;
}

/* ---------- Landing / authentication ---------- */

function landing(){
  return `
  <nav class="landing-nav">
    ${brand()}
    <div class="navlinks"><span onclick="document.getElementById('product')?.scrollIntoView({behavior:'smooth'})">Product</span><span onclick="document.getElementById('journey')?.scrollIntoView({behavior:'smooth'})">Workflow</span><span onclick="go('signup')">Security</span><span onclick="go('signup')">Passport</span></div>
    <div style="display:flex;gap:8px"><button class="btn secondary" onclick="go('login')">Log in</button><button class="btn primary" onclick="go('signup')">Start verifying</button></div>
  </nav>
  <section class="hero" id="product">
    <div>
      ${badge("◈ Software reproducibility intelligence","info")}
      <h1>Your code works here.<br>Prove it works again.</h1>
      <p>RunProof understands a project, checks its setup, explains problems, scores readiness, verifies repeatability, and creates a proof passport — in one guided developer experience.</p>
      <div class="hero-actions"><button class="btn primary" style="padding:15px 21px" onclick="go('signup')">⚡ Start RunProof</button><button class="btn secondary" style="padding:15px 21px" onclick="demoLogin()">▶ Enter Demo Workspace</button></div>
      <div style="display:flex;gap:17px;flex-wrap:wrap;margin-top:23px;color:var(--muted);font-size:12px"><span>✓ Beginner friendly</span><span>✓ Phone OTP</span><span>✓ Secure-by-design</span><span>✓ CLI + Web</span><span>✓ Proof passport</span></div>
    </div>
    <div class="demo-screen">
      <div class="windowbar"><div class="traffic"><i class="dot r"></i><i class="dot y"></i><i class="dot g"></i></div>${badge("LIVE PRODUCT PREVIEW","good")}</div>
      <div class="mock-grid">
        <div class="mock-side">${brand()}<div style="margin-top:25px;color:var(--muted);display:grid;gap:13px;font-size:12px"><b style="color:white">⌂ Dashboard</b><span>＋ New Analysis</span><span>▣ Projects</span><span>🩺 Doctor</span><span>✓ Verifications</span><span>🛂 Passports</span><span>🔐 Security</span></div></div>
        <div class="mock-main">
          <div class="mock-card"><small class="muted">PROJECT</small><h3 style="margin:6px 0">CivicPulse</h3><div style="display:flex;gap:7px">${badge("Python 3.11","info")}${badge("Verified","good")}</div></div>
          <div class="mock-card mock-score"><div class="ring"><b>92</b></div><div><h3 style="margin:0">Very Ready</h3><p class="muted tiny">Warnings explained by RunProof Doctor</p></div></div>
          <div class="mock-card"><div style="display:flex;justify-content:space-between"><b>Build A</b><span class="mono tiny">A72F91C8...</span></div><div style="display:flex;justify-content:space-between;margin-top:11px"><b>Build B</b><span class="mono tiny">A72F91C8...</span></div><div style="margin-top:13px">${badge("✓ ARTIFACT MATCH","good")}</div></div>
        </div>
      </div>
    </div>
  </section>
  <section class="journey" id="journey">
    ${[
      ["01","Understand","Know what the project needs."],
      ["02","Inspect","Check runtime, files, packages and settings."],
      ["03","Doctor","Explain problems and how to fix them."],
      ["04","Verify","Compare clean results using fingerprints."],
      ["05","Passport","Create proof that can be shared."]
    ].map(x=>`<div class="journey-card"><div class="num">${x[0]}</div><h3>${x[1]}</h3><p>${x[2]}</p></div>`).join("")}
  </section>`;
}

function auth(type){
  const signup=type==="signup";
  return `<div class="auth">
    <section class="auth-art">${brand()}<div><h1>${signup?"Create a secure RunProof identity.":"Welcome back to your verification workspace."}</h1><p>Every project, issue, verification and passport stays connected to your account.</p></div><div>${badge("Private by default","good")} ${badge("Phone OTP","info")} ${badge("Secret redaction","info")}</div></section>
    <section class="auth-panel"><div class="auth-card">${brand()}<h2>${signup?"Create your account":"Welcome back 👋"}</h2><p class="muted">${signup?"Phone verification is required before account access.":"Log in to continue your projects."}</p>
      ${signup?`<div class="field"><label>Full name</label><input id="name" placeholder="Your name"></div><div class="field"><label>Phone number with country code</label><input id="phone" placeholder="+919876543210"></div>`:""}
      <div class="field"><label>Email</label><input id="email" type="email" placeholder="you@example.com"></div>
      <div class="field"><label>Password</label><input id="password" type="password" placeholder="Minimum 8 characters"></div>
      <button class="btn primary" style="width:100%;margin-top:8px" onclick="${signup?"signup()":"login()"}">${signup?"Create account & send OTP":"Log in"}</button>
      <p style="text-align:center" class="muted">${signup?"Already registered?":"New to RunProof?"} <a href="#${signup?"login":"signup"}" style="color:#9edbff;font-weight:800">${signup?"Log in":"Create account"}</a></p>
      <div class="sec-note">🔐 Passwords are hashed on the backend and are never displayed back to the user.</div>
    </div></section>
  </div>`;
}
async function signup(){
  try{
    const d=await api("/api/auth/signup",{method:"POST",body:JSON.stringify({name:val("name"),phone:val("phone"),email:val("email"),password:val("password")})});
    sessionStorage.demoOtp=d.demo_otp||"";
    sessionStorage.otpPhone=d.masked_phone||"";
    sessionStorage.otpDelivery=d.delivery||"";
    go("otp");
  }catch(e){toast(e.message);}
}
async function login(){
  try{
    const d=await api("/api/auth/login",{method:"POST",body:JSON.stringify({email:val("email"),password:val("password")})});
    if(d.requires_otp){
      const r=await api("/api/auth/resend-otp",{method:"POST",body:"{}"});
      sessionStorage.demoOtp=r.demo_otp||""; sessionStorage.otpPhone=r.masked_phone||"your phone";
      go("otp"); return;
    }
    S.user=await api("/api/me"); go("dashboard");
  }catch(e){toast(e.message);}
}
function otpPage(){
  const delivery=sessionStorage.otpDelivery;
  return `<div class="auth"><section class="auth-art">${brand()}<div><h1>Verify your phone. Then continue.</h1><p>RunProof does not complete signup until the OTP is approved.</p></div><div>${badge("5-minute code","info")} ${badge("Attempt limits","good")}</div></section>
  <section class="auth-panel"><div class="auth-card">${brand()}<h2>Enter your OTP</h2><p class="muted">Code sent to <b>${esc(sessionStorage.otpPhone||"your phone")}</b>.</p>
  <div class="otp">${[0,1,2,3,4,5].map(i=>`<input maxlength="1" id="o${i}" oninput="nextOtp(${i})">`).join("")}</div>
  <button class="btn primary" style="width:100%" onclick="verifyOtp()">Verify OTP</button><button class="btn secondary" style="width:100%;margin-top:9px" onclick="resendOtp()">Resend OTP</button>
  ${sessionStorage.demoOtp?`<p class="muted tiny" style="text-align:center">Demo OTP: <b>${esc(sessionStorage.demoOtp)}</b></p>`:""}
  <div class="sec-note">${delivery==="sms"?"📱 A real SMS verification was requested through the configured provider.":"📱 Real phone SMS requires Twilio Verify credentials in .env. Demo mode is only for local testing."}</div>
  </div></section></div>`;
}
function nextOtp(i){if(val("o"+i)&&i<5)document.getElementById("o"+(i+1))?.focus();}
async function verifyOtp(){
  let code=""; for(let i=0;i<6;i++)code+=val("o"+i);
  try{await api("/api/auth/verify-otp",{method:"POST",body:JSON.stringify({code})});S.user=await api("/api/me");sessionStorage.removeItem("demoOtp");go("dashboard");}
  catch(e){toast(e.message);}
}
async function resendOtp(){
  try{const d=await api("/api/auth/resend-otp",{method:"POST",body:"{}"});sessionStorage.demoOtp=d.demo_otp||"";sessionStorage.otpPhone=d.masked_phone||"";sessionStorage.otpDelivery=d.delivery||"";toast("New OTP requested.");render();}
  catch(e){toast(e.message);}
}
async function demoLogin(){
  try{await api("/api/auth/demo",{method:"POST",body:"{}"});S.user=await api("/api/me");go("dashboard");}
  catch(e){toast(e.message);go("signup");}
}

/* ---------- App shell ---------- */

const menu=[
  ["⌂","Dashboard","dashboard"],["＋","New Analysis","new"],["▣","Projects","projects"],
  ["⚠","Issues","issues"],["✓","Verifications","verifications"],["🛂","Passports","passports"],["▤","Reports","reports"],
  ["sep"],["〉_","CLI","cli"],["▧","Documentation","documentation"],["⚙","Settings","settings"]
];
function shell(body,active){
  const first=(S.user?.name||"RunProof User").split(" ")[0];
  return `<div class="shell">
    <aside class="sidebar">
      ${brand()}
      <div class="side-list">
        ${menu.map(x=>x[0]==="sep"
          ?'<div class="side-sep"></div>'
          :`<div class="side-item ${active===x[2]?"active":""}" onclick="go('${x[2]}')">
              <b>${x[0]}</b><span>${x[1]}</span>${x[2]==="issues"?'<i id="side-issue-count" class="side-count hidden">0</i>':""}
            </div>`).join("")}
      </div>
      <button class="sidebar-profile" onclick="showProfileMenu(event)">
        <span class="sidebar-avatar">${esc((S.user?.name||"R")[0].toUpperCase())}</span>
        <span class="sidebar-profile-copy"><b>${esc(first)}</b><small>${esc(S.user?.role||"Developer")}</small></span>
        <span class="sidebar-chevron">⌄</span>
      </button>
    </aside>
    <main class="appmain">
      <div class="topbar">
        <button class="search" onclick="openCommand()"><span>⌕ Search projects, issues, reports…</span><span>Ctrl K</span></button>
        <button class="circlebtn" title="Light / Dark mode" onclick="toggleTheme()">${S.theme==="dark"?"☀":"☾"}</button>
        <button class="circlebtn bell-wrap" title="Notifications" onclick="showNotifications(event)">♧<span id="bell-count" class="bell-count hidden">0</span></button>
        <button class="avatar avatar-btn top-avatar" title="Profile" onclick="showProfileMenu(event)">${esc((S.user?.name||"R")[0].toUpperCase())}</button>
      </div>
      <div class="content">${body}</div>
    </main>
    ${assistantWidget()}
  </div>`;
}
function toggleTheme(){
  S.theme=S.theme==="dark"?"light":"dark";
  localStorage.setItem("rp_theme",S.theme);
  document.documentElement.dataset.theme=S.theme;
  render();
}
function toggleBeginner(){
  S.beginner=!S.beginner; localStorage.setItem("rp_beginner",S.beginner?"1":"0");
  toast(`Beginner Mode ${S.beginner?"ON":"OFF"}`); render();
}

/* ---------- Notification/profile popups ---------- */

async function loadBell(){
  try{
    const d=await api("/api/notifications");
    const count=document.getElementById("bell-count");
    if(count){
      count.textContent=d.unread||0;
      count.classList.toggle("hidden",!d.unread);
    }
  }catch{}
  try{
    const d=await api("/api/issues");
    const c=document.getElementById("side-issue-count");
    if(c){
      c.textContent=d.items?.length||0;
      c.classList.toggle("hidden",!(d.items?.length));
    }
  }catch{}
}
async function showNotifications(ev){
  ev?.stopPropagation(); closePopups();
  let d={items:[],unread:0}; try{d=await api("/api/notifications")}catch{}
  const layer=document.createElement("div"); layer.className="popup-layer";
  layer.innerHTML=`<div class="top-popup notification-popup">
    <div class="popup-title"><b>🔔 Notifications ${d.unread?`(${d.unread})`:""}</b><button onclick="markAllRead()">Mark all read</button></div>
    ${d.items.length?d.items.slice(0,7).map(n=>`<div class="notify-item ${n.unread?"unread":""}"><b>${esc(n.title)}</b><span>${esc(n.detail||"RunProof activity")}</span><small>${formatDate(n.created_at)}</small></div>`).join(""):'<div class="empty-small">No notifications yet.</div>'}
    <button class="popup-footer" onclick="go('notifications')">View all notifications →</button>
  </div>`;
  document.body.appendChild(layer); layer.onclick=e=>{if(e.target===layer)closePopups();};
}
async function markAllRead(){
  try{await api("/api/notifications/read-all",{method:"POST",body:"{}"});closePopups();loadBell();toast("Notifications marked as read.");}
  catch(e){toast(e.message);}
}
async function showProfileMenu(ev){
  ev?.stopPropagation(); closePopups();
  let p; try{p=await api("/api/profile");}catch{p={user:S.user||{},stats:{projects:0,verified:0,average_score:0}};}
  const u=p.user,st=p.stats;
  const layer=document.createElement("div");layer.className="popup-layer";
  layer.innerHTML=`<div class="top-popup profile-popup">
    <div class="profile-summary"><div class="profile-big">${esc((u.name||"R")[0].toUpperCase())}</div><div><b>${esc(u.name||"RunProof User")}</b><span>${esc(u.email||"")}</span><small>${esc(maskPhone(u.phone||""))}</small></div></div>
    <div class="profile-stats"><div><b>${st.projects||0}</b><span>Projects</span></div><div><b>${st.verified||0}</b><span>Verified</span></div><div><b>${st.average_score||0}</b><span>Avg Score</span></div></div>
    <div class="profile-menu"><button onclick="go('profile')">👤 View Profile</button><button onclick="go('profile-edit')">✎ Edit Profile</button><button onclick="go('security')">🔐 Security</button><button onclick="go('developer')">⌘ Developer Settings</button><button onclick="go('settings')">⚙ Account Settings</button><hr><button class="logout-item" onclick="logout()">↪ Sign Out</button></div>
  </div>`;
  document.body.appendChild(layer);layer.onclick=e=>{if(e.target===layer)closePopups();};
}

/* ---------- Search / command palette ---------- */

function openCommand(){
  closePopups();
  const layer=document.createElement("div");layer.className="command-layer";
  layer.innerHTML=`<div class="command-box"><input id="cmd-input" placeholder="Search RunProof…" oninput="commandSearch(this.value)"><div id="command-items" class="command-items"><div class="empty-small">Type to search projects, or choose a RunProof action.</div></div></div>`;
  document.body.appendChild(layer);layer.onclick=e=>{if(e.target===layer)closePopups();};
  setTimeout(()=>{document.getElementById("cmd-input")?.focus();commandSearch("");},10);
}
async function commandSearch(q){
  const box=document.getElementById("command-items"); if(!box)return;
  try{
    const d=await api(`/api/search?q=${encodeURIComponent(q)}`);
    box.innerHTML=d.results.length?d.results.map(r=>r.type==="project"
      ?`<button onclick="openProject(${r.project_id});closePopups()"><b>▣ ${esc(r.title)}</b><span>${esc(r.detail)}</span></button>`
      :`<button onclick="go('${r.route}');closePopups()"><b>${esc(r.title)}</b><span>${esc(r.detail)}</span></button>`).join("")
      :'<div class="empty-small">No matching RunProof item.</div>';
  }catch(e){box.innerHTML=`<div class="empty-small">${esc(e.message)}</div>`;}
}

/* ---------- AI guide ---------- */

function assistantWidget(){
  return `<button class="ai-fab" title="Ask RunProof Guide" onclick="toggleAssistant()">✦</button>
  <div id="ai-panel" class="ai-panel hidden">
    <div class="ai-head"><div><b>✦ RunProof Guide</b><small>Ask how to use this app</small></div><button onclick="toggleAssistant()">×</button></div>
    <div id="ai-messages" class="ai-messages"><div class="ai-msg bot">Hi! Ask “How do I add a project?”, “Why is my score low?”, “How do I verify?”, or “How can my friend open RunProof?”</div></div>
    <div class="ai-quick"><button onclick="askQuick('How do I add a project?')">Add project</button><button onclick="askQuick('Why is my score low?')">Score</button><button onclick="askQuick('How do I verify?')">Verify</button><button onclick="askQuick('How can my friend open RunProof?')">Share</button></div>
    <div class="ai-input"><input id="ai-input" placeholder="Ask RunProof…" onkeydown="if(event.key==='Enter')sendAssistant()"><button onclick="sendAssistant()">Send</button></div>
  </div>`;
}
function toggleAssistant(){document.getElementById("ai-panel")?.classList.toggle("hidden");}
function askQuick(q){const i=document.getElementById("ai-input");if(i){i.value=q;sendAssistant();}}
async function sendAssistant(){
  const input=document.getElementById("ai-input"),q=input?.value.trim();if(!q)return;
  const box=document.getElementById("ai-messages");box.innerHTML+=`<div class="ai-msg user">${esc(q)}</div>`;input.value="";
  try{const d=await api("/api/assistant",{method:"POST",body:JSON.stringify({message:q,route:S.route,project_id:S.projectId})});box.innerHTML+=`<div class="ai-msg bot">${esc(d.answer)}</div>`;}
  catch(e){box.innerHTML+=`<div class="ai-msg bot">${esc(e.message)}</div>`;}
  box.scrollTop=box.scrollHeight;
}

/* ---------- Dashboard / workspace / project history ---------- */

async function dashboard(){
  let d={projects:[],stats:{projects:0,verified:0,average_score:0},activity:[]};
  try{d=await api("/api/dashboard")}catch{}
  let issueCount=0;
  try{const i=await api("/api/issues"); issueCount=i.items?.length||0;}catch{}
  const first=S.user?.name?.split(" ")[0]||"there";
  const recent=d.projects?.[0]||null;
  let recentDetail=null;
  if(recent){
    try{recentDetail=await api(`/api/projects/${recent.id}`);}catch{}
  }
  const a=recentDetail?.analysis;
  const score=recent?.last_score ?? a?.score?.score ?? 0;
  const status=recent?.last_status || a?.score?.label || "New";
  const needAttention=issueCount || Math.max(0,(d.stats.projects||0)-(d.stats.verified||0));
  const checks = a ? [
    ["Runtime",a.runtime?.available,"Passed",a.runtime?.available?"good":"bad"],
    ["Dependencies",!(a.dependencies?.unpinned),"Passed",a.dependencies?.unpinned?`${a.dependencies.unpinned} warning(s)`:"Passed",a.dependencies?.unpinned?"warn":"good"],
    ["Environment",!(a.environment?.missing_names?.length),"Passed",a.environment?.missing_names?.length?`${a.environment.missing_names.length} issue(s)`:"Passed",a.environment?.missing_names?.length?"warn":"good"],
    ["Tests",true,"Detected","Detected","good"],
    ["Build",status.toLowerCase().includes("failed")?false:true,"Passed",status.toLowerCase().includes("failed")?"Needs review":"Passed",status.toLowerCase().includes("failed")?"bad":"good"],
    ["Determinism",status.toLowerCase().includes("verified"),"Verified",status.toLowerCase().includes("verified")?"Passed":"Not verified",status.toLowerCase().includes("verified")?"good":"bad"]
  ] : [];
  return shell(`
    <div class="dash-hero">
      <div>
        <h1>${greeting()}, ${esc(first)}! <span class="wave">👋</span></h1>
        <p>Let's prove your next build is reproducible.</p>
      </div>
      <div class="dash-actions">
        <button class="btn primary dash-primary" onclick="go('new')">🚀 Analyze New Project</button>
        <button class="btn github-btn" onclick="openGithubImport()">◉ Import from GitHub</button>
        <button class="btn secondary share-btn" onclick="shareRunProof()">⌁ Share RunProof</button>
      </div>
    </div>

    <div class="stats screenshot-stats">
      <div class="stat dashboard-stat clickable" onclick="go('workspace')"><span class="stat-icon blue">▣</span><div><small>Projects</small><strong>${d.stats.projects||0}</strong><span>Total projects</span></div></div>
      <div class="stat dashboard-stat clickable" onclick="go('verifications')"><span class="stat-icon green">◇</span><div><small>Verified</small><strong>${d.stats.verified||0}</strong><span>Projects reproducible</span></div></div>
      <div class="stat dashboard-stat clickable" onclick="go('issues')"><span class="stat-icon orange">△</span><div><small>Need Attention</small><strong>${needAttention}</strong><span>Requires fixes</span></div></div>
      <div class="stat dashboard-stat clickable" onclick="go('score')"><span class="stat-icon purple">◔</span><div><small>Average Score</small><strong>${d.stats.average_score||0}<em>/100</em></strong><span>Across all projects</span></div></div>
    </div>

    <section class="dashboard-section">
      <div class="section-title"><h3>↶ Recent Projects</h3><button class="link-btn" onclick="go('projects')">View all projects →</button></div>
      ${recent?`
      <div class="recent-project-card">
        <div class="project-main-line">
          <button class="code-logo" onclick="openProject(${recent.id})">&lt;/&gt;</button>
          <div class="recent-project-info">
            <div class="project-name-line"><button class="project-name-button" onclick="openProject(${recent.id})">${esc(recent.name)}</button>${badge("Private","info")}</div>
            <p>◉ RunProof · ${esc(a?.project_type?.type||"Project")} · ${esc(a?.runtime?.runtime||"Runtime")}</p>
            <small>Analyzed ${formatDate(recent.created_at)}</small>
          </div>
          <div class="score-donut ${kindForScore(score)}"><div><b>${score}</b><span>/100</span></div></div>
          <div class="attention-copy"><b>${esc(status).toUpperCase()}</b><span>${status.toLowerCase().includes("verified")?"Project reproducibility proof is available.":"Project has issues or checks that need review."}</span></div>
          <button class="btn analysis-btn" onclick="openProject(${recent.id})">View Analysis →</button>
        </div>
        <div class="check-strip">
          ${checks.map(c=>`<button class="check-tile" onclick="openProject(${recent.id})"><i class="${c[3]}">${c[3]==="good"?"✓":c[3]==="warn"?"!":"×"}</i><span><b>${c[0]}</b><small class="${c[3]}">${c[2]==="Passed"?c[2]:c[3]==="warn"?c[2]:c[2]}</small></span></button>`).join("")}
        </div>
      </div>`:emptyState("▣","No projects yet","Analyze your first project and this card will become your live project summary.","new","Analyze New Project")}
    </section>

    <section class="dashboard-section">
      <div class="section-title"><h3>⌁ Recent Activity</h3><button class="link-btn" onclick="go('notifications')">View all activity →</button></div>
      <div class="activity-table">
        ${d.activity?.length?d.activity.slice(0,6).map((x,i)=>`
          <button class="activity-table-row" onclick="${recent?`openProject(${recent.id})`:"go('new')"}">
            <span class="activity-status ${i===1?"warn":i===2?"info":"good"}">${i===1?"!":i===2?"i":"✓"}</span>
            <b>${esc(String(x.action||"Activity").replaceAll("_"," "))}</b>
            <span>${esc(x.detail||recent?.name||"RunProof")}</span>
            <span class="activity-pill">${i===1?"Warning":score?score+"/100":"Info"}</span>
            <span>${formatDate(x.created_at)}</span>
            <span class="activity-link">${i===1?"View Details":"View Report"} →</span>
          </button>`).join(""):`<div class="empty-small activity-empty">No recent activity yet. Your RunProof actions will appear here.</div>`}
      </div>
    </section>
  `,"dashboard");
}
async function workspace(){
  let d={projects:[],empty:true};try{d=await api("/api/workspace")}catch{}
  return shell(`<div class="headrow"><div><h2>◇ My Workspace</h2><p>All projects connected to your RunProof account.</p></div><button class="btn primary" onclick="go('new')">＋ Add Project</button></div>
  ${d.empty?emptyState("◇","No workspace projects yet","Nothing has been done here yet. Add a project and this workspace will fill automatically.","new","Start First Project"):`<div class="card"><div class="cardhead"><h3>${d.projects.length} project(s)</h3></div>${d.projects.map(projectRow).join("")}</div>`}`,"workspace");
}
async function projects(){
  let d={projects:[]};try{d=await api("/api/workspace")}catch{}
  return shell(`<div class="headrow"><div><h2>Projects</h2><p>Click any project to open its complete details.</p></div><button class="btn primary" onclick="go('new')">＋ New Analysis</button></div>
  ${d.projects.length?`<div class="card">${d.projects.map(projectRow).join("")}</div>`:emptyState("📁","No projects yet","Nothing is available yet.","new","Add Project")}`,"projects");
}
async function openProject(id){S.projectId=id;S.analysis=null;S.verification=null;S.passport=null;go("project");}
async function projectPage(){
  if(!S.projectId)return shell(emptyState("▣","No project selected","Open Projects and choose one.","projects","Open Projects"),"projects");
  let d;try{d=await api(`/api/projects/${S.projectId}`);S.projectDetail=d;S.analysis=d.analysis;}catch(e){return shell(emptyState("⚠","Could not open project",e.message,"projects","Back to Projects"),"projects");}
  const p=d.project,a=d.analysis;
  return shell(`<div class="headrow"><div><h2>${esc(p.name)}</h2><p>Complete RunProof project view.</p></div>${badge(p.last_status||a.score.label,(p.last_status||"").toLowerCase().includes("verified")?"good":kindForScore(a.score.score))}</div>
  <div class="stats">
    <div class="stat clickable" onclick="go('score')"><small>Readiness</small><strong>${a.score.score}</strong>${badge(a.score.label,kindForScore(a.score.score))}</div>
    <div class="stat clickable" onclick="go('understand')"><small>Project Type</small><strong style="font-size:18px">${esc(a.project_type.type)}</strong>${badge("Execution Contract","info")}</div>
    <div class="stat clickable" onclick="go('doctor')"><small>Doctor findings</small><strong>${a.issues.length}</strong>${badge("Open","warn")}</div>
    <div class="stat clickable" onclick="${d.passport_exists?`openPassport(${p.id})`:"openVerify("+p.id+")"}"><small>Passport</small><strong>${d.passport_exists?"✓":"—"}</strong>${badge(d.passport_exists?"Available":"Verify first",d.passport_exists?"good":"info")}</div>
  </div>
  <div class="two">
    <div class="card"><h3>Project Overview</h3><div class="contract">${item("Created",formatDate(p.created_at))}${item("Runtime",a.runtime.version||"Unavailable")}${item("Dependencies",a.dependencies.count)}${item("Files",a.scan.file_count)}${item("Environment names",a.environment.required_names.length)}${item("Fingerprint",a.source_fingerprint.slice(0,18)+"…")}</div></div>
    <div class="card"><h3>Actions</h3><div class="action-stack"><button class="btn secondary" onclick="go('check')">🔍 Open Checks</button><button class="btn secondary" onclick="go('doctor')">🩺 Open Doctor</button><button class="btn success" onclick="openVerify(${p.id})">🔐 Verify Project</button><a class="btn primary" href="/api/projects/${p.id}/report">📄 Download Report</a></div></div>
  </div>`,"projects");
}


async function openGithubImport(){
  closePopups();
  const layer=document.createElement("div");layer.className="command-layer";
  layer.innerHTML=`<div class="command-box github-import-box">
    <h2>◉ Import Public GitHub Repository</h2>
    <p class="muted">Paste a public GitHub repository URL. RunProof will download the default branch as a ZIP and analyze it.</p>
    <div class="field"><label>GitHub repository URL</label><input id="github-url" placeholder="https://github.com/owner/repository"></div>
    <div class="sec-note">🔐 Public repositories only. Private repositories require OAuth and are not requested by this screen.</div>
    <div style="display:flex;gap:9px;justify-content:flex-end;margin-top:15px"><button class="btn secondary" onclick="closePopups()">Cancel</button><button class="btn primary" onclick="importGithubRepo()">Import & Analyze</button></div>
  </div>`;
  document.body.appendChild(layer);
}
async function importGithubRepo(){
  const url=val("github-url").trim();
  if(!url){toast("Paste a GitHub repository URL.");return;}
  try{
    const d=await api("/api/projects/import-github",{method:"POST",body:JSON.stringify({url})});
    S.projectId=d.project_id;S.analysis=null;S.verification=null;S.passport=null;closePopups();go("scan");
  }catch(e){toast(e.message);}
}
async function shareRunProof(){
  try{
    const n=await api("/api/network-info");
    const layer=document.createElement("div");layer.className="command-layer";
    layer.innerHTML=`<div class="command-box"><h2>⌁ Open RunProof on another laptop</h2>
      <p class="muted">Both laptops must be connected to the same Wi-Fi.</p>
      <div class="network-url">${esc(n.url||"Address unavailable")}</div>
      <p class="muted tiny">${esc(n.same_wifi_note||"")}</p>
      <div style="display:flex;gap:9px"><button class="btn primary" onclick="copyText('${esc(n.url||"")}')">Copy Address</button><button class="btn secondary" onclick="go('security');closePopups()">Security & Network</button></div>
    </div>`;
    document.body.appendChild(layer);
  }catch(e){toast(e.message);}
}

/* ---------- New analysis workflow ---------- */

function newProject(){
  return shell(`<div class="headrow"><div><h2>Analyze New Project</h2><p>One guided journey from project folder to proof.</p></div></div>${stepbar(0)}
  <div class="upload"><div><div class="big">📁</div><h2>Give RunProof your project</h2><p>Upload a ZIP project, or choose a built-in demo that proves a different RunProof behavior.</p>
  <input id="zip" type="file" accept=".zip" style="display:none">
  <div style="display:flex;gap:9px;justify-content:center;flex-wrap:wrap">
    <button class="btn primary" onclick="document.getElementById('zip').click()">Choose Project ZIP</button>
    <button class="btn secondary" onclick="createProject('good')">✓ Good Demo</button>
    <button class="btn secondary" onclick="createProject('broken')">⚠ Broken Demo</button>
    <button class="btn secondary" onclick="createProject('nonrepro')">≠ Non-Repro Demo</button>
  </div>
  <div style="margin-top:20px" class="sec-note">🔐 Uploaded code is not executed in Safe Mode. Built-in demos are trusted RunProof samples and can perform their controlled build step.</div></div></div>
  <div style="display:flex;justify-content:flex-end;margin-top:12px"><button class="btn primary" onclick="createProject('upload')">Continue with ZIP →</button></div>`,"new");
}
async function createProject(kind){
  try{
    const f=new FormData();
    const isUpload=kind==="upload";
    f.append("name",isUpload?"MyProject":"Demo Project");
    if(isUpload){
      const file=document.getElementById("zip")?.files?.[0];
      if(!file){toast("Choose a ZIP or select one of the demo projects.");return;}
      f.append("project_zip",file);
    } else {
      f.append("demo_kind",kind||"good");
    }
    const d=await apiForm("/api/projects",f);S.projectId=d.project_id;S.analysis=null;S.verification=null;S.passport=null;go("scan");
  }catch(e){toast(e.message);}
}
function scanPage(){
  setTimeout(runScanAnimation,120);
  return shell(`<div class="headrow"><div><h2>RunProof is reading your project</h2><p>You can see what the system is doing.</p></div>${badge("LIVE ANALYSIS","info")}</div>${stepbar(1)}
  <div class="card"><div style="display:flex;justify-content:space-between"><b>Project Scan</b><span id="pct">${badge("0%","info")}</span></div><div class="progress" style="margin:14px 0"><div id="fill" class="fill"></div></div><div id="scanrows" class="scanrows"></div></div>`,"new");
}
function runScanAnimation(){
  const tasks=["Reading files","Detecting language","Finding dependency files","Checking runtime","Checking configuration","Checking environment names","Preparing reproducibility analysis"];
  let i=0;const rows=document.getElementById("scanrows");if(!rows)return;
  const timer=setInterval(()=>{
    if(i<tasks.length){rows.innerHTML+=`<div class="scanrow"><span>${tasks[i]}</span>${badge("Done ✓","good")}</div>`;i++;const p=Math.round(i/tasks.length*100);document.getElementById("fill").style.width=p+"%";document.getElementById("pct").innerHTML=badge(p+"%","info");}
    else{clearInterval(timer);setTimeout(analyzeNow,300);}
  },260);
}
async function analyzeNow(){
  try{S.analysis=await api(`/api/projects/${S.projectId}/analyze`,{method:"POST",body:"{}"});go("understand");}
  catch(e){toast(e.message);}
}
function needAnalysis(){
  return shell(emptyState("🔍","Analyze a project first","There is nothing to show yet. Add or open a project.","new","Analyze Project"),"new");
}
function understand(){
  if(!S.analysis)return needAnalysis();
  const a=S.analysis;
  return shell(`<div class="headrow"><div><h2>We understand your project ✓</h2><p>RunProof turns its findings into an Execution Contract.</p></div>${badge(a.project_type.type,"info")}</div>${stepbar(2)}
  <div class="card"><div class="cardhead"><h3>RunProof Execution Contract</h3><span class="muted tiny">The project's recipe card.</span></div><div class="contract">${item("Project",a.scan.project_name)}${item("Type",a.project_type.type)}${item("Runtime",a.runtime.version||"Not available")}${item("Manifest",a.project_type.manifest||"None")}${item("Dependencies",a.dependencies.count)}${item("Environment names",a.environment.required_names.length)}${item("Files scanned",a.scan.file_count)}${item("Tests",a.scan.files.some(f=>f.toLowerCase().includes("test"))?"Detected":"Not detected")}${item("Source fingerprint",a.source_fingerprint.slice(0,18)+"…")}</div></div>
  <div style="display:flex;justify-content:flex-end;margin-top:14px"><button class="btn primary" onclick="go('check')">Open Deep Checks →</button></div>`,"new");
}
function checkCard(ic,k,title,desc,status){
  return `<div class="check"><div class="checkicon ${k}">${ic}</div><div><div style="display:flex;justify-content:space-between;gap:9px"><h4>${esc(title)}</h4>${badge(status,k==="good"?"good":k==="warn"?"warn":"bad")}</div><p>${esc(desc)}</p>${S.beginner?'<p style="margin-top:7px;color:#9edbff">RunProof will explain what this means and what to do next.</p>':""}</div></div>`;
}
function checks(){
  if(!S.analysis)return needAnalysis();
  const a=S.analysis;
  const arr=[
    ["✓","good","Project Detection","RunProof understands the project type.","PASS"],
    [a.runtime.available?"✓":"✕",a.runtime.available?"good":"bad","Runtime",a.runtime.available?"Required runtime is available.":"Required runtime is missing.",a.runtime.available?"PASS":"ISSUE"],
    [a.dependencies.unpinned?"⚠":"✓",a.dependencies.unpinned?"warn":"good","Dependencies",a.dependencies.unpinned?`${a.dependencies.unpinned} dependency version(s) are not fixed.`:"Dependency versions look stable.",a.dependencies.unpinned?"WARNING":"PASS"],
    [a.environment.missing_names.length?"✕":"✓",a.environment.missing_names.length?"bad":"good","Environment",a.environment.missing_names.length?`${a.environment.missing_names.length} required setting(s) are missing.`:"Required environment names are ready.",a.environment.missing_names.length?"ISSUE":"PASS"],
    [a.security.sensitive_files.length?"⚠":"✓",a.security.sensitive_files.length?"warn":"good","Sensitive Files",a.security.sensitive_files.length?`${a.security.sensitive_files.length} sensitive file name(s) were found.`:"No obvious secret-bearing filenames found.",a.security.sensitive_files.length?"WARNING":"PASS"],
    ["✓","good","Source Fingerprint","A SHA-256 source fingerprint was created.","PASS"]
  ];
  return shell(`<div class="headrow"><div><h2>Deep Project Check</h2><p>Every result explains itself.</p></div>${badge(`Beginner Mode ${S.beginner?"ON":"OFF"}`,S.beginner?"good":"info")}</div>${stepbar(3)}
  <div class="checks">${arr.map(x=>checkCard(...x)).join("")}</div><div style="display:flex;justify-content:flex-end;margin-top:14px"><button class="btn primary" onclick="go('doctor')">Open RunProof Doctor →</button></div>`,"new");
}
function doctor(){
  if(!S.analysis)return shell(emptyState("🩺","No selected project","Choose a project or open the all-project Issues page.","issues","View All Issues"),"issues");
  const issues=S.analysis.issues||[];
  return shell(`<div class="headrow"><div><h2>🩺 RunProof Doctor</h2><p>What happened, why it matters, and how to fix it.</p></div>${badge(`${issues.length} finding(s)`,issues.some(x=>x.severity==="high")?"bad":"good")}</div>${stepbar(4)}
  ${issues.map(i=>`<div class="doctor"><div class="doctor-top"><div><h3>${esc(i.title)}</h3><p class="muted tiny">${esc(i.severity.toUpperCase())} severity</p></div>${badge(i.severity.toUpperCase(),i.severity==="high"?"bad":i.severity==="medium"?"warn":"info")}</div><div class="doctor3"><div><small>What happened?</small><b>${esc(i.what)}</b></div><div><small>Why it matters</small><b>${esc(i.why)}</b></div><div><small>How to fix</small><b>${esc(i.fix)}</b></div></div></div>`).join("")}
  <div style="display:flex;justify-content:flex-end"><button class="btn primary" onclick="go('score')">See Readiness Score →</button></div>`,"new");
}
function score(){
  if(!S.analysis)return needAnalysis();
  const s=S.analysis.score;
  const maxMap={project:5,runtime:10,files:10,dependencies:10,dependency_pinning:15,environment:10,configuration:5,static_security:10,build:10,tests:15};
  return shell(`<div class="headrow"><div><h2>Readiness Score</h2><p>A transparent score, not a mystery number.</p></div>${badge(s.label,kindForScore(s.score))}</div>${stepbar(5)}
  <div class="scorearea"><div class="card"><div class="bigscore" style="background:conic-gradient(var(--green) ${s.score}%,#1b3048 0)"><div><strong>${s.score}</strong><span>/100</span></div></div><h2 style="text-align:center;margin:0">${esc(s.label)}</h2><p class="muted" style="text-align:center">Open Doctor to understand lost points.</p></div>
  <div class="card"><div class="cardhead"><h3>Where the score comes from</h3></div>${Object.entries(s.categories).map(([k,v])=>{const mx=maxMap[k]||15,p=Math.round(v/mx*100);return `<div class="scoreline"><span>${esc(k.replaceAll("_"," "))}</span><div class="track"><span style="width:${Math.max(0,Math.min(100,p))}%"></span></div><b>${v}/${mx}</b></div>`}).join("")}</div></div>
  <div style="display:flex;justify-content:flex-end;margin-top:14px"><button class="btn success" onclick="openVerify(${S.projectId})">🔐 Prove Reproducibility →</button></div>`,"new");
}

/* ---------- Issues, verification, passports, reports ---------- */

async function issuesPage(){
  let d={items:[]};try{d=await api("/api/issues")}catch(e){return shell(emptyState("⚠","Could not load issues",e.message,"dashboard","Back"),"issues");}
  return shell(`<div class="headrow"><div><h2>🩺 RunProof Doctor — All Projects</h2><p>Every issue across your workspace.</p></div>${badge(`${d.items.length} issue(s)`,d.items.length?"warn":"good")}</div>
  ${d.items.length?`<div class="card">${d.items.map(i=>`<div class="issue-list-row clickable" onclick="openDoctor(${i.project_id})"><div><b>${esc(i.title)}</b><span>${esc(i.project_name)} · ${esc(i.severity.toUpperCase())}</span></div>${badge("Open →",i.severity==="high"?"bad":i.severity==="medium"?"warn":"info")}</div>`).join("")}</div>`:emptyState("✓","No current issues","There are no stored project issues to show right now.","new","Analyze Project")}`,"issues");
}
async function openDoctor(id){
  S.projectId=id;S.verification=null;S.passport=null;
  try{const d=await api(`/api/projects/${id}`);S.analysis=d.analysis;go("doctor");}catch(e){toast(e.message);}
}
async function verificationsPage(){
  let d={items:[]};try{d=await api("/api/verifications")}catch(e){return shell(emptyState("⚠","Could not load verifications",e.message,"dashboard","Back"),"verifications");}
  return shell(`<div class="headrow"><div><h2>✓ Verifications</h2><p>Choose any project to verify or inspect its proof.</p></div></div>
  ${d.items.length?`<div class="card">${d.items.map(p=>`<div class="history-row"><div class="clickable" onclick="openProject(${p.id})"><b>${esc(p.name)}</b><span>${esc(p.last_status||"Not verified")} · Score ${p.last_score??"—"}</span></div><div>${p.passport_exists?`<button class="btn secondary" onclick="openPassport(${p.id})">🛂 Passport</button>`:`<button class="btn success" onclick="openVerify(${p.id})">Verify</button>`}</div></div>`).join("")}</div>`:emptyState("✓","No projects to verify","Add a project first.","new","Analyze Project")}`,"verifications");
}
async function openVerify(id){
  S.projectId=id;S.verification=null;S.passport=null;
  try{const d=await api(`/api/projects/${id}`);S.analysis=d.analysis;}catch{}
  go("verify");
}
async function verifyPage(){
  if(!S.projectId)return shell(emptyState("✓","No project selected","Choose a project before verification.","verifications","Open Verifications"),"verifications");
  if(!S.verification){
    try{S.verification=await api(`/api/projects/${S.projectId}/verify`,{method:"POST",body:"{}"});S.passport=S.verification.passport;}
    catch(e){return shell(emptyState("⚠","Verification could not start",e.message,"projects","Open Projects"),"verifications");}
  }
  const v=S.verification.verification;
  const state = v.verified ? "VERIFIED" : v.status==="NOT_REPRODUCIBLE" ? "MISMATCH" : v.status==="BUILD_FAILED" ? "BUILD FAILED" : v.status==="SOURCE_MATCH_ONLY" ? "SOURCE MATCH" : "NOT VERIFIED";
  const stateKind = v.verified ? "good" : v.status==="SOURCE_MATCH_ONLY" ? "warn" : "bad";
  const heading = v.verified ? "✓ VERIFIED REPRODUCIBLE" : v.status==="NOT_REPRODUCIBLE" ? "✕ NOT REPRODUCIBLE" : v.status==="BUILD_FAILED" ? "⚠ BUILD VERIFICATION FAILED" : "⚠ SOURCE MATCH ONLY";
  const action = v.verified ? `<button class="btn primary" onclick="go('passport')">Open RunProof Passport →</button>` : `<button class="btn secondary" onclick="go('project')">Back to Project</button>`;
  return shell(`<div class="headrow"><div><h2>Reproducibility Lab</h2><p>${esc(v.proof_level||"Verification")} · RunProof shows exactly what level of proof was performed.</p></div>${badge(state,stateKind)}</div>${stepbar(6)}
  <div class="card">
    <div class="lab">
      <div class="build"><div style="font-size:36px">A</div><h3>${v.build_a?.attempted?"Build A":"Clean Copy A"}</h3>${badge(v.build_a?.success?"Build passed":v.build_a?.attempted?"Build failed":"Fingerprint ready",v.build_a?.success||!v.build_a?.attempted?"good":"bad")}<div class="hash">${esc(v.hash_a||"No artifact hash")}</div></div>
      <div><div class="match">${v.match?"✓":"✕"}</div><p style="text-align:center;font-weight:900">${v.match?"MATCH":"NO MATCH"}</p></div>
      <div class="build"><div style="font-size:36px">B</div><h3>${v.build_b?.attempted?"Build B":"Clean Copy B"}</h3>${badge(v.build_b?.success?"Build passed":v.build_b?.attempted?"Build failed":"Fingerprint ready",v.build_b?.success||!v.build_b?.attempted?"good":"bad")}<div class="hash">${esc(v.hash_b||"No artifact hash")}</div></div>
    </div>
    <div style="text-align:center;margin-top:23px"><h1 style="color:${v.verified?"#9bf0c2":v.status==="SOURCE_MATCH_ONLY"?"#ffd99a":"#ffc5ce"}">${heading}</h1><p class="muted">${esc(v.note)}</p>${action}</div>
  </div>`,"verifications");
}
async function passportsPage(){
  let d={items:[]};try{d=await api("/api/passports")}catch(e){return shell(emptyState("⚠","Could not load passports",e.message,"dashboard","Back"),"passports");}
  return shell(`<div class="headrow"><div><h2>🛂 Passports</h2><p>Your verified software proof records.</p></div></div>
  ${d.items.length?`<div class="card">${d.items.map(p=>`<div class="history-row clickable" onclick="openPassport(${p.project_id})"><div><b>${esc(p.name)}</b><span>Score ${p.score??"—"} · ${formatDate(p.issued_at)}</span></div>${badge("VERIFIED","good")}</div>`).join("")}</div>`:emptyState("🛂","No passports yet","Verify a project to create its RunProof Passport.","verifications","Open Verifications")}`,"passports");
}
async function openPassport(id){
  S.projectId=id;
  try{S.passport=await api(`/api/projects/${id}/passport`);go("passport");}catch(e){toast(e.message);openVerify(id);}
}
function passportPage(){
  const p=S.passport||S.verification?.passport;
  if(!p)return shell(emptyState("🛂","No passport selected","Choose a verified project first.","passports","Open Passports"),"passports");
  return shell(`<div class="headrow"><div><h2>🛂 RunProof Passport</h2><p>A shareable proof record without exposing source code.</p></div><button class="btn secondary" onclick="downloadPassport()">Download JSON</button></div>${stepbar(7)}
  <div class="passport"><div style="display:flex;justify-content:space-between;align-items:center">${brand()}${badge("VERIFIED","good")}</div><div class="passportgrid">${passField("Project",p.project)}${passField("Type",p.project_type)}${passField("Readiness",(p.score??"—")+"/100")}${passField("Issued",formatDate(p.issued_at))}${passField("Build A",p.verification?.hash_a?.slice(0,24)+"…")}${passField("Build B",p.verification?.hash_b?.slice(0,24)+"…")}${passField("Signature",p.signature?.slice(0,24)+"…")}${passField("Version",p.version)}</div><div class="verified">✓ VERIFIED REPRODUCIBLE</div></div>`,"passports");
}
function passField(a,b){return `<div class="passitem"><small>${esc(a)}</small><b>${esc(b||"")}</b></div>`;}
function downloadPassport(){
  const p=S.passport||S.verification?.passport;if(!p)return;
  const b=new Blob([JSON.stringify(p,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(b);a.download="runproof-passport.json";a.click();URL.revokeObjectURL(a.href);
}
async function reportsPage(){
  let d={items:[]};try{d=await api("/api/reports")}catch(e){return shell(emptyState("⚠","Could not load reports",e.message,"dashboard","Back"),"reports");}
  return shell(`<div class="headrow"><div><h2>📄 Reports</h2><p>Download a clear HTML report for any project.</p></div></div>
  ${d.items.length?`<div class="card">${d.items.map(p=>`<div class="history-row"><div class="clickable" onclick="openProject(${p.id})"><b>${esc(p.name)}</b><span>Score ${p.last_score??"—"} · ${esc(p.last_status||"New")}</span></div><a class="btn primary" href="/api/projects/${p.id}/report">Download Report</a></div>`).join("")}</div>`:emptyState("📄","No reports yet","Add a project first.","new","Analyze Project")}`,"reports");
}

/* ---------- Notifications ---------- */

async function notificationsPage(){
  let d={items:[],unread:0};try{d=await api("/api/notifications")}catch{}
  return shell(`<div class="headrow"><div><h2>🔔 Notifications</h2><p>Every important RunProof update in one place.</p></div><button class="btn secondary" onclick="markAllRead();setTimeout(()=>go('notifications'),150)">Mark all read</button></div>
  <div class="card">${d.items.length?d.items.map(n=>`<div class="notify-full ${n.unread?"unread":""}"><div><b>${esc(n.title)}</b><span>${esc(n.detail||"RunProof activity")}</span></div><small>${formatDate(n.created_at)}</small></div>`).join(""):`<div class="empty"><div class="big">🔔</div><h3>No notifications yet</h3><p class="muted">New logins, analyses, verifications, reports and security changes will appear here.</p></div>`}</div>`,"notifications");
}

/* ---------- Profile ---------- */

async function profilePage(edit=false){
  let p;try{p=await api("/api/profile");}catch(e){return shell(emptyState("👤","Profile unavailable",e.message,"dashboard","Back"),"profile");}
  const u=p.user,st=p.stats;
  if(edit)return shell(`<div class="headrow"><div><h2>✎ Edit Profile</h2><p>Change visible account details. Phone number changes need a new OTP flow.</p></div></div>
  <div class="card form-card"><div class="field"><label>Name</label><input id="ep-name" value="${esc(u.name)}"></div><div class="field"><label>Organization / College</label><input id="ep-org" value="${esc(u.organization||"")}"></div><div class="field"><label>Role</label><input id="ep-role" value="${esc(u.role||"Developer")}"></div><div class="field"><label>Bio</label><input id="ep-bio" value="${esc(u.bio||"")}"></div><div class="field"><label>Verified phone</label><input value="${esc(maskPhone(u.phone))}" disabled></div><button class="btn primary" onclick="saveProfile()">Save Profile</button></div>`,"settings");
  return shell(`<div class="headrow"><div><h2>👤 My Profile</h2><p>Your RunProof identity and activity.</p></div><button class="btn secondary" onclick="go('profile-edit')">✎ Edit Profile</button></div>
  <div class="profile-page-head"><div class="profile-huge">${esc((u.name||"R")[0].toUpperCase())}</div><div><h2>${esc(u.name)}</h2><p>${esc(u.email)}</p><div style="display:flex;gap:7px;flex-wrap:wrap">${badge(u.phone_verified?"Phone verified":"Phone not verified",u.phone_verified?"good":"warn")}${badge(u.role||"Developer","info")}</div></div></div>
  <div class="stats"><div class="stat clickable" onclick="go('workspace')"><small>Projects</small><strong>${st.projects}</strong></div><div class="stat clickable" onclick="go('verifications')"><small>Verified</small><strong>${st.verified}</strong></div><div class="stat"><small>Average Score</small><strong>${st.average_score}</strong></div><div class="stat clickable" onclick="go('passports')"><small>Passports</small><strong>${st.passports}</strong></div></div>
  <div class="two"><div class="card"><h3>Account Details</h3><div class="rows"><div><b>Email</b><p class="muted">${esc(u.email)}</p></div><div><b>Phone</b><p class="muted">${esc(maskPhone(u.phone))}</p></div><div><b>Organization</b><p class="muted">${esc(u.organization||"Not added")}</p></div><div><b>Member Since</b><p class="muted">${formatDate(u.created_at)}</p></div><div><b>Reports</b><p class="muted">${st.reports||0} generated</p></div></div></div>
  <div class="card"><h3>About</h3><p class="muted">${esc(u.bio||"No bio added yet.")}</p><button class="btn secondary" onclick="go('security')">🔐 Open Security Center</button></div></div>`,"settings");
}
async function saveProfile(){
  try{await api("/api/profile",{method:"PUT",body:JSON.stringify({name:val("ep-name"),organization:val("ep-org"),role:val("ep-role"),bio:val("ep-bio")})});S.user=await api("/api/me");toast("Profile saved.");go("profile");}
  catch(e){toast(e.message);}
}

/* ---------- Security ---------- */

async function securityPage(){
  let n={url:"",same_wifi_note:""},otp={real_sms_configured:false,demo_mode:true,provider:"Unknown"};
  try{n=await api("/api/network-info");}catch{}
  try{otp=await api("/api/otp-status");}catch{}
  return shell(`<div class="headrow"><div><h2>🔐 Security Center</h2><p>Security is visible, understandable and controllable.</p></div>${badge("Protected","good")}</div>
  <div class="stats">
    <div class="stat"><small>Phone verification</small><strong>${S.user?.phone_verified?"✓":"!"}</strong>${badge(S.user?.phone_verified?"Verified":"Required",S.user?.phone_verified?"good":"warn")}</div>
    <div class="stat"><small>SMS OTP provider</small><strong style="font-size:17px">${esc(otp.provider)}</strong>${badge(otp.real_sms_configured?"Real SMS ready":otp.demo_mode?"Demo mode":"Setup required",otp.real_sms_configured?"good":otp.demo_mode?"warn":"bad")}</div>
    <div class="stat"><small>Passwords</small><strong>Hash</strong>${badge("Never displayed","good")}</div>
    <div class="stat"><small>Project access</small><strong>Private</strong>${badge("Owner checked","good")}</div>
  </div>
  <div class="two">
    <div class="card"><h3>Other Laptop Access</h3><p class="muted">For a friend on the same Wi-Fi, RunProof is configured to listen on all local interfaces. Share this address:</p><div class="network-url">${esc(n.url||"Local address unavailable")}</div><p class="muted tiny">${esc(n.same_wifi_note||"")}</p><button class="btn secondary" onclick="copyText('${esc(n.url||"")}')">Copy Address</button></div>
    <div class="card"><h3>Change Password</h3><div class="field"><label>Current password</label><input type="password" id="oldpass"></div><div class="field"><label>New password</label><input type="password" id="newpass"></div><button class="btn primary" onclick="changePassword()">Update Password</button></div>
  </div>
  <div class="card" style="margin-top:14px"><h3>Advanced Protections</h3><div class="security-list"><div>✓ OTP before first account access</div><div>✓ Password hashing</div><div>✓ HttpOnly browser sessions</div><div>✓ Project ownership authorization</div><div>✓ ZIP path traversal checks</div><div>✓ Secret-value redaction design</div><div>✓ Login and OTP rate limits</div><div>✓ API tokens stored as hashes</div></div></div>`,"security");
}
async function changePassword(){
  try{await api("/api/auth/change-password",{method:"POST",body:JSON.stringify({old_password:val("oldpass"),new_password:val("newpass")})});toast("Password updated securely.");}
  catch(e){toast(e.message);}
}
function copyText(t){if(!t){toast("Nothing to copy.");return;}navigator.clipboard?.writeText(t).then(()=>toast("Copied.")).catch(()=>toast(t));}

/* ---------- Settings / developer / integrations ---------- */

function settingsPage(){
  return shell(`<div class="headrow"><div><h2>⚙ Settings</h2><p>Every option opens or changes something.</p></div></div>
  <div class="card settings-grid">
    <button class="setting-row" onclick="toggleBeginner()"><div><b>Beginner Mode</b><span>Explain technical terms in simple English.</span></div>${badge(S.beginner?"ON":"OFF",S.beginner?"good":"info")}</button>
    <button class="setting-row" onclick="toggleTheme()"><div><b>Appearance</b><span>Switch between dark and light RunProof.</span></div>${badge(S.theme==="dark"?"Dark":"Light","info")}</button>
    <button class="setting-row" onclick="go('integrations')"><div><b>GitHub Integration</b><span>See repository integration setup and status.</span></div>${badge("Open","info")}</button>
    <button class="setting-row" onclick="go('developer')"><div><b>Developer Settings</b><span>Create and revoke RunProof CLI/API tokens.</span></div>${badge("Open","info")}</button>
    <button class="setting-row" onclick="go('profile')"><div><b>Account Details</b><span>View profile, phone verification and statistics.</span></div>${badge("Open","info")}</button>
    <button class="setting-row" onclick="logout()"><div><b>Sign Out</b><span>End this RunProof session.</span></div>${badge("Logout","bad")}</button>
  </div>`,"settings");
}
async function integrationsPage(){
  let s={github:{configured:false}};try{s=await api("/api/settings/status");}catch{}
  return shell(`<div class="headrow"><div><h2>◈ GitHub Integration</h2><p>This page always explains the current connection state.</p></div>${badge(s.github?.configured?"Connected":"Not connected",s.github?.configured?"good":"warn")}</div>
  <div class="two"><div class="card"><h3>Repository Connection</h3><p class="muted">A live GitHub account connection needs a GitHub OAuth App with a Client ID, Client Secret and callback URL. These credentials must stay on the backend.</p><button class="btn primary" onclick="showGithubSetup()">Show Setup Steps</button></div>
  <div class="card"><h3>What it will enable</h3><div class="rows"><div>Import a repository</div><div>Re-run RunProof after commits</div><div>Attach Passport to a project</div><div>Future CI/CD checks</div></div></div></div>`,"settings");
}
function showGithubSetup(){
  const layer=document.createElement("div");layer.className="command-layer";layer.innerHTML=`<div class="command-box"><h3>GitHub Setup</h3><div class="rows"><div>1. Create a GitHub OAuth App.</div><div>2. Put Client ID and Client Secret in backend environment variables.</div><div>3. Add an OAuth callback endpoint.</div><div>4. Request only the minimum repository permissions needed.</div></div><button class="btn secondary" style="margin-top:12px" onclick="closePopups()">Close</button></div>`;document.body.appendChild(layer);
}
async function developerPage(){
  let d={items:[]};try{d=await api("/api/tokens");}catch{}
  return shell(`<div class="headrow"><div><h2>⌘ Developer Settings</h2><p>Create secure tokens for RunProof CLI/API access.</p></div><button class="btn primary" onclick="createToken()">＋ Create Token</button></div>
  <div class="card"><h3>CLI Example</h3><div class="network-url">Authorization: Bearer rp_live_••••••••••</div><p class="muted tiny">Full tokens are shown only once at creation. The backend stores only a SHA-256 hash.</p></div>
  <div class="card" style="margin-top:14px"><h3>Your Tokens</h3>${d.items.length?d.items.map(t=>`<div class="history-row"><div><b>${esc(t.label)}</b><span>${esc(t.prefix)}••••${esc(t.last4)} · ${t.revoked?"Revoked":"Active"} · Created ${formatDate(t.created_at)}</span></div>${t.revoked?badge("REVOKED","bad"):`<button class="btn danger" onclick="revokeToken(${t.id})">Revoke</button>`}</div>`).join(""):'<div class="empty-small">No tokens created yet.</div>'}</div>`,"settings");
}
async function createToken(){
  const label=prompt("Token name","My Laptop CLI");if(label===null)return;
  try{
    const d=await api("/api/tokens",{method:"POST",body:JSON.stringify({label})});
    const layer=document.createElement("div");layer.className="command-layer";layer.innerHTML=`<div class="command-box"><h3>Copy your token now</h3><p class="muted">For security, the full token will not be shown again.</p><div class="network-url mono">${esc(d.token)}</div><button class="btn primary" onclick="copyText('${esc(d.token)}')">Copy Token</button><button class="btn secondary" onclick="closePopups();go('developer')">Done</button></div>`;document.body.appendChild(layer);
  }catch(e){toast(e.message);}
}
async function revokeToken(id){if(!confirm("Revoke this token?"))return;try{await api(`/api/tokens/${id}`,{method:"DELETE"});toast("Token revoked.");go("developer");}catch(e){toast(e.message);}}

/* ---------- Team ---------- */

async function teamPage(){
  let d={items:[]};try{d=await api("/api/team/invites");}catch{}
  return shell(`<div class="headrow"><div><h2>👥 Team Workspace</h2><p>Create project collaboration invitations.</p></div></div>
  <div class="two"><div class="card"><h3>Invite Member</h3><div class="field"><label>Email</label><input id="team-email" placeholder="member@example.com"></div><div class="field"><label>Role</label><select id="team-role" class="select-input"><option>Developer</option><option>Viewer</option></select></div><button class="btn primary" onclick="inviteMember()">Send Invite</button><p class="muted tiny">The invite is stored in RunProof. Live email delivery needs an email provider.</p></div>
  <div class="card"><h3>Role Meaning</h3><div class="rows"><div><b>Owner</b> — full control</div><div><b>Developer</b> — analyze and verify</div><div><b>Viewer</b> — read results</div></div></div></div>
  <div class="card" style="margin-top:14px"><h3>Pending Invites</h3>${d.items.length?d.items.map(i=>`<div class="history-row"><div><b>${esc(i.email)}</b><span>${esc(i.role)} · ${esc(i.status)} · ${formatDate(i.created_at)}</span></div><button class="btn danger" onclick="cancelInvite(${i.id})">Cancel</button></div>`).join(""):'<div class="empty-small">No team invitations yet.</div>'}</div>`,"team");
}
async function inviteMember(){
  try{const d=await api("/api/team/invites",{method:"POST",body:JSON.stringify({email:val("team-email"),role:val("team-role")})});toast(d.message);go("team");}
  catch(e){toast(e.message);}
}
async function cancelInvite(id){try{await api(`/api/team/invites/${id}`,{method:"DELETE"});toast("Invite cancelled.");go("team");}catch(e){toast(e.message);}}


function cliPage(){
  return shell(`<div class="headrow"><div><h2>〉_ RunProof CLI</h2><p>The same RunProof engine can be used from the terminal.</p></div><button class="btn primary" onclick="go('developer')">Create CLI Token</button></div>
  <div class="two">
    <div class="card"><h3>Three Main Commands</h3><div class="cli-command"><code>runproof check ./MyProject</code><span>Scan and diagnose the project.</span></div><div class="cli-command"><code>runproof verify ./MyProject</code><span>Verify reproducibility.</span></div><div class="cli-command"><code>runproof report ./MyProject</code><span>Create the report and passport.</span></div></div>
    <div class="card"><h3>Connect CLI to Account</h3><p class="muted">Create an API token in Developer Settings. Full tokens are shown only once.</p><button class="btn secondary" onclick="go('developer')">Open Developer Settings</button></div>
  </div>
  <div class="card" style="margin-top:14px"><h3>What CLI means</h3><p class="muted">CLI is the command-line version of RunProof. The web dashboard and CLI should use the same core checking logic.</p></div>`,"cli");
}
function documentationPage(){
  const docs=[
    ["Start Here","Create an account → add project → scan → Doctor → score → verify → passport."],
    ["Project Scanner","Detects project type, files, dependencies and configuration."],
    ["RunProof Doctor","Explains what failed, why it matters, and how to fix it."],
    ["Reproducibility Verification","Creates two controlled results and compares SHA-256 fingerprints."],
    ["Security","Passwords are hashed, secrets are not shown, and project access is checked."],
    ["Friend Laptop Access","Use the local Wi-Fi address shown in Security Center."],
    ["Real Phone OTP","Configure Twilio Verify in .env and turn demo mode off."]
  ];
  return shell(`<div class="headrow"><div><h2>▧ Documentation</h2><p>Simple documentation that explains every important RunProof feature.</p></div><button class="btn primary" onclick="toggleAssistant()">✦ Ask RunProof Guide</button></div>
  <div class="docs-grid">${docs.map(d=>`<button class="doc-card" onclick="toast('${d[1].replaceAll("'","")}')"><b>${d[0]}</b><span>${d[1]}</span><small>Open explanation →</small></button>`).join("")}</div>`,"documentation");
}

/* ---------- Help ---------- */

function helpPage(){
  const q=[
    ["What is reproducibility?","Being able to create the same software result again."],
    ["What is a runtime?","The language environment a project needs, such as Python or Java."],
    ["What is a dependency?","Another package your project needs."],
    ["What is SHA-256?","A digital fingerprint used to compare data."],
    ["What is an environment variable?","A setting supplied outside source code."],
    ["What is a build?","The process that creates a runnable result."],
    ["What is a test?","A check that confirms code behaves correctly."],
    ["What is a RunProof Passport?","The proof record created after verification."]
  ];
  return shell(`<div class="headrow"><div><h2>? Help Center</h2><p>RunProof should explain itself without needing someone beside you.</p></div><button class="btn primary" onclick="toggleAssistant()">✦ Ask RunProof Guide</button></div><div class="checks">${q.map(x=>checkCard("?","good",x[0],x[1],"LEARN")).join("")}</div>`,"help");
}

/* ---------- Logout ---------- */

async function logout(){
  try{await api("/api/auth/logout",{method:"POST",body:"{}"});}catch{}
  S.user=null;S.projectId=null;S.analysis=null;S.verification=null;S.passport=null;go("landing");
}

/* ---------- Auth guard / render ---------- */

async function ensureUser(){
  if(["landing","signup","login","otp"].includes(S.route))return true;
  try{S.user=await api("/api/me");}catch{S.user=null;}
  if(!S.user){go("login");return false;}
  return true;
}
async function render(){
  if(!await ensureUser())return;
  let html;
  switch(S.route){
    case "landing":html=landing();break;
    case "signup":html=auth("signup");break;
    case "login":html=auth("login");break;
    case "otp":html=otpPage();break;
    case "dashboard":html=await dashboard();break;
    case "workspace":html=await workspace();break;
    case "projects":html=await projects();break;
    case "project":html=await projectPage();break;
    case "new":html=newProject();break;
    case "scan":html=scanPage();break;
    case "understand":html=understand();break;
    case "check":html=checks();break;
    case "doctor":html=doctor();break;
    case "score":html=score();break;
    case "issues":html=await issuesPage();break;
    case "verifications":html=await verificationsPage();break;
    case "verify":html=await verifyPage();break;
    case "passports":html=await passportsPage();break;
    case "passport":html=passportPage();break;
    case "reports":html=await reportsPage();break;
    case "notifications":html=await notificationsPage();break;
    case "profile":html=await profilePage(false);break;
    case "profile-edit":html=await profilePage(true);break;
    case "security":html=await securityPage();break;
    case "settings":html=settingsPage();break;
    case "integrations":html=await integrationsPage();break;
    case "developer":html=await developerPage();break;
    case "team":html=await teamPage();break;
    case "cli":html=cliPage();break;
    case "documentation":html=documentationPage();break;
    case "help":html=helpPage();break;
    default:html=landing();
  }
  app.innerHTML=html;
  if(S.user)setTimeout(loadBell,30);
}

render();
