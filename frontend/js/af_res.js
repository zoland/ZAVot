// js/af_res.js
requireRole("admin");
const pid = getParam("id");

let resSelected = null;
let resStartX = 0;
let resStartY = 0;
let resLastWheel = 0;

function voteClass(v){
  if (v === "+") return "vote-plus";
  if (v === "-") return "vote-minus";
  if (v === "@") return "vote-abstain";
  return "vote-empty";
}

async function loadResults(){
  const res = await fetch(`/api/admin/protocols/${pid}/results`);
  const data = await res.json();

  let html = `<h3>Итоги</h3>`;
  data.totals.forEach(t => {
    html += `<div>Q${t.qnum}: ${t.opt1}:${t.c1}, ${t.opt2}:${t.c2}, ${t.opt3}:${t.c3}</div>`;
  });

  html += `<hr/><h4>Голоса</h4>`;
  html += `<table class="res-table" id="resTable">
            <thead>
              <tr><th>Код</th><th>Вопрос</th><th>Голос</th><th></th></tr>
            </thead><tbody>`;

  data.rows.forEach(r => {
    html += `<tr class="res-row" data-code="${r.user_code}" data-qid="${r.question_id}">
      <td>${r.user_code}</td>
      <td>${r.question_id}</td>
      <td class="${voteClass(r.vote)}">${r.vote || ""}</td>
      <td><button class="btn" onclick="editVote('${r.user_code}',${r.question_id})">Правка</button></td>
    </tr>`;
  });

  html += `</tbody></table>`;
  qs("resultsBox").innerHTML = html;

  initResTable();
}

function initResTable(){
  document.querySelectorAll("#resTable tbody tr.res-row").forEach(tr => {
    tr.addEventListener("click", () => selectResRow(tr));
    tr.addEventListener("pointerdown", e => resPointerDown(e, tr));
    tr.addEventListener("pointerup", e => resPointerUp(e, tr));
    tr.addEventListener("wheel", e => resWheelSwipe(e, tr), {passive:false});
  });
}

function selectResRow(tr){
  document.querySelectorAll("#resTable tbody tr.res-row").forEach(r => r.classList.remove("selected"));
  tr.classList.add("selected");
  resSelected = tr;
}

function clearResSelection(){
  document.querySelectorAll("#resTable tbody tr.res-row").forEach(r => r.classList.remove("selected"));
  resSelected = null;
}

function resPointerDown(e, tr){
  if (e.pointerType !== "touch") return;
  resStartX = e.clientX;
  resStartY = e.clientY;
  selectResRow(tr);
}

function resPointerUp(e, tr){
  if (e.pointerType !== "touch") return;

  const dx = e.clientX - resStartX;
  const dy = e.clientY - resStartY;

  if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
    const code = tr.dataset.code;
    const qid = Number(tr.dataset.qid);

    if (dx < 0) { // влево — удалить (очистить голос)
      if (confirm("Удалить голос?")) {
        updateVote(code, qid, "");
      } else {
        clearResSelection();
      }
    } else { // вправо — правка
      editVote(code, qid);
    }
  }
}

function resWheelSwipe(e, tr){
  const now = Date.now();
  if (now - resLastWheel < 500) return;

  if (Math.abs(e.deltaX) > Math.abs(e.deltaY) && Math.abs(e.deltaX) > 40) {
    e.preventDefault();
    resLastWheel = now;

    selectResRow(tr);

    const code = tr.dataset.code;
    const qid = Number(tr.dataset.qid);

    if (e.deltaX > 0) { // влево
      if (confirm("Удалить голос?")) {
        updateVote(code, qid, "");
      } else {
        clearResSelection();
      }
    } else { // вправо
      editVote(code, qid);
    }
  }
}

async function updateVote(code, qid, vote){
  await fetch(`/api/admin/protocols/${pid}/results/vote`, {
    method:"PUT",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({user_code: code, question_id: qid, vote})
  });
  loadResults();
}

async function editVote(code, qid){
  const vote = prompt("Новый голос (+/-/@):");
  if (vote === null) { clearResSelection(); return; }
  await updateVote(code, qid, vote);
}

function downloadCSV(){
  window.open(`/api/admin/protocols/${pid}/results.csv`, "_blank");
}

loadResults();