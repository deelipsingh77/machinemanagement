const menuButton = document.getElementById("menu-button");
const mobileMenu = document.getElementById("mobile-menu");

menuButton.addEventListener("click", () => {
  mobileMenu.classList.toggle("-translate-y-full");
});

const darkModeToggle = document.getElementById("dark-mode-toggle");
const dot = document.querySelector(".dot");

// Initialize dark mode based on localStorage
if (localStorage.getItem("theme") === "dark") {
  document.documentElement.classList.add("dark");
  darkModeToggle.checked = true;
  dot.classList.add("translate-x-full");
} else {
  document.documentElement.classList.remove("dark");
  darkModeToggle.checked = false;
}

darkModeToggle.addEventListener("change", () => {
  if (darkModeToggle.checked) {
    document.documentElement.classList.add("dark");
    localStorage.setItem("theme", "dark");
    dot.classList.add("translate-x-full");
  } else {
    document.documentElement.classList.remove("dark");
    localStorage.setItem("theme", "light");
    dot.classList.remove("translate-x-full");
  }
});
