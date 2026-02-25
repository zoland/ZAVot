// a_dir.js
requireRole("admin");

const BASE_PATH = "disk:/04ЧР_ОП";

function goBack() {
  window.location.href = "a_root.html";
}

function formatSize(bytes) {
  if (!bytes) return "";
  const units = ["B","KB","MB","GB","TB"];
  let i = 0;
  let b = bytes;
  while (b >= 1024 && i < units.length - 1) { b /= 1024; i++; }
  return `${b.toFixed(1)} ${units[i]}`;
}

async function loadQuota(){
  const res = await fetch("/api/admin/dir/quota");
  const data = await res.json();
  qs("quotaBox").textContent = 
    `Занято: ${formatSize(data.used)} / Всего: ${formatSize(data.total)}`;
}

async function loadTree(){
  qs("pathBox").textContent = BASE_PATH;