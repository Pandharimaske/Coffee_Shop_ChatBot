/**
 * Central API service — all backend calls go through here.
 * Base URL from .env → VITE_API_URL
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ── Helpers ───────────────────────────────────────────────────────────────────

function getToken() {
  return localStorage.getItem("token");
}

function getSessionId() {
  let sid = localStorage.getItem("session_id");
  if (!sid) {
    sid = crypto.randomUUID();
    localStorage.setItem("session_id", sid);
  }
  return sid;
}

async function request(method, path, body = null, auth = true) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }

  if (res.status === 204) return null;
  return res.json();
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authAPI = {
  register: (username, email, password) =>
    request("POST", "/auth/register", { username, email, password }, false),

  login: async (email, password) => {
    const data = await request("POST", "/auth/login", { email, password }, false);
    localStorage.setItem("token", data.access_token);
    // Fresh session on login
    localStorage.setItem("session_id", crypto.randomUUID());
    return data;
  },

  logout: () => {
    localStorage.removeItem("token");
    localStorage.removeItem("session_id");
  },
};

// ── User ──────────────────────────────────────────────────────────────────────

export const userAPI = {
  getMe: () => request("GET", "/user/me"),
  getPreferences: () => request("GET", "/user/preferences"),
  updatePreferences: (prefs) => request("PUT", "/user/preferences", prefs),
};

// ── Products ──────────────────────────────────────────────────────────────────

export const productsAPI = {
  getAll: (category = null, search = null) => {
    const params = new URLSearchParams();
    if (category) params.append("category", category);
    if (search) params.append("search", search);
    const qs = params.toString();
    return request("GET", `/products${qs ? `?${qs}` : ""}`, null, false);
  },
};

// ── Chat ──────────────────────────────────────────────────────────────────────

export const chatAPI = {
  send: (userInput) =>
    request("POST", "/chat", {
      user_input: userInput,
      session_id: getSessionId(),
    }),

  // Load message history for current session (called on mount/refresh)
  getHistory: () =>
    request("GET", `/chat/history?session_id=${getSessionId()}`),
};

// ── Orders ────────────────────────────────────────────────────────────────────

export const ordersAPI = {
  getActive: () => request("GET", "/orders/active"),
  getHistory: () => request("GET", "/orders/history"),
  // Called whenever frontend cart changes
  updateActive: (items) => request("PUT", "/orders/active", { items }),
  clearActive: () => request("DELETE", "/orders/active"),
};

export { getSessionId, getToken };
