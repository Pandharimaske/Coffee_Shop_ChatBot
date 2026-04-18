import { useState, useEffect } from "react";
import { Routes, Route, Link, Navigate, useLocation } from "react-router-dom";
import Menu from "./components/Menu";
import Order from "./components/Order";
import Home from "./components/Home";
import Chatbot from "./components/Chatbot";
import Login from "./components/Login";
import Register from "./components/Register";
import RequireAuth from "./components/RequireAuth";
import RequireAdmin from "./components/RequireAdmin";
import ProfileDrawer from "./components/ProfileDrawer";
import AdminDashboard from "./components/AdminDashboard";
import CartToast from "./components/CartToast";
import { useAuth } from "./context/AuthContext";
import { useCart } from "./context/CartContext";
import { AnimatePresence, motion } from "framer-motion";
import { Coffee, User, LogOut, LayoutDashboard, ShoppingBag } from "lucide-react";

function Navbar() {
  const { user, logout } = useAuth();
  const { cartItems } = useCart();
  const [showProfile, setShowProfile] = useState(false);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const location = useLocation();

  const cartCount = cartItems.reduce((sum, i) => sum + i.quantity, 0);
  const isActive = (path) => location.pathname === path;

  return (
    <>
      <header className="fixed top-6 left-0 right-0 z-50 flex justify-center px-4 pointer-events-none">
        <motion.div 
          initial={{ y: -50, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
          className="glass-panel rounded-full px-6 py-3 flex items-center justify-between gap-8 pointer-events-auto shadow-[0_20px_40px_rgba(0,0,0,0.4)]"
        >
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#dfc18b] to-[#a37c35] flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
              <Coffee size={16} className="text-[#1a1714]" />
            </div>
            <span className="text-lg font-black tracking-tighter text-white group-hover:text-[#dfc18b] transition-colors">
              Merry's
            </span>
          </Link>

          {/* Center Nav */}
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium">
            <NavLink to="/menu" active={isActive("/menu")}>Menu</NavLink>
            {user && (
              <NavLink to="/order" active={isActive("/order")} badge={cartCount}>
                <span className="flex items-center gap-1.5"><ShoppingBag size={14} /> Order</span>
              </NavLink>
            )}
          </nav>

          {/* Right Actions */}
          <div className="flex items-center gap-3">
            {user ? (
              <>
                {user.is_admin && (
                  <Link
                    to="/admin"
                    className="flex items-center gap-1.5 text-xs font-bold text-[#1a1714] bg-gradient-to-r from-[#dfc18b] to-[#a37c35] px-3 py-1.5 rounded-full hover:shadow-[0_0_15px_rgba(223,193,139,0.4)] transition-all hover:scale-105"
                  >
                    <LayoutDashboard size={14} /> <span className="hidden sm:inline">Admin</span>
                  </Link>
                )}
                <button
                  onClick={() => setShowProfile(true)}
                  className="w-8 h-8 rounded-full bg-[#201d1a] border border-white/10 flex items-center justify-center text-white hover:bg-white/10 hover:border-white/20 hover:scale-105 transition-all text-xs font-bold shadow-md"
                  title={user.username || user.email}
                >
                  {(user.username || user.email)[0].toUpperCase()}
                </button>
                <button
                  onClick={() => setShowLogoutConfirm(true)}
                  className="text-[#a8a19c] hover:text-white transition-colors"
                >
                  <LogOut size={18} />
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="text-xs font-bold text-[#1a1714] bg-white hover:bg-gray-200 px-4 py-1.5 rounded-full transition-all hover:scale-105 shadow-lg"
              >
                Sign In
              </Link>
            )}
          </div>
        </motion.div>
      </header>

      {showProfile && user && (
        <ProfileDrawer user={user} onClose={() => setShowProfile(false)} />
      )}

      <AnimatePresence>
        {showLogoutConfirm && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-md"
            onClick={() => setShowLogoutConfirm(false)}
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.9, y: 20 }}
              className="glass-panel p-8 rounded-3xl max-w-sm w-full mx-4 border border-white/10 text-center"
              onClick={e => e.stopPropagation()}
            >
              <div className="w-16 h-16 rounded-full bg-[#201d1a] border border-white/5 mx-auto flex items-center justify-center text-[#dfc18b] mb-4">
                <LogOut size={24} />
              </div>
              <h3 className="text-xl font-bold text-white mb-2 tracking-tight">Signing Out?</h3>
              <p className="text-[#a8a19c] mb-8 text-sm leading-relaxed">
                You will need to log back in to access your bespoke orders and personalized chat history.
              </p>
              <div className="flex gap-3">
                <button 
                  onClick={() => setShowLogoutConfirm(false)}
                  className="flex-1 py-3 rounded-full text-white font-medium bg-white/5 hover:bg-white/10 border border-white/5 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  onClick={() => { setShowLogoutConfirm(false); logout(); }}
                  className="flex-1 py-3 rounded-full text-[#1a1714] font-bold bg-white hover:bg-gray-200 transition-colors"
                >
                  Confirm
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

function NavLink({ to, active, children, badge }) {
  return (
    <Link
      to={to}
      className={`relative py-1 transition-colors ${
        active ? "text-white" : "text-[#a8a19c] hover:text-[#dfc18b]"
      }`}
    >
      {children}
      {active && (
        <motion.div layoutId="nav-underline" className="absolute -bottom-1 left-0 right-0 h-0.5 bg-gradient-to-r from-[#dfc18b] to-[#a37c35] rounded-full" />
      )}
      {badge > 0 && (
        <span className="absolute -top-2 -right-3 w-[18px] h-[18px] bg-[#dfc18b] text-[#1a1714] text-[9px] font-bold rounded-full flex items-center justify-center shadow">
          {badge > 9 ? "9+" : badge}
        </span>
      )}
    </Link>
  );
}

function PageWrapper({ children }) {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 15, filter: "blur(8px)" }}
        animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        exit={{ opacity: 0, y: -15, filter: "blur(8px)" }}
        transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
        className="w-full pt-32 pb-24"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
}

function App() {
  return (
    <div className="min-h-screen text-white relative isolate">
      <div className="absolute top-[10%] left-[5%] w-[40vw] h-[40vw] bg-[#a37c35]/15 rounded-full mix-blend-screen filter blur-[120px] animate-pulse-glow -z-[1]" />
      <div className="absolute bottom-[10%] right-[5%] w-[30vw] h-[30vw] bg-[#dfc18b]/10 rounded-full mix-blend-screen filter blur-[100px] animate-pulse-glow -z-[1]" style={{ animationDelay: '2s' }} />

      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <PageWrapper>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/menu" element={<Menu />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/order" element={<RequireAuth><Order /></RequireAuth>} />
            <Route path="/admin" element={<RequireAdmin><AdminDashboard /></RequireAdmin>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </PageWrapper>
      </main>

      <CartToast />
      <Chatbot />
    </div>
  );
}

export default App;
