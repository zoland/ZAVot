// a_log.js
requireRole("admin");

async function loadLogs(){
  const res = await fetch("/api/admin/logs");
  const data = await res.json();
  const tbody = document.querySelector("#logTable tbody");
  tbody.innerHTML = "";
  data.items.forEach(l => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${l.created_at}</td><td>${l.code}</td><td>${l.action}</td>
                    <td>
                      <button onclick="openLog(${l.id})">Просмотр</button>
                      <button onclick="delLog(${l.id})">Удалить</button>
                    </td>`;
    tbody.appendChild(tr);
  });
}
function openLog(id){ location.href = `/af_log.html?id=${id}`; }
async function delLog(id){
  await fetch(`/api/admin/logs/${id}`, {method:"DELETE"});
  loadLogs();
}
loadLogs();