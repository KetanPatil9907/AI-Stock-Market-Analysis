document.addEventListener("DOMContentLoaded", () => {
    window.setTimeout(() => {
        document.querySelectorAll(".alert").forEach((alertElement) => {
            const alert = bootstrap.Alert.getOrCreateInstance(alertElement);
            alert.close();
        });
    }, 5000);
});