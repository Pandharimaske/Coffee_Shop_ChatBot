import React from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { motion } from "framer-motion";
import { Coffee, Bot, ArrowRight, Sparkles, BookOpen } from "lucide-react";

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1, delayChildren: 0.2 } }
};
const item = {
  hidden: { opacity: 0, y: 30, filter: "blur(10px)" },
  show: { opacity: 1, y: 0, filter: "blur(0px)", transition: { duration: 0.8, ease: [0.22, 1, 0.36, 1] } }
};

const ActionCard = ({ to, onClick, icon: Icon, title, desc, border }) => {
  const content = (
    <div className={`group relative flex flex-col items-start p-8 glass-card glass-card-hover h-full w-full rounded-3xl overflow-hidden cursor-pointer border-l-2 ${border}`}>
      <div className="absolute -top-10 -right-10 opacity-5 group-hover:opacity-10 transition-opacity">
        <Icon size={120} />
      </div>
      <div className="w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-[#dfc18b] mb-6 shadow-md group-hover:scale-110 transition-transform">
        <Icon size={24} />
      </div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-[#a8a19c] mb-6 flex-grow text-sm leading-relaxed">{desc}</p>
      <div className="flex items-center text-[#dfc18b] font-semibold text-sm group-hover:gap-2 transition-all">
        Explore <ArrowRight size={14} className="ml-1" />
      </div>
    </div>
  );

  return to ? <Link to={to} className="block h-full block">{content}</Link> : <button onClick={onClick} className="block w-full h-full text-left">{content}</button>;
};

const Home = () => {
  const { user } = useAuth();

  const handleOpenChatbot = () => {
    window.dispatchEvent(new Event("openChatbot"));
  };

  if (user) {
    const firstName = user.username || user.email.split("@")[0];
    return (
      <motion.div variants={container} initial="hidden" animate="show" className="max-w-5xl mx-auto space-y-16 py-8">
        <motion.section variants={item} className="flex flex-col md:flex-row items-center justify-between glass-panel rounded-[2.5rem] p-10 md:p-14 overflow-hidden relative">
          <div className="absolute -right-20 -bottom-20 w-80 h-80 bg-[#dfc18b]/10 rounded-full blur-[80px] pointer-events-none" />
          
          <div className="space-y-6 text-center md:text-left md:w-3/5 relative z-10">
            <h1 className="text-5xl md:text-6xl font-black text-white tracking-tighter leading-[1.1]">
              Welcome back,<br/> <span className="text-gradient-gold">{firstName}</span> ☕
            </h1>
            <p className="text-lg text-[#a8a19c] max-w-lg leading-relaxed">
              Your personal AI barista is ready. What are we brewing for you today? Ask for a recommendation or perfectly reorder your favorites.
            </p>
          </div>
          <div className="hidden md:flex md:w-2/5 justify-center z-10 mt-10 md:mt-0">
            <motion.div animate={{ y: [0, -15, 0] }} transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}>
               <div className="w-56 h-56 rounded-full bg-gradient-to-tr from-[#2a1c14] to-[#0a0a0a] p-2 shadow-[0_0_60px_rgba(223,193,139,0.15)] border border-[#dfc18b]/20">
                 <img src="/images/cappuccino.jpg" onError={e=>e.target.src="https://images.unsplash.com/photo-1497935586351-b67a49e012bf?auto=format&fit=crop&q=80&w=400&h=400"} alt="Coffee" className="w-full h-full object-cover rounded-full mix-blend-luminosity hover:mix-blend-normal transition-all duration-700" />
               </div>
            </motion.div>
          </div>
        </motion.section>

        <motion.section variants={item} className="space-y-8">
          <div className="flex items-center gap-4 px-2 opacity-60">
            <h2 className="text-sm font-bold uppercase tracking-[0.2em] text-[#dfc18b]">Quick Actions</h2>
            <div className="h-px bg-gradient-to-r from-[#dfc18b]/30 to-transparent flex-1" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ActionCard onClick={handleOpenChatbot} icon={Bot} title="AI Barista" desc="Ask for customized drinks or secret menu items." border="border-l-[#dfc18b]" />
            <ActionCard to="/menu" icon={BookOpen} title="Full Menu" desc="Browse our elegant espresso and fresh pastries." border="border-l-[#a37c35]" />
            <ActionCard to="/order" icon={Coffee} title="Active Cart" desc="Review your tailored order and proceed to checkout instantly." border="border-l-[#6a4f22]" />
          </div>
        </motion.section>
      </motion.div>
    );
  }

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-center relative">
      <motion.div variants={container} initial="hidden" animate="show" className="max-w-6xl w-full flex flex-col md:flex-row items-center justify-between gap-16 relative z-10">
        
        <div className="md:w-1/2 space-y-10 text-center md:text-left">
          <motion.div variants={item} className="space-y-6">
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-[#dfc18b] text-xs font-bold tracking-[0.1em] uppercase backdrop-blur-md">
              <Sparkles size={14} /> AI-Powered Coffee
            </span>
            <h1 className="text-6xl sm:text-7xl lg:text-8xl font-black text-white leading-[1.05] tracking-tighter mix-blend-lighten">
              Elite <br/>
              <span className="text-gradient-gold">Espresso</span> 
            </h1>
            <p className="text-[#a8a19c] text-lg sm:text-xl leading-relaxed max-w-md mx-auto md:mx-0">
              The world's most advanced coffee ordering experience. Zero friction, total personalization.
            </p>
          </motion.div>

          <motion.div variants={item} className="flex flex-col sm:flex-row items-center justify-center md:justify-start gap-4">
            <Link to="/login" className="w-full sm:w-auto">
              <button className="w-full flex items-center justify-center gap-3 bg-white text-[#1a1714] px-8 py-4 rounded-full font-bold hover:scale-105 transition-all shadow-[0_0_30px_rgba(255,255,255,0.2)]">
                Access Panel
              </button>
            </Link>
            <Link to="/menu" className="w-full sm:w-auto">
              <button className="w-full border border-white/20 text-white px-8 py-4 rounded-full font-bold hover:bg-white/5 transition-all">
                Explore Menu
              </button>
            </Link>
          </motion.div>
        </div>

        <motion.div variants={item} className="md:w-1/2 flex justify-center relative">
          <div className="relative animate-float pointer-events-none">
            <div className="absolute inset-0 bg-gradient-to-tr from-[#dfc18b] to-[#a37c35] rounded-full blur-[100px] opacity-20" />
            <img
              src="https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&q=80&w=600&h=600"
              alt="Elite Pour"
              className="relative w-72 sm:w-96 lg:w-[450px] h-[600px] object-cover rounded-full shadow-[0_30px_60px_rgba(0,0,0,0.6)] mix-blend-luminosity hover:mix-blend-normal transition-all duration-1000 border border-white/5"
            />
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Home;
