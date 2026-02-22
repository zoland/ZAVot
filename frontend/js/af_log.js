// af_log.js
requireRole("admin");
const id = getParam("id");

async function loadLog(){
  const res = await fetch("/api/admin/logs");
  const data = await res.json();
  const l = data.items.find(x => x.id == id);
  if (!l) return;
  qs("logBox").innerHTML = `
    <div><b>Дата:</b> ${l.created_at}</div>
    <div><b>Код:</b> ${l.code}</div>
    <div><b>Действие:</b> ${l.action}</div>`;
}
loadLog();