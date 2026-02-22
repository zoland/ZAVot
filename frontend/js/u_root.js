// js/u_root.js
requireRole("участник");

async function loadProtocols(){
  const res = await fetch("/api/protocols");
  const data = await res.json();
  const list = qs("protocolList");
  list.innerHTML = "";
  data.items.forEach(p => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <strong>Протокол №${p.num}</strong><br>
      Срок: ${p.start} — ${p.end}<br>
      Статус: ${p.status}<br>
      Голосов: ${p.voted}/${p.total}<br>
      <button onclick="openProtocol(${p.id})">Открыть</button>`;
    list.appendChild(div);
  });
}

function openProtocol(id){
  location.href = `/u_protocol.html?id=${id}`;
}

loadProtocols();