document.addEventListener("DOMContentLoaded", () => {
    window.setTimeout(() => {
        document.querySelectorAll(".alert").forEach((alertElement) => {
            try {
                const alert = bootstrap.Alert.getOrCreateInstance(alertElement);
                alert.close();
            } catch (e) {
                console.warn("Failed to close alert:", e);
            }
        });
    }, 5000);

    document.querySelectorAll("a[href]").forEach((link) => {
        link.addEventListener("click", (e) => {
            if (e.defaultPrevented || e.button !== 0) return;
            if (link.target === "_blank" || link.hasAttribute("download")) return;
            if (link.href.startsWith("javascript:")) return;
            console.log("Navigating to:", link.href);
        });
    });
});
