import { useState } from "react";
import { Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import Menu from "./components/Menu";
import Order from "./components/Order";
import Home from "./components/Home";
import Chatbot from "./components/Chatbot";
import Login from "./components/Login";
import Register from "./components/Register";
import RequireAuth from "./components/RequireAuth";
import ProfileDrawer from "./components/ProfileDrawer";
import { useAuth } from "./context/AuthContext";
import { useCart } from "./context/CartContext";

function Navbar() {
  const { user, logout } = useAuth();
  const { cartItems } = useCart();
  const [showProfile, setShowProfile] = useState(false);
  const location = useLocation();

  const cartCount = cartItems.reduce((sum, i) => sum + i.quantity, 0);
  const isActive = (path) => location.pathname === path;

  return (
    <>
      <header className="bg-[#4B3832] shadow-2xl sticky top-0 z-30">
        <div className="flex justify-between items-center px-6 py-3.5 max-w-7xl mx-auto">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <span className="text-2xl">☕</span>
            <span className="text-xl font-bold text-[#ffe8b3] group-hover:text-white transition tracking-tight">
              Merry's Way
            </span>
          </Link>

          {/* Nav links */}
          <nav className="flex items-center gap-1">
            <NavLink to="/menu" active={isActive("/menu")}>Menu</NavLink>

            {user && (
              <NavLink to="/order" active={isActive("/order")} badge={cartCount}>
                Order
              </NavLink>
            )}

            {user ? (
              <>
                {/* Avatar / username button */}
                <button
                  onClick={() => setShowProfile(true)}
                  className="ml-2 flex items-center gap-2 bg-[#b68d40] hover:bg-[#a37b2c] text-white px-3 py-1.5 rounded-full text-sm font-semibold transition-all active:scale-95 shadow"
                >
                  <span className="w-6 h-6 bg-[#4B3832] rounded-full flex items-center justify-center text-xs font-bold text-[#ffe8b3]">
                    {(user.username || user.email)[0].toUpperCase()}
                  </span>
                  <span className="hidden sm:block">{user.username || user.email.split("@")[0]}</span>
                </button>

                <button
                  onClick={logout}
                  className="ml-1 text-[#c8b09a] hover:text-white text-sm px-3 py-1.5 rounded-full hover:bg-[#3a2d27] transition"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="ml-2 bg-[#b68d40] hover:bg-[#a37b2c] text-white text-sm font-semibold px-4 py-1.5 rounded-full transition shadow"
              >
                Login
              </Link>
            )}
          </nav>
        </div>
      </header>

      {/* Profile drawer */}
      {showProfile && user && (
        <ProfileDrawer user={user} onClose={() => setShowProfile(false)} />
      )}
    </>
  );
}

function NavLink({ to, active, children, badge }) {
  return (
    <Link
      to={to}
      className={`relative px-4 py-1.5 rounded-full text-sm font-medium transition-all ${
        active
          ? "bg-[#b68d40] text-white shadow"
          : "text-[#c8b09a] hover:text-white hover:bg-[#3a2d27]"
      }`}
    >
      {children}
      {badge > 0 && (
        <span className="absolute -top-1 -right-1 w-4 h-4 bg-orange-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center shadow">
          {badge > 9 ? "9+" : badge}
        </span>
      )}
    </Link>
  );
}

function App() {
  return (
    <div className="bg-[#F2E6D9] min-h-screen text-[#4B3832] relative">
      <Navbar />

      <main className="max-w-7xl mx-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/menu" element={<Menu />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/order"
            element={
              <RequireAuth>
                <Order />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Chatbot />
    </div>
  );
}

export default App;
