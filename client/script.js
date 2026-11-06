const API_URL = "http://127.0.0.1:8000";

// Citizen section elements
const complaintForm = document.getElementById("complaintForm");
const complaintResult = document.getElementById("complaintResult");

const trackForm = document.getElementById("trackForm");
const trackResult = document.getElementById("trackResult");

// Admin section elements
const loadComplaintsBtn = document.getElementById("loadComplaintsBtn");
const adminComplaints = document.getElementById("adminComplaints");
const adminMessage = document.getElementById("adminMessage");


// --------------------------------------------------
// 1. SUBMIT A COMPLAINT
// --------------------------------------------------

complaintForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const description =
        document.getElementById("description").value.trim();

    const location =
        document.getElementById("location").value.trim();

    if (!description || !location) {
        alert("Please enter both description and location.");
        return;
    }

    complaintResult.textContent = "Submitting complaint...";

    try {

        const response = await fetch(`${API_URL}/complaints/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                description: description,
                location: location
            })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                data.detail
                    ? JSON.stringify(data.detail)
                    : "Unable to submit complaint."
            );
        }

        complaintResult.innerHTML = `
            <h3>Complaint Submitted Successfully!</h3>
            <p><strong>Complaint ID:</strong> ${data.id}</p>
            <p><strong>Category:</strong> ${escapeHTML(data.category ?? "Not assigned")}</p>
            <p><strong>Department:</strong> ${escapeHTML(data.department ?? "Not assigned")}</p>
            <p><strong>Status:</strong> ${escapeHTML(data.status)}</p>
            <p>Please save your complaint ID for tracking.</p>
        `;

        complaintForm.reset();

    } catch (error) {

        console.error("Submission error:", error);

        complaintResult.textContent =
            "Failed to submit complaint: " + error.message;
    }
});


// --------------------------------------------------
// 2. TRACK A COMPLAINT
// --------------------------------------------------

trackForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const complaintId =
        document.getElementById("complaintId").value.trim();

    if (!complaintId) {
        alert("Please enter your complaint ID.");
        return;
    }

    trackResult.textContent = "Searching for complaint...";

    try {

        const response = await fetch(
            `${API_URL}/complaints/${encodeURIComponent(complaintId)}`
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Complaint not found."
            );
        }

        trackResult.innerHTML = `
            <h3>Complaint Details</h3>
            <p><strong>Complaint ID:</strong> ${data.id}</p>
            <p><strong>Description:</strong> ${escapeHTML(data.description)}</p>
            <p><strong>Category:</strong> ${escapeHTML(data.category ?? "Not assigned")}</p>
            <p><strong>Location:</strong> ${escapeHTML(data.location)}</p>
            <p><strong>Department:</strong> ${escapeHTML(data.department ?? "Not assigned")}</p>
            <p><strong>Status:</strong> ${escapeHTML(data.status)}</p>
            <p><strong>Created:</strong> ${new Date(data.created_at).toLocaleString()}</p>
        `;

    } catch (error) {

        console.error("Tracking error:", error);

        trackResult.textContent =
            "Failed to track complaint: " + error.message;
    }
});


// --------------------------------------------------
// 3. LOAD ALL COMPLAINTS FOR ADMIN
// --------------------------------------------------

loadComplaintsBtn.addEventListener("click", loadComplaints);

async function loadComplaints() {

    adminComplaints.innerHTML = "<p>Loading complaints...</p>";
    adminMessage.textContent = "";

    try {

        const response = await fetch(`${API_URL}/complaints/`);

        const data = await response.json();

        if (!response.ok) {
            throw new Error("Unable to load complaints.");
        }

        if (!Array.isArray(data) || data.length === 0) {
            adminComplaints.innerHTML = "<p>No complaints found.</p>";
            return;
        }

        displayComplaints(data);

    } catch (error) {

        console.error("Admin loading error:", error);

        adminComplaints.textContent =
            "Failed to load complaints: " + error.message;
    }
}


// --------------------------------------------------
// 4. DISPLAY COMPLAINTS
// --------------------------------------------------

function displayComplaints(complaints) {

    adminComplaints.innerHTML = "";

    const statuses = [
        "Submitted",
        "Verified",
        "In Progress",
        "Resolved",
        "Rejected"
    ];

    const departments = [
        "Road Maintenance Department",
        "Sanitation Department",
        "Electrical Department",
        "Water Supply Department",
        "Drainage Department",
        "General Administration Department"
    ];

    complaints.forEach((complaint) => {

        const complaintCard = document.createElement("div");

        complaintCard.className = "admin-complaint-card";

        const statusOptions = statuses.map(status => `
            <option
                value="${escapeHTML(status)}"
                ${complaint.status === status ? "selected" : ""}
            >
                ${escapeHTML(status)}
            </option>
        `).join("");

        const departmentOptions = departments.map(department => `
            <option
                value="${escapeHTML(department)}"
                ${complaint.department === department ? "selected" : ""}
            >
                ${escapeHTML(department)}
            </option>
        `).join("");

        complaintCard.innerHTML = `
            <h3>Complaint #${complaint.id}</h3>

            <p>
                <strong>Description:</strong>
                ${escapeHTML(complaint.description)}
            </p>

            <p>
                <strong>Category:</strong>
                ${escapeHTML(complaint.category ?? "Not assigned")}
            </p>

            <p>
                <strong>Location:</strong>
                ${escapeHTML(complaint.location)}
            </p>

            <p>
                <strong>Current Status:</strong>
                ${escapeHTML(complaint.status)}
            </p>

            <p>
                <strong>Current Department:</strong>
                ${escapeHTML(complaint.department ?? "Not assigned")}
            </p>

            <label>Status</label>

            <select class="admin-status-select">
                ${statusOptions}
            </select>

            <button
                type="button"
                class="primary-button update-status-btn"
            >
                Update Status
            </button>

            <label>Department</label>

            <select class="admin-department-select">
                ${departmentOptions}
            </select>

            <button
                type="button"
                class="primary-button update-department-btn"
            >
                Update Department
            </button>
        `;

        // Store the complaint ID for update operations
        complaintCard.dataset.complaintId = complaint.id;

        adminComplaints.appendChild(complaintCard);
    });
}


// --------------------------------------------------
// 5. UPDATE COMPLAINT STATUS
// --------------------------------------------------

adminComplaints.addEventListener("click", async (event) => {

    if (!event.target.classList.contains("update-status-btn")) {
        return;
    }

    const card = event.target.closest(".admin-complaint-card");

    const complaintId = card.dataset.complaintId;

    const status =
        card.querySelector(".admin-status-select").value;

    try {

        const response = await fetch(
            `${API_URL}/complaints/${complaintId}/status`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: status
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Unable to update status."
            );
        }

        adminMessage.textContent =
            `Complaint #${complaintId} status updated successfully.`;

        await loadComplaints();

    } catch (error) {

        console.error("Status update error:", error);

        adminMessage.textContent =
            "Status update failed: " + error.message;
    }
});


// --------------------------------------------------
// 6. UPDATE COMPLAINT DEPARTMENT
// --------------------------------------------------

adminComplaints.addEventListener("click", async (event) => {

    if (!event.target.classList.contains("update-department-btn")) {
        return;
    }

    const card = event.target.closest(".admin-complaint-card");

    const complaintId = card.dataset.complaintId;

    const department =
        card.querySelector(".admin-department-select").value;

    try {

        const response = await fetch(
            `${API_URL}/complaints/${complaintId}/department`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    department: department
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(
                typeof data.detail === "string"
                    ? data.detail
                    : "Unable to update department."
            );
        }

        adminMessage.textContent =
            `Complaint #${complaintId} department updated successfully.`;

        await loadComplaints();

    } catch (error) {

        console.error("Department update error:", error);

        adminMessage.textContent =
            "Department update failed: " + error.message;
    }
});


// --------------------------------------------------
// 7. PREVENT HTML INJECTION
// --------------------------------------------------

function escapeHTML(value) {

    return String(value).replace(/[&<>"']/g, (character) => {

        const entities = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        };

        return entities[character];
    });
}