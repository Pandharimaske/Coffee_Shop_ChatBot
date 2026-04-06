import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingBag, Plus, Minus, Trash2, ArrowRight } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useNavigate, useLocation } from "react-router-dom";

export default function FloatingCart() {
  const { user } = useAuth();
  const { cartItems, updateCartItem, removeFromCart } = useCart();
  const [expanded, setExpanded] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  // Don't show on order page or when not logged in
  if (!user || !cartItems.length || location.pathname === "/order") return null;

  const totalItems = cartItems.reduce((s, i) => s + i.quantity, 0);
  const totalPrice = cartItems.reduce((s, i) => s + i.price * i.quantity, 0);

  const handleQty = (item, delta) => {
    const next = item.quantity + delta;
    if (next <= 0) removeFromCart(item.name);
    else updateCartItem(item, next);
  };

  return (
    <motion.div
      className="fixed bottom-28 left-6 z-50"
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 300, damping: 30, delay: 0.3 }}
    >
      <AnimatePresence mode="wait">
        {expanded ? (
          <motion.div
            key="expanded"
            initial={{ opacity: 0, scale: 0.85, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.85, y: 20 }}
            transition={{ type: "spring", stiffness: 400, damping: 35 }}
            className="w-72 rounded-3xl overflow-hidden shadow-[0_30px_80px_rgba(0,0,0,0.5)] border border-white/10 bg-[#1a1714]/95 backdrop-blur-2xl"
          >
            {/* Header */}
            <div
              className="flex items-center justify-between px-4 py-3.5 border-b border-white/5 cursor-pointer hover:bg-white/5 transition-colors"
              onClick={() => setExpanded(false)}
            >
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#dfc18b] to-[#a37c35] flex items-center justify-center">
                  <ShoppingBag size={13} className="text-[#1a1714]" />
                </div>
                <span className="text-white text-sm font-bold tracking-wide">Your Cart</span>
                <span className="bg-[#dfc18b] text-[#1a1714] text-[10px] font-black px-2 py-0.5 rounded-full">
                  {totalItems}
                </span>
              </div>
              <span className="text-[#a8a19c] text-xs">↙ collapse</span>
            </div>

            {/* Items */}
            <div className="max-h-52 overflow-y-auto px-3 py-2 space-y-1.5 scrollbar-thin">
              {cartItems.map((item, i) => (
                <motion.div
                  key={item.name}
                  layout
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="flex items-center gap-2 py-1.5 px-2 rounded-xl hover:bg-white/5 transition-colors group"
                >
                  {/* Item name */}
                  <span className="flex-1 text-white text-xs truncate">{item.name}</span>

                  {/* Qty controls */}
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleQty(item, -1)}
                      className="w-5 h-5 rounded-full bg-white/10 hover:bg-red-500/40 text-white flex items-center justify-center transition-colors"
                    >
                      {item.quantity === 1 ? <Trash2 size={8} /> : <Minus size={8} />}
                    </button>
                    <span className="w-5 text-center text-xs font-bold text-white">{item.quantity}</span>
                    <button
                      onClick={() => handleQty(item, 1)}
                      className="w-5 h-5 rounded-full bg-white/10 hover:bg-[#dfc18b]/40 text-white flex items-center justify-center transition-colors"
                    >
                      <Plus size={8} />
                    </button>
                  </div>

                  {/* Line total */}
                  <span className="text-[#a8a19c] text-xs w-12 text-right shrink-0">
                    ₹{(item.price * item.quantity).toFixed(0)}
                  </span>
                </motion.div>
              ))}
            </div>

            {/* Footer */}
            <div className="px-4 pt-2 pb-4 border-t border-white/5">
              <div className="flex justify-between items-center mb-3">
                <span className="text-[#a8a19c] text-xs">Order Total</span>
                <span className="text-white text-sm font-bold">₹{totalPrice.toFixed(0)}</span>
              </div>
              <button
                onClick={() => { setExpanded(false); navigate("/order"); }}
                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-[#dfc18b] to-[#a37c35] hover:from-[#c29c5b] hover:to-[#8a5c1a] text-[#1a1714] font-bold text-sm py-2.5 rounded-full transition-all hover:scale-[1.02] shadow-lg"
              >
                View & Confirm <ArrowRight size={14} />
              </button>
            </div>
          </motion.div>
        ) : (
          /* Collapsed Pill */
          <motion.button
            key="pill"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
            onClick={() => setExpanded(true)}
            className="relative group flex items-center gap-2.5 bg-[#1a1714]/90 backdrop-blur-xl border border-white/10 hover:border-[#dfc18b]/40 rounded-full px-4 py-2.5 shadow-[0_10px_40px_rgba(0,0,0,0.4)] hover:shadow-[0_10px_40px_rgba(223,193,139,0.15)] transition-all hover:scale-105"
          >
            {/* Animated glow ring on hover */}
            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-[#dfc18b]/0 to-[#a37c35]/0 group-hover:from-[#dfc18b]/10 group-hover:to-[#a37c35]/10 transition-all duration-500" />

            <div className="relative w-7 h-7 rounded-full bg-gradient-to-br from-[#dfc18b] to-[#a37c35] flex items-center justify-center shadow-md">
              <ShoppingBag size={13} className="text-[#1a1714]" />
              {/* bounce badge */}
              <span className="absolute -top-1.5 -right-1.5 w-4 h-4 bg-orange-500 text-white text-[9px] font-black rounded-full flex items-center justify-center animate-bounce" style={{ animationDuration: "2.5s" }}>
                {totalItems > 9 ? "9+" : totalItems}
              </span>
            </div>

            <div className="relative flex flex-col items-start leading-none">
              <span className="text-[11px] text-[#a8a19c] font-medium">Your cart</span>
              <span className="text-sm text-white font-black tracking-tight">₹{totalPrice.toFixed(0)}</span>
            </div>
          </motion.button>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
