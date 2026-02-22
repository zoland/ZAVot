// af_user.js
requireRole("admin");
const id = getParam("id");

async function loadUser(){
  const res = await fetch("/api/admin/users");
  const data = await res.json();
  const u = data.items.find(x => x.id == id);
  if (!u) return;
  qs("u_code").value = u.code;
  qs("u_pass").value = u.password;
  qs("u_role").value = u.role;
}

async function saveUser(){
  await fetch(`/api/admin/users/${id}`, {
    method:"PUT",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      code: qs("u_code").value,
      password: qs("u_pass").value,
      role: qs("u_role").value
    })
  });
  alert("Сохранено");
}

loadUser();