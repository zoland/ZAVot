// js/af_protocol.js
requireRole("admin");
let pid = getParam("id");

const QUORUMS = ["1/2","3/4","1"];
let quorumDefault = "1/2";

let initial = null;
let materials = [];
let pendingMaterials = [];
let pendingRemovals = [];
let selectedMatIndex = null;

let matStartX = 0;
let matStartY = 0;
let matSwipeRow = null;
let matSwipeIndex = null;
let matLastWheel = 0;

function qs(id){ return document.getElementById(id); }

function showWait(text="Сохранение..."){
  const el = document.getElementById("waitOverlay");
  if (!el) return;
  el.querySelector(".wait-text").textContent = text;
  el.classList.add("active");
}
function hideWait(){
  const el = document.getElementById("waitOverlay");
  if (!el) return;
  el.classList.remove("active");
}

function snapshot(){
  return {
    num: qs("p_num").value.trim(),
    date: qs("p_date").value.trim(),
    status: document.querySelector("input[name=p_status]:checked").value,
    vote_type: document.querySelector("input[name=p_type]:checked").value,
    qcount: Number(qs("p_qcount").value || 0),
    file: qs("p_file_name").value.trim(),
    quorum_default: quorumDefault,
    materials: materials.map(m => (m && m.name) ? m.name : "").join("|")
  };
}

function isDirty(){
  if (pendingMaterials.length || pendingRemovals.length) return true;
  if (!initial) return true;
  const curr = snapshot();
  return Object.keys(curr).some(k => curr[k] !== initial[k]);
}

function triggerProtocolFile(){ qs("p_file").click(); }

qs("p_file").addEventListener("change", () => {
  const f = qs("p_file").files[0];
  qs("p_file_name").value = f ? f.name : "";
});

function addMaterials(){ qs("p_materials").click(); }

qs("p_materials").addEventListener("change", async () => {
  const files = Array.from(qs("p_materials").files);
  for (const f of files) {
    if (!f.name.toLowerCase().endsWith(".pdf")) continue;
    if (materials.find(m => m.name === f.name)) continue;
    materials.push({name: f.name, persisted:false});
    pendingMaterials.push(f);
  }
  qs("p_materials").value = "";
  renderMaterials();
});

async function uploadMaterial(file){
  if (!pid) return;
  const fd = new FormData();
  fd.append("file", file);
  const res = await fetch(`/api/admin/protocols/${pid}/materials`, { method:"POST", body:fd });
  if (!res.ok) alert("Не удалось загрузить приложение");
}

async function deleteMaterial(name){
  if (!pid) return;
  const res = await fetch(`/api/admin/protocols/${pid}/materials?name=${encodeURIComponent(name)}`, { method:"DELETE" });
  if (!res.ok) alert("Не удалось удалить приложение");
}

function displayName(x){
  if (!x) return "";
  if (typeof x === "string") return x.split(/[\\/]/).pop();
  if (x.name) return x.name.split(/[\\/]/).pop();
  return "";
}

function renderMaterials(){
  const tbody = document.querySelector("#materialsTable tbody");
  tbody.innerHTML = "";

  materials.forEach((m, i) => {
    const name = displayName(m);
    const tr = document.createElement("tr");
    tr.classList.add("mat-row");
    tr.dataset.index = i;
    tr.innerHTML = `<td>${name}</td>`;

    tr.addEventListener("click", () => selectMatRow(tr, i));
    tr.addEventListener("pointerdown", e => matPointerDown(e, tr, i));
    tr.addEventListener("pointerup", e => matPointerUp(e, tr, i));
    tr.addEventListener("wheel", e => matWheelSwipe(e, tr, i), {passive:false});

    if (selectedMatIndex === i) tr.classList.add("selected");
    tbody.appendChild(tr);
  });

  const add = document.createElement("tr");
  add.className = "add-row";
  add.innerHTML = `<td>--- добавить ---</td>`;
  add.onclick = addMaterials;
  tbody.appendChild(add);
}

function selectMatRow(tr, i){
  document.querySelectorAll("#materialsTable tbody tr.mat-row")
    .forEach(r => r.classList.remove("selected"));
  tr.classList.add("selected");
  selectedMatIndex = i;
}

function clearMatSelection(){
  document.querySelectorAll("#materialsTable tbody tr.mat-row")
    .forEach(r => r.classList.remove("selected"));
  selectedMatIndex = null;
}

async function removeMaterial(i){
  const m = materials[i];
  materials.splice(i, 1);
  clearMatSelection();
  renderMaterials();

  if (m.persisted) pendingRemovals.push(m.name);
  else pendingMaterials = pendingMaterials.filter(f => f.name !== m.name);
}

function matPointerDown(e, tr, i){
  if (e.pointerType !== "touch") return;
  matStartX = e.clientX;
  matStartY = e.clientY;
  matSwipeRow = tr;
  matSwipeIndex = i;
  selectMatRow(tr, i);
}

function matPointerUp(e, tr, i){
  if (e.pointerType !== "touch") return;
  if (!matSwipeRow) return;

  const dx = e.clientX - matStartX;
  const dy = e.clientY - matStartY;

  if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
    if (dx < 0) {
      if (confirm("Удалить приложение?")) removeMaterial(matSwipeIndex);
      else clearMatSelection();
    }
  }

  matSwipeRow = null;
  matSwipeIndex = null;
}

