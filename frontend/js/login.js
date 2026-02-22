// js/login.js
qs("loginBtn").onclick = async () => {
  const code = qs("code").value;
  const password = qs("pass").value;

  const res = await fetch("/api/login", {
    method:"POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({code, password})
  });

  if (!res.ok) { qs("status").textContent = "Ошибка входа"; return; }

  const data = await res.json();
  sessionStorage.setItem("role", data.role);
  sessionStorage.setItem("code", code);
  location.href = "/index.html";
};