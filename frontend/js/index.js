// index.js
const token = localStorage.getItem("authToken");
const role = localStorage.getItem("role");

if (!token) {
  location.href = "/login.html";
} else {
  if (role === "admin") location.href = "/a_root.html";
  else location.href = "/u_root.html";
}