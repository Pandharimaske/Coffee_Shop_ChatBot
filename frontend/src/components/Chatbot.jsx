import { useEffect, useState, useRef } from "react";
import { Send as FaPaperPlane, Bot as FaRobot, X as FaTimes } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { chatAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useNavigate } from "react-router-dom";
import { CheckoutModal } from "./CheckoutModal";

const Spinner = () => (
  <div className="w-5 h-5 border-2 border-t-transparent border-white rounded-full animate-spin" />
);

const formatTime = (timestamp) =>
  new Date(timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

// ── Markdown renderer ─────────────────────────────────────────────────────────
function BotMarkdown({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        p: ({ children }) => <p className="leading-relaxed mb-1.5 last:mb-0">{children}</p>,
        strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
        em: ({ children }) => <em className="italic opacity-90">{children}</em>,
        ul: ({ children }) => <ul className="mt-0.5 mb-1.5 space-y-0.5">{children}</ul>,
        ol: ({ children }) => <ol className="mt-0.5 mb-1.5 space-y-0.5 pl-1 list-decimal list-inside">{children}</ol>,
        li: ({ children }) => (
          <li className="flex gap-1.5 items-start leading-snug">
            <span className="shrink-0 text-[#dfc18b] mt-px">•</span>
            <span>{children}</span>
          </li>
        ),
        hr: () => <hr className="my-2 border-white/10 opacity-50" />,
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer"
            className="underline text-[#dfc18b] hover:text-white transition-colors break-all">
            {children}
          </a>
        ),
        code: ({ children }) => (
          <code className="bg-white/10 text-[#dfc18b] px-1.5 py-0.5 rounded text-xs font-mono">{children}</code>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-[#dfc18b] pl-2 my-1 italic opacity-80">{children}</blockquote>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

// ── Live Order Panel ──────────────────────────────────────────────────────────

// ── Interactive Interrupt Bubble ──────────────────────────────────────────────

function InterruptBubble({ payload, onResolve }) {
  if (payload.resolved) {
    return (
      <div className="text-sm opacity-60 italic">
        {payload.resolvedStatus === "approve" ? "✅ Action approved." : "❌ Action rejected."}
      </div>
    );
  }

  const isMemory = payload.action === "memory_validation";
  
  // Format extraction details for better UX
  const renderDetails = () => {
    if (!isMemory || !payload.details) return null;
    const { add_or_update, remove, replace } = payload.details;
    
    const items = [];
    if (add_or_update) {
      Object.entries(add_or_update).forEach(([key, val]) => {
        items.push(<div key={key}>Save <span className="text-white font-bold">{Array.isArray(val) ? val.join(", ") : val}</span> to <span className="opacity-70 italic">{key}</span>?</div>);
      });
    }
    if (remove) {
      Object.entries(remove).forEach(([key, val]) => {
        items.push(<div key={key}>Remove <span className="text-white font-bold">{Array.isArray(val) ? val.join(", ") : val}</span> from <span className="opacity-70 italic">{key}</span>?</div>);
      });
    }
    if (replace) {
      Object.entries(replace).forEach(([key, val]) => {
        items.push(<div key={key}>Update <span className="opacity-70 italic">{key}</span> to <span className="text-white font-bold">{val}</span>?</div>);
      });
    }
    return <div className="mt-2 space-y-1 text-xs border-l-2 border-[#dfc18b]/30 pl-2 py-1 bg-white/5 rounded-r-md">{items}</div>;
  };

  return (
    <div className="text-sm p-1">
      <p className="mb-2 font-semibold text-[#dfc18b]">
        {isMemory ? "Health & Preference Update" : "Order Confirmation"}
      </p>
      <div className="mb-4 opacity-90 leading-relaxed text-sm">
        {isMemory 
          ? (
            <>
              I noticed you mentioned a preference. Would you like me to securely save this to your profile?
              {renderDetails()}
            </>
          )
          : `Are you sure you want to finalize your order for ₹${payload.total}?`}
      </div>
      
      <div className="flex gap-2">
        <button 
          onClick={() => onResolve("approve")}
          className="flex-1 bg-gradient-to-r from-[#dfc18b] to-[#a37c35] hover:opacity-90 text-[#1a1714] font-bold py-1.5 px-3 rounded-lg transition-transform hover:scale-105 shadow-md flex items-center justify-center gap-1.5"
        >
          {isMemory ? "Save Securely" : "Yes, Checkout"}
        </button>
        <button 
          onClick={() => onResolve("reject")}
          className="flex-1 bg-white/10 hover:bg-white/20 text-white font-medium py-1.5 px-3 rounded-lg transition-colors border border-white/10 flex items-center justify-center"
        >
          {isMemory ? "No, Ignore" : "Wait, Modify"}
        </button>
      </div>
    </div>
  );
}

// ── Helpers ───────────────────────────────────────────────────────────────────
const STATUS_MAP = {
  guard: "Checking your request",
  memory: "Reviewing preferences",
  intent_refiner: "Understanding your intent",
  router: "Routing your request",
  details_management_agent: "Looking up details",
  order_management_agent: "Processing your order",
  recommendation_management_agent: "Finding recommendations",
  general_agent: "Drafting response",
};

// ── Main Chatbot component ────────────────────────────────────────────────────
const Chatbot = () => {
  const { user } = useAuth();
  const { cartItems, updateCartItem, removeFromCart, refreshCart } = useCart();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [botStatus, setBotStatus] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [checkoutPayload, setCheckoutPayload] = useState(null);
  const inputRef = useRef(null);
  const textRef = useRef("");
  const bottomRef = useRef(null);

  // True when there's an unresolved interrupt bubble in the chat
  const isInterruptPending = messages.some(
    (m) => m.type === "interrupt" && !m.content?.resolved
  );

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Global event listener to open chatbot
  useEffect(() => {
    const handleOpen = () => setIsOpen(true);
    window.addEventListener("openChatbot", handleOpen);
    return () => window.removeEventListener("openChatbot", handleOpen);
  }, []);

  // Load message history on mount
  useEffect(() => {
    if (!user) return;
    chatAPI.getHistory()
      .then((history) => {
        if (history.length > 0) {
          setMessages(history.map((m) => ({
            role: m.role === "user" ? "user" : "bot",
            content: m.content,
            timestamp: new Date(),
          })));
        } else {
          setMessages([{
            role: "bot",
            content: `Hey ${user.username || user.email.split("@")[0]}! Welcome to Merry's Way ☕ What can I get you today?`,
            timestamp: new Date(),
          }]);
        }
      })
      .catch(() => {
        setMessages([{
          role: "bot",
          content: "Welcome to Merry's Way ☕ What can I get you today?",
          timestamp: new Date(),
        }]);
      });
  }, [user]);

  const handleSend = async () => {
    const message = textRef.current.trim();
    if (!message || isTyping) return;

    textRef.current = "";
    if (inputRef.current) inputRef.current.value = "";

    setMessages((prev) => [...prev, { role: "user", content: message, timestamp: new Date() }]);
    setIsTyping(true);

    try {
      const stream = await chatAPI.sendStream(message);
      const reader = stream.getReader();
      const decoder = new TextDecoder("utf-8");

      let done = false;
      let buffer = "";
      let firstTokenReceived = false;

      while (!done) {
        const { value, done: readerDone } = await reader.read();
        done = readerDone;

        if (value) {
          buffer += decoder.decode(value, { stream: true });
          
          let parts = buffer.split("\n\n");
          buffer = parts.pop();

          for (const part of parts) {
            if (part.startsWith("data: ")) {
              const dataStr = part.slice(6);
              try {
                const data = JSON.parse(dataStr);

                if (data.type === "status") {
                  if (!firstTokenReceived) {
                    const friendlyMessage = STATUS_MAP[data.node] || "Thinking";
                    setBotStatus(friendlyMessage);
                  }
                } else if (data.type === "token") {
                  if (!firstTokenReceived) {
                    firstTokenReceived = true;
                    setBotStatus("");
                    setIsTyping(false);
                    setMessages((prev) => [...prev, {
                      role: "bot",
                      content: data.content,
                      timestamp: new Date(),
                    }]);
                  } else {
                    setMessages((prev) => {
                      const newMessages = [...prev];
                      const lastMsgIndex = newMessages.length - 1;
                      const lastMsg = newMessages[lastMsgIndex];
                      newMessages[lastMsgIndex] = { ...lastMsg, content: lastMsg.content + data.content };
                      return newMessages;
                    });
                  }
                } else if (data.type === "interrupt") {
                  if (data.payload?.action === "order_confirmation" || data.payload?.action === "memory_validation") {
                    setIsTyping(false);
                    setBotStatus("");
                    setMessages((prev) => [...prev, {
                      role: "bot",
                      type: "interrupt",
                      content: data.payload,
                      timestamp: new Date(),
                    }]);
                  }
                }
              } catch (e) {
                // Ignore parsing errors for partial/corrupt chunks
              }
            }
          }
        }
      }
      await refreshCart();
    } catch {
      setMessages((prev) => [...prev, {
        role: "bot",
        content: "⚠️ Something went wrong. Please try again.",
        timestamp: new Date(),
      }]);
    } finally {
      setIsTyping(false);
      setBotStatus("");
    }
  };

  const handleResolveInterrupt = async (index, payload, status) => {
    const userLabel = status === "approve" 
      ? (payload.action === "memory_validation" ? "Yes, please save that." : "Yes, let's checkout.") 
      : "No, cancel that.";

    // 1. Mark message as resolved
    setMessages(prev => {
       const next = [...prev];
       next[index] = { ...next[index], content: { ...payload, resolved: true, resolvedStatus: status } };
       
       // 2. Add implicit user reply
       next.push({
           role: "user",
           content: userLabel,
           timestamp: new Date()
       });
       return next;
    });

    if (payload.action === "order_confirmation" && status === "approve") {
        setTimeout(() => {
           setMessages(prev => [...prev, {
              role: "bot",
              content: "Thank you for the order! Bringing up the secure checkout now...",
              timestamp: new Date()
           }]);
           setTimeout(() => {
               setCheckoutPayload(payload);
           }, 1500);
        }, 500);
        return;
    }

    setIsTyping(true);
    setBotStatus("Processing...");
    try {
        const data = await chatAPI.resumeChat(status, userLabel);
        setMessages(prev => [...prev, { role: "bot", content: data.response, timestamp: new Date() }]);
    } catch {
        setMessages(prev => [...prev, { role: "bot", content: "⚠️ Failed to process action.", timestamp: new Date() }]);
    } finally {
        setIsTyping(false);
        setBotStatus("");
        await refreshCart();
    }
  };

  const handleResumePayment = async (status) => {
    setCheckoutPayload(null);
    const userLabel = status === 'approve' ? 'Payment authorized.' : 'Payment canceled.';

    setIsTyping(true);
    setBotStatus("Confirming order...");
    try {
      const data = await chatAPI.resumeChat(status, userLabel);
      setMessages((prev) => [...prev, {
        role: "bot",
        content: data.response,
        timestamp: new Date(),
      }]);
    } catch (err) {
      setMessages((prev) => [...prev, {
        role: "bot",
        content: "⚠️ Payment confirmation failed. Please try again.",
        timestamp: new Date(),
      }]);
    } finally {
      setIsTyping(false);
      setBotStatus("");
      await refreshCart();
    }
  };

  const handleQtyChange = (item, newQty) => {
    if (newQty <= 0) removeFromCart(item.name);
    else updateCartItem(item, newQty);
  };

  if (!user) return null;

  const totalCartQty = cartItems.reduce((s, i) => s + i.quantity, 0);

  return (
    <>
      {/* Cute Mascot Floating Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 sm:right-10 z-[100] flex flex-col items-center group focus:outline-none"
        >
          {/* Floating Speech Bubble */}
          <div className="bg-white text-[#1a1714] text-xs font-bold px-4 py-2.5 rounded-2xl rounded-br-none shadow-xl border border-[#dfc18b]/30 mb-2 transform origin-bottom group-hover:-translate-y-2 group-hover:scale-105 transition-all duration-300 animate-bounce" style={{ animationDuration: '4s' }}>
            Can I help? ✨
          </div>

          {/* The Cup Character */}
          <div className="relative transform group-hover:scale-105 transition-transform duration-300 origin-bottom">
            
            {/* Steam Animation */}
            <div className="absolute -top-8 left-4 w-1.5 h-6 bg-white/60 blur-sm rounded-full animate-pulse-soft opacity-0 group-hover:opacity-100 transition-opacity" style={{ animationDuration: '2s' }}></div>
            <div className="absolute -top-10 left-8 w-1.5 h-8 bg-white/60 blur-sm rounded-full animate-pulse-soft opacity-0 group-hover:opacity-100 transition-opacity" style={{ animationDuration: '2s', animationDelay: '0.5s' }}></div>

            {/* Lid */}
            <div className="absolute -top-3 -left-1 w-[72px] h-5 bg-[#1a1714] border-4 border-[#3a2d27] rounded-t-xl shadow-sm z-10 group-hover:-translate-y-1 transition-transform duration-300"></div>
            
            {/* Cup Body */}
            <div className="w-16 h-20 bg-[#1a1714] border-x-4 border-[#3a2d27] rounded-b-sm relative shadow-[0_10px_20px_rgba(0,0,0,0.2)] overflow-hidden transition-colors">
               
               {/* Coffee Sleeve */}
               <div className="absolute top-4 w-full h-11 bg-gradient-to-r from-[#dfc18b] to-[#a37c35] border-y-4 border-[#3a2d27] flex flex-col items-center justify-center group-hover:from-[#a37b2c] group-hover:to-[#7a5c44] transition-all">
                  
                  {/* Cute Face */}
                  <div className="flex gap-2.5 items-center mt-0.5">
                     {/* Left Eye */}
                     <div className="w-2.5 h-2.5 bg-[#1a1714] rounded-full relative overflow-hidden">
                        <div className="absolute top-0.5 left-0.5 w-[3px] h-[3px] bg-white rounded-full"></div>
                     </div>
                     
                     {/* Right Eye */}
                     <div className="w-2.5 h-2.5 bg-[#1a1714] rounded-full relative group-hover:scale-y-0 transition-transform duration-150">
                        {/* Wink effect */}
                        <div className="absolute top-0.5 left-0.5 w-[3px] h-[3px] bg-white rounded-full"></div>
                     </div>
                  </div>
                  
                  {/* Little Mouth */}
                  <div className="w-2.5 h-2 border-b-2 border-r-2 border-[#3a2d27] rounded-br-full transform rotate-45 mt-0.5 group-hover:scale-125 transition-transform"></div>
               </div>
               
               {/* Bottom shadow curve */}
               <div className="absolute bottom-0 w-full h-3 bg-[#dfc18b]"></div>
            </div>
            
            {/* Cart Badge */}
            {totalCartQty > 0 && (
              <span className="absolute -top-4 -right-3 w-6 h-6 bg-red-500 text-white text-[11px] font-extrabold rounded-full flex items-center justify-center shadow-lg border-2 border-white animate-bounce" style={{ animationDuration: '2s' }}>
                {totalCartQty > 9 ? "9+" : totalCartQty}
              </span>
            )}
          </div>
        </button>
      )}

      {/* Chat window — wider + taller */}
      <div className={`fixed bottom-0 inset-x-2 sm:right-6 sm:inset-x-auto w-full sm:w-[440px] h-[85vh] sm:h-[650px] bg-[#1a1714]/95 backdrop-blur-3xl shadow-2xl rounded-t-3xl transform ${
        isOpen ? "translate-y-0 opacity-100" : "translate-y-full opacity-0"
      } transition-all duration-500 ease-[cubic-bezier(0.2,0.8,0.2,1)] z-40 flex flex-col border border-white/40 ring-1 ring-[#dfc18b]/20`}>

        {/* Header */}
        <div className="flex justify-between items-center px-6 py-5 bg-[#1a1714] border-b border-white/5 text-white rounded-t-3xl shrink-0 shadow-md relative overflow-hidden">
          {/* subtle decorative background element inside header */}
          <div className="absolute -right-10 -top-10 w-32 h-32 bg-[#dfc18b] rounded-full blur-3xl opacity-20 pointer-events-none"></div>
          
          <div className="relative z-10 flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-full flex items-center justify-center backdrop-blur-md border border-white/20">
              <FaRobot size={20} className="text-[#dfc18b]" />
            </div>
            <div>
              <h2 className="text-lg font-bold tracking-wide">Merry's Way ✨</h2>
              <p className="text-xs text-[#a8a19c] font-medium">Your AI barista is online</p>
            </div>
          </div>
          <button onClick={() => setIsOpen(false)} className="relative z-10 w-8 h-8 flex items-center justify-center rounded-full bg-white/10 hover:bg-white/20 text-white text-xl transition-colors">×</button>
        </div>

        {/* Messages */}
        <div className="flex-grow overflow-y-auto p-4 space-y-3 bg-[#1a1714]">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`px-4 py-3 max-w-[85%] rounded-2xl shadow-sm ${
                msg.role === "user"
                  ? "bg-gradient-to-br from-[#dfc18b] to-[#a37c35] text-[#1a1714] rounded-br-none shadow-md font-medium text-sm"
                  : "bg-white/5 border border-white/10 text-white rounded-bl-none shadow-[0_8px_32px_rgba(0,0,0,0.4)]"
              }`}>
                {msg.role === "user"
                  ? <p className="leading-relaxed whitespace-pre-wrap text-sm">{msg.content}</p>
                  : msg.type === "interrupt" 
                    ? <InterruptBubble payload={msg.content} onResolve={(status) => handleResolveInterrupt(i, msg.content, status)} />
                    : <BotMarkdown content={msg.content} />}
                <div className="text-[10px] text-right mt-1 opacity-50">{formatTime(msg.timestamp)}</div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="px-4 py-3 bg-white/5 border border-white/10 rounded-2xl rounded-bl-none flex items-center gap-3 shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
                <span className="flex gap-1.5 items-center h-4">
                  <span className="w-1.5 h-1.5 bg-[#dfc18b] rounded-full animate-bounce [animation-delay:0ms]" />
                  <span className="w-1.5 h-1.5 bg-[#dfc18b] rounded-full animate-bounce [animation-delay:150ms]" />
                  <span className="w-1.5 h-1.5 bg-[#dfc18b] rounded-full animate-bounce [animation-delay:300ms]" />
                </span>
                {botStatus && (
                  <span className="text-xs italic text-[#a8a19c] font-medium tracking-wide">
                    {botStatus}...
                  </span>
                )}
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="px-4 py-4 border-t border-[#dfc18b]/30 flex flex-col gap-2 bg-[#1a1714]/80 backdrop-blur-md rounded-b-3xl shrink-0">
          {isInterruptPending && (
            <p className="text-center text-xs text-[#dfc18b] font-medium animate-pulse">
              👆 Please tap a button above to continue
            </p>
          )}
          <div className="flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              placeholder={isInterruptPending ? "Use the buttons above to respond..." : "Ask about our menu or place an order..."}
              disabled={isTyping || isInterruptPending}
              className={`flex-grow px-5 py-3 rounded-full border text-sm focus:outline-none focus:ring-2 focus:ring-[#dfc18b] focus:border-transparent transition-all shadow-inner ${
                isInterruptPending
                  ? "bg-white/2 border-white/5 text-[#a8a19c] cursor-not-allowed opacity-50"
                  : "bg-white/5 border-white/10 text-white placeholder-[#a8a19c]"
              }`}
              onChange={(e) => (textRef.current = e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !isInterruptPending && handleSend()}
            />
            <button
              onClick={handleSend}
              disabled={isTyping || isInterruptPending}
              className={`w-12 h-12 rounded-full text-white flex items-center justify-center transition-all shrink-0 shadow-lg ${
                isTyping || isInterruptPending ? "bg-gray-600 opacity-50 cursor-not-allowed" : "bg-gradient-to-r from-[#dfc18b] to-[#a37c35] hover:from-[#c29c5b] hover:to-[#8a652a] hover:scale-105"
              }`}
            >
              {isTyping ? <Spinner /> : <FaPaperPlane size={16} className="-ml-1 mt-1" />}
            </button>
          </div>
        </div>
      </div>

      {checkoutPayload && (
        <CheckoutModal 
          isOpen={true} 
          total={checkoutPayload.total || 0} 
          onClose={() => {
            setCheckoutPayload(null);
            handleResumePayment("reject");
          }}
          onComplete={handleResumePayment} 
        />
      )}
    </>
  );
};

export default Chatbot;
