import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CreditCard, Lock, CheckCircle2, X } from "lucide-react";

export const CheckoutModal = ({ isOpen, onClose, total, onComplete }) => {
  const [processing, setProcessing] = useState(false);
  const [success, setSuccess] = useState(false);
  const [cardNumber, setCardNumber] = useState("");
  const [expiry, setExpiry] = useState("");
  const [cvv, setCvv] = useState("");

  useEffect(() => {
    if (isOpen) {
      setProcessing(false);
      setSuccess(false);
      setCardNumber("");
      setExpiry("");
      setCvv("");
    }
  }, [isOpen]);

  const handleFormatCard = (e) => {
    let val = e.target.value.replace(/\D/g, "");
    if (val.length > 16) val = val.substring(0, 16);
    let formatted = val.match(/.{1,4}/g)?.join(" ") || val;
    setCardNumber(formatted);
  };

  const handleFormatExpiry = (e) => {
    let val = e.target.value.replace(/\D/g, "");
    if (val.length > 4) val = val.substring(0, 4);
    if (val.length > 2) {
      val = `${val.substring(0, 2)}/${val.substring(2, 4)}`;
    }
    setExpiry(val);
  };

  const handleFormatCvv = (e) => {
    let val = e.target.value.replace(/\D/g, "");
    if (val.length > 3) val = val.substring(0, 3);
    setCvv(val);
  };

  const handlePay = (e) => {
    e.preventDefault();
    setProcessing(true);
    
    // Simulate 2 second network processing time
    setTimeout(() => {
      setProcessing(false);
      setSuccess(true);
      
      // Notify parent after visual success
      setTimeout(() => {
        onComplete("payment_success");
      }, 1000);
    }, 2000);
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[200] bg-black/70 backdrop-blur-xl flex items-center justify-center p-4 overflow-hidden"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          className="relative w-full max-w-sm bg-[#1a1714] border border-white/10 rounded-[2rem] shadow-2xl overflow-hidden p-6"
          onClick={(e) => e.stopPropagation()}
        >
          {/* Close button */}
          {!processing && !success && (
            <button 
              onClick={onClose}
              className="absolute top-4 right-4 text-white/50 hover:text-white transition-colors"
            >
              <X size={20} />
            </button>
          )}

          {/* Success State */}
          {success ? (
            <motion.div 
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              className="flex flex-col items-center justify-center py-12"
            >
              <CheckCircle2 size={64} className="text-[#dfc18b] mb-4 drop-shadow-[0_0_15px_rgba(223,193,139,0.5)]" />
              <h2 className="text-xl font-black text-white tracking-widest uppercase">Payment Successful</h2>
              <p className="text-[#a8a19c] text-sm mt-2 font-medium">Redirecting to order confirmation...</p>
            </motion.div>
          ) : (
            <>
              {/* Header */}
              <div className="mb-8">
                <p className="text-[#dfc18b] text-[10px] font-bold uppercase tracking-widest mb-1">Secure Checkout</p>
                <div className="flex items-end justify-between">
                  <h2 className="text-2xl font-black text-white">Total Due</h2>
                  <span className="text-2xl font-bold text-white">₹{total.toFixed(2)}</span>
                </div>
              </div>

              {/* Form */}
              <form onSubmit={handlePay} className="space-y-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Card details</label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <CreditCard size={18} className="text-[#a8a19c]" />
                    </div>
                    <input
                      required
                      type="text"
                      placeholder="0000 0000 0000 0000"
                      value={cardNumber}
                      onChange={handleFormatCard}
                      disabled={processing}
                      className="block w-full pl-10 pr-3 py-3 border border-white/10 rounded-xl bg-white/5 text-white placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-[#dfc18b] focus:border-transparent transition-all sm:text-sm tracking-widest font-mono"
                    />
                  </div>
                </div>

                <div className="flex gap-4">
                  <div className="space-y-1 flex-1">
                    <label className="text-[10px] font-bold text-white/40 uppercase tracking-widest">Expiry</label>
                    <input
                      required
                      type="text"
                      placeholder="MM/YY"
                      value={expiry}
                      onChange={handleFormatExpiry}
                      disabled={processing}
                      className="block w-full px-3 py-3 border border-white/10 rounded-xl bg-white/5 text-white placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-[#dfc18b] focus:border-transparent transition-all sm:text-sm text-center font-mono"
                    />
                  </div>
                  <div className="space-y-1 flex-1">
                    <label className="text-[10px] font-bold text-white/40 uppercase tracking-widest">CVV</label>
                    <input
                      required
                      type="text"
                      placeholder="123"
                      value={cvv}
                      onChange={handleFormatCvv}
                      disabled={processing}
                      className="block w-full px-3 py-3 border border-white/10 rounded-xl bg-white/5 text-white placeholder-white/20 focus:outline-none focus:ring-1 focus:ring-[#dfc18b] focus:border-transparent transition-all sm:text-sm text-center font-mono"
                    />
                  </div>
                </div>

                <div className="pt-4">
                  <button
                    type="submit"
                    disabled={processing || cardNumber.length < 19 || expiry.length < 5 || cvv.length < 3}
                    className="w-full py-4 px-4 bg-gradient-to-r from-[#dfc18b] to-[#c29c5b] text-[#1a1714] font-bold rounded-xl flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:grayscale hover:shadow-[0_0_20px_rgba(223,193,139,0.3)]"
                  >
                    {processing ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ repeat: Infinity, ease: "linear", duration: 1 }}
                        className="w-5 h-5 border-2 border-[#1a1714]/30 border-t-[#1a1714] rounded-full"
                      />
                    ) : (
                      <>
                        <Lock size={16} />
                        Pay ₹{total.toFixed(2)}
                      </>
                    )}
                  </button>
                </div>
              </form>
            </>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};