function matWheelSwipe(e, tr, i){
  const now = Date.now();
  if (now - matLastWheel < 500) return;

  if (Math.abs(e.deltaX) > Math.abs(e.deltaY) && Math.abs(e.deltaX) > 40) {
    e.preventDefault();
    matLastWheel = now;
    selectMatRow(tr, i);

    if (e.deltaX > 0) {
      if (confirm("Удалить приложение?")) removeMaterial(i);
      else clearMatSelection();
    }
  }
}

function updateQuorumBtn(){
  const btn = qs("btnQuorum");
  btn.textContent = `Кворум: ${quorumDefault}`;
  btn.classList.remove("q-half","q-34","q-1");
  btn.classList.add(quorumDefault === "1/2" ? "q-half" :
                    quorumDefault === "3/4" ? "q-34" : "q-1");
}

function toggleQuorumDefault(){
  const idx = QUORUMS.indexOf(quorumDefault);
  quorumDefault = QUORUMS[(idx+1) % QUORUMS.length];
  updateQuorumBtn();
}

function buildJson(){
  return {
    num: qs("p_num").value.trim(),
    date: qs("p_date").value.trim(),
    status: document.querySelector("input[name=p_status]:checked").value,
    vote_type: document.querySelector("input[name=p_type]:checked").value,
    qcount: Number(qs("p_qcount").value || 0),
    file: qs("p_file_name").value.trim(),
    quorum_default: quorumDefault
  };
}

async function sendJson(url, method, body){
  const res = await fetch(url, {
    method,
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(body)
  });

  if (!res.ok) return { ok:false };
  const ct = res.headers.get("content-type") || "";
  const data = ct.includes("application/json") ? await res.json() : null;
  return { ok:true, data };
}

async function sendForm(url, method, fd){
  const res = await fetch(url, { method, body: fd });
  if (!res.ok) return { ok:false };
  const ct = res.headers.get("content-type") || "";
  const data = ct.includes("application/json") ? await res.json() : null;
  return { ok:true, data };
}

async function saveProtocol(){
  const num = qs("p_num").value.trim();
  if (!/^\d+$/.test(num)) {
    alert("Номер протокола должен содержать только цифры");
    return false;
  }

  let ok = false;

  if (pid){
    const r = await sendJson(`/api/admin/protocols/${pid}`, "PUT", buildJson());
    ok = r.ok;
  } else {
    const file = qs("p_file").files[0];
    if (!file) {
      alert("Файл протокола обязателен");
      return false;
    }

    const fd = new FormData();
    fd.append("num", num);
    fd.append("date", qs("p_date").value.trim());
    fd.append("status", document.querySelector("input[name=p_status]:checked").value);
    fd.append("vote_type", document.querySelector("input[name=p_type]:checked").value);
    fd.append("qcount", qs("p_qcount").value.trim());
    fd.append("quorum_default", quorumDefault);
    fd.append("file", file);

    const r = await sendForm("/api/admin/protocols/create", "POST", fd);
    if (r.ok && r.data && r.data.id) {
      pid = r.data.id;
      ok = true;
    } else ok = false;
  }

  if (!ok) return false;

  for (const f of pendingMaterials) await uploadMaterial(f);
  pendingMaterials = [];

  for (const name of pendingRemovals) await deleteMaterial(name);
  pendingRemovals = [];

  initial = snapshot();
  return true;
}

async function exitCard(){
  if (!isDirty()) {
    location.href = "/a_protocols.html";
    return;
  }

  const save = confirm("Сохранить изменения?\nOK — сохранить, Отмена — не сохранять");
  if (save) {
    showWait("Сохранение...");
    const ok = await saveProtocol();
    hideWait();
    if (ok) location.href = "/a_protocols.html";
  } else {
    pendingMaterials = [];
    pendingRemovals = [];
    location.href = "/a_protocols.html";
  }
}

function openResults(){
  if (pid) location.href = `/af_res.html?id=${pid}`;
}

async function openQuestions(){
  if (!pid){
    const ok = await saveProtocol();
    if (!ok) return;
  }
  location.href = `/af_questions.html?id=${pid}`;
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") exitCard();
  if (e.key === "Enter") e.preventDefault();
});

async function loadMaterials(){
  materials = [];
  const res = await fetch(`/api/admin/protocols/${pid}/materials`);
  if (!res.ok) { renderMaterials(); return; }

  const data = await res.json();
  let list = null;

  if (Array.isArray(data.items)) list = data.items;
  else if (data.items && data.items._embedded && Array.isArray(data.items._embedded.items)) {
    list = data.items._embedded.items;
  } else if (data._embedded && Array.isArray(data._embedded.items)) {
    list = data._embedded.items;
  }

  if (Array.isArray(list)) {
    materials = list
      .map(x => {
        if (typeof x === "string") return { name:x, persisted:true };
        if (x && x.name) return { name:x.name, persisted:true };
        return null;
      })
      .filter(x => x);
  }

  renderMaterials();
}

async function loadProtocol(){
  if (!pid) {
    qs("p_qcount").value = 1;
    updateQuorumBtn();
    initial = snapshot();
    renderMaterials();
    return;
  }

  const res = await fetch("/api/admin/protocols");
  const data = await res.json();
  const p = data.items.find(x => x.id == pid);
  if (!p) return;

  qs("p_num").value = p.num;
  qs("p_date").value = p.date;
  document.getElementById(p.status === "closed" ? "st_closed" : "st_open").checked = true;
  document.getElementById(p.vote_type === "open" ? "vt_open" : "vt_secret").checked = true;
  qs("p_file_name").value = p.file || "";
  qs("p_qcount").value = p.qcount || 1;

  quorumDefault = p.quorum_default || "1/2";
  updateQuorumBtn();

  await loadMaterials();
  initial = snapshot();
}

loadProtocol();