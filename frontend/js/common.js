function qs(id){ return document.getElementById(id); }
function getParam(name){ return new URLSearchParams(location.search).get(name); }

async function logout(){
  await fetch("/api/logout", {method:"POST"});
  sessionStorage.clear();
  location.href = "/login.html";
}

function requireRole(role){
  const r = sessionStorage.getItem("role");
  if (r !== role) location.href = "/login.html";
}
function requireAnyRole(roles){
  const r = sessionStorage.getItem("role");
  if (!roles.includes(r)) location.href = "/login.html";
}

function showModal(id){ qs(id).classList.add("active"); }
function closeModal(id){ qs(id).classList.remove("active"); }