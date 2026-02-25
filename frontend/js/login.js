// login.js
const btn = document.getElementById("loginBtn");
btn.onclick = async () => {
  const code = document.getElementById("code").value.trim();
  const password = document.getElementById("pass").value.trim();

  const res = await fetch("/api/login", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({code, password})
  });

  const data = await res.json();
  if (!data.ok) {
    qs("status").textContent = data.error || "Ошибка входа";
    return;
  }

  localStorage.setItem("authToken", data.token);
  localStorage.setItem("role", data.role);

  if (data.role === "admin") location.href = "/a_root.html";
  else location.href = "/u_root.html";
};