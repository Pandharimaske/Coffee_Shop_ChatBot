# 🎨 Frontend — Merry's Way

> React 18 + Vite frontend for the Coffee Shop AI Assistant, deployed on Vercel.

---

## Contents

- [Project Layout](#-project-layout)
- [Routing & Pages](#-routing--pages)
- [Component Guide](#-component-guide)
- [State Management](#-state-management)
- [API Service Layer](#-api-service-layer)
- [SSE Streaming](#-sse-streaming)
- [HITL Checkout Flow](#-hitl-checkout-flow)
- [Admin Dashboard](#-admin-dashboard)
- [Environment Variables](#-environment-variables)
- [Local Development](#-local-development)

---

## 📁 Project Layout

```
frontend/
├── src/
│   ├── App.jsx                  # Root router — all routes defined here
│   ├── main.jsx                 # Entry point — wraps app in AuthContext + CartContext
│   ├── index.css                # Global styles + CSS variables
│   │
│   ├── components/
│   │   ├── Chatbot.jsx          # Customer AI chat — SSE streaming, HITL, history
│   │   ├── AdminDashboard.jsx   # Admin BI chat — Text-to-SQL + chart rendering
│   │   ├── Home.jsx             # Landing page
│   │   ├── Menu.jsx             # Product catalog with filtering
│   │   ├── Order.jsx            # Active order management page
│   │   ├── Login.jsx            # Email/password login form
│   │   ├── Register.jsx         # New account registration
│   │   ├── ProfileDrawer.jsx    # Slide-in user profile + preferences editor
│   │   ├── UserProfilePanel.jsx # Preferences form inside ProfileDrawer
│   │   ├── CheckoutModal.jsx    # Payment confirmation UI (HITL resume trigger)
│   │   ├── FloatingCart.jsx     # Floating cart button + quick summary
│   │   ├── CartToast.jsx        # Item-added notification toast
│   │   ├── Sidebar.jsx          # Navigation sidebar
│   │   ├── RequireAuth.jsx      # Route guard: redirect to /login if no token
│   │   └── RequireAdmin.jsx     # Route guard: redirect if not is_admin
│   │
│   ├── context/
│   │   ├── AuthContext.jsx      # JWT token + user info (email, username, is_admin)
│   │   ├── CartContext.jsx      # Cart state + add/remove/update/clear actions
│   │   └── ProgressContext.jsx  # Global loading/progress indicator
│   │
│   ├── services/
│   │   └── api.js               # All backend calls — single source of truth
│   │
│   ├── config/                  # App-level config (base URL, constants)
│   └── data/                    # Static data (category lists, etc.)
│
├── vercel.json                  # SPA rewrite rules → all paths → index.html
├── vite.config.js
└── package.json
```

---

## 🗺️ Routing & Pages

All routes are in `App.jsx`. Protected routes use `<RequireAuth>` and `<RequireAdmin>` wrappers.

```
/              → Home         (public)
/login         → Login        (public — redirects if already logged in)
/register      → Register     (public)
/chat          → Chatbot      🔒 RequireAuth
/menu          → Menu         🔒 RequireAuth
/order         → Order        🔒 RequireAuth
/admin         → AdminDashboard  🔒 RequireAuth + RequireAdmin
```

`RequireAdmin` checks `user.is_admin` from `AuthContext` (populated from `GET /user/me`).

---

## 🧩 Component Guide

### `Chatbot.jsx` — the heart of the customer experience

The largest component (25KB). Handles:

**On Mount:**
```
GET /chat/history?session_id=...
  → Reconstructs message list (text bubbles)
  → Identifies [Approval Required] messages → re-renders HITL bubbles
  → Scrolls to bottom
```

**On Send:**
```
POST /chat/stream (body: { user_input, session_id })
  → Returns a ReadableStream (SSE)
  → Reads events token by token
  → 3 event types:
     • status  → shows "Thinking..." / "Routing..." indicator
     • token   → appends to current bot bubble character by character
     • interrupt → hides text bubble, shows CheckoutModal
```

**State:**
```js
messages      // [{role: "user"|"bot", content: "...", type: "text"|"interrupt"}]
inputValue    // current input box value
isStreaming   // true while SSE is open
sessionId     // from localStorage (persists across refreshes)
```

---

### `AdminDashboard.jsx` — BI Intelligence interface

**On Mount:**
```
adminAPI.getSessionId()  → get/create admin_session_id from localStorage
GET /admin/history?session_id=...
  → Reconstructs conversation (text bubbles + chart states)
  → Re-renders ChartRenderer for any historical chart responses
```

**On Send:**
```
POST /admin/chat { query, session_id }
  → Returns AdminState JSON:
     {
       narrative: "...",
       chart_type: "bar" | "pie" | "line" | "table" | "none",
       chart_data: [{ name: "...", value: 123 }],
       sql: "SELECT ..."
     }
  → ChartRenderer (inline) renders the appropriate Recharts component
```

**Chart rendering is driven entirely by the structured agent state** — no client-side SQL parsing.

---

### `CheckoutModal.jsx` — HITL payment confirmation

Shown when the chatbot receives an `interrupt` event. Contains the order summary and a payment button. On confirm:

```js
await chatAPI.resumeChat("confirmed", "Payment Confirmed")
// → POST /chat/resume { session_id, payment_status: "confirmed" }
// → LangGraph resumes from the interrupt checkpoint
// → Returns order confirmation message
```

---

### `Menu.jsx`

- Fetches all products from `GET /products`
- Client-side filtering by category
- "Add to Cart" → CartContext action → `CartToast` notification

---

### `ProfileDrawer.jsx` + `UserProfilePanel.jsx`

- Slide-in panel triggered from Sidebar
- Loads `GET /user/preferences` → pre-fills form
- On save: `PUT /user/preferences` with the updated fields
- Allergies, likes, dislikes are comma-separated input → parsed to arrays

---

## 🧠 State Management

State is kept **minimal and local**. Only two things are global (React Context):

### `AuthContext`

```js
{
  user: { id, email, username, is_admin },
  token: "...",             // from localStorage
  login(email, password),   // calls authAPI.login, sets token + user
  logout(),                 // clears localStorage, resets state
  isLoading: bool           // true during initial /user/me check
}
```

Used by: `RequireAuth`, `RequireAdmin`, `Sidebar`, `Chatbot`, `AdminDashboard`

### `CartContext`

```js
{
  cart: [{ id, name, price, quantity, image_url }],
  addToCart(product),        // adds or increments quantity
  removeFromCart(productId), // decrements, removes at 0
  updateQuantity(id, qty),
  clearCart(),
  totalItems: int,
  totalPrice: float
}
```

Used by: `Menu`, `FloatingCart`, `Order`, `CartToast`

---

## 🔌 API Service Layer

**All backend calls go through `src/services/api.js`** — no raw `fetch()` anywhere else in the codebase.

```js
// The 5 API namespaces:
authAPI    // register, login, logout
userAPI    // getMe, getPreferences, updatePreferences
productsAPI // getAll (with optional category + search filters)
chatAPI    // send, sendStream, getHistory, resumeChat
ordersAPI  // getActive, getHistory, updateActive, clearActive
adminAPI   // chat, getHistory, getSessionId
```

### Session ID Management

Session IDs are created on first use and persisted in `localStorage`:

```js
// Customer session
getSessionId()       // key: "session_id"      — reset on login
getAdminSessionId()  // key: "admin_session_id" — independent from customer session
```

Both session IDs are stable across page refreshes — this is what enables history restoration.

---

## ⚡ SSE Streaming

The chatbot uses `fetch` (not `EventSource`) for SSE because it needs to send a POST request with a body. `EventSource` only supports GET.

```js
// chatAPI.sendStream returns a ReadableStream
const stream = await chatAPI.sendStream(userInput);
const reader = stream.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const text = decoder.decode(value);
  const lines = text.split("\n").filter(l => l.startsWith("data: "));

  for (const line of lines) {
    const event = JSON.parse(line.slice(6));

    if (event.type === "status") {
      setStatusIndicator(event.node); // "Routing...", "Thinking..."
    } else if (event.type === "token") {
      appendToCurrentBubble(event.content);
    } else if (event.type === "interrupt") {
      showCheckoutModal(event.payload);
    }
  }
}
```

---

## ⏸️ HITL Checkout Flow

```
1. User: "yes confirm my order"
   ↓
2. Chatbot streams tokens until event.type === "interrupt"
   → payload: { items: [...], total: 123.00 }
   ↓
3. CheckoutModal renders with order summary
   ↓
4. User clicks "Pay & Confirm"
   → chatAPI.resumeChat("confirmed")
   → POST /chat/resume { session_id, payment_status: "confirmed" }
   ↓
5. Backend resumes LangGraph from checkpoint
   → Order agent confirms order in DB
   → Email receipt sent via Resend
   → Returns confirmation message
   ↓
6. Chatbot appends confirmation message to conversation
   CheckoutModal closes
```

If user clicks "Cancel": `resumeChat("cancelled")` → order stays in `active` state.

---

## 🧑‍💼 Admin Dashboard

The Admin Dashboard is only accessible to users where `is_admin = true` in `coffee_shop_profiles`.

### Chart Types

The backend `AdminState` controls what the frontend renders:

| `chart_type` | Recharts Component | Use Case |
|-------------|-------------------|---------|
| `bar` | `BarChart` | Rankings, comparisons |
| `pie` | `PieChart` | Distribution, shares |
| `line` | `LineChart` | Trends over time |
| `table` | HTML `<table>` | Raw tabular data |
| `none` | No chart | Text-only narrative |

### Chart Renderer

The `ChartRenderer` (inline in `AdminDashboard.jsx`) receives:
```js
{ chart_type, chart_data: [{ name, value }] }
```
and renders the appropriate Recharts component. `chart_data` is already in the exact shape Recharts expects — no transformation needed.

---

## 🔑 Environment Variables

```env
# .env (local development)
VITE_API_URL=http://localhost:8000

# .env.production (Vercel — set via dashboard, NOT committed to git)
VITE_API_URL=https://your-backend.onrender.com
```

`VITE_API_URL` is the only required variable. All other config is static.

> ⚠️ `.env.production` is in `.gitignore` — set it via Vercel's environment variable dashboard.

---

## 🚀 Local Development

```bash
cd frontend

# Install dependencies
npm install

# Set API URL for local backend
echo "VITE_API_URL=http://localhost:8000" > .env

# Start dev server
npm run dev
# App: http://localhost:5173

# Build for production (only needed for deployment validation)
npm run build
```

### Vercel Deployment

The `vercel.json` handles SPA rewrites so that direct URL access (e.g. `/chat`) works:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/" }]
}
```

Set `VITE_API_URL` to your Render backend URL in the Vercel project settings under **Environment Variables**.
