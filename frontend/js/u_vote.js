// u_vote.js
requireRole("участник");
const pid = getParam("id");

function voteClass(v){
  if (v === "+") return "vote-plus";
  if (v === "-") return "vote-minus";
  if (v === "@") return "vote-abstain";
  return "vote-empty";
}

async function loadQuestions(){
  const res = await fetch(`/api/protocols/${pid}/questions`);
  const data = await res.json();
  const qlist = qs("questionList");
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
        g.querySelectorAll("button").forEach(x => {
          x.classList.remove("default","vote-plus","vote-minus","vote-abstain");
        });
        b.classList.add("default", voteClass(b.textContent));
      };
    });
  });

  // начальная подсветка
  document.querySelectorAll(".vote-group .default").forEach(b => {
    b.classList.add(voteClass(b.textContent));
  });
}

function fillAll(){
  const v = qs("fillValue").value;
  document.querySelectorAll(".vote-group").forEach(g => {
    g.querySelectorAll("button").forEach(b => {
      b.classList.toggle("default", b.textContent === v);
      b.classList.remove("vote-plus","vote-minus","vote-abstain");
      if (b.classList.contains("default")) b.classList.add(voteClass(b.textContent));
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
    body: JSON.stringify({protocol_id: Number(pid), votes})
  });
  alert("Голос сохранён");
}

loadQuestions();