
/* CivicConnect Shared Helpers */

const STATUSES = [
    "Submitted",
    "Under Review",
    "Assigned",
    "In Progress",
    "Resolved",
    "Rejected"
];

const FLOW = [
    "Submitted",
    "Under Review",
    "Assigned",
    "In Progress",
    "Resolved"
];

const CATEGORIES = [
    "Road Damage",
    "Garbage",
    "Streetlight",
    "Water Leakage",
    "Drainage",
    "Public Infrastructure",
    "Other"
];

const qs = (s, r = document) => r.querySelector(s);
const qsa = (s, r = document) => [...r.querySelectorAll(s)];

class ApiError extends Error {
    constructor(message, status = 0, fields = {}) {
        super(message);
        this.name = "ApiError";
        this.status = status;
        this.fields = fields;
    }
}

/* API helper */
async function api(path, { method = "GET", body, form } = {}) {
    const options = {
        method,
        credentials: "include",
        headers: {}
    };

    if (form) {
        options.body = form;
    } else if (body !== undefined) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    let response;

    try {
        response = await fetch(
            "http://127.0.0.1:8000/api" + path,
            options
        );
    } catch (error) {
        throw new ApiError(
            "Cannot connect to backend. Make sure the server is running.",
            0
        );
    }

    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        if (
            response.status === 401 &&
            !path.startsWith("/auth/")
        ) {
            location.replace("login.html");
        }

        let message =
            data.error ||
            data.message ||
            data.detail;

        if (Array.isArray(message)) {
            message = message
                .map(item => item.msg || JSON.stringify(item))
                .join(", ");
        }

        if (typeof message !== "string") {
            message = "Request failed. HTTP " + response.status;
        }

        throw new ApiError(
            message,
            response.status,
            data.fields || {}
        );
    }

    return data;
}

/* HTML escaping */
function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    }[char]));
}

/* Date formatting */
const utc = iso =>
    new Date(/Z|[+-]\d\d:\d\d$/.test(iso) ? iso : iso + "Z");

const fmtDate = iso =>
    iso ? utc(iso).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    }) : "-";

const fmtDateTime = iso =>
    iso ? utc(iso).toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    }) : "-";

const fmtLocal = iso =>
    iso ? new Date(iso).toLocaleString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    }) : "-";

/* Other helpers */
const slug = s =>
    String(s).toLowerCase().replace(/\s+/g, "-");

const statusBadge = s =>
    `<span class="badge-status s-${slug(s)}">${esc(s)}</span>`;

const prioBadge = p =>
    p ? `<span class="badge-status p-${slug(p)}">${esc(p)}</span>` : "-";

const imgUrl = f =>
    "/api/uploads/" + encodeURIComponent(f);

const progressPct = s =>
    s === "Rejected"
        ? 100
        : Math.round(((FLOW.indexOf(s) + 1) / FLOW.length) * 100);

const debounce = (fn, ms = 400) => {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
    };
};

/* Toast messages */
function toast(message, type = "") {
    let wrapper = qs(".toast-wrap");

    if (!wrapper) {
        wrapper = document.createElement("div");
        wrapper.className = "toast-wrap";
        document.body.appendChild(wrapper);
    }

    const item = document.createElement("div");
    item.className = "toast-msg " + type;
    item.textContent = message;

    wrapper.appendChild(item);
    setTimeout(() => item.remove(), 4200);
}

const ok = message => toast(message, "ok");
const fail = error => toast(error.message || String(error), "err");

/* Form errors */
function showFieldErrors(form, fields) {
    qsa(".invalid-msg", form).forEach(item => item.remove());

    Object.entries(fields || {}).forEach(([name, message]) => {
        const element = form.elements[name];

        if (element) {
            const error = document.createElement("div");
            error.className = "invalid-msg";
            error.textContent = message;
            element.insertAdjacentElement("afterend", error);
        }
    });
}

/* Logout */
let logoutInProgress = false;

async function logout() {
    if (logoutInProgress) return;

    logoutInProgress = true;

    try {
        await api("/auth/logout", { method: "POST" });
    } catch (error) {
        console.error("Logout error:", error);
    }

    location.replace("login.html");
}

/* Citizen navigation */
const CITIZEN_NAV = [
    ["dashboard.html", "bi-speedometer2", "Dashboard", "dashboard"],
    ["report.html", "bi-megaphone", "Report a Problem", "report"],
    ["complaints.html", "bi-card-checklist", "My Complaints", "complaints"],
    ["tracking.html", "bi-geo-alt", "Track Complaints", "tracking"],
    ["notification.html", "bi-bell", "Notifications", "notifications"],
    ["profile.html", "bi-person-circle", "Profile", "profile"]
];

/* Admin navigation */
const ADMIN_NAV = [
    ["admin.html#dashboard", "bi-speedometer2", "Dashboard", "dashboard"],
    ["admin.html#complaints", "bi-inboxes", "Manage Complaints", "complaints"],
    ["admin.html#ml", "bi-cpu", "ML Module", "ml"]
];

/* Authentication and sidebar */
async function initShell({ role = "citizen", active = "" }) {
    let user;

    try {
        const result = await api("/auth/me");
        user = result.user;
    } catch (error) {
        fail(error);
        return null;
    }

    if (!user) {
        location.replace(
            role === "admin" ? "login.html?admin=1" : "login.html"
        );
        return null;
    }

    if (user.role !== role) {
        location.replace(
            user.role === "admin" ? "admin.html" : "dashboard.html"
        );
        return null;
    }

    const navigation = role === "admin" ? ADMIN_NAV : CITIZEN_NAV;
    const sidebar = qs("#sidebar");

    if (!sidebar) return user;

    sidebar.innerHTML = `
        <a class="brand" href="index.html">
            <img src="images/logo.svg" alt="">
            <span>Community Problem<br>Platform</span>
        </a>

        ${navigation.map(([href, icon, label, key]) => `
            <a class="nav-i ${key === active ? "active" : ""}"
               href="${href}" data-k="${key}">
                <i class="bi ${icon}"></i>
                ${label}
                ${key === "notifications"
                    ? '<span class="badge-n d-none" id="unread"></span>'
                    : ""}
            </a>
        `).join("")}

        <div class="spacer"></div>

        <a class="nav-i" href="#" id="logoutBtn">
            <i class="bi bi-box-arrow-right"></i>
            Logout
        </a>
    `;

    const logoutButton = qs("#logoutBtn");

    if (logoutButton) {
        logoutButton.onclick = event => {
            event.preventDefault();
            logout();
        };
    }

    const chip = qs("#userChip");

    if (chip) {
        const firstLetter = user.full_name
            ? user.full_name[0].toUpperCase()
            : "U";

        chip.innerHTML = `
            <span>${esc(user.full_name)}</span>
            <div class="avatar">${esc(firstLetter)}</div>
        `;
    }

    const menuButton = qs("#menuBtn");

    if (menuButton) {
        menuButton.onclick = () => sidebar.classList.toggle("open");
    }

    document.addEventListener("click", event => {
        if (!sidebar.classList.contains("open")) return;

        if (
            !sidebar.contains(event.target) &&
            event.target !== menuButton &&
            !(menuButton && menuButton.contains(event.target))
        ) {
            sidebar.classList.remove("open");
        }
    });

    if (role === "citizen") {
        api("/notifications")
            .then(result => {
                const badge = qs("#unread");

                if (badge && result.unread) {
                    badge.textContent = result.unread;
                    badge.classList.remove("d-none");
                }
            })
            .catch(() => {});
    }

    return user;
}
