// js/a_protocols.js
requireRole("admin");

let selectedId = null;
let selectedProtocol = null;

let swipeStartX = 0;
let swipeStartY = 0;
let swipeRow = null;
let swipeProtocol = null;

let lastWheelSwipe = 0;

async function loadProtocols() {
  const res = await fetch("/api/admin/protocols");
  const data = await res.json();

  const tbody = document.querySelector("#protocolTable tbody");
  tbody.innerHTML = "";

  data.items.forEach(p => {
    const tr = document.createElement("tr");
    tr.classList.add("protocol-row");
    tr.dataset.id = p.id;
    tr.innerHTML = `<td>${p.num}</td><td>${p.file||""}</td><td>${p.date||""}</td>
                    <td>${p.status}</td><td>${p.vote_type}</td>`;

    tr.addEventListener("click", () => selectRow(tr, p));
    tr.addEventListener("pointerdown", e => onPointerDown(e, tr, p));
    tr.addEventListener("pointerup", e => onPointerUp(e, tr, p));
    tr.addEventListener("wheel", e => onWheelSwipe(e, tr, p), {passive:false});

    if (selectedId === p.id) {
      tr.classList.add("selected");
      selectedProtocol = p;
    }

    tbody.appendChild(tr);
  });

  const add = document.createElement("tr");
  add.className = "add-row";
  add.innerHTML = `<td colspan="5">-- добавить --</td>`;
  add.onclick = createProtocol;
  tbody.appendChild(add);
}

function createProtocol(){
  location.href = "/af_protocol.html";
}

function openEdit(p){
  if (!p) return;
  location.href = `/af_protocol.html?id=${p.id}`;
}

async function delProtocol(id){
  await fetch(`/api/admin/protocols/${id}`, {method:"DELETE"});
  loadProtocols();
}

function selectRow(tr, p){
  document.querySelectorAll("#protocolTable tbody tr.protocol-row")
    .forEach(r => r.classList.remove("selected"));

  tr.classList.add("selected");
  selectedId = p.id;
  selectedProtocol = p;
}

function clearSelection(){
  document.querySelectorAll("#protocolTable tbody tr.protocol-row")
    .forEach(r => r.classList.remove("selected"));
  selectedId = null;
  selectedProtocol = null;
}

function onPointerDown(e, tr, p){
  if (e.pointerType !== "touch") return;
  swipeStartX = e.clientX;
  swipeStartY = e.clientY;
  swipeRow = tr;
  swipeProtocol = p;
  selectRow(tr, p);
}

function onPointerUp(e, tr, p){
  if (e.pointerType !== "touch") return;
  if (!swipeRow || !swipeProtocol) return;

  const dx = e.clientX - swipeStartX;
  const dy = e.clientY - swipeStartY;

  if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
    if (dx < 0) {
      if (confirm("Удалить протокол?")) {
        delProtocol(swipeProtocol.id);
      } else {
        clearSelection();
      }
    } else {
      openEdit(swipeProtocol);
    }
  }

  swipeRow = null;
  swipeProtocol = null;
}

function onWheelSwipe(e, tr, p){
  const now = Date.now();
  if (now - lastWheelSwipe < 500) return;

  if (Math.abs(e.deltaX) > Math.abs(e.deltaY) && Math.abs(e.deltaX) > 40) {
    e.preventDefault();
    lastWheelSwipe = now;

    selectRow(tr, p);

    if (e.deltaX > 0) {
      if (confirm("Удалить протокол?")) {
        delProtocol(p.id);
      } else {
        clearSelection();
      }
    } else {
      openEdit(p);
    }
  }
}

function exitPage(){
  location.href = "/a_root.html";
}

document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    exitPage();
  }
  if (e.key === "Enter") {
    e.preventDefault();
  }
});

loadProtocols();