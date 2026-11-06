
/* CivicConnect Login */

(() => {
    const form = qs("#loginForm");
    const button = qs("#btn");
    const title = qs("#title");
    const citizenTab = qs("#tabCit");
    const adminTab = qs("#tabAdm");
    const registerLink = qs("#reg");

    if (!form || !button) {
        console.error("Login form elements are missing.");
        return;
    }

    let admin = new URLSearchParams(location.search).has("admin");

    function setMode(isAdmin) {
        admin = isAdmin;

        citizenTab.className =
            "btn " + (admin ? "btn-outline-navy" : "btn-navy");

        adminTab.className =
            "btn " + (admin ? "btn-navy" : "btn-outline-navy");

        title.textContent = admin
            ? "Administrator login"
            : "Welcome back";

        registerLink.classList.toggle("d-none", admin);
    }

    citizenTab.onclick = () => setMode(false);
    adminTab.onclick = () => setMode(true);

    setMode(admin);

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const email = form.elements.email.value.trim().toLowerCase();
        const password = form.elements.password.value;

        if (!email || !password) {
            fail(new Error("Please enter your email and password."));
            return;
        }

        button.disabled = true;
        button.textContent = "Logging in...";

        try {
            const result = await api(
                admin ? "/auth/admin-login" : "/auth/login",
                {
                    method: "POST",
                    body: { email, password }
                }
            );

            if (!result.user) {
                throw new Error("Login response did not contain a user.");
            }

            location.replace(
                result.user.role === "admin"
                    ? "admin.html"
                    : "dashboard.html"
            );

        } catch (error) {
            console.error("Login failed:", error);
            fail(error);

            button.disabled = false;
            button.textContent = "Login";
        }
    });
})();
