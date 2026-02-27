function login() {
  let role = document.getElementById("role").value;
  localStorage.setItem("userRole", role);

  if (role === 'student') {
    window.location.href = "student_dashboard.html";
  } else {
    window.location.href = "dashboard.html";
  }
}
