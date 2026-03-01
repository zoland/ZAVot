// common.js

function qs(id){ return document.getElementById(id); }
function getParam(name){ return new URLSearchParams(location.search).get(name); }

function logout(){
  localStorage.clear();
  sessionStorage.clear();
  location.href = "/login.html";
}

function requireRole(role){
  const r = localStorage.getItem("role");
  if (r !== role) location.href = "/login.html";
}

function requireAnyRole(roles){
  const r = localStorage.getItem("role");
  if (!roles.includes(r)) location.href = "/login.html";
}

function showModal(id){ qs(id).classList.add("active"); }
function closeModal(id){ qs(id).classList.remove("active"); }

function logout(){
  fetch("/logout").finally(() => {
    location.href = "/login.html";
  });
}