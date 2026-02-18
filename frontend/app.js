let currentProtocolId = null;
let currentRole = null;

function show(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  document.getElementById(id).classList.add("active");
}
function showModal(id){ document.getElementById(id).classList.add("active"); }
function closeModal(id){ document.getElementById(id).classList.remove("active"); }

async function logout() {
  await fetch("/api/logout", {method:"POST"});
  show("login");
}

document.getElementById("loginBtn").onclick = async () => {
  const code = document.getElementById("code").value;
  const password = document.getElementById("pass").value;

  const res = await fetch("/api/login", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({code, password})
  });

  if (!res.ok) { status.textContent = "Ошибка входа"; return; }
  const data = await res.json();
  currentRole = data.role;

  if (data.role === "admin") { show("admin"); loadAdmin(); }
  else { show("list"); setRole(data.role); loadProtocols(); }
};

document.getElementById("p_materials").onchange = (e) => {
  const list = document.getElementById("materialsList");
  list.innerHTML = [...e.target.files].map(f => f.name).join("<br>");
};
    

function setRole(role) {
  const votePanel = document.getElementById("votePanel");
  votePanel.style.display = (role === "наблюдатель") ? "none" : "block";
}


/* ------- ADMIN ------- */
async function loadAdmin() {
  await loadAdminUsers();
  await loadAdminProtocols();
  await loadAdminLogs();
}

async function loadAdminUsers() {
  const res = await fetch("/api/admin/users");
  const data = await res.json();
  const tbody = document.querySelector("#userTable tbody");
  tbody.innerHTML = "";
  data.items.forEach(u => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${u.code}</td><td>${u.role}</td><td>${u.password}</td>
                    <td><button onclick="delUser(${u.id})">Удалить</button></td>`;
    tbody.appendChild(tr);
  });
  tbody.innerHTML += `<tr class="add-row" onclick="showUserModal()"><td colspan="4">-- добавить --</td></tr>`;
}
function showUserModal(){ showModal("modalUser"); }

async function createUser() {
  const code = document.getElementById("u_code").value;
  const role = document.getElementById("u_role").value;
  const password = document.getElementById("u_pass").value;
  await fetch("/api/admin/users", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({code, role, password})
  });
  closeModal("modalUser");
  loadAdminUsers();
}
async function delUser(id) {
  await fetch(`/api/admin/users/${id}`, {method:"DELETE"});
  loadAdminUsers();
}

async function loadAdminProtocols() {
  const res = await fetch("/api/admin/protocols");
  const data = await res.json();
  const tbody = document.querySelector("#protocolTable tbody");
  tbody.innerHTML = "";
  data.items.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${p.num}</td><td>${p.file||""}</td><td>${p.start}</td><td>${p.end}</td>
                    <td>${p.status}</td><td>${p.vote_type}</td>
                    <td>
                      <button onclick="editProtocol(${p.id})">Редактировать</button>
                      <button onclick="delProtocol(${p.id})">Удалить</button>
                    </td>`;
    tbody.appendChild(tr);
  });
  tbody.innerHTML += `<tr class="add-row" onclick="showProtocolModal()"><td colspan="7">-- добавить --</td></tr>`;
}




                                          
async function editProtocol(id){
  const res = await fetch("/api/admin/protocols");
  const data = await res.json();
  const p = data.items.find(x => x.id === id);
  if (!p) return;

  document.getElementById("p_num").value = p.num;
  document.getElementById("p_start").value = p.start;
  document.getElementById("p_end").value = p.end;
  document.getElementById("p_status").value = p.status;
  document.getElementById("p_type").value = p.vote_type;

// показать имя файла протокола в заголовке модалки
  const fileLabel = document.getElementById("p_file_label");
  if (fileLabel) fileLabel.textContent = "Файл: " + (p.file || "");

  // загрузить список материалов
  const filesRes = await fetch(`/api/protocols/${id}/files`);
  const filesData = await filesRes.json();

  const tbody = document.querySelector("#materialsTable tbody");
  tbody.innerHTML = "";

  filesData.files.forEach(f => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${f.name}</td>
    <td><button onclick="deleteMaterial('${f.name}')">Удалить</button></td>`;
    tbody.appendChild(tr);
  });
    
  // добавить строку "-- добавить --"
  const addRow = document.createElement("tr");
  addRow.className = "add-row";
  addRow.innerHTML = `<td>-- добавить --</td>`;
  addRow.onclick = () => selectMaterials();
  tbody.appendChild(addRow);    
    
  currentProtocolId = id;
  showModal("modalProtocol");

  // при сохранении обновляем
  document.getElementById("saveProtocolBtn").onclick = async () => {
    await fetch(`/api/admin/protocols/${id}`, {
      method:"PUT",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({
        num: p_num.value, start: p_start.value, end: p_end.value,
        status: p_status.value, vote_type: p_type.value, file: p.file
      })
    });
    closeModal("modalProtocol");
    loadAdminProtocols();
  };
}


async function deleteMaterial(name){
  await fetch(`/api/admin/protocols/${currentProtocolId}/materials?name=${encodeURIComponent(name)}`, {
    method:"DELETE"
  });
  editProtocol(currentProtocolId);
}

function showProtocolModal(){
  // очистка полей
  document.getElementById("p_num").value = "";
  document.getElementById("p_start").value = "";
  document.getElementById("p_end").value = "";
  document.getElementById("p_status").value = "открыт";
  document.getElementById("p_type").value = "открытое";
  document.getElementById("p_file").value = "";
  document.getElementById("p_materials").value = "";
  document.getElementById("p_qcount").value = "";
  document.getElementById("materialsList").innerHTML = "";
  document.getElementById("p_file_label").textContent = "";

  // сброс материалов таблицы
  const tbody = document.querySelector("#materialsTable tbody");
  if (tbody) {
    tbody.innerHTML = `<tr class="add-row" onclick="selectMaterials()"><td>-- добавить --</td></tr>`;
  }

  showModal("modalProtocol");
}    
    
async function delProtocol(id) {
  await fetch(`/api/admin/protocols/${id}`, {method:"DELETE"});
  loadAdminProtocols();
}

async function loadAdminLogs() {
  const res = await fetch("/api/admin/logs");
  const data = await res.json();
  const tbody = document.querySelector("#logTable tbody");
  tbody.innerHTML = "";
  data.items.forEach(l => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${l.created_at}</td><td>${l.code}</td><td>${l.action}</td>
                    <td>
                      <button onclick="alert('${l.created_at} | ${l.code} | ${l.action}')">Просмотр</button>
                      <button onclick="delLog(${l.id})">Удалить</button>
                    </td>`;
    tbody.appendChild(tr);
  });
}
async function delLog(id){
  await fetch(`/api/admin/logs/${id}`, {method:"DELETE"});
  loadAdminLogs();
}

/* ------- QUESTIONS ------- */
function showQuestionsModal(){
  const n = Number(document.getElementById("p_qcount").value || 0);
  const box = document.getElementById("questionsBox");
  box.innerHTML = "";
  for (let i=1;i<=n;i++){
    box.innerHTML += `
      <div class="card">
        Вопрос ${i}
        <input id="q${i}_1" value="+" />
        <input id="q${i}_2" value="-" />
        <input id="q${i}_3" value="@" />
      </div>`;
  }
  showModal("modalQuestions");
}

async function saveQuestions(){
  const n = Number(document.getElementById("p_qcount").value);
  const items = [];
  for (let i=1;i<=n;i++){
    items.push({
      qnum:i,
      opt1: document.getElementById(`q${i}_1`).value,
      opt2: document.getElementById(`q${i}_2`).value,
      opt3: document.getElementById(`q${i}_3`).value
    });
  }
  await fetch(`/api/admin/protocols/${currentProtocolId}/questions`, {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({items})
  });
  closeModal("modalQuestions");
}

/* ------- PARTICIPANT ------- */
async function loadProtocols() {
  const res = await fetch("/api/protocols");
  const data = await res.json();
  const list = document.getElementById("protocolList");
  list.innerHTML = "";
  data.items.forEach(p => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <strong>Протокол №${p.num}</strong><br>
      Срок: ${p.start} — ${p.end}<br>
      Статус: ${p.status} | Голосов: ${p.voted}/${p.total}
      <br><button onclick="openProtocol(${p.id})">Открыть</button>`;
    list.appendChild(div);
  });
}

async function openProtocol(id) {
  currentProtocolId = id;
  show("protocol");
  await loadFiles(id);
  await loadQuestions(id);
}

async function loadFiles(id) {
  const infoRes = await fetch(`/api/protocols/${id}/info`);
  const info = await infoRes.json();

  const res = await fetch(`/api/protocols/${id}/files`);
  const data = await res.json();

  const fileList = document.getElementById("fileList");
  const pdfViewer = document.getElementById("pdfViewer");
  fileList.innerHTML = "";
  pdfViewer.innerHTML = "";

  data.files.forEach(f => {
    const link = document.createElement("a");
    link.href = f.href;
    link.textContent = f.name;
    link.target = "_blank";
    link.className = "file-link";
    fileList.appendChild(link);
    fileList.appendChild(document.createElement("br"));

    // показываем только файл протокола
    if (f.name === info.file) {
        pdfViewer.innerHTML = `<button class="btn" onclick="window.open('${f.href}','_blank')">Открыть протокол</button>`;
    }
  });
}


function selectMaterials(){
  document.getElementById("p_materials").click();
}

document.getElementById("p_materials").onchange = (e) => {
  const tbody = document.querySelector("#materialsTable tbody");
  const files = [...e.target.files];
  files.forEach(f => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${f.name}</td>`;
    tbody.insertBefore(tr, tbody.querySelector(".add-row"));
  });
};


async function loadQuestions(id){
  const res = await fetch(`/api/protocols/${id}/questions`);
  const data = await res.json();
  const qlist = document.getElementById("questionList");
  qlist.innerHTML = "";

  data.items.forEach(q => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <strong>Вопрос ${q.qnum}</strong>
      <div class="vote-group" data-qid="${q.id}">
        <button class="vote-btn">${q.opt1}</button>
        <button class="vote-btn">${q.opt2}</button>
        <button class="vote-btn default">${q.opt3}</button>
      </div>`;
    qlist.appendChild(div);
  });

  document.querySelectorAll(".vote-group").forEach(g => {
    g.querySelectorAll("button").forEach(b => {
      b.onclick = () => {
        g.querySelectorAll("button").forEach(x => x.classList.remove("default"));
        b.classList.add("default");
      };
    });
  });
}

async function submitVote(){
  const votes = [];
  document.querySelectorAll(".vote-group").forEach(g => {
    const qid = g.dataset.qid;
    const selected = g.querySelector(".default").textContent;
    votes.push({question_id: Number(qid), vote: selected});
  });
  await fetch("/api/vote", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({protocol_id: currentProtocolId, votes})
  });
  alert("Голос сохранён");
}

async function showResults(){
  const res = await fetch(`/api/protocols/${currentProtocolId}/results`);
  const data = await res.json();
  let html = "<h3>Результаты</h3>";
  data.totals.forEach(t => {
    html += `<div>Вопрос ${t.qnum}: ${t.opt1}:${t.c1}, ${t.opt2}:${t.c2}, ${t.opt3}:${t.c3}</div>`;
  });
  if (data.rows) {
    html += "<hr/><h4>Открытое голосование</h4>";
    data.rows.forEach(r => { html += `<div>${r.user_code} — Q${r.question_id}: ${r.vote}</div>`; });
  }
  document.getElementById("resultsBox").innerHTML = html;
  showModal("modalResults");
}

function downloadCSV(){
  window.open(`/api/protocols/${currentProtocolId}/results.csv`, "_blank");
}