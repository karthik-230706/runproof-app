const app = document.getElementById("app");

const state = {
  user: JSON.parse(localStorage.getItem("runproof_user") || "null"),
  theme: localStorage.getItem("runproof_theme") || "dark",
  beginner: localStorage.getItem("runproof_beginner") !== "false",
  route: location.hash.replace("#","") || "landing",
  project: {
    name: "MyProject",
    type: "Python",
    runtime: "Python 3.11",
    dependencies: 18,
    tests: 12,
    score: 92,
    hashA: "A72F91C8E2D7B104...",
    hashB: "A72F91C8E2D7B104..."
  }
};
document.documentElement.dataset.theme = state.theme;

function go(route){ location.hash = route; state.route = route; render(); window.scrollTo({top:0, behavior:"smooth"}); }
window.addEventListener("hashchange",()=>{state.route=location.hash.replace("#","")||"landing";render();});

function logo(){
  return `<div class="logo"><div class="logo-mark">R✓</div><div><span>RunProof</span><small>Build • Verify • Prove</small></div></div>`;
}
function toast(msg){
  document.querySelector(".toast")?.remove();
  const t=document.createElement("div");t.className="toast";t.textContent=msg;document.body.appendChild(t);
  setTimeout(()=>t.remove(),2600);
}
function esc(v){return String(v||"").replace(/[&<>"']/g,s=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[s]));}

function landing(){
return `
<div class="page">
  <nav class="topnav">
    ${logo()}
    <div class="navlinks"><span>Product</span><span>How it works</span><span>Security</span><span>Docs</span></div>
    <div style="display:flex;gap:9px">
      <button class="btn btn-secondary" onclick="go('login')">Log in</button>
      <button class="btn btn-primary" onclick="go('signup')">Start verifying</button>
    </div>
  </nav>
  <section class="hero">
    <div>
      <span class="badge info">◈ Reproducibility intelligence for software</span>
      <h1 class="gradient-text">Your code works here.<br>Will it work anywhere?</h1>
      <p>RunProof scans, explains, builds, tests and verifies whether a software project can be reproduced on another machine — then creates a proof passport you can share.</p>
      <div class="hero-actions">
        <button class="btn btn-primary btn-large" onclick="go('signup')">⚡ Start verifying</button>
        <button class="btn btn-secondary btn-large" onclick="go('demo')">▶ View product demo</button>
      </div>
      <div style="display:flex;gap:18px;flex-wrap:wrap;margin-top:25px;color:var(--muted);font-size:13px">
        <span>✓ Beginner friendly</span><span>✓ CLI + Dashboard</span><span>✓ Secure by design</span><span>✓ Reproducibility proof</span>
      </div>
    </div>
    <div class="hero-card glass">
      <div class="terminal">
        <div class="term-top"><span class="dot red"></span><span class="dot yellow"></span><span class="dot green"></span></div>
        <div style="font-weight:800;color:white;margin-bottom:12px">runproof check ./MyProject</div>
        <div class="term-line"><span>Project detected</span><span class="term-ok">PASS ✓</span></div>
        <div class="term-line"><span>Python 3.11</span><span class="term-ok">PASS ✓</span></div>
        <div class="term-line"><span>requirements.txt</span><span class="term-ok">FOUND ✓</span></div>
        <div class="term-line"><span>18 dependencies</span><span class="term-warn">2 warnings ⚠</span></div>
        <div class="term-line"><span>Environment</span><span class="term-warn">1 issue ⚠</span></div>
        <div class="term-line"><span>Build</span><span class="term-ok">PASS ✓</span></div>
        <div class="term-line"><span>12 tests</span><span class="term-ok">PASS ✓</span></div>
        <div class="score-hero"><div class="score-ring"><span>92</span></div><div><b style="font-size:18px;color:white">Very Ready</b><div style="color:#94a3b8;margin-top:4px">Reproducibility readiness score</div></div></div>
      </div>
    </div>
  </section>
  <section class="feature-strip">
    <div class="feature"><div style="font-size:27px">🔍</div><h3>Inspect</h3><p>Understand language, runtime, files, packages and settings automatically.</p></div>
    <div class="feature"><div style="font-size:27px">🩺</div><h3>RunProof Doctor</h3><p>Shows what is wrong, why it matters and how to fix it.</p></div>
    <div class="feature"><div style="font-size:27px">🔐</div><h3>Verify</h3><p>Build twice, fingerprint artifacts and compare the results.</p></div>
    <div class="feature"><div style="font-size:27px">🛂</div><h3>Passport</h3><p>Create a clear digital proof record for the verified project.</p></div>
  </section>
</div>`;
}

function authPage(type){
 const signup=type==="signup";
 return `<div class="auth-wrap">
   <div class="auth-card glass">
     ${logo()}
     <h1>${signup?"Create your account":"Welcome back 👋"}</h1>
     <p>${signup?"Start your first secure software verification.":"Continue to your RunProof workspace."}</p>
     ${signup?`
       <div class="field"><label>Full name</label><input id="name" placeholder="Your name"></div>
       <div class="field"><label>Phone number</label><input id="phone" placeholder="+91 98765 43210"></div>`:""}
     <div class="field"><label>Email</label><input id="email" type="email" placeholder="you@example.com"></div>
     <div class="field"><label>Password</label><input id="password" type="password" placeholder="••••••••"></div>
     ${signup?`<div class="field"><label>Confirm password</label><input id="confirm" type="password" placeholder="••••••••"></div>`:""}
     <div class="auth-row"><span>${signup?"By continuing, you agree to our security rules.":"☐ Remember me"}</span><span class="auth-link">${signup?"":"Forgot password?"}</span></div>
     <div class="auth-actions">
       <button class="btn btn-primary btn-large" onclick="${signup?"startSignup()":"login()"}">${signup?"Create account":"Log in"}</button>
       <button class="btn btn-secondary" onclick="toast('GitHub sign-in is a UI demo in this prototype.')">◈ Continue with GitHub</button>
     </div>
     <p style="text-align:center;margin-top:18px">${signup?"Already have an account?":"New to RunProof?"} <span class="auth-link" onclick="go('${signup?"login":"signup"}')">${signup?"Log in":"Create account"}</span></p>
     <div class="security-note">🔐 Passwords, OTP secrets and API keys should be handled by a secure backend/auth provider. This prototype keeps the OTP as a demo only.</div>
   </div>
 </div>`;
}

function startSignup(){
 const name=document.getElementById("name").value.trim()||"RunProof User";
 const email=document.getElementById("email").value.trim()||"user@example.com";
 const phone=document.getElementById("phone").value.trim()||"+91 XXXXXXX123";
 const pwd=document.getElementById("password").value;
 const confirm=document.getElementById("confirm").value;
 if(pwd && confirm && pwd!==confirm){toast("Passwords do not match.");return;}
 sessionStorage.setItem("pending_user",JSON.stringify({name,email,phone}));
 go("otp");
}
function login(){
 const email=document.getElementById("email").value.trim()||"user@example.com";
 state.user={name:"RunProof User",email,phone:"+91 XXXXXXX123"};
 localStorage.setItem("runproof_user",JSON.stringify(state.user));go("dashboard");
}
function otpPage(){
 const p=JSON.parse(sessionStorage.getItem("pending_user")||'{"name":"RunProof User","phone":"+91 XXXXXXX123","email":"user@example.com"}');
 return `<div class="auth-wrap"><div class="auth-card glass">
 ${logo()}<h1>Verify your phone</h1><p>We sent a 6-digit demo code to <b>${esc(p.phone)}</b>.</p>
 <div class="otp-boxes">${[0,1,2,3,4,5].map(i=>`<input maxlength="1" id="otp${i}" oninput="otpNext(${i})">`).join("")}</div>
 <button class="btn btn-primary btn-large" style="width:100%" onclick="verifyOtp()">Verify OTP</button>
 <p style="text-align:center">Demo code: <b>482175</b> · <span class="auth-link" onclick="toast('A new demo OTP would be sent here.')">Resend code</span></p>
 <div class="security-note">🔐 In production: OTP must be generated and verified on the backend, expire quickly, and be rate-limited.</div>
 </div></div>`;
}
function otpNext(i){const el=document.getElementById("otp"+i);if(el.value&&i<5)document.getElementById("otp"+(i+1)).focus();}
function verifyOtp(){
 let code="";for(let i=0;i<6;i++)code+=(document.getElementById("otp"+i).value||"");
 if(code!=="482175"){toast("Use demo OTP: 482175");return;}
 const p=JSON.parse(sessionStorage.getItem("pending_user")||"{}");
 state.user={name:p.name||"RunProof User",email:p.email||"user@example.com",phone:p.phone||"+91 XXXXXXX123"};
 localStorage.setItem("runproof_user",JSON.stringify(state.user));go("onboarding");
}
function onboarding(){
 return `<div class="auth-wrap"><div class="auth-card glass" style="width:min(690px,94vw)">
 ${logo()}<h1>Welcome to RunProof 👋</h1><p>Tell us how you plan to use RunProof. You can change this later.</p>
 <div class="mini-cards">
   <div class="mini">🎓<strong>Student Project</strong></div><div class="mini">🚀<strong>Hackathon</strong></div><div class="mini">💻<strong>Development</strong></div>
 </div>
 <div class="field"><label>Primary technology</label><select><option>Python</option><option>Node.js</option><option>Java</option><option>Other</option></select></div>
 <button class="btn btn-primary btn-large" style="width:100%" onclick="go('dashboard')">Finish setup →</button>
 </div></div>`;
}

const sideItems=[
 ["⌂","Dashboard","dashboard"],["＋","New Analysis","new"],["▣","Projects","projects"],["✓","Verifications","verify"],
 ["🩺","Issues","doctor"],["🛂","Passports","passport"],["📄","Reports","reports"],["","spacer",""],
 ["👥","Team","team"],["🔔","Notifications","notifications"],["🔐","Security","security"],["⚙","Settings","settings"],["?","Help","help"]
];
function shell(content,active){
 if(!state.user){state.user={name:"RunProof User",email:"user@example.com",phone:"+91 XXXXXXX123"};}
 return `<div class="shell">
  <aside class="sidebar">${logo()}<div class="side-nav">
  ${sideItems.map(([ic,tx,r])=>tx==="spacer"?`<div class="side-spacer"></div>`:`<div class="side-item ${active===r?"active":""}" onclick="go('${r}')"><b>${ic}</b><span>${tx}</span></div>`).join("")}
  </div></aside>
  <main class="main">
    <div class="appbar">
      <div class="searchbox" onclick="openCommand()">⌕ <span>Search projects, issues, reports…</span><span style="margin-left:auto">Ctrl K</span></div>
      <button class="icon-btn" onclick="toggleTheme()">${state.theme==="dark"?"☀":"🌙"}</button>
      <button class="icon-btn" onclick="toast('No new notifications.')">🔔</button>
      <div class="avatar">${esc((state.user.name||"R")[0])}</div>
    </div>
    <div class="content">${content}</div>
  </main>
 </div>`;
}
function dashboard(){
 const n=esc(state.user?.name?.split(" ")[0]||"there");
 return shell(`
 <div class="welcome"><div><h1>Good morning, ${n} 👋</h1><p>Ready to prove your next build?</p></div><button class="btn btn-primary btn-large" onclick="go('new')">＋ Analyze New Project</button></div>
 <div class="stats">
   <div class="stat"><small>Projects checked</small><strong>12</strong><span class="badge info">+3 this week</span></div>
   <div class="stat"><small>Verified</small><strong>9</strong><span class="badge success">✓ 75%</span></div>
   <div class="stat"><small>Need attention</small><strong>5</strong><span class="badge warning">⚠ Review</span></div>
   <div class="stat"><small>Average score</small><strong>93</strong><span class="badge success">Very Ready</span></div>
 </div>
 <div class="grid-2">
   <div class="card"><div class="card-title"><h3>Recent projects</h3><span class="auth-link" onclick="go('projects')">View all</span></div>
     ${projectRow("CivicPulse","Python",98,"Verified","success")}
     ${projectRow("StudentApp","Node.js",91,"Ready","success")}
     ${projectRow("MyAPI","Python",74,"Issues","warning")}
     ${projectRow("JavaStore","Java",62,"Failed","danger")}
   </div>
   <div class="card"><div class="card-title"><h3>Activity</h3><span class="muted">Today</span></div>
     <div class="activity">
       ${activity("✓","CivicPulse verified","Artifact hashes matched · 12:49 PM")}
       ${activity("🩺","MyAPI issue found","DATABASE_URL missing · 12:31 PM")}
       ${activity("📄","Passport generated","StudentApp · 11:58 AM")}
       ${activity("🔍","Project scanned","JavaStore · 11:20 AM")}
     </div>
   </div>
 </div>`, "dashboard");
}
function projectRow(name,type,score,status,kind){return `<div class="project-row"><div class="project-name">${name}</div><div>${type}</div><div>${score}/100</div><div><span class="badge ${kind}">${status}</span></div></div>`}
function activity(ic,title,sub){return `<div class="activity-item"><div class="activity-icon">${ic}</div><div><b style="font-size:14px">${title}</b><div class="muted" style="font-size:12px;margin-top:3px">${sub}</div></div></div>`}

function wizardSteps(active){
 const labels=["Project","Scan","Check","Doctor","Score","Verify","Result"];
 return `<div class="steps">${labels.map((l,i)=>`<div class="step ${i<active?"done":i===active?"active":""}"><span class="step-bullet">${i<active?"✓":i+1}</span>${l}</div>${i<labels.length-1?`<span class="muted">→</span>`:""}`).join("")}</div>`;
}
function newProject(){
 return shell(`
 <div class="wizard-head"><div><h2 style="margin:0">New RunProof Analysis</h2><p class="muted">One guided journey from project to proof.</p></div></div>
 ${wizardSteps(0)}
 <div class="upload-zone" style="margin-top:22px">
   <div>
     <div class="upload-icon">📁</div><h2>Choose your project</h2><p>Drop a project folder here or browse from your computer.</p>
     <button class="btn btn-primary btn-large" onclick="simulatePick()">Browse Project</button>
     <button class="btn btn-secondary btn-large" onclick="toast('GitHub import is a frontend demo in this ZIP.')">◈ Import from GitHub</button>
     <div style="margin-top:22px" class="security-note">🔐 Your code stays private in this frontend demo. In production, use authenticated upload endpoints and strict access controls.</div>
   </div>
 </div>`, "new");
}
function simulatePick(){state.project.name="MyProject";go("scan");}

function scan(){
 setTimeout(startScan,150);
 return shell(`
 <div class="wizard-head"><div><h2 style="margin:0">Scanning ${esc(state.project.name)}</h2><p class="muted">RunProof is learning what your project needs.</p></div></div>
 ${wizardSteps(1)}
 <div class="progress-wrap">
   <div class="card" style="margin-top:22px">
     <div style="display:flex;justify-content:space-between;align-items:center"><b>Live Project Scan</b><span id="scanPercent" class="badge info">0%</span></div>
     <div class="progress-bar"><div id="scanFill" class="progress-fill"></div></div>
     <div id="scanList" class="scan-list"></div>
   </div>
   <div id="scanMini" class="mini-cards"></div>
 </div>`, "new");
}
function startScan(){
 const tasks=["Reading files","Detecting language","Checking runtime","Finding dependency files","Checking configuration","Checking environment","Preparing build"];
 let idx=0;
 const list=document.getElementById("scanList"),fill=document.getElementById("scanFill"),pct=document.getElementById("scanPercent");
 if(!list)return;
 const timer=setInterval(()=>{
   if(idx<tasks.length){
     list.innerHTML += `<div class="scan-row"><span>${tasks[idx]}</span><span class="badge success">Done ✓</span></div>`;
     idx++;let p=Math.round(idx/tasks.length*100);fill.style.width=p+"%";pct.textContent=p+"%";
   } else {
     clearInterval(timer);
     document.getElementById("scanMini").innerHTML=`
       <div class="mini"><small>Project Type</small><strong>🐍 Python</strong></div>
       <div class="mini"><small>Dependencies</small><strong>18</strong></div>
       <div class="mini"><small>Tests Detected</small><strong>12</strong></div>`;
     setTimeout(()=>go("check"),700);
   }
 },350);
}

function checks(){
 const desc=(simple,tech)=>state.beginner?simple:tech;
 return shell(`
 <div class="wizard-head"><div><h2 style="margin:0">Project Check</h2><p class="muted">Every check can be opened and understood.</p></div><span class="badge info">Beginner Mode ${state.beginner?"ON":"OFF"}</span></div>
 ${wizardSteps(2)}
 <div class="check-grid" style="margin-top:22px">
  ${check("✓","ok","Project Detection",desc("RunProof understands what project this is.","Project type and manifest detection passed."),"PASS")}
  ${check("✓","ok","Runtime",desc("The correct Python version is available.","Runtime compatibility passed: Python 3.11."),"PASS")}
  ${check("✓","ok","Required Files",desc("Important setup files were found.","All required manifests and config examples found."),"PASS")}
  ${check("⚠","warn","Dependencies",desc("2 package versions are not fixed.","2 dependencies are unpinned and may drift."),"WARNING")}
  ${check("✕","bad","Environment",desc("One important setting is missing.","DATABASE_URL is not configured."),"ISSUE")}
  ${check("✓","ok","Build",desc("The project can be built.","Build command completed successfully."),"PASS")}
  ${check("✓","ok","Tests",desc("All detected tests passed.","12/12 tests passed."),"PASS")}
  ${check("✓","ok","Security",desc("Secret values are hidden from the report.","Secret redaction policy passed."),"PASS")}
 </div>
 <div style="display:flex;justify-content:flex-end;margin-top:18px"><button class="btn btn-primary" onclick="go('doctor')">Open RunProof Doctor →</button></div>`, "new");
}
function check(ic,kind,title,desc,status){return `<div class="check-item"><div class="check-icon ${kind}">${ic}</div><div style="flex:1"><div style="display:flex;justify-content:space-between;gap:10px"><h4>${title}</h4><span class="badge ${kind==="ok"?"success":kind==="warn"?"warning":"danger"}">${status}</span></div><p>${desc}</p><div style="margin-top:8px"><span class="auth-link" onclick="toast('What is this? Why does it matter? How do I fix it?')">What is this? →</span></div></div></div>`}

function doctor(){
 return shell(`
 <div class="wizard-head"><div><h2 style="margin:0">🩺 RunProof Doctor</h2><p class="muted">Find the problem. Understand it. Fix it.</p></div><span class="badge danger">2 problems found</span></div>
 ${wizardSteps(3)}
 <div style="margin-top:22px">
  ${doctorCard("🔴","DATABASE_URL is missing","High","The project expects a database connection.","The application may fail during startup.","Configure DATABASE_URL before running.","danger")}
  ${doctorCard("🟡","NumPy version is not fixed","Medium","The dependency is written without an exact version.","A future package version may behave differently.","Pin an exact compatible NumPy version.","warning")}
 </div>
 <div style="display:flex;justify-content:flex-end"><button class="btn btn-primary" onclick="go('score')">View Readiness Score →</button></div>`, "doctor");
}
function doctorCard(ic,title,severity,what,risk,fix,kind){return `<div class="doctor-card">
 <div class="doctor-head"><div><h3>${ic} ${title}</h3><div class="muted" style="margin-top:5px">RunProof found a reproducibility risk.</div></div><span class="badge ${kind}">${severity}</span></div>
 <div class="doctor-grid">
  <div class="doctor-block"><small>What happened?</small><b>${what}</b></div>
  <div class="doctor-block"><small>Why it matters</small><b>${risk}</b></div>
  <div class="doctor-block"><small>How to fix</small><b>${fix}</b></div>
 </div>
 <div style="margin-top:14px"><button class="btn btn-secondary" onclick="toast('A safe fix suggestion would be generated here.')">✨ Generate safe fix</button></div>
 </div>`}

function score(){
 const lines=[["Project",100],["Runtime",100],["Files",100],["Dependencies",82],["Environment",85],["Build",100],["Tests",100]];
 return shell(`
 <div class="wizard-head"><div><h2 style="margin:0">Readiness Score</h2><p class="muted">A transparent score — never a mystery number.</p></div></div>
 ${wizardSteps(4)}
 <div class="grid-2" style="margin-top:22px">
  <div class="card"><div class="big-score"><div><strong>92</strong><span>/100</span></div></div><h2 style="text-align:center;margin:4px">Very Ready</h2><p class="muted" style="text-align:center">Ready for final reproducibility verification.</p></div>
  <div class="card"><div class="card-title"><h3>Why 92?</h3></div><div class="score-lines">${lines.map(([l,p])=>`<div class="score-line"><span>${l}</span><div class="line-track"><div class="line-fill" style="width:${p}%"></div></div><b>${p}%</b></div>`).join("")}</div>
  <div style="margin-top:18px;padding-top:14px;border-top:1px solid var(--line)"><div>−5 Unpinned dependency versions</div><div style="margin-top:7px">−3 Missing environment setting</div></div></div>
 </div>
 <div style="display:flex;justify-content:flex-end;margin-top:18px"><button class="btn btn-success btn-large" onclick="go('verify')">🔐 Prove Reproducibility</button></div>`, "new");
}

function verifyPage(){
 return shell(`
 <div class="wizard-head"><div><h2 style="margin:0">Reproducibility Lab</h2><p class="muted">Two clean builds. Two fingerprints. One proof.</p></div><span class="badge success">Verification Ready</span></div>
 ${wizardSteps(5)}
 <div class="card" style="margin-top:22px;padding:24px">
  <div class="verify-lab">
   <div class="build-card"><div style="font-size:34px">A</div><h3>Clean Build A</h3><p class="muted">Independent temporary copy</p><div class="progress-bar"><div class="progress-fill" style="width:100%"></div></div><span class="badge success">Build passed ✓</span><div class="hash">${state.project.hashA}</div></div>
   <div><div class="compare-icon">✓</div><div style="text-align:center;margin-top:9px;font-weight:800;color:#86efac">MATCH</div></div>
   <div class="build-card"><div style="font-size:34px">B</div><h3>Clean Build B</h3><p class="muted">Second independent temporary copy</p><div class="progress-bar"><div class="progress-fill" style="width:100%"></div></div><span class="badge success">Build passed ✓</span><div class="hash">${state.project.hashB}</div></div>
  </div>
  <div style="text-align:center;margin-top:24px"><h1 style="color:#86efac;margin-bottom:7px">✓ VERIFIED REPRODUCIBLE</h1><p class="muted">Both build artifacts produced the same fingerprint.</p><button class="btn btn-primary btn-large" onclick="go('passport')">View RunProof Passport →</button></div>
 </div>`, "verify");
}

function passport(){
 return shell(`
 <div class="section-head"><div><h2>🛂 RunProof Passport</h2><p class="muted">A shareable proof record — without exposing source code.</p></div><div style="display:flex;gap:8px"><button class="btn btn-secondary" onclick="downloadPassport()">Download JSON</button><button class="btn btn-primary" onclick="toast('Share link would be created by the backend.')">Share verification</button></div></div>
 <div class="passport">
  <div class="passport-top">${logo()}<span class="badge success">VERIFIED</span></div>
  <div class="passport-grid">
   ${passField("Project","MyProject")}${passField("Project ID","RP-8A97CF")}${passField("Language","Python 3.11")}${passField("Readiness","100 / 100")}
   ${passField("Build","Passed ✓")}${passField("Tests","12 / 12 Passed")}${passField("Artifact A","A72F91C8...")}${passField("Artifact B","A72F91C8...")}
  </div>
  <div class="verified">✓ VERIFIED REPRODUCIBLE</div>
 </div>`, "passport");
}
function passField(a,b){return `<div class="pass-field"><small>${a}</small><strong>${b}</strong></div>`}
function downloadPassport(){
 const data={project:"MyProject",project_id:"RP-8A97CF",language:"Python",version:"3.11",score:100,build:"passed",tests:"12/12",hash_a:state.project.hashA,hash_b:state.project.hashB,verified:true};
 const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="runproof-passport.json";a.click();URL.revokeObjectURL(a.href);
}

function projects(){
 return shell(`<div class="section-head"><div><h2>Projects</h2><p class="muted">Every project and its current RunProof status.</p></div><button class="btn btn-primary" onclick="go('new')">＋ New Analysis</button></div>
 <div class="card">${projectRow("CivicPulse","Python",98,"Verified","success")}${projectRow("StudentApp","Node.js",91,"Ready","success")}${projectRow("MyAPI","Python",74,"Issues","warning")}${projectRow("JavaStore","Java",62,"Failed","danger")}</div>`,"projects");
}
function reports(){
 return shell(`<div class="section-head"><div><h2>Reports</h2><p class="muted">Human-readable checks, problems, fixes and proof.</p></div></div>
 <div class="card"><h3>MyProject — Latest Report</h3><p class="muted">Project information · Runtime · Dependencies · Environment · Build · Tests · Issues · Fixes · Verification</p>
 <div style="display:flex;gap:10px;margin-top:16px"><button class="btn btn-primary" onclick="downloadReport()">Download HTML Report</button><button class="btn btn-secondary" onclick="go('passport')">Open Passport</button></div></div>`,"reports");
}
function downloadReport(){
 const html=`<!doctype html><title>RunProof Report</title><style>body{font-family:Arial;padding:40px;max-width:900px;margin:auto}h1{color:#2563eb}.ok{color:green}.warn{color:#b7791f}</style><h1>RunProof Report</h1><h2>MyProject</h2><p>Python 3.11</p><h3>Checks</h3><p class="ok">Project ✓ Runtime ✓ Files ✓ Build ✓ Tests ✓</p><p class="warn">Dependencies: 2 unpinned · Environment: DATABASE_URL missing</p><h3>Reproducibility</h3><p class="ok">Build A hash matched Build B hash. VERIFIED REPRODUCIBLE ✓</p>`;
 const blob=new Blob([html],{type:"text/html"});const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="runproof-report.html";a.click();URL.revokeObjectURL(a.href);
}

function security(){
 return shell(`<div class="section-head"><div><h2>🔐 Security Center</h2><p class="muted">Control identity, access and privacy.</p></div><span class="badge success">Secure session</span></div>
 <div class="security-grid">
  ${securityItem("Phone verification","Verified ✓","success")}
  ${securityItem("Email verification","Verified ✓","success")}
  ${securityItem("Two-factor authentication","Enabled ✓","success")}
  ${securityItem("Active sessions","1 device","info")}
  ${securityItem("Secret redaction","Always on ✓","success")}
  ${securityItem("Project visibility","Private by default","info")}
 </div>
 <div class="card" style="margin-top:15px"><h3>Your code belongs to you.</h3><p class="muted">Production version should use HTTPS, secure sessions, backend-side OTP verification, password hashing, rate limits, strict authorization and secret redaction. Never place production credentials in frontend JavaScript.</p></div>`,"security");
}
function securityItem(a,b,k){return `<div class="security-item"><small class="muted">${a}</small><h3>${b}</h3><span class="badge ${k}">${k==="success"?"Protected":"Active"}</span></div>`}

function settings(){
 return shell(`<div class="section-head"><div><h2>Settings</h2><p class="muted">Personalize RunProof.</p></div></div>
 <div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--line)"><div><b>Beginner Mode</b><div class="muted" style="font-size:13px">Explain technical words in simple English.</div></div><span class="toggle ${state.beginner?"on":""}" onclick="toggleBeginner()"></span></div>
  <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--line)"><div><b>Appearance</b><div class="muted" style="font-size:13px">Dark or light interface.</div></div><button class="btn btn-secondary" onclick="toggleTheme()">${state.theme==="dark"?"Switch to Light":"Switch to Dark"}</button></div>
  <div style="display:flex;justify-content:space-between;align-items:center;padding:12px 0"><div><b>Sign out</b><div class="muted" style="font-size:13px">End this demo session.</div></div><button class="btn btn-danger" onclick="logout()">Sign out</button></div>
 </div>`,"settings");
}
function toggleBeginner(){state.beginner=!state.beginner;localStorage.setItem("runproof_beginner",state.beginner);render();}
function toggleTheme(){state.theme=state.theme==="dark"?"light":"dark";localStorage.setItem("runproof_theme",state.theme);document.documentElement.dataset.theme=state.theme;render();}
function logout(){localStorage.removeItem("runproof_user");state.user=null;go("landing");}

function simplePage(title,desc,active,body=""){
 return shell(`<div class="section-head"><div><h2>${title}</h2><p class="muted">${desc}</p></div></div><div class="card">${body||`<h3>RunProof ${title}</h3><p class="muted">This screen is included in the starter frontend and is ready to connect to your backend.</p>`}</div>`,active);
}
function demo(){state.user={name:"Demo User",email:"demo@runproof.local",phone:"+91 XXXXXXX123"};localStorage.setItem("runproof_user",JSON.stringify(state.user));go("dashboard");}

function openCommand(){
 document.querySelector(".command")?.remove();
 const el=document.createElement("div");el.className="command";el.innerHTML=`<div class="command-box"><input autofocus placeholder="Search RunProof…" onkeydown="if(event.key==='Escape')closeCommand()"><div class="cmd-item" onclick="go('new');closeCommand()">＋ New project analysis</div><div class="cmd-item" onclick="go('verify');closeCommand()">🔐 Verify project</div><div class="cmd-item" onclick="go('passport');closeCommand()">🛂 Open passport</div><div class="cmd-item" onclick="go('security');closeCommand()">🔐 Security center</div><div class="cmd-item" onclick="go('settings');closeCommand()">⚙ Settings</div></div>`;
 el.onclick=e=>{if(e.target===el)closeCommand()};document.body.appendChild(el);el.querySelector("input").focus();
}
function closeCommand(){document.querySelector(".command")?.remove();}
window.addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==="k"){e.preventDefault();openCommand();}});

function render(){
 const r=state.route;
 let html;
 if(r==="landing")html=landing();
 else if(r==="signup")html=authPage("signup");
 else if(r==="login")html=authPage("login");
 else if(r==="otp")html=otpPage();
 else if(r==="onboarding")html=onboarding();
 else if(r==="dashboard")html=dashboard();
 else if(r==="new")html=newProject();
 else if(r==="scan")html=scan();
 else if(r==="check")html=checks();
 else if(r==="doctor")html=doctor();
 else if(r==="score")html=score();
 else if(r==="verify")html=verifyPage();
 else if(r==="passport")html=passport();
 else if(r==="projects")html=projects();
 else if(r==="reports")html=reports();
 else if(r==="security")html=security();
 else if(r==="settings")html=settings();
 else if(r==="team")html=simplePage("👥 Team Workspace","Invite people and control project roles.","team",`<h3>CivicPulse Team</h3><div class="project-row"><b>Divya</b><span>Owner</span><span class="hide-mobile">Full access</span><span class="badge success">Active</span></div><div class="project-row"><b>Karthik</b><span>Developer</span><span class="hide-mobile">Check + Verify</span><span class="badge success">Active</span></div><div class="project-row"><b>Cherry</b><span>Viewer</span><span class="hide-mobile">View only</span><span class="badge info">Viewer</span></div>`);
 else if(r==="notifications")html=simplePage("🔔 Notifications","Verification, issue and passport updates.","notifications",`<div class="activity">${activity("✓","Verification completed","CivicPulse reached 100/100")}${activity("⚠","New issue detected","MyAPI has 2 issues")}${activity("📄","Passport generated","StudentApp passport is ready")}</div>`);
 else if(r==="help")html=simplePage("? Help Center","Every technical term explained simply.","help",`<div class="check-grid">${["What is reproducibility?","What is a runtime?","What is a dependency?","What is SHA-256?","What is an environment variable?","What is a build?","What is a test?","What is a RunProof Passport?"].map(t=>`<div class="check-item"><div class="check-icon ok">?</div><div><h4>${t}</h4><p>Click in the production app to see a beginner-friendly explanation.</p></div></div>`).join("")}</div>`);
 else html=landing();
 app.innerHTML=html;
}
render();