// js/af_protocol.js
requireRole("admin");
let pid = getParam("id");

async function loadProtocol(){
  if (!pid) return;
  const res = await fetch("/api/admin/protocols");
  const data = await res.json();
  const p = data.items.find(x => x.id == pid);
  if (!p) return;
  qs("p_num").value = p.num;
  qs("p_start").value = p.start;
  qs("p_end").value = p.end;
  qs("p_status").value = p.status;
  qs("p_type").value = p.vote_type;
}

async function saveProtocol(){
  const body = {
    num: qs("p_num").value,
    start: qs("p_start").value,
    end: qs("p_end").value,
    status: qs("p_status").value,
    vote_type: qs("p_type").value
  };
  if (pid){
    await fetch(`/api/admin/protocols/${pid}`, {
      method:"PUT", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body)
    });
  } else {
    const res = await fetch("/api/admin/protocols", {
      method:"POST", headers: {"Content-Type":"application/json"}, body: JSON.stringify(body)
    });
    const data = await res.json();
    pid = data.id;
  }
  alert("Сохранено");
}

function openResults(){
  if (pid) location.href = `/af_res.html?id=${pid}`;
}

function showQuestions(){
  const n = Number(qs("p_qcount").value || 0);
  const box = qs("questionsBox");
  box.innerHTML = "";
  for (let i=1;i<=n;i++){
    box.innerHTML += `
      <div class="card">
        Вопрос ${i}
        <input id="q${i}_1" value="+" />
        <input id="q${i}_2" value="-" />
        <input id="q${i}_3" value="@" />
        <input id="q${i}_d" placeholder="default (+/-/@)" value="@" />
      </div>`;
  }
  showModal("modalQuestions");
}

async function saveQuestions(){
  const n = Number(qs("p_qcount").value);
  const items = [];
  for (let i=1;i<=n;i++){
    items.push({
      qnum:i,
      opt1: qs(`q${i}_1`).value,
      opt2: qs(`q${i}_2`).value,
      opt3: qs(`q${i}_3`).value,
      default_vote: qs(`q${i}_d`).value
    });
  }
  await fetch(`/api/admin/protocols/${pid}/questions`, {
    method:"POST", headers: {"Content-Type":"application/json"},
    body: JSON.stringify({items})
  });
  closeModal("modalQuestions");
}

loadProtocol();