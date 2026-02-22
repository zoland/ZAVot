// u_res.js
requireRole("участник");
const pid = getParam("id");

function voteClass(v){
  if (v === "+") return "vote-plus";
  if (v === "-") return "vote-minus";
  if (v === "@") return "vote-abstain";
  return "vote-empty";
}

async function loadResults(){
  const res = await fetch(`/api/protocols/${pid}/results`);
  const data = await res.json();

  let html = `<h3>Итоги</h3>`;
  data.totals.forEach(t => {
    html += `<div>Q${t.qnum}: ${t.opt1}:${t.c1}, ${t.opt2}:${t.c2}, ${t.opt3}:${t.c3}</div>`;
  });

  html += `<hr/><h4>Голоса</h4>`;
  html += `<table class="res-table">
            <thead>
              <tr><th>Код</th><th>Вопрос</th><th>Голос</th></tr>
            </thead><tbody>`;

  data.rows.forEach(r => {
    html += `<tr>
      <td>${r.user_code || ""}</td>
      <td>${r.question_id}</td>
      <td class="${voteClass(r.vote)}">${r.vote || ""}</td>
    </tr>`;
  });

  html += `</tbody></table>`;
  qs("resultsBox").innerHTML = html;
}

loadResults();