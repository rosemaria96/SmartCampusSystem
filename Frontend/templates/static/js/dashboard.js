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
  window.location.href = "/login/";
}

function openVideoModal() {
  const modal = new bootstrap.Modal(document.getElementById('videoModal'));
  modal.show();
}

/* ===== MOBILE SIDEBAR TOGGLE ===== */
document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector(".sidebar");
  const toggleBtn = document.getElementById("mobile-sidebar-toggle");

  // Create or Select Overlay
  let overlay = document.querySelector(".sidebar-overlay");
  if (!overlay) {
    overlay = document.createElement("div");
    overlay.className = "sidebar-overlay";
    document.body.appendChild(overlay);
  }

  // Toggle Function
  const toggleSidebar = (e) => {
    if (e) e.stopPropagation();
    sidebar.classList.toggle("mobile-open");
    overlay.classList.toggle("show");
  };

  // Direct Listener
  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener("click", toggleSidebar);
  }

  // Delegation Fallback (for dynamically added buttons if any)
  document.body.addEventListener('click', (e) => {
    const btn = e.target.closest('#mobile-sidebar-toggle');
    // Only file if we haven't already attached a direct listener to this element
    if (btn && btn !== toggleBtn) {
      toggleSidebar(e);
    }
  });

  // Close on overlay click
  if (overlay && sidebar) {
    overlay.addEventListener("click", () => {
      sidebar.classList.remove("mobile-open");
      overlay.classList.remove("show");
    });
  }
});
