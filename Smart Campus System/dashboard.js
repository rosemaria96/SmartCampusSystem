let role = localStorage.getItem("userRole");

if (role === "student") {
  // show attendance view
}

if (role === "faculty") {
  // show attendance marking option
}

if (role === "admin") {
  // show admin controls
}

const toggleBtn = document.getElementById("toggleBtn");

// Check Local Storage on Load
if (localStorage.getItem("theme") === "light") {
  document.body.classList.add("light-mode");
  if (toggleBtn) toggleBtn.classList.add("active");
}

if (toggleBtn) {
  toggleBtn.addEventListener("click", () => {
    toggleBtn.classList.toggle("active");
    document.body.classList.toggle("light-mode");

    // Save Preference
    if (document.body.classList.contains("light-mode")) {
      localStorage.setItem("theme", "light");
    } else {
      localStorage.setItem("theme", "dark");
    }
  });
}

/* ===== ACTIVE SIDEBAR MENU ===== */
const menuItems = document.querySelectorAll(".menu-item");

menuItems.forEach(item => {
  item.addEventListener("click", () => {
    menuItems.forEach(i => i.classList.remove("active"));
    item.classList.add("active");
  });
});

function goToLogin() {
  window.location.href = "index.html";
}

function openVideoModal() {
  const modal = new bootstrap.Modal(document.getElementById('videoModal'));
  modal.show();
}
