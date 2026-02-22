// u_protocol.js
requireAnyRole(["участник", "наблюдатель"]);
const pid = getParam("id");

async function loadFiles(){
  const infoRes = await fetch(`/api/protocols/${pid}/info`);
  const info = await infoRes.json();

  const res = await fetch(`/api/protocols/${pid}/files`);
  const data = await res.json();

  const fileList = qs("fileList");
  const pdfViewer = qs("pdfViewer");
  fileList.innerHTML = "";
  pdfViewer.innerHTML = "";

  data.files.forEach(f => {
    const link = document.createElement("a");
    link.href = f.href;
    link.textContent = f.name;
    link.target = "_blank";
    link.className = "file-link";
    fileList.appendChild(link);
    fileList.appendChild(document.createElement("br"));

    if (f.name === info.file) {
      pdfViewer.innerHTML = `<button class="btn" onclick="window.open('${f.href}','_blank')">Открыть протокол</button>`;
    }
  });
}

function openVote(){
  location.href = `/u_vote.html?id=${pid}`;
}
function openResults(){
  location.href = `/u_res.html?id=${pid}`;
}
function openApps(){
  location.href = `/u_apps.html?id=${pid}`;
}

async function uploadOpinion(){
  const file = qs("opinionFile").files[0];
  if (!file) return alert("Выберите файл");
  const fd = new FormData();
  fd.append("file", file);

  await fetch(`/api/protocols/${pid}/opinion`, {
    method:"POST",
    body: fd
  });
  alert("Файл отправлен");
}

loadFiles();