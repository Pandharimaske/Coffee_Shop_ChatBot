import { useEffect, useState, useRef } from "react";
import { FaPaperPlane, FaRobot, FaShoppingCart, FaTrash } from "react-icons/fa";
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
function LiveOrderPanel({ cartItems, onViewOrder }) {
  if (!cartItems.length) return null;

  const total = cartItems.reduce((sum, i) => sum + (i.price * i.quantity), 0);

  return (
    <div className="mx-3 mb-2 bg-[#4B3832] rounded-xl overflow-hidden shadow-md">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 bg-[#3a2d27]">
        <div className="flex items-center gap-1.5">
          <FaShoppingCart size={12} className="text-[#ffe8b3]" />
          <span className="text-[#ffe8b3] text-xs font-semibold tracking-wide uppercase">
            Current Order
          </span>
        </div>
        <span className="text-[#ffe8b3] text-xs font-bold">₹{total.toFixed(0)}</span>
      </div>

      {/* Items */}
      <div className="px-3 py-2 space-y-1 max-h-28 overflow-y-auto">
        {cartItems.map((item, i) => (
          <div key={i} className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              {/* quantity badge */}
              <span className="shrink-0 w-5 h-5 bg-[#b68d40] text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                {item.quantity}
              </span>
              <span className="text-white text-xs truncate">{item.name}</span>
            </div>
            <span className="text-[#d1beab] text-xs shrink-0 ml-2">
              ₹{(item.price * item.quantity).toFixed(0)}
            </span>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="px-3 py-2 border-t border-[#5a4540]">
        <button
          onClick={onViewOrder}
          className="w-full text-xs text-[#ffe8b3] hover:text-white font-semibold text-center transition"
        >
          View full order →
        </button>
      </div>
    </div>
  );
}

// ── Main Chatbot component ────────────────────────────────────────────────────
const Chatbot = () => {
  const { user } = useAuth();
  const { cartItems, refreshCart } = useCart();
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
      // Sync cart after every bot response — catches order changes made by the bot
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

  if (!user) return null;

  return (
    <>
      {/* Floating button with cart badge */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 bg-[#4B3832] text-white p-4 rounded-full shadow-lg hover:bg-[#3a2d27] transition z-50"
        >
          <FaRobot size={24} />
          {cartItems.length > 0 && (
            <span className="absolute -top-1 -right-1 w-5 h-5 bg-orange-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center shadow">
              {cartItems.reduce((s, i) => s + i.quantity, 0) > 9
                ? "9+"
                : cartItems.reduce((s, i) => s + i.quantity, 0)}
            </span>
          )}
        </button>
      )}

      {/* Chat window */}
      <div className={`fixed bottom-0 inset-x-4 sm:right-6 sm:inset-x-auto w-full sm:w-96 h-[80vh] sm:h-[560px] bg-[#fefcf9] shadow-2xl rounded-t-xl transform ${
        isOpen ? "translate-y-0" : "translate-y-full"
      } transition-transform duration-300 ease-in-out z-40 flex flex-col border border-[#d1beab]`}>

        {/* Header */}
        <div className="flex justify-between items-center p-4 bg-[#4B3832] text-white rounded-t-xl shrink-0">
          <div>
            <h2 className="text-lg font-semibold">Merry's Way ☕</h2>
            <p className="text-xs text-[#d1beab]">Your coffee assistant</p>
          </div>
          <button onClick={() => setIsOpen(false)} className="text-white text-2xl hover:text-[#d1beab]">×</button>
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
                {msg.role === "user" ? (
                  <p className="leading-relaxed whitespace-pre-wrap text-sm">{msg.content}</p>
                ) : (
                  <BotMarkdown content={msg.content} />
                )}
                <div className="text-[10px] text-right mt-1 opacity-50">{formatTime(msg.timestamp)}</div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="px-4 py-3 bg-[#e8ddd0] text-[#4B3832] rounded-2xl rounded-bl-none">
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

        {/* Live order panel — appears above input when cart has items */}
        <LiveOrderPanel
          cartItems={cartItems}
          onViewOrder={() => { setIsOpen(false); navigate("/order"); }}
        />

        {/* Input */}
        <div className="p-3 border-t border-[#d1beab] flex items-center gap-2 bg-[#f5efe6] rounded-b-xl shrink-0">
          <input
            ref={inputRef}
            type="text"
            placeholder="Ask about our menu, place an order..."
            className="flex-grow px-4 py-2 rounded-full border border-[#d1beab] bg-[#fffaf3] text-[#4B3832] text-sm focus:outline-none focus:ring-2 focus:ring-[#4B3832]"
            onChange={(e) => (textRef.current = e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
          />
          <button
            onClick={handleSend}
            disabled={isTyping}
            className={`p-2.5 rounded-full text-white flex items-center justify-center transition ${
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
