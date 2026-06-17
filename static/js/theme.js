document.addEventListener("DOMContentLoaded", function () {
    const themeBtn = document.getElementById("themeToggle");

    // Load saved theme
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "light") {
        document.body.classList.add("light-mode");
        themeBtn.innerHTML = "☀";
    } else {
        themeBtn.innerHTML = "🌙";
    }

    // Toggle theme
    themeBtn.addEventListener("click", function () {
        document.body.classList.toggle("light-mode");

        if (document.body.classList.contains("light-mode")) {
            localStorage.setItem("theme", "light");
            themeBtn.innerHTML = "☀";
        } else {
            localStorage.setItem("theme", "dark");
            themeBtn.innerHTML = "🌙";
        }

        // Reload to refresh charts colors
        location.reload();
    });
});