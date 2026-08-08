(() => {
    "use strict";

    let savedTheme = null;

    try {
        savedTheme = window.localStorage.getItem("weekendia-theme");
    } catch (_error) {
        savedTheme = null;
    }

    const theme = savedTheme === "light" || savedTheme === "dark"
        ? savedTheme
        : "dark";

    document.body.dataset.theme = theme;
    document.querySelector('meta[name="theme-color"]')?.setAttribute(
        "content",
        theme === "dark" ? "#07101d" : "#edf6fb",
    );
})();
