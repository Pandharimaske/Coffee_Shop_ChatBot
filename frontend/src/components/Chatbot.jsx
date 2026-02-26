import { useEffect, useState, useRef } from "react";
import { FaPaperPlane, FaRobot, FaShoppingCart, FaChevronUp, FaChevronDown, FaPlus, FaMinus, FaTrash } from "react-icons/fa";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { chatAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useNavigate } from "react-router-dom";

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
        strong: ({ children }) => <strong className="font-semibold text-[#3a2318]">{children}</strong>,
        em: ({ children }) => <em className="italic opacity-90">{children}</em>,
        ul: ({ children }) => <ul className="mt-0.5 mb-1.5 space-y-0.5">{children}</ul>,
        ol: ({ children }) => <ol className="mt-0.5 mb-1.5 space-y-0.5 pl-1 list-decimal list-inside">{children}</ol>,
        li: ({ children }) => (
          <li className="flex gap-1.5 items-start leading-snug">
            <span className="shrink-0 text-[#7a5c44] mt-px">•</span>
            <span>{children}</span>
          </li>
        ),
        hr: () => <hr className="my-2 border-[#c4a882] opacity-50" />,
        a: ({ href, children }) => (
          <a href={href} target="_blank" rel="noopener noreferrer"
            className="underline text-[#5c3d1e] hover:text-[#4B3832] transition-colors break-all">
            {children}
          </a>
        ),
        code: ({ children }) => (
          <code className="bg-[#c9af96] text-[#3a2318] px-1 rounded text-xs font-mono">{children}</code>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-2 border-[#b68d40] pl-2 my-1 italic opacity-80">{children}</blockquote>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

// ── Live Order Panel ──────────────────────────────────────────────────────────
function LiveOrderPanel({ cartItems, onViewOrder, onUpdateQty, onRemove }) {
  const [expanded, setExpanded] = useState(true);

  if (!cartItems.length) return null;

  const total = cartItems.reduce((sum, i) => sum + i.price * i.quantity, 0);
  const totalQty = cartItems.reduce((s, i) => s + i.quantity, 0);

  return (
    <div className="mx-3 mb-2 rounded-xl overflow-hidden shadow-lg border border-[#5a4540] bg-[#3a2d27]">
      {/* Toggle header — click to expand/collapse */}
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-3 py-2.5 bg-[#4B3832] hover:bg-[#5a4540] transition"
      >
        <div className="flex items-center gap-2">
          <FaShoppingCart size={12} className="text-[#ffe8b3]" />
          <span className="text-[#ffe8b3] text-xs font-semibold tracking-wide uppercase">
            Your Order
          </span>
          {/* item count pill */}
          <span className="bg-orange-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">
            {totalQty} {totalQty === 1 ? "item" : "items"}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[#ffe8b3] text-xs font-bold">₹{total.toFixed(0)}</span>
          {expanded
            ? <FaChevronDown size={10} className="text-[#d1beab]" />
            : <FaChevronUp size={10} className="text-[#d1beab]" />}
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="px-3 pt-2 pb-1">
          {/* Item rows */}
          <div className="space-y-2 max-h-40 overflow-y-auto pr-1">
            {cartItems.map((item, i) => (
              <div key={i} className="flex items-center gap-2">
                {/* name */}
                <span className="text-white text-xs flex-1 truncate">{item.name}</span>

                {/* qty controls */}
                <div className="flex items-center gap-1 shrink-0">
                  <button
                    onClick={() => onUpdateQty(item, item.quantity - 1)}
                    className="w-5 h-5 rounded-full bg-[#5a4540] hover:bg-[#7a5c44] text-white flex items-center justify-center transition"
                  >
                    {item.quantity === 1
                      ? <FaTrash size={8} />
                      : <FaMinus size={8} />}
                  </button>
                  <span className="text-white text-xs w-4 text-center font-medium">
                    {item.quantity}
                  </span>
                  <button
                    onClick={() => onUpdateQty(item, item.quantity + 1)}
                    className="w-5 h-5 rounded-full bg-[#5a4540] hover:bg-[#7a5c44] text-white flex items-center justify-center transition"
                  >
                    <FaPlus size={8} />
                  </button>
                </div>

                {/* line total */}
                <span className="text-[#d1beab] text-xs w-12 text-right shrink-0">
                  ₹{(item.price * item.quantity).toFixed(0)}
                </span>
              </div>
            ))}
          </div>

          {/* Divider + total + CTA */}
          <div className="border-t border-[#5a4540] mt-2 pt-2 flex items-center justify-between">
            <span className="text-[#d1beab] text-xs">Total</span>
            <span className="text-white text-xs font-bold">₹{total.toFixed(0)}</span>
          </div>
          <button
            onClick={onViewOrder}
            className="w-full mt-2 mb-1 text-xs bg-[#b68d40] hover:bg-[#a37b2c] text-white font-semibold py-1.5 rounded-lg transition"
          >
            View & Confirm Order →
          </button>
        </div>
      )}
    </div>
  );
}

// ── Main Chatbot component ────────────────────────────────────────────────────
const Chatbot = () => {
  const { user } = useAuth();
  const { cartItems, updateCartItem, removeFromCart, refreshCart } = useCart();
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef(null);
  const textRef = useRef("");
  const bottomRef = useRef(null);

  // Auto scroll
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

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
      const data = await chatAPI.send(message);
      setMessages((prev) => [...prev, {
        role: "bot",
        content: data.response,
        timestamp: new Date(),
      }]);
      await refreshCart();
    } catch {
      setMessages((prev) => [...prev, {
        role: "bot",
        content: "⚠️ Something went wrong. Please try again.",
        timestamp: new Date(),
      }]);
    } finally {
      setIsTyping(false);
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
      {/* Floating button with cart badge */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-[#4B3832] text-white p-4 rounded-full shadow-lg hover:bg-[#3a2d27] transition z-50"
        >
          <FaRobot size={24} />
          {totalCartQty > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-orange-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center shadow">
              {totalCartQty > 9 ? "9+" : totalCartQty}
            </span>
          )}
        </button>
      )}

      {/* Chat window — wider + taller */}
      <div className={`fixed bottom-0 inset-x-2 sm:right-6 sm:inset-x-auto w-full sm:w-[440px] h-[85vh] sm:h-[620px] bg-[#fefcf9] shadow-2xl rounded-t-2xl transform ${
        isOpen ? "translate-y-0" : "translate-y-full"
      } transition-transform duration-300 ease-in-out z-40 flex flex-col border border-[#d1beab]`}>

        {/* Header */}
        <div className="flex justify-between items-center px-5 py-4 bg-[#4B3832] text-white rounded-t-2xl shrink-0">
          <div>
            <h2 className="text-lg font-semibold">Merry's Way ☕</h2>
            <p className="text-xs text-[#d1beab]">Your coffee assistant</p>
          </div>
          <button onClick={() => setIsOpen(false)} className="text-white text-2xl hover:text-[#d1beab] leading-none">×</button>
        </div>

        {/* Messages */}
        <div className="flex-grow overflow-y-auto p-4 space-y-3 bg-[#fefcf9]">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`px-4 py-2.5 max-w-[82%] rounded-2xl shadow-sm ${
                msg.role === "user"
                  ? "bg-[#4B3832] text-white rounded-br-none text-sm"
                  : "bg-[#e8ddd0] text-[#4B3832] rounded-bl-none"
              }`}>
                {msg.role === "user"
                  ? <p className="leading-relaxed whitespace-pre-wrap text-sm">{msg.content}</p>
                  : <BotMarkdown content={msg.content} />}
                <div className="text-[10px] text-right mt-1 opacity-50">{formatTime(msg.timestamp)}</div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="px-4 py-3 bg-[#e8ddd0] rounded-2xl rounded-bl-none">
                <span className="flex gap-1 items-center h-4">
                  <span className="w-1.5 h-1.5 bg-[#7a5c44] rounded-full animate-bounce [animation-delay:0ms]" />
                  <span className="w-1.5 h-1.5 bg-[#7a5c44] rounded-full animate-bounce [animation-delay:150ms]" />
                  <span className="w-1.5 h-1.5 bg-[#7a5c44] rounded-full animate-bounce [animation-delay:300ms]" />
                </span>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Live order panel */}
        <LiveOrderPanel
          cartItems={cartItems}
          onViewOrder={() => { setIsOpen(false); navigate("/order"); }}
          onUpdateQty={handleQtyChange}
          onRemove={(name) => removeFromCart(name)}
        />

        {/* Input */}
        <div className="px-3 py-3 border-t border-[#d1beab] flex items-center gap-2 bg-[#f5efe6] rounded-b-2xl shrink-0">
          <input
            ref={inputRef}
            type="text"
            placeholder="Ask about our menu, place an order..."
            className="flex-grow px-4 py-2.5 rounded-full border border-[#d1beab] bg-[#fffaf3] text-[#4B3832] text-sm focus:outline-none focus:ring-2 focus:ring-[#4B3832]"
            onChange={(e) => (textRef.current = e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            onClick={handleSend}
            disabled={isTyping}
            className={`p-2.5 rounded-full text-white flex items-center justify-center transition shrink-0 ${
              isTyping ? "bg-gray-400" : "bg-[#4B3832] hover:bg-[#3a2d27]"
            }`}
          >
            {isTyping ? <Spinner /> : <FaPaperPlane size={16} />}
          </button>
        </div>
      </div>
    </>
  );
};

export default Chatbot;
