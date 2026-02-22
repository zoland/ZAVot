// u_apps.js
requireAnyRole(["участник","наблюдатель"]);
const pid = getParam("id");

async function loadApps(){
  const res = await fetch(`/api/protocols/${pid}/files`);
  const data = await res.json();
  const list = qs("appList");
  list.innerHTML = "";
  data.files.forEach(f => {
    const link = document.createElement("a");
    link.href = f.href;
    link.textContent = f.name;
    link.target = "_blank";
    link.className = "file-link";
    list.appendChild(link);
    list.appendChild(document.createElement("br"));
  });
}
loadApps();