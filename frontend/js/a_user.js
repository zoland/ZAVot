// js/a_user.js
requireRole("admin");

function showUserModal(){ showModal("modalUser"); }

async function loadUsers(){
  const res = await fetch("/api/admin/users");
  const data = await res.json();
  const tbody = document.querySelector("#userTable tbody");
  tbody.innerHTML = "";
  data.items.forEach(u => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${u.code}</td><td>${u.role}</td><td>${u.password}</td>
                    <td><button onclick="delUser(${u.id})">Удалить</button></td>`;
    tbody.appendChild(tr);
  });
  tbody.innerHTML += `<tr class="add-row" onclick="showUserModal()"><td colspan="4">-- добавить --</td></tr>`;
}

async function createUser(){
  await fetch("/api/admin/users", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      code: qs("u_code").value,
      role: qs("u_role").value,
      password: qs("u_pass").value
    })
  });
  closeModal("modalUser");
  loadUsers();
}

async function delUser(id){
  await fetch(`/api/admin/users/${id}`, {method:"DELETE"});
  loadUsers();
}

loadUsers();