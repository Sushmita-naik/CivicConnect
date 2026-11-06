
(async () => {

  const user = await initShell({
    role: "citizen",
    active: "report"
  });

  if (!user) return;

  const f = qs("#reportForm");
  const cat = f.elements.category;
  const box = qs("#predBox");
  const locationInput = f.elements.location;

  // -----------------------------
  // CATEGORY SETUP
  // -----------------------------

  cat.innerHTML =
    '<option value="">Select category</option>' +
    CATEGORIES.map(c => `<option>${esc(c)}</option>`).join("");

  locationInput.value = user.location || "";

  // -----------------------------
  // DATE AND TIME
  // -----------------------------

  const now = new Date();

  now.setMinutes(
    now.getMinutes() - now.getTimezoneOffset()
  );

  f.elements.incident_datetime.value =
    now.toISOString().slice(0, 16);

  // -----------------------------
  // MAP SETUP
  // -----------------------------

  const DEFAULT_LAT = 13.02295;
  const DEFAULT_LNG = 74.96889;

  const map = L.map("locationMap").setView(
    [DEFAULT_LAT, DEFAULT_LNG],
    13
  );

  L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
      attribution: "&copy; OpenStreetMap contributors",
      maxZoom: 19
    }
  ).addTo(map);

  // Separate layers for selected location and complaints
  const selectedLocationLayer = L.layerGroup().addTo(map);
  const complaintLayer = L.layerGroup().addTo(map);

  let marker = null;
  let reverseRequest = 0;

  // -----------------------------
  // EXISTING GPS COORDINATES
  // -----------------------------

  function getExistingCoordinates(value) {

    const match = value.match(
      /GPS\s*(-?\d+(?:\.\d+)?)[,\s]+(-?\d+(?:\.\d+)?)/i
    );

    if (!match) return null;

    const lat = Number(match[1]);
    const lng = Number(match[2]);

    if (
      !Number.isFinite(lat) ||
      !Number.isFinite(lng) ||
      lat < -90 ||
      lat > 90 ||
      lng < -180 ||
      lng > 180
    ) {
      return null;
    }

    return { lat, lng };
  }

  // -----------------------------
  // LOAD COMMUNITY COMPLAINTS
  // -----------------------------

  async function loadCommunityComplaints() {

    try {

      const result = await api("/complaints/map");

      const complaints = result.complaints || [];

      let mappedCount = 0;

      complaints.forEach(complaint => {

        const lat = Number(complaint.latitude);
        const lng = Number(complaint.longitude);

        // Skip complaints without valid GPS coordinates
        if (
          complaint.latitude === null ||
          complaint.longitude === null ||
          !Number.isFinite(lat) ||
          !Number.isFinite(lng) ||
          lat < -90 ||
          lat > 90 ||
          lng < -180 ||
          lng > 180
        ) {
          return;
        }

        const complaintMarker = L.circleMarker(
          [lat, lng],
          {
            radius: 9,
            color: "#b42318",
            fillColor: "#ef4444",
            fillOpacity: 0.9,
            weight: 2
          }
        );

        // Safe popup content
        const popupContent = document.createElement("div");

        const title = document.createElement("strong");
        title.textContent = complaint.title || "Untitled complaint";

        const category = document.createElement("div");
        category.textContent =
          "Category: " + (complaint.category || "Not specified");

        const status = document.createElement("div");
        status.textContent =
          "Status: " + (complaint.status || "Unknown");

        const id = document.createElement("small");
        id.textContent = "Complaint #" + complaint.id;

        popupContent.append(
          title,
          document.createElement("hr"),
          category,
          status,
          id
        );

        complaintMarker.bindPopup(popupContent);

        complaintMarker.addTo(complaintLayer);

        mappedCount++;

      });

      console.log(
        `${mappedCount} of ${complaints.length} complaints displayed on the map.`
      );

      if (complaints.length > mappedCount) {

        console.info(
          `${complaints.length - mappedCount} complaints have no valid GPS coordinates yet.`
        );

      }

    } catch (error) {

      console.error(
        "Could not load community complaints:",
        error
      );

      toast(
        "Could not load existing community complaints.",
        "err"
      );

    }

  }

  // Load all existing complaints
  await loadCommunityComplaints();

  // -----------------------------
  // REVERSE GEOCODING
  // -----------------------------

  async function getAddress(lat, lng) {

    const fallback =
      `GPS ${lat.toFixed(5)}, ${lng.toFixed(5)}`;

    try {

      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`,
        {
          headers: {
            "Accept-Language": "en"
          }
        }
      );

      if (!response.ok) return fallback;

      const data = await response.json();
      const a = data.address || {};

      const parts = [
        a.road,
        a.suburb || a.neighbourhood,
        a.city || a.town || a.village,
        a.state
      ].filter(Boolean);

      const place = parts.length
        ? parts.join(", ")
        : data.display_name;

      return place
        ? `${place} (GPS ${lat.toFixed(5)}, ${lng.toFixed(5)})`
        : fallback;

    } catch (error) {

      return fallback;

    }

  }

  // -----------------------------
  // UPDATE SELECTED LOCATION
  // -----------------------------

  async function selectLocation(lat, lng) {

    const requestId = ++reverseRequest;

    if (marker) {

      marker.setLatLng([lat, lng]);

    } else {

      marker = L.marker(
        [lat, lng],
        {
          draggable: true
        }
      ).addTo(selectedLocationLayer);

      marker.on("dragend", () => {

        const position = marker.getLatLng();

        selectLocation(
          position.lat,
          position.lng
        );

      });

    }

    map.setView([lat, lng], 16);

    locationInput.value = "Finding address...";

    const address = await getAddress(lat, lng);

    if (requestId !== reverseRequest) return;

    locationInput.value = address;

    ok("Location selected successfully.");

  }

  // -----------------------------
  // MAP CLICK
  // -----------------------------

  map.on("click", event => {

    selectLocation(
      event.latlng.lat,
      event.latlng.lng
    );

  });

  // Restore existing GPS location
  const existing = getExistingCoordinates(
    locationInput.value
  );

  if (existing) {

    marker = L.marker(
      [existing.lat, existing.lng],
      {
        draggable: true
      }
    ).addTo(selectedLocationLayer);

    map.setView(
      [existing.lat, existing.lng],
      16
    );

    marker.on("dragend", () => {

      const position = marker.getLatLng();

      selectLocation(
        position.lat,
        position.lng
      );

    });

  }

  // -----------------------------
  // GPS BUTTON
  // -----------------------------

  qs("#geoBtn").onclick = () => {

    if (!navigator.geolocation) {

      return toast(
        "Geolocation is not supported by this browser.",
        "err"
      );

    }

    toast("Getting your current location...");

    navigator.geolocation.getCurrentPosition(

      position => {

        selectLocation(
          position.coords.latitude,
          position.coords.longitude
        );

      },

      error => {

        let message = "Could not get your location.";

        if (error.code === 1) {
          message = "Location permission was denied. Please allow location access.";
        }

        if (error.code === 2) {
          message = "Your current location is unavailable.";
        }

        if (error.code === 3) {
          message = "Location request timed out. Please try again.";
        }

        toast(message, "err");

      },

      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 0
      }

    );

  };

  // -----------------------------
  // ML CATEGORY PREDICTION
  // -----------------------------

  let userPicked = false;
  let pred = null;

  function renderPred() {

    if (!pred) return;

    const pct = Math.round(pred.confidence * 100);

    const changed =
      cat.value && cat.value !== pred.category;

    box.className = "col-12 pred-box";

    box.innerHTML = `
      <div class="d-flex justify-content-between">

        <div>
          <div class="muted small">Predicted category</div>

          <div class="fs-5 fw-bold" style="color:var(--navy)">
            <i class="bi bi-stars text-success"></i>
            ${esc(pred.category)}
          </div>
        </div>

        <div class="text-end">
          <div class="muted small">Confidence</div>
          <div class="fs-5 fw-bold">${pct}%</div>
        </div>

      </div>

      <div class="conf-bar my-2">
        <div style="width:${pct}%"></div>
      </div>

      <div class="small ${changed ? "text-warning-emphasis" : "muted"}">

        ${
          changed
            ? `You changed the category to <b>${esc(cat.value)}</b> - your choice will be saved.`
            : pct < 50
              ? "Low confidence - please check the category below."
              : "Not right? Choose a different category below to correct it."
        }

      </div>
    `;

  }

  async function classify() {

    const description =
      f.elements.description.value.trim();

    const title =
      f.elements.title.value.trim();

    if (description.length < 20) {

      box.className = "col-12 d-none";

      return;

    }

    box.className = "col-12 pred-box";

    box.innerHTML = `
      <span class="spinner-border spinner-border-sm me-2"></span>
      Analysing description...
    `;

    try {

      pred = await api(
        "/ml/predict",
        {
          method: "POST",
          body: {
            title,
            description
          }
        }
      );

      f.elements.predicted_category.value =
        pred.category;

      f.elements.prediction_confidence.value =
        pred.confidence;

      if (!userPicked) {
        cat.value = pred.category;
      }

      renderPred();

    } catch (e) {

      pred = null;

      f.elements.predicted_category.value = "";
      f.elements.prediction_confidence.value = "";

      box.innerHTML =
        e.status === 503
          ? "Automatic classification is not available yet. Please choose a category."
          : esc(e.message);

    }

  }

  const run = debounce(classify, 700);

  f.elements.description.addEventListener("input", run);
  f.elements.title.addEventListener("input", run);

  cat.addEventListener("change", () => {

    userPicked = true;

    renderPred();

  });

  // -----------------------------
  // PHOTO PREVIEW
  // -----------------------------

  f.elements.photo.addEventListener("change", () => {

    const file = f.elements.photo.files[0];
    const img = qs("#preview");

    if (file) {

      img.src = URL.createObjectURL(file);
      img.classList.remove("d-none");

    } else {

      img.classList.add("d-none");

    }

  });

  // -----------------------------
  // SUBMIT COMPLAINT
  // -----------------------------

  f.onsubmit = async event => {

    event.preventDefault();

    const button = qs("#submitBtn");

    button.disabled = true;

    showFieldErrors(f, {});

    try {

      const result = await api(
        "/complaints",
        {
          method: "POST",
          form: new FormData(f)
        }
      );

      ok("Complaint submitted!");

      setTimeout(() => {

        location.href =
          "tracking.html?id=" + result.complaint.id;

      }, 900);

    } catch (error) {

      showFieldErrors(f, error.fields);

      fail(error);

      button.disabled = false;

    }

  };

})();
