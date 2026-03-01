// js/af_questions.js
requireRole("admin");
const pid = getParam("id");
const QUORUMS = ["1/2","3/4","1"];

let items = [];

function qs(id){ return document.getElementById(id); }

function quorumClass(q){
  return q === "1/2" ? "q-half" : q === "3/4" ? "q-34" : "q-1";
}

function render(){
  const grid = qs("qgrid");
  grid.innerHTML = "";
  items.forEach((it, i) => {
    const div = document.createElement("div");
    div.className = `q-box ${quorumClass(it.quorum)}`;
    div.textContent = it.qnum;
    div.onclick = () => toggle(i);
    grid.appendChild(div);
  });
}

function toggle(i){
  const idx = QUORUMS.indexOf(items[i].quorum);
  items[i].quorum = QUORUMS[(idx+1) % QUORUMS.length];
  render();
  save();
}

let saveTimer = null;
function save(){
  clearTimeout(saveTimer);
  saveTimer = setTimeout(async () => {
    await fetch(`/api/admin/protocols/${pid}/questions`, {
      method: "PUT",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({items})
    });
  }, 300);
}

function goBack(){
  location.href = `/af_protocol.html?id=${pid}`;
}

async function load(){
  const res = await fetch(`/api/admin/protocols/${pid}/questions`);
  const data = await res.json();
  items = data.items || [];
  render();
}

load();