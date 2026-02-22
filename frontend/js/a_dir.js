// a_dir.js
requireRole("admin");
let path = "/";

async function loadQuota(){
  const res = await fetch("/api/admin/dir/quota");
  const data = await res.json();
  qs("quotaBox").textContent = `Занято: ${data.used} / Всего: ${data.total}`;
}

async function loadDir(){
  qs("pathBox").textContent = path;

  const res = await fetch(`/api/admin/dir?path=${encodeURIComponent(path)}`);
  const data = await res.json();

  const tbody = document.querySelector("#dirTable tbody");
  tbody.innerHTML = "";

  if (path !== "/"){
    const up = document.createElement("tr");
    up.innerHTML = `<td class="dir-folder">..</td><td>dir</td><td></td>`;
    up.onclick = () => {
      path = path.split("/").slice(0,-2).join("/") + "/";
      loadDir();
    };
    tbody.appendChild(up);
  }

  data.items.forEach(f => {
    const tr = document.createElement("tr");
    const cls = (f.type === "dir") ? "dir-folder" : "dir-file";
    tr.innerHTML = `<td class="${cls}">${f.name}</td><td>${f.type}</td><td>${f.size||""}</td>`;
    if (f.type === "dir") {
      tr.onclick = () => { path = path + f.name + "/"; loadDir(); };
    }
    tbody.appendChild(tr);
  });
}

loadQuota();
loadDir();