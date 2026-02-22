// js/a_protocol.js
requireRole("admin");

async function loadProtocols() {
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
  tbody.innerHTML += `<tr class="add-row" onclick="createProtocol()"><td colspan="7">-- добавить --</td></tr>`;
}

function createProtocol(){
  location.href = "/af_protocol.html";
}
function editProtocol(id){
  location.href = `/af_protocol.html?id=${id}`;
}
async function delProtocol(id){
  await fetch(`/api/admin/protocols/${id}`, {method:"DELETE"});
  loadProtocols();
}

loadProtocols();