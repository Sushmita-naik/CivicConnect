
(async () => {
  const user = await initShell({
    role: "citizen",
    active: "tracking"
  });

  if (!user) return;

  const pick = qs("#pick");
  const body = qs("#trackBody");

  let list = [];

  // Load complaints belonging to the logged-in citizen
  try {
    const result = await api("/complaints");
    list = result.complaints || [];
  } catch (e) {
    return fail(e);
  }

  if (!list.length) {
    pick.closest(".card-x").remove();

    body.innerHTML = `
      <div class="card-x text-center muted py-5">
        Nothing to track yet.
        <a href="report.html">Report a problem</a>
      </div>
    `;
    return;
  }

  // Fill the complaint dropdown
  pick.innerHTML = list.map(c => `
    <option value="${c.id}">
      #${c.id} - ${esc(c.title)} (${esc(c.status)})
    </option>
  `).join("");

  // Select complaint ID from the URL
  const params = new URLSearchParams(location.search);
  const wantedId = params.get("id");

  if (wantedId && list.some(c => String(c.id) === wantedId)) {
    pick.value = wantedId;
  }

  async function load() {
    const id = pick.value;

    body.innerHTML = `
      <div class="card-x muted">Loading complaint...</div>
    `;

    try {
      // Fetch selected complaint
      const result = await api(`/complaints/${id}`);
      const c = result.complaint;

      // Current status progress
      const steps = [
        "Submitted",
        "Verified",
        "In Progress",
        "Resolved"
      ];

      const statusIndex = steps.indexOf(c.status);

      const icons = [
        "bi-send",
        "bi-search",
        "bi-tools",
        "bi-check2-circle"
      ];

      body.innerHTML = `
        <div class="card-x mb-4">

          <div class="d-flex flex-wrap justify-content-between gap-2">

            <div>
              <h5 class="fw-bold mb-1">
                #${c.id} · ${esc(c.title)}
              </h5>

              <div class="muted small">
                ${esc(c.category || "Uncategorized")}
                · ${esc(c.location)}
                ${c.ward ? " · " + esc(c.ward) : ""}
                · Submitted ${fmtDateTime(c.created_at)}
              </div>
            </div>

            <div>
              ${statusBadge(c.status)}
            </div>

          </div>

          ${
            c.status === "Rejected"
              ? `<div class="alert alert-danger mt-3">
                   This complaint has been rejected.
                 </div>`
              : ""
          }

          <div class="stepper">

            ${steps.map((step, i) => `
              <div class="step ${
                statusIndex >= i ? "reached" : ""
              } ${
                statusIndex === i ? "current" : ""
              }">

                <div class="dot">
                  <i class="bi ${icons[i]}"></i>
                </div>

                ${esc(step)}

              </div>
            `).join("")}

          </div>

        </div>

        <div class="row g-4">

          <div class="col-lg-7">

            <div class="card-x mb-4">
              <h6 class="fw-bold">Description</h6>
              <p class="mb-0">${esc(c.description)}</p>
            </div>

            <div class="card-x">
              <h6 class="fw-bold">Complaint Information</h6>

              <p class="mb-2">
                <strong>Category:</strong>
                ${esc(c.category || "Not specified")}
              </p>

              <p class="mb-2">
                <strong>Location:</strong>
                ${esc(c.location)}
              </p>

              <p class="mb-2">
                <strong>Department:</strong>
                ${esc(c.department || "Not assigned")}
              </p>

              <p class="mb-2">
                <strong>Current Status:</strong>
                ${esc(c.status)}
              </p>

              <p class="mb-0">
                <strong>Photograph:</strong>
                ${c.photo_filename ? "Photo attached" : "No photograph attached"}
              </p>
            </div>

          </div>

          <div class="col-lg-5">

            <div class="card-x">
              <h6 class="fw-bold mb-3">Tracking Information</h6>

              <p class="muted">
                Your complaint has been recorded successfully.
                Its current status is shown above.
              </p>

              <p class="mb-0">
                <strong>Complaint ID:</strong> #${c.id}
              </p>
            </div>

          </div>

        </div>
      `;

    } catch (e) {
      body.innerHTML = "";
      fail(e);
    }
  }

  // Load selected complaint
  pick.onchange = () => {
    history.replaceState(null, "", "?id=" + pick.value);
    load();
  };

  load();

})();
