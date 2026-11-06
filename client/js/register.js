
/* CivicConnect Citizen Registration */

(() => {
    const form = qs("#regForm");
    const button = qs("#btn");

    if (!form || !button) {
        console.error("Registration form elements are missing.");
        return;
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();

        showFieldErrors(form, {});

        const fullName = form.elements.full_name.value.trim();
        const email = form.elements.email.value.trim().toLowerCase();
        const phone = form.elements.phone.value.trim();
        const password = form.elements.password.value;
        const confirmPassword = form.elements.confirm_password.value;
        const locationValue = form.elements.location.value.trim();

        if (fullName.length < 2) {
            fail(new Error("Please enter your full name."));
            return;
        }

        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            fail(new Error("Please enter a valid email address."));
            return;
        }

        if (phone.length < 7 || phone.length > 15) {
            fail(new Error("Enter a valid phone number."));
            return;
        }

        if (password.length < 8) {
            fail(new Error("Password must contain at least 8 characters."));
            return;
        }

        if (password !== confirmPassword) {
            fail(new Error("Passwords do not match."));
            return;
        }

        const userData = {
            full_name: fullName,
            email,
            phone,
            password,
            confirm_password: confirmPassword,
            location: locationValue
        };

        button.disabled = true;
        button.textContent = "Creating Account...";

        try {
            const result = await api("/auth/register", {
                method: "POST",
                body: userData
            });

            ok(result.message || "Account created successfully!");

            form.reset();

            setTimeout(() => {
                location.replace("login.html");
            }, 1000);

        } catch (error) {
            console.error("Registration failed:", error);

            showFieldErrors(form, error.fields);
            fail(error);

        } finally {
            button.disabled = false;
            button.textContent = "Create Account";
        }
    });
})();
