const baseUrlInput = document.getElementById("base-url");
const baseUrlLabel = document.getElementById("base-url-label");
const healthOutput = document.getElementById("health-output");
const quickOutput = document.getElementById("quick-output");
const labOutput = document.getElementById("lab-output");
const tokenField = document.getElementById("token");

const authUser = document.getElementById("auth-user");
const authPass = document.getElementById("auth-pass");

const destQuery = document.getElementById("dest-query");
const destDetailQuery = document.getElementById("dest-detail-query");
const destPoiLocation = document.getElementById("dest-poi-location");
const destRadius = document.getElementById("dest-radius");
const destLimit = document.getElementById("dest-limit");
const weatherLocation = document.getElementById("weather-location");
const itineraryTitle = document.getElementById("itinerary-title");
const itineraryStart = document.getElementById("itinerary-start");
const itineraryEnd = document.getElementById("itinerary-end");
const itineraryDesc = document.getElementById("itinerary-desc");
const itineraryOutput = document.getElementById("itinerary-output");
const activityItinerary = document.getElementById("activity-itinerary");
const activityTitle = document.getElementById("activity-title");
const activityStart = document.getElementById("activity-start");
const activityEnd = document.getElementById("activity-end");
const activityLocation = document.getElementById("activity-location");
const activityNote = document.getElementById("activity-note");

const citiesKeyword = document.getElementById("cities-keyword");
const citiesCountry = document.getElementById("cities-country");
const citiesLimit = document.getElementById("cities-limit");

const flightOrigin = document.getElementById("flight-origin");
const flightDestination = document.getElementById("flight-destination");
const flightDeparture = document.getElementById("flight-departure");
const flightReturn = document.getElementById("flight-return");
const flightAdults = document.getElementById("flight-adults");
const flightCurrency = document.getElementById("flight-currency");
const flightClass = document.getElementById("flight-class");
const flightNonstop = document.getElementById("flight-nonstop");
const flightMax = document.getElementById("flight-max");
const flightOfferId = document.getElementById("flight-offer-id");

const hotelCity = document.getElementById("hotel-city");
const hotelCurrency = document.getElementById("hotel-currency");
const hotelCheckin = document.getElementById("hotel-checkin");
const hotelCheckout = document.getElementById("hotel-checkout");
const hotelAdults = document.getElementById("hotel-adults");
const hotelChildren = document.getElementById("hotel-children");
const hotelRooms = document.getElementById("hotel-rooms");
const hotelRadius = document.getElementById("hotel-radius");
const hotelBoard = document.getElementById("hotel-board");
const hotelPayment = document.getElementById("hotel-payment");
const hotelMax = document.getElementById("hotel-max");
const hotelId = document.getElementById("hotel-id");
const hotelOfferCheckin = document.getElementById("hotel-offer-checkin");
const hotelOfferCheckout = document.getElementById("hotel-offer-checkout");
const hotelOfferAdults = document.getElementById("hotel-offer-adults");
const hotelOfferRooms = document.getElementById("hotel-offer-rooms");
const hotelOfferCurrency = document.getElementById("hotel-offer-currency");
const bookingOutput = document.getElementById("booking-output");

const labMethod = document.getElementById("lab-method");
const labPath = document.getElementById("lab-path");
const labBody = document.getElementById("lab-body");

const storageKey = "trip-hub-token";

const getBaseUrl = () => baseUrlInput.value.trim().replace(/\/$/, "");

const setToken = (token) => {
  tokenField.value = token || "";
  if (token) {
    localStorage.setItem(storageKey, token);
  } else {
    localStorage.removeItem(storageKey);
  }
};

const getToken = () => tokenField.value.trim();

const pretty = (data) => JSON.stringify(data, null, 2);

const setOutput = (element, message) => {
  element.textContent = message;
};

const requireToken = (outputElement) => {
  const token = getToken();
  if (!token) {
    outputElement.textContent = "Vui lòng đăng nhập để lấy JWT trước khi gọi API.";
    return null;
  }
  return token;
};


const itineraryIndex = new Map();

const withOptional = (payload, key, value) => {
  if (value !== "" && value !== null && value !== undefined) {
    payload[key] = value;
  }
};

const apiFetch = async (path, options = {}) => {
  const url = `${getBaseUrl()}${path}`;
  const headers = options.headers || {};
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  if (options.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const response = await fetch(url, { ...options, headers });
  const contentType = response.headers.get("content-type") || "";
  const body = contentType.includes("application/json")
    ? await response.json()
    : await response.text();
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}: ${pretty(body)}`);
  }
  return body;
};

const renderItineraryOptions = (items) => {
  itineraryIndex.clear();
  items.forEach((item) => {
    if (item && item.id) {
      itineraryIndex.set(item.id, item);
    }
  });
  const options = items
    .map((item) => {
      const label = `${item.title || "Untitled"} (${item.id})`;
      return `<option value="${item.id}">${label}</option>`;
    })
    .join("");
  activityItinerary.innerHTML = `<option value="">Select itinerary</option>${options}`;
};

const refreshItineraries = async () => {
  try {
    const data = await apiFetch("/api/v1/itinerary/itineraries");
    if (Array.isArray(data)) {
      renderItineraryOptions(data);
    }
  } catch (err) {
    // Ignore refresh errors; keep UI usable.
  }
};

document.getElementById("save-base").addEventListener("click", () => {
  baseUrlLabel.textContent = getBaseUrl();
});

document.getElementById("open-swagger").addEventListener("click", () => {
  window.open(`${getBaseUrl()}/docs`, "_blank");
});

document.getElementById("ping-health").addEventListener("click", async () => {
  healthOutput.textContent = "Loading...";
  try {
    const data = await apiFetch("/health");
    healthOutput.textContent = pretty(data);
  } catch (err) {
    healthOutput.textContent = err.message;
  }
});

document.getElementById("register").addEventListener("click", async () => {
  quickOutput.textContent = "Registering...";
  try {
    const data = await apiFetch("/api/v1/auth/register", {
      method: "POST",
      body: JSON.stringify({
        username: authUser.value.trim(),
        password: authPass.value.trim(),
      }),
    });
    quickOutput.textContent = pretty(data);
  } catch (err) {
    quickOutput.textContent = err.message;
  }
});

document.getElementById("login").addEventListener("click", async () => {
  quickOutput.textContent = "Logging in...";
  try {
    const data = await apiFetch("/api/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({
        username: authUser.value.trim(),
        password: authPass.value.trim(),
      }),
    });
    setToken(data.access_token || "");
    quickOutput.textContent = pretty(data);
    await refreshItineraries();
  } catch (err) {
    quickOutput.textContent = err.message;
  }
});

document.getElementById("clear-token").addEventListener("click", () => {
  setToken("");
});

document.getElementById("destinations").addEventListener("click", async () => {
  quickOutput.textContent = "Loading destinations...";
  try {
    if (!requireToken(quickOutput)) {
      return;
    }
    const query = encodeURIComponent(destQuery.value.trim());
    const data = await apiFetch(`/api/v1/destination/destinations?query=${query}`);
    quickOutput.textContent = pretty(data);
  } catch (err) {
    quickOutput.textContent = err.message;
  }
});

document.getElementById("destination-detail").addEventListener("click", async () => {
  quickOutput.textContent = "Loading destination detail...";
  try {
    if (!requireToken(quickOutput)) {
      return;
    }
    const query = destDetailQuery.value.trim() || destQuery.value.trim();
    if (!query) {
      throw new Error("Please provide a destination detail query.");
    }
    const data = await apiFetch(`/api/v1/destination/destinations/${encodeURIComponent(query)}`);
    quickOutput.textContent = pretty(data);
  } catch (err) {
    quickOutput.textContent = err.message;
  }
});

document.getElementById("dest-attractions").addEventListener("click", async () => {
  quickOutput.textContent = "Loading attractions...";
  try {
    if (!requireToken(quickOutput)) {
      return;
    }
    const location = destPoiLocation.value.trim() || destQuery.value.trim();
    if (!location) {
      throw new Error("Please provide a location for attractions.");
    }
    const params = new URLSearchParams({ location });
    if (destRadius.value) {
      params.set("radius_m", destRadius.value);
    }
    if (destLimit.value) {
      params.set("limit", destLimit.value);
    }
    const data = await apiFetch(`/api/v1/destination/attractions?${params.toString()}`);
    quickOutput.textContent = pretty(data);
  } catch (err) {
    quickOutput.textContent = err.message;
  }
});

document.getElementById("dest-hotels").addEventListener("click", async () => {
  quickOutput.textContent = "Loading hotels...";
  try {
    if (!requireToken(quickOutput)) {
      return;
    }
    const location = destPoiLocation.value.trim() || destQuery.value.trim();
    if (!location) {
      throw new Error("Please provide a location for hotels.");
    }
    const params = new URLSearchParams({ location });
    if (destRadius.value) {
      params.set("radius_m", destRadius.value);
    }
    if (destLimit.value) {
      params.set("limit", destLimit.value);
    }
    const data = await apiFetch(`/api/v1/destination/hotels?${params.toString()}`);
    quickOutput.textContent = pretty(data);
  } catch (err) {
    quickOutput.textContent = err.message;
  }
});

document.getElementById("weather-current").addEventListener("click", async () => {
  quickOutput.textContent = "Loading weather...";
  try {
    if (!requireToken(quickOutput)) {
      return;
    }
    const location = encodeURIComponent(weatherLocation.value.trim());
    const data = await apiFetch(`/api/v1/weather/current?location=${location}`);
    quickOutput.textContent = pretty(data);
  } catch (err) {
    quickOutput.textContent = err.message;
  }
});

document.getElementById("weather-forecast").addEventListener("click", async () => {
  quickOutput.textContent = "Loading weather forecast...";
  try {
    if (!requireToken(quickOutput)) {
      return;
    }
    const location = encodeURIComponent(weatherLocation.value.trim());
    const data = await apiFetch(`/api/v1/weather/forecast?location=${location}`);
    quickOutput.textContent = pretty(data);
  } catch (err) {
    quickOutput.textContent = err.message;
  }
});

document.getElementById("itinerary-create").addEventListener("click", async () => {
  setOutput(itineraryOutput, "Creating itinerary...");
  try {
    const data = await apiFetch("/api/v1/itinerary/itineraries", {
      method: "POST",
      body: JSON.stringify({
        title: itineraryTitle.value.trim(),
        start_date: itineraryStart.value,
        end_date: itineraryEnd.value,
        description: itineraryDesc.value.trim(),
      }),
    });
    setOutput(itineraryOutput, pretty(data));
    await refreshItineraries();
  } catch (err) {
    setOutput(itineraryOutput, err.message);
  }
});

document.getElementById("itinerary-list").addEventListener("click", async () => {
  setOutput(itineraryOutput, "Loading itineraries...");
  try {
    const data = await apiFetch("/api/v1/itinerary/itineraries");
    setOutput(itineraryOutput, pretty(data));
    if (Array.isArray(data)) {
      renderItineraryOptions(data);
    }
  } catch (err) {
    setOutput(itineraryOutput, err.message);
  }
});

document.getElementById("activity-create").addEventListener("click", async () => {
  setOutput(itineraryOutput, "Creating activity...");
  try {
    if (!activityItinerary.value) {
      throw new Error("Please select an itinerary.");
    }
    const itinerary = itineraryIndex.get(activityItinerary.value);
    if (!itinerary) {
      throw new Error("Selected itinerary not found. Please refresh itineraries.");
    }
    const start = new Date(activityStart.value);
    const end = new Date(activityEnd.value);
    if (!activityStart.value || !activityEnd.value) {
      throw new Error("Please provide start and end time.");
    }
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      throw new Error("Invalid activity time format.");
    }
    if (start > end) {
      throw new Error("Activity start time must be before end time.");
    }
    const itineraryStart = new Date(itinerary.start_date);
    const itineraryEnd = new Date(itinerary.end_date);
    if (start < itineraryStart || end > itineraryEnd) {
      throw new Error("Activity time must be within the itinerary date range.");
    }
    const data = await apiFetch("/api/v1/itinerary/activities", {
      method: "POST",
      body: JSON.stringify({
        itinerary_id: activityItinerary.value,
        title: activityTitle.value.trim(),
        start_time: activityStart.value,
        end_time: activityEnd.value,
        location: activityLocation.value.trim(),
        note: activityNote.value.trim() || null,
      }),
    });
    setOutput(itineraryOutput, pretty(data));
  } catch (err) {
    setOutput(itineraryOutput, err.message);
  }
});

document.getElementById("activities-list").addEventListener("click", async () => {
  setOutput(itineraryOutput, "Loading activities...");
  try {
    if (!activityItinerary.value) {
      throw new Error("Please select an itinerary.");
    }
    const itinerary = encodeURIComponent(activityItinerary.value);
    if (!itinerary) {
      throw new Error("Please provide an itinerary id.");
    }
    const data = await apiFetch(`/api/v1/itinerary/activities/${itinerary}`);
    setOutput(itineraryOutput, pretty(data));
  } catch (err) {
    setOutput(itineraryOutput, err.message);
  }
});

document.getElementById("cities-search").addEventListener("click", async () => {
  setOutput(bookingOutput, "Searching cities...");
  try {
    const params = new URLSearchParams();
    if (citiesKeyword.value.trim()) {
      params.set("keyword", citiesKeyword.value.trim());
    }
    if (citiesCountry.value.trim()) {
      params.set("country_code", citiesCountry.value.trim());
    }
    if (citiesLimit.value) {
      params.set("limit", citiesLimit.value);
    }
    const query = params.toString();
    const path = query ? `/api/v1/booking/cities?${query}` : "/api/v1/booking/cities";
    const data = await apiFetch(path);
    setOutput(bookingOutput, pretty(data));
  } catch (err) {
    setOutput(bookingOutput, err.message);
  }
});

document.getElementById("flight-search").addEventListener("click", async () => {
  setOutput(bookingOutput, "Searching flights...");
  try {
    const payload = {
      origin: flightOrigin.value.trim(),
      destination: flightDestination.value.trim(),
      departure_date: flightDeparture.value,
      return_date: flightReturn.value,
      adults: Number(flightAdults.value || 1),
      currency: flightCurrency.value.trim(),
      non_stop: flightNonstop.value === "true",
      max_results: Number(flightMax.value || 10),
    };
    withOptional(payload, "travel_class", flightClass.value || undefined);
    const data = await apiFetch("/api/v1/booking/flights/search", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setOutput(bookingOutput, pretty(data));
  } catch (err) {
    setOutput(bookingOutput, err.message);
  }
});

document.getElementById("flight-offer").addEventListener("click", async () => {
  setOutput(bookingOutput, "Loading flight offer...");
  try {
    const offerId = flightOfferId.value.trim();
    if (!offerId) {
      throw new Error("Please provide a flight offer id.");
    }
    const data = await apiFetch(`/api/v1/booking/flights/${encodeURIComponent(offerId)}`);
    setOutput(bookingOutput, pretty(data));
  } catch (err) {
    setOutput(bookingOutput, err.message);
  }
});

document.getElementById("hotel-search").addEventListener("click", async () => {
  setOutput(bookingOutput, "Searching hotels...");
  try {
    const payload = {
      city_code: hotelCity.value.trim(),
      check_in_date: hotelCheckin.value,
      check_out_date: hotelCheckout.value,
      adults: Number(hotelAdults.value || 1),
      children: Number(hotelChildren.value || 0),
      rooms: Number(hotelRooms.value || 1),
      radius: Number(hotelRadius.value || 5),
      currency: hotelCurrency.value.trim() || "USD",
      max_results: Number(hotelMax.value || 10),
    };
    withOptional(payload, "board_type", hotelBoard.value.trim() || undefined);
    withOptional(payload, "payment_policy", hotelPayment.value.trim() || undefined);
    const data = await apiFetch("/api/v1/booking/hotels/search", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setOutput(bookingOutput, pretty(data));
  } catch (err) {
    setOutput(bookingOutput, err.message);
  }
});

document.getElementById("hotel-offers").addEventListener("click", async () => {
  setOutput(bookingOutput, "Loading hotel offers...");
  try {
    const payload = {
      hotel_id: hotelId.value.trim(),
      check_in_date: hotelOfferCheckin.value,
      check_out_date: hotelOfferCheckout.value,
      adults: Number(hotelOfferAdults.value || 1),
      rooms: Number(hotelOfferRooms.value || 1),
      currency: hotelOfferCurrency.value.trim() || "USD",
    };
    const data = await apiFetch("/api/v1/booking/hotels/offers", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setOutput(bookingOutput, pretty(data));
  } catch (err) {
    setOutput(bookingOutput, err.message);
  }
});

document.getElementById("send-lab").addEventListener("click", async () => {
  labOutput.textContent = "Sending...";
  try {
    const options = { method: labMethod.value };
    if (labBody.value.trim()) {
      options.body = labBody.value;
    }
    const data = await apiFetch(labPath.value.trim(), options);
    labOutput.textContent = pretty(data);
  } catch (err) {
    labOutput.textContent = err.message;
  }
});

document.getElementById("clear-lab").addEventListener("click", () => {
  labBody.value = "";
  labOutput.textContent = "Ready.";
});

const storedToken = localStorage.getItem(storageKey);
if (storedToken) {
  tokenField.value = storedToken;
  refreshItineraries();
}
