// js/a_user.js
requireRole("admin");

let selectedId = null;
let selectedUser = null;
let mode = "create";

let swipeStartX = 0;
let swipeStartY = 0;
let swipeRow = null;
let swipeUser = null;

let lastWheelSwipe = 0;

function showUserModal(){
  mode = "create";
  qs("u_code").value = "";
  qs("u_role").value = "участник";
  qs("u_pass").value = "";
  showModal("modalUser");
}

function openEdit(user){
  if (!user) return;
  mode = "edit";
  selectedId = user.id;
  selectedUser = user;
  qs("u_code").value = user.code;
  qs("u_role").value = user.role;
  qs("u_pass").value = user.password;
  showModal("modalUser");
}

function clearSelection(){
  document.querySelectorAll("#userTable tbody tr.user-row")
    .forEach(r => r.classList.remove("selected"));
  selectedId = null;
  selectedUser = null;
}

async function exitPage(){
  if (document.getElementById("modalUser").classList.contains("active")) {
    modalExit();
    return;
  }
  location.href = "/a_root.html";
}

async function loadUsers(){
  const res = await fetch("/api/admin/users");
  if (!res.ok) { console.error(await res.text()); return; }

  const data = await res.json();
  const tbody = document.querySelector("#userTable tbody");
  tbody.innerHTML = "";

  data.items.forEach(u => {
    const tr = document.createElement("tr");
    tr.classList.add("user-row");
    tr.dataset.id = u.id;
    tr.innerHTML = `<td>${u.code}</td><td>${u.role}</td><td>${u.password}</td><td></td>`;

    tr.addEventListener("click", () => selectRow(tr, u));

    // touch свайпы (телефон)
    tr.addEventListener("pointerdown", e => onPointerDown(e, tr, u));
    tr.addEventListener("pointerup", e => onPointerUp(e, tr, u));

    // trackpad свайпы (двухпальцевые)
    tr.addEventListener("wheel", e => onWheelSwipe(e, tr, u), {passive:false});

    if (selectedId === u.id) {
      tr.classList.add("selected");
      selectedUser = u;
    }

    tbody.appendChild(tr);
  });

  const add = document.createElement("tr");
  add.className = "add-row";
  add.innerHTML = `<td colspan="4">-- добавить --</td>`;
  add.onclick = showUserModal;
  tbody.appendChild(add);
}

function selectRow(tr, user){
  document.querySelectorAll("#userTable tbody tr.user-row")
    .forEach(r => r.classList.remove("selected"));

  tr.classList.add("selected");
  selectedId = user.id;
  selectedUser = user;
}

function onPointerDown(e, tr, user){
  if (e.pointerType !== "touch") return;
  swipeStartX = e.clientX;
  swipeStartY = e.clientY;
  swipeRow = tr;
  swipeUser = user;
  selectRow(tr, user);
}

function onPointerUp(e, tr, user){
  if (e.pointerType !== "touch") return;
  if (!swipeRow || !swipeUser) return;

  const dx = e.clientX - swipeStartX;
  const dy = e.clientY - swipeStartY;

  if (Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy)) {
    if (dx < 0) { // влево — удалить
      if (confirm("Удалить запись?")) {
        delUser(swipeUser.id);
      } else {
        clearSelection();
      }
    } else { // вправо — редактировать
      openEdit(swipeUser);
    }
  }

  swipeRow = null;
  swipeUser = null;
}

function onWheelSwipe(e, tr, user){
  const now = Date.now();
  if (now - lastWheelSwipe < 500) return;

  if (Math.abs(e.deltaX) > Math.abs(e.deltaY) && Math.abs(e.deltaX) > 40) {
    e.preventDefault();
    lastWheelSwipe = now;

    selectRow(tr, user);

    if (e.deltaX > 0) { // влево
      if (confirm("Удалить запись?")) {
        delUser(user.id);
      } else {
        clearSelection();
      }
    } else { // вправо
      openEdit(user);
    }
  }
}

async function createOrUpdateUser(redirectAfter=false){
  const code = qs("u_code").value.trim();
  const pass = qs("u_pass").value.trim();
  if (!code || !pass) { alert("Код и пароль обязательны"); return false; }

  const payload = { code, role: qs("u_role").value, password: pass };

  let res;
  if (mode === "edit" && selectedId){
    res = await fetch(`/api/admin/users/${selectedId}`, {
      method:"PUT",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
  } else {
    res = await fetch("/api/admin/users", {
      method:"POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(payload)
    });
  }

  if (!res.ok) { console.error(await res.text()); return false; }
  closeModal("modalUser");
  clearSelection();

  if (redirectAfter) {
    location.href = "/a_root.html";
    return true;
  }
  loadUsers();
  return true;
}

async function delUser(id){
  const res = await fetch(`/api/admin/users/${id}`, {method:"DELETE"});
  if (!res.ok) { console.error(await res.text()); return; }
  loadUsers();
}

async function modalExit(){
  const code = qs("u_code").value.trim();
  const pass = qs("u_pass").value.trim();

  if (!code || !pass) {
    closeModal("modalUser");
    clearSelection();
    return;
  }

  if (confirm("Сохранить?")) {
    const ok = await createOrUpdateUser();
    if (!ok) return;
  } else {
    closeModal("modalUser");
    clearSelection();
  }
}

document.addEventListener("keydown", (e) => {
  const modalOpen = document.getElementById("modalUser").classList.contains("active");

  if (e.key === "Escape") {
    if (modalOpen) {
      modalExit();
    } else {
      exitPage(); // ESC в табличном режиме
    }
  }

  if (e.key === "Enter" && !modalOpen) {
    e.preventDefault(); // отключить Enter в табличном режиме
  }
});

loadUsers();