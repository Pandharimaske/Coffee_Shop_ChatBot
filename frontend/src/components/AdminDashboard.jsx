import React, { useState, useRef, useEffect } from "react";
import { Terminal as FaTerminal, Send as FaPaperPlane, BarChart3 as FaChartBar, Table as FaTable, Bot, User, Sparkles } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { adminAPI } from "../services/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

const Spinner = () => (
  <div className="w-5 h-5 border-2 border-t-transparent border-[#dfc18b] rounded-full animate-spin" />
);

// Custom markdown renderer intercepting JSON blocks for graphs
function AdminMarkdown({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ node, inline, className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || "");
          if (!inline && match && match[1] === "json") {
            try {
              const data = JSON.parse(String(children).replace(/\n$/, ""));
              
              if (data.type === "recharts_bar") {
                return (
                  <div className="h-80 w-full bg-white/5 backdrop-blur-md p-6 rounded-2xl shadow-2xl my-6 border border-white/10">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={data.data} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                        <defs>
                          <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#dfc18b" />
                            <stop offset="100%" stopColor="#a37c35" />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                        <XAxis 
                          dataKey={data.xKey} 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{fill: '#a8a19c', fontSize: 12}} 
                          dy={10} 
                        />
                        <YAxis 
                          axisLine={false} 
                          tickLine={false} 
                          tick={{fill: '#a8a19c', fontSize: 12}} 
                        />
                        <Tooltip 
                          cursor={{fill: 'rgba(255,255,255,0.05)'}} 
                          contentStyle={{
                            backgroundColor: '#1a1714', 
                            borderRadius: '12px', 
                            border: '1px solid rgba(255,255,255,0.1)', 
                            boxShadow: '0 10px 25px rgba(0,0,0,0.5)',
                            color: '#fff'
                          }} 
                        />
                        <Bar 
                          dataKey={data.yKey} 
                          fill="url(#barGradient)" 
                          radius={[6, 6, 0, 0]} 
                          barSize={32} 
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                );
              }
            } catch (e) {
              return <code className={className} {...props}>{children}</code>;
            }
          }
          return <code className="bg-white/10 text-[#dfc18b] px-1.5 py-0.5 rounded text-sm font-mono" {...props}>{children}</code>;
        },
        table: ({ children }) => (
          <div className="overflow-x-auto my-6 w-full rounded-2xl border border-white/10 shadow-2xl bg-white/5 backdrop-blur-md">
            <table className="min-w-full text-sm text-left">{children}</table>
          </div>
        ),
        thead: ({ children }) => <thead className="bg-white/10 text-[#dfc18b] font-bold uppercase tracking-wider text-xs">{children}</thead>,
        tbody: ({ children }) => <tbody className="divide-y divide-white/5">{children}</tbody>,
        th: ({ children }) => <th className="px-6 py-4">{children}</th>,
        td: ({ children }) => <td className="px-6 py-4 text-white/90">{children}</td>,
        p: ({ children }) => <p className="mb-3 last:mb-0 leading-relaxed text-[15px] opacity-90">{children}</p>,
        h3: ({ children }) => <h3 className="text-lg font-bold text-[#dfc18b] mt-6 mb-3 flex items-center gap-2"><Sparkles size={18} /> {children}</h3>,
        strong: ({ children }) => <strong className="font-bold text-white tracking-tight">{children}</strong>,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}

const AdminDashboard = () => {
  const [messages, setMessages] = useState([
    { role: "bot", content: "Welcome to the BI Command Center. Ask anything! Try:\n- `Plot the top 3 selling items by total quantity`\n- `Show me all active orders as a table`\n- `What was our total revenue today?`" }
  ]);
  const [query, setQuery] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const handleSend = async () => {
    if (!query.trim() || isTyping) return;
    const msg = query;
    setQuery("");
    setMessages(prev => [...prev, { role: "user", content: msg }]);
    setIsTyping(true);
    
    try {
      const res = await adminAPI.chat(msg);
      setMessages(prev => [...prev, { role: "bot", content: res.reply }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: "bot", content: `**Error communicating with BI Agent:** ${e.message}` }]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-[85vh] bg-[#1a1714] flex flex-col mt-6 shadow-[0_30px_100px_rgba(0,0,0,0.6)] rounded-3xl overflow-hidden border border-white/10 relative ring-1 ring-[#dfc18b]/10">
      {/* Decorative Orbs */}
      <div className="absolute -top-24 -left-24 w-96 h-96 bg-[#dfc18b] rounded-full blur-[120px] opacity-[0.07] pointer-events-none" />
      <div className="absolute top-1/2 -right-48 w-80 h-80 bg-[#a37c35] rounded-full blur-[100px] opacity-[0.05] pointer-events-none" />

      {/* Header */}
      <div className="bg-[#1a1714]/80 backdrop-blur-xl text-white p-8 border-b border-white/5 flex items-center justify-between relative z-10 shrink-0">
        <div className="flex items-center gap-5">
          <div className="p-4 bg-gradient-to-br from-[#dfc18b]/20 to-[#a37c35]/20 rounded-2xl backdrop-blur-md border border-[#dfc18b]/20 shadow-[0_0_20px_rgba(223,193,139,0.2)]">
            <FaChartBar size={28} className="text-[#dfc18b]" />
          </div>
          <div>
            <h1 className="text-2xl font-black tracking-tight uppercase italic flex items-center gap-2">
              BI <span className="text-[#dfc18b]">Intelligence</span>
            </h1>
            <p className="text-[#a8a19c] text-sm font-medium tracking-wide">Secure conversation with your data warehouse</p>
          </div>
        </div>
        <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-white/5 rounded-full border border-white/10">
          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-[10px] font-bold uppercase tracking-widest text-[#a8a19c]">System Active</span>
        </div>
      </div>

      {/* Chat Area */}
      <div className="flex-grow p-6 sm:p-10 overflow-y-auto space-y-8 custom-scrollbar">
        <AnimatePresence initial={false}>
          {messages.map((m, i) => (
            <motion.div 
              key={i} 
              initial={{ opacity: 0, y: 20, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={{ type: "spring", stiffness: 260, damping: 20 }}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className="group relative flex items-start gap-3 max-w-[90%] sm:max-w-[85%]">
                {m.role === "bot" && (
                  <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center shrink-0 mt-1">
                    <Bot size={16} className="text-[#dfc18b]" />
                  </div>
                )}
                <div className={`px-7 py-5 rounded-3xl shadow-xl ${
                  m.role === "user" 
                  ? "bg-gradient-to-br from-[#dfc18b] to-[#a37c35] text-[#1a1714] rounded-tr-none font-semibold" 
                  : "bg-white/5 border border-white/10 text-white rounded-tl-none backdrop-blur-md"
                }`}>
                  {m.role === "user" 
                    ? <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p> 
                    : <AdminMarkdown content={m.content} />
                  }
                </div>
                {m.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-[#dfc18b] flex items-center justify-center shrink-0 mt-1">
                    <User size={16} className="text-[#1a1714]" />
                  </div>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        
        {isTyping && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex justify-start items-center gap-3"
          >
            <div className="w-8 h-8 rounded-full bg-white/5 border border-white/10 flex items-center justify-center">
              <Bot size={16} className="text-[#dfc18b]" />
            </div>
            <div className="px-6 py-4 bg-white/5 border border-white/10 rounded-2xl rounded-tl-none flex items-center gap-3 backdrop-blur-md shadow-lg">
              <div className="flex gap-1">
                {[0, 1, 2].map(dot => (
                  <motion.div 
                    key={dot}
                    animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ repeat: Infinity, duration: 1.5, delay: dot * 0.2 }}
                    className="w-1.5 h-1.5 rounded-full bg-[#dfc18b]"
                  />
                ))}
              </div>
              <span className="text-[#dfc18b] text-xs font-black uppercase tracking-widest italic">SQL Agent Thinking...</span>
            </div>
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-[#1a1714]/80 backdrop-blur-2xl border-t border-white/5 relative z-20 shrink-0">
        <div className="max-w-4xl mx-auto relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#dfc18b] to-[#a37c35] rounded-3xl blur opacity-10 group-focus-within:opacity-20 transition duration-500" />
          <div className="relative flex items-center gap-4 bg-[#1a1714] border border-white/10 rounded-2xl px-6 py-2 shadow-2xl focus-within:border-[#dfc18b]/40 transition-all">
            <FaTerminal className="text-[#dfc18b] opacity-40 shrink-0" size={18} />
            <input 
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Query data (e.g. Plot top selling coffee types)..."
              className="flex-grow bg-transparent focus:outline-none text-white py-4 text-lg placeholder-white/20 font-medium"
            />
            <motion.button 
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleSend}
              disabled={isTyping}
              className={`px-8 py-3.5 rounded-xl text-[#1a1714] font-black uppercase tracking-widest italic text-sm transition-all flex items-center gap-2 shadow-[0_10px_30px_rgba(223,193,139,0.3)] ${
                isTyping ? "bg-gray-700/50 cursor-not-allowed text-gray-400" : "bg-gradient-to-r from-[#dfc18b] to-[#a37c35] hover:shadow-[0_15px_40px_rgba(223,193,139,0.4)]"
              }`}
            >
              {isTyping ? <Spinner /> : <><FaPaperPlane size={14} /> Execute</>}
            </motion.button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar { width: 6px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.05); border-radius: 10px; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: rgba(223,193,139,0.2); }
      `}</style>
    </div>
  );
};

export default AdminDashboard;
