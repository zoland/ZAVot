// js/index.js
const role = sessionStorage.getItem("role");
if (!role) location.href = "/login.html";
else if (role === "admin") location.href = "/a_root.html";
else location.href = "/u_root.html";