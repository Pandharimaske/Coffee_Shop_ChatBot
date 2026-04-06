import { useState, useEffect } from "react";
import { useCart } from "../context/CartContext";
import { useNavigate } from "react-router-dom";
import { ordersAPI } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";
import { ShoppingBag, Receipt, Minus, Plus, Trash2, Tag, ChevronRight } from "lucide-react";

const PLATFORM_FEE = 4;
const DISCOUNT_RATE = 0.1;
const PROMO_CODE = "SUMMER10";

function OrderHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    ordersAPI.getHistory()
      .then(setHistory)
      .catch(() => setHistory([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center py-32">
        <div className="w-10 h-10 border-2 border-[#dfc18b] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!history.length) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-32">
        <div className="w-20 h-20 bg-white/5 border border-white/10 rounded-3xl mx-auto flex items-center justify-center text-[#a8a19c] mb-6 shadow-xl">
          <Receipt size={32} />
        </div>
        <p className="text-xl font-bold text-white tracking-tight">No past orders</p>
        <p className="text-sm text-[#a8a19c] mt-2 max-w-sm mx-auto">When your coffee cravings run high, your documented indulgences will appear right here.</p>
      </motion.div>
    );
  }

  return (
    <motion.div layout className="space-y-6 max-w-3xl mx-auto pb-20">
      {history.map((order, index) => (
        <motion.div 
          initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }}
          key={order.id} 
          className="glass-card rounded-[2rem] overflow-hidden group"
        >
          <div className="flex items-center justify-between px-8 py-5 bg-white/5 border-b border-white/5 group-hover:bg-white/10 transition-colors">
            <div>
              <span className="text-[10px] text-[#dfc18b] font-bold uppercase tracking-[0.2em] block mb-1">Order Log</span>
              <p className="text-xs text-white uppercase font-bold tracking-wider">
                {new Date(order.updated_at).toLocaleDateString("en-IN", {
                  day: "numeric", month: "short", year: "numeric",
                  hour: "2-digit", minute: "2-digit",
                })}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-white font-black text-lg">₹{order.total.toFixed(2)}</span>
              <span className="bg-green-500/20 text-green-400 text-[10px] font-bold tracking-[0.1em] uppercase px-3 py-1.5 rounded-full border border-green-500/20 shadow-inner">
                Confirmed
              </span>
            </div>
          </div>

          <div className="px-8 py-5 space-y-4">
            {order.items.map((item, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-3">
                  <span className="w-6 h-6 bg-[#dfc18b]/10 border border-[#dfc18b]/30 text-[#dfc18b] text-[10px] font-black rounded-full flex items-center justify-center shrink-0">
                    {item.quantity}
                  </span>
                  <span className="text-white font-medium text-sm">{item.name}</span>
                </div>
                <span className="text-[#a8a19c] font-medium tracking-wide">₹{(item.per_unit_price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}

function ActiveOrder() {
  const { cartItems, removeFromCart, updateCartItem } = useCart();
  const [promoCode, setPromoCode] = useState("");
  const [originalTotal, setOriginalTotal] = useState(0);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [total, setTotal] = useState(0);
  const [discountApplied, setDiscountApplied] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const subtotal = cartItems.reduce((sum, item) => sum + item.price * item.quantity, 0);
    const discount = discountApplied ? subtotal * DISCOUNT_RATE : 0;
    setOriginalTotal(subtotal);
    setDiscountAmount(discount);
    setTotal(subtotal - discount + PLATFORM_FEE);
  }, [cartItems, discountApplied]);

  const handleQuantityChange = (item, newQuantity) => {
    if (newQuantity < 1) { removeFromCart(item.name); return; }
    updateCartItem(item, newQuantity);
  };

  const applyDiscount = () => {
    if (promoCode === PROMO_CODE && !discountApplied) setDiscountApplied(true);
    else if (discountApplied) alert("Promo code already applied");
    else alert("Invalid promo code");
  };

  if (!cartItems.length) {
    return (
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-32">
        <div className="w-24 h-24 bg-gradient-to-br from-[#dfc18b] to-[#a37c35] p-[1px] rounded-full mx-auto mb-6 shadow-[0_0_40px_rgba(223,193,139,0.3)]">
           <div className="w-full h-full bg-[#1a1714] rounded-full flex items-center justify-center text-[#dfc18b]">
             <ShoppingBag size={32} />
           </div>
        </div>
        <p className="text-2xl font-black text-white tracking-tight mb-2">Cart is pristine</p>
        <p className="text-sm text-[#a8a19c] max-w-sm mx-auto mb-8 leading-relaxed">It seems your bespoke order has not yet been assembled. Return to the menu to explore the collection.</p>
        <button
          onClick={() => navigate("/menu")}
          className="bg-white hover:scale-105 transition-all text-[#1a1714] font-black text-[11px] uppercase tracking-widest px-8 py-3.5 rounded-full shadow-[0_10px_20px_rgba(255,255,255,0.15)]"
        >
          Explore Collection
        </button>
      </motion.div>
    );
  }

  return (
    <div className="flex flex-col lg:flex-row justify-between gap-10 lg:gap-14 pb-20 mt-4">
      <div className="flex-1 space-y-6">
        <AnimatePresence>
          {cartItems.map((item, idx) => (
            <motion.div 
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              key={item.name} 
              className="flex items-center glass-card rounded-[2rem] p-4 sm:p-5 group"
            >
              <img
                src={item.image_url || `/images/${item.image_path}` || "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&q=80&w=400&h=400"}
                alt={item.name}
                className="w-24 h-24 sm:w-32 sm:h-32 object-cover rounded-[1.5rem] mr-5 sm:mr-8 shrink-0 mix-blend-luminosity hover:mix-blend-normal transition-all duration-700 border border-white/5"
                onError={(e) => { e.target.src = "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&q=80&w=400&h=400"; }}
              />
              <div className="flex-1 min-w-0 pr-4">
                <h3 className="text-lg sm:text-xl font-black text-white truncate mb-1">{item.name}</h3>
                <p className="text-xs font-bold text-[#dfc18b] tracking-wider uppercase opacity-80 mb-4">₹{item.price?.toFixed(2)} / ea</p>
                <div className="flex items-center gap-1.5 sm:gap-2">
                  <button onClick={() => handleQuantityChange(item, item.quantity - 1)} className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white flex items-center justify-center transition focus:outline-none">
                    <Minus size={14} />
                  </button>
                  <span className="w-8 text-center font-black text-white">{item.quantity}</span>
                  <button onClick={() => handleQuantityChange(item, item.quantity + 1)} className="w-8 h-8 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white flex items-center justify-center transition focus:outline-none">
                    <Plus size={14} />
                  </button>
                </div>
              </div>
              <div className="text-right shrink-0 flex flex-col items-end gap-6 border-l border-white/5 pl-4 sm:pl-6 my-2">
                <p className="text-xl sm:text-2xl font-black text-white leading-none">₹{(item.price * item.quantity).toFixed(2)}</p>
                <button onClick={() => removeFromCart(item.name)} className="w-8 h-8 rounded-full bg-red-500/10 hover:bg-red-500 hover:text-white border border-red-500/20 text-red-400 flex items-center justify-center transition-all focus:outline-none shrink-0" title="Remove">
                  <Trash2 size={14} />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div className="w-full lg:max-w-[400px] shrink-0">
        <div className="glass-panel p-8 rounded-[2.5rem] sticky top-32 border border-white/10 shadow-[0_30px_60px_rgba(0,0,0,0.5)]">
          <h4 className="text-xl font-black text-white mb-8 tracking-tight">Financial Summary</h4>

          <div className="space-y-4 text-sm font-medium">
            <div className="flex justify-between items-center text-[#a8a19c]">
              <span>Subtotal <span className="opacity-50">({cartItems.length} items)</span></span>
              <span className="text-white font-bold">₹{originalTotal.toFixed(2)}</span>
            </div>
            
            {discountAmount > 0 && (
              <div className="flex justify-between items-center text-green-400">
                <span className="flex items-center gap-1.5"><Tag size={12} /> Courtesy App</span>
                <span className="font-bold">−₹{discountAmount.toFixed(2)}</span>
              </div>
            )}
            
            <div className="flex justify-between items-center text-[#a8a19c]">
              <span>Preparation Levy</span>
              <span className="text-white font-bold">₹{PLATFORM_FEE.toFixed(2)}</span>
            </div>
          </div>

          <div className="h-px bg-gradient-to-r from-transparent via-white/10 to-transparent my-6" />

          <div className="flex justify-between items-end text-white">
            <span className="text-sm font-bold uppercase tracking-widest text-[#a8a19c]">Total Due</span>
            <span className="text-4xl font-black text-gradient-gold leading-none tracking-tighter">₹{total.toFixed(2)}</span>
          </div>

          <div className="mt-10 relative">
            <input
              type="text"
              value={promoCode}
              onChange={(e) => setPromoCode(e.target.value)}
              placeholder="Enter Access Code"
              className="w-full px-5 py-4 rounded-2xl bg-white/5 border border-white/10 text-white placeholder-[#a8a19c]/50 text-xs font-bold tracking-widest uppercase focus:outline-none focus:border-[#dfc18b]/50 focus:ring-1 focus:ring-[#dfc18b]/50 transition-all shadow-inner"
              disabled={discountApplied}
            />
            <button
              onClick={applyDiscount}
              disabled={discountApplied || !promoCode}
              className={`absolute right-2 top-2 bottom-2 px-4 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all ${
                discountApplied ? "bg-transparent text-green-400 border border-green-500/20" : "bg-white text-[#1a1714] hover:bg-gray-200"
              } disabled:opacity-50`}
            >
              {discountApplied ? "Applied" : "Apply"}
            </button>
          </div>

          <button 
            onClick={() => window.dispatchEvent(new Event("openChatbot"))}
            className="w-full mt-8 py-4 px-4 bg-gradient-to-r from-[#dfc18b] to-[#c29c5b] text-[#1a1714] font-black uppercase tracking-widest rounded-2xl hover:shadow-[0_0_30px_rgba(223,193,139,0.3)] transition-all hover:scale-[1.02] flex items-center justify-center gap-2"
          >
            Checkout with Assistant
          </button>
          <div className="mt-4 text-[10px] text-[#a8a19c] font-bold tracking-widest uppercase text-center relative max-w-[200px] mx-auto">
            Tell the assistant <br />
            <span className="text-white">"Confirm my order"</span>
          </div>

          <button onClick={() => navigate("/menu")} className="mt-6 w-full flex items-center justify-center gap-2 text-xs font-bold tracking-[0.15em] uppercase text-[#a8a19c] hover:text-white transition-colors py-2">
            Append further items <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}

const Order = () => {
  const [tab, setTab] = useState("active");

  return (
    <div className="max-w-6xl mx-auto space-y-10 mt-8">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 px-2">
         <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter">
           Your <span className="text-gradient-gold">Cart</span>
         </h1>
      </div>

      <div className="flex bg-white/5 p-1 rounded-2xl w-fit border border-white/10 shadow-lg">
        <button
          onClick={() => setTab("active")}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold tracking-[0.1em] uppercase transition-all ${
            tab === "active" ? "bg-white text-[#1a1714] shadow-md" : "text-[#a8a19c] hover:text-white"
          }`}
        >
          <ShoppingBag size={14} /> Current
        </button>
        <button
          onClick={() => setTab("history")}
          className={`flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-bold tracking-[0.1em] uppercase transition-all ${
            tab === "history" ? "bg-white text-[#1a1714] shadow-md" : "text-[#a8a19c] hover:text-white"
          }`}
        >
          <Receipt size={14} /> Log
        </button>
      </div>

      <AnimatePresence mode="wait">
        <motion.div key={tab} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} transition={{ duration: 0.3 }}>
           {tab === "active" ? <ActiveOrder /> : <OrderHistory />}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default Order;
