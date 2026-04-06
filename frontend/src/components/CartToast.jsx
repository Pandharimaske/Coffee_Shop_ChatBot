import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingBag, ArrowRight, X } from "lucide-react";
import { useCart } from "../context/CartContext";
import { useAuth } from "../context/AuthContext";
import { useNavigate, useLocation } from "react-router-dom";

export default function CartToast() {
  const { user } = useAuth();
  const { cartItems } = useCart();
  const navigate = useNavigate();
  const location = useLocation();

  const [toast, setToast] = useState(null); // { label, total, items }
  const [visible, setVisible] = useState(false);
  const prevCountRef = useRef(0);
  const prevItemsRef = useRef([]);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!user) return;

    const prevCount = prevCountRef.current;
    const prevItems = prevItemsRef.current;
    const currCount = cartItems.reduce((s, i) => s + i.quantity, 0);
    const currTotal = cartItems.reduce((s, i) => s + i.price * i.quantity, 0);

    // Detect what changed
    if (currCount !== prevCount) {
      let label = "";

      if (cartItems.length === 0) {
        label = "🗑 Cart cleared";
      } else {
        // Find the item that changed
        const changed = cartItems.find((item) => {
          const prev = prevItems.find((p) => p.name === item.name);
          return !prev || prev.quantity !== item.quantity;
        });
        const added = cartItems.find(
          (item) => !prevItems.find((p) => p.name === item.name)
        );
        const target = added || changed;
        const prevQty = target
          ? (prevItems.find((p) => p.name === target?.name)?.quantity ?? 0)
          : 0;
        const delta = target ? target.quantity - prevQty : currCount - prevCount;

        if (target) {
          if (delta > 0) label = `+${delta} ${target.name} added`;
          else if (delta < 0 && target.quantity > 0) label = `${target.name} updated`;
          else if (delta < 0) label = `${target.name} removed`;
          else label = "Cart updated";
        } else {
          label = "Cart updated";
        }
      }

      // Don't show on /order page — user is already looking at the cart
      if (location.pathname !== "/order") {
        setToast({ label, total: currTotal, count: currCount });
        setVisible(true);

        // Auto-dismiss after 4s
        if (timerRef.current) clearTimeout(timerRef.current);
        timerRef.current = setTimeout(() => setVisible(false), 4000);
      }
    }

    prevCountRef.current = currCount;
    prevItemsRef.current = [...cartItems];
  }, [cartItems]);

  const dismiss = () => {
    setVisible(false);
    if (timerRef.current) clearTimeout(timerRef.current);
  };

  if (!user || !toast) return null;

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          key="cart-toast"
          initial={{ y: 100, opacity: 0, scale: 0.92 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          exit={{ y: 80, opacity: 0, scale: 0.95 }}
          transition={{ type: "spring", stiffness: 380, damping: 30 }}
          className="fixed bottom-24 right-4 sm:right-6 z-[90] max-w-xs w-full"
        >
          <div className="relative bg-[#1a1714]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-[0_20px_60px_rgba(0,0,0,0.5)] overflow-hidden">
            {/* Gold progress bar — depletes over 4s */}
            <motion.div
              className="absolute top-0 left-0 h-[2px] bg-gradient-to-r from-[#dfc18b] to-[#a37c35]"
              initial={{ width: "100%" }}
              animate={{ width: "0%" }}
              transition={{ duration: 4, ease: "linear" }}
            />

            <div className="flex items-center gap-3 px-4 py-3.5">
              {/* Icon */}
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#dfc18b] to-[#a37c35] flex items-center justify-center shadow-md shrink-0">
                <ShoppingBag size={16} className="text-[#1a1714]" />
              </div>

              {/* Text */}
              <div className="flex-1 min-w-0">
                <p className="text-white text-sm font-semibold truncate">{toast.label}</p>
                {toast.count > 0 && (
                  <p className="text-[#a8a19c] text-xs mt-0.5">
                    {toast.count} item{toast.count !== 1 ? "s" : ""} · ₹{toast.total.toFixed(0)} total
                  </p>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 shrink-0">
                {toast.count > 0 && (
                  <button
                    onClick={() => { dismiss(); navigate("/order"); }}
                    className="flex items-center gap-1 text-[#dfc18b] text-xs font-bold hover:text-white transition-colors"
                  >
                    View <ArrowRight size={12} />
                  </button>
                )}
                <button
                  onClick={dismiss}
                  className="ml-1 w-6 h-6 rounded-full flex items-center justify-center text-[#a8a19c] hover:text-white hover:bg-white/10 transition-all"
                >
                  <X size={12} />
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
