import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { motion } from "framer-motion";
import { LogIn, CheckCircle2 } from "lucide-react";

const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || "/";

  const justRegistered = location.state?.registered === true;

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || "Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95, filter: "blur(10px)" }}
        animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="glass-panel p-10 w-full max-w-md relative overflow-hidden rounded-[2.5rem]"
      >
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#dfc18b]/10 rounded-full blur-[80px] pointer-events-none -mr-10 -mt-10" />

        <div className="relative z-10 w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-[#dfc18b] mb-6 shadow-xl">
          <LogIn size={28} />
        </div>

        <h2 className="text-3xl font-black text-white tracking-tight mb-2">Welcome Back</h2>
        <p className="text-[#a8a19c] font-medium text-sm tracking-wide mb-8">Sign in to your elite experience</p>

        {justRegistered && (
          <div className="flex items-center gap-3 bg-green-500/10 border border-green-500/20 text-green-400 rounded-2xl px-4 py-4 mb-6 text-sm backdrop-blur-md">
            <CheckCircle2 size={20} className="shrink-0" />
            <span className="font-medium">Account verified. You may now sign in.</span>
          </div>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-2xl px-4 py-4 mb-6 text-sm font-medium backdrop-blur-md">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5 relative z-10">
          <div className="space-y-2">
            <label className="block text-xs font-bold text-[#a8a19c] uppercase tracking-widest pl-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-5 py-4 rounded-2xl border border-white/10 bg-white/5 text-white placeholder-[#a8a19c]/50 focus:outline-none focus:border-[#dfc18b]/50 focus:ring-1 focus:ring-[#dfc18b]/50 transition-all shadow-inner"
              placeholder="you@example.com"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold text-[#a8a19c] uppercase tracking-widest pl-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-5 py-4 rounded-2xl border border-white/10 bg-white/5 text-white placeholder-[#a8a19c]/50 focus:outline-none focus:border-[#dfc18b]/50 focus:ring-1 focus:ring-[#dfc18b]/50 transition-all shadow-inner"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-gradient-to-r from-[#dfc18b] to-[#a37c35] text-[#1a1714] py-4 rounded-2xl font-black text-sm tracking-widest uppercase hover:scale-[1.02] shadow-[0_10px_30px_rgba(223,193,139,0.2)] transition-all disabled:opacity-60 disabled:hover:scale-100 mt-4"
          >
            {loading ? "Authenticating..." : "Sign In"}
          </button>
        </form>

        <p className="mt-8 text-center text-sm font-medium text-[#a8a19c] relative z-10">
          Don't have an account?{" "}
          <Link to="/register" className="text-[#dfc18b] font-bold hover:text-white transition-colors">
            Request Access
          </Link>
        </p>
      </motion.div>
    </div>
  );
};

export default Login;
