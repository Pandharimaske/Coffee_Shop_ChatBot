import { useState, useEffect, useRef } from "react";
import { userAPI } from "../services/api";
import { X, User, Mail, MapPin, Heart, ThumbsDown, AlertTriangle, Save, Plus, Trash2, CheckCircle2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

const TagInput = ({ tags, onChange, placeholder, colorClass }) => {
  const [input, setInput] = useState("");

  const add = () => {
    const val = input.trim();
    if (val && !tags.includes(val)) {
      onChange([...tags, val]);
    }
    setInput("");
  };

  const remove = (i) => onChange(tags.filter((_, idx) => idx !== i));

  return (
    <div className="space-y-3">
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {tags.map((tag, i) => (
            <span key={i} className={`flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full font-bold tracking-wide uppercase ${colorClass}`}>
              {tag}
              <button onClick={() => remove(i)} className="hover:opacity-70 transition-opacity focus:outline-none">
                <X size={10} strokeWidth={3} />
              </button>
            </span>
          ))}
        </div>
      )}
      <div className="relative">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && add()}
          placeholder={placeholder}
          className="w-full bg-white/5 border border-white/10 rounded-xl pl-4 pr-12 py-3 text-white text-sm placeholder-[#a8a19c]/50 focus:outline-none focus:border-[#dfc18b]/50 focus:ring-1 focus:ring-[#dfc18b]/50 transition-all shadow-inner"
        />
        <button onClick={add} className="absolute right-2 top-2 bottom-2 bg-white/10 hover:bg-white/20 text-white w-8 rounded-lg flex items-center justify-center transition-colors focus:outline-none">
          <Plus size={16} />
        </button>
      </div>
    </div>
  );
};

const Section = ({ icon, title, children }) => (
  <div className="glass-panel border border-white/5 rounded-3xl p-6 relative overflow-hidden group hover:border-white/10 transition-colors">
    <div className="flex items-center gap-2 text-white mb-5">
      <span className="text-[#dfc18b]">{icon}</span>
      <h3 className="text-xs font-black uppercase tracking-[0.15em]">{title}</h3>
    </div>
    {children}
  </div>
);

const ProfileDrawer = ({ user, onClose }) => {
  const [prefs, setPrefs] = useState(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [editName, setEditName] = useState("");
  const [editLocation, setEditLocation] = useState("");
  const drawerRef = useRef();

  useEffect(() => {
    userAPI.getPreferences().then((data) => {
      setPrefs(data);
      setEditName(data.name || "");
      setEditLocation(data.location || "");
    }).catch(() => {});
  }, []);

  useEffect(() => {
    const handler = (e) => {
      if (drawerRef.current && !drawerRef.current.contains(e.target)) onClose();
    };
    // small delay before binding prevent immediate close when clicking avatar
    const timer = setTimeout(() => document.addEventListener("mousedown", handler), 100);
    return () => {
      clearTimeout(timer);
      document.removeEventListener("mousedown", handler);
    };
  }, [onClose]);

  const handleSave = async () => {
    setSaving(true);
    try {
      await userAPI.updatePreferences({
        name: editName || null,
        likes: prefs.likes || [],
        dislikes: prefs.dislikes || [],
        allergies: prefs.allergies || [],
        location: editLocation || null,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (e) {
      console.error("Save failed", e);
    } finally {
      setSaving(false);
    }
  };

  const avatar = (user?.username || user?.email || "?")[0].toUpperCase();

  return (
    <AnimatePresence>
      <div className="fixed inset-0 z-50 flex justify-end">
        <motion.div 
          initial={{ opacity: 0 }} 
          animate={{ opacity: 1 }} 
          exit={{ opacity: 0 }} 
          className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        />

        <motion.div
          ref={drawerRef}
          initial={{ x: "100%" }}
          animate={{ x: 0 }}
          exit={{ x: "100%" }}
          transition={{ type: "spring", damping: 30, stiffness: 300, mass: 0.8 }}
          className="relative w-full max-w-[420px] bg-[#1a1714]/90 backdrop-blur-3xl h-full flex flex-col shadow-2xl border-l border-white/10"
        >
          {/* Header */}
          <div className="flex items-center justify-between p-6 shrink-0 border-b border-white/5">
            <h2 className="text-xl font-black text-white tracking-tighter">Your Profile</h2>
            <button onClick={onClose} className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 flex items-center justify-center text-white transition-colors focus:outline-none">
              <X size={18} />
            </button>
          </div>

          {/* Profile Identity */}
          <div className="p-8 shrink-0 flex items-center gap-5">
            <div className="relative">
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-[#dfc18b] to-[#a37c35] p-[2px] shadow-[0_0_30px_rgba(223,193,139,0.3)]">
                <div className="w-full h-full bg-[#1a1714] rounded-full flex items-center justify-center text-3xl font-black text-[#dfc18b]">
                  {avatar}
                </div>
              </div>
            </div>
            <div className="min-w-0">
              <p className="font-black text-2xl text-white truncate tracking-tight">
                {user?.username || user?.email?.split("@")[0]}
              </p>
              <div className="flex items-center gap-1.5 text-[#a8a19c] mt-1">
                <Mail size={12} />
                <p className="text-sm font-medium truncate">{user?.email}</p>
              </div>
            </div>
          </div>

          {/* Body */}
          <div className="flex-1 overflow-y-auto px-6 pb-6 space-y-4 custom-scrollbar">
            {!prefs ? (
              <div className="flex justify-center items-center h-40">
                <div className="w-8 h-8 border-2 border-[#dfc18b] border-t-transparent rounded-full animate-spin" />
              </div>
            ) : (
              <>
                <Section icon={<User size={16} />} title="Identity & Location">
                  <div className="space-y-4 relative z-10">
                    <div>
                      <label className="block text-[10px] font-bold text-[#a8a19c] uppercase tracking-widest pl-1 mb-1.5">Preferred Name</label>
                      <input
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        placeholder="What should we call you?"
                        className="w-full px-4 py-3 rounded-xl border border-white/10 bg-white/5 text-white placeholder-[#a8a19c]/50 focus:outline-none focus:border-[#dfc18b]/50 focus:ring-1 focus:ring-[#dfc18b]/50 transition-all text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-[10px] font-bold text-[#a8a19c] uppercase tracking-widest pl-1 mb-1.5 flex items-center gap-1">
                        <MapPin size={10} /> Delivery Area
                      </label>
                      <input
                        value={editLocation}
                        onChange={(e) => setEditLocation(e.target.value)}
                        placeholder="e.g. Area 51, Floor 3"
                        className="w-full px-4 py-3 rounded-xl border border-white/10 bg-white/5 text-white placeholder-[#a8a19c]/50 focus:outline-none focus:border-[#dfc18b]/50 focus:ring-1 focus:ring-[#dfc18b]/50 transition-all text-sm"
                      />
                    </div>
                  </div>
                </Section>

                <Section icon={<Heart size={16} />} title="Taste Preferences">
                  <TagInput
                    tags={prefs.likes || []}
                    onChange={(val) => setPrefs({ ...prefs, likes: val })}
                    placeholder="e.g. extra espresso, oat milk"
                    colorClass="bg-[#dfc18b]/10 text-[#dfc18b] border border-[#dfc18b]/20"
                  />
                </Section>

                <Section icon={<ThumbsDown size={16} />} title="Dislikes">
                  <TagInput
                    tags={prefs.dislikes || []}
                    onChange={(val) => setPrefs({ ...prefs, dislikes: val })}
                    placeholder="e.g. too sweet, cinnamon"
                    colorClass="bg-red-500/10 text-red-400 border border-red-500/20"
                  />
                </Section>

                <Section icon={<AlertTriangle size={16} />} title="Allergies">
                  <TagInput
                    tags={prefs.allergies || []}
                    onChange={(val) => setPrefs({ ...prefs, allergies: val })}
                    placeholder="e.g. peanuts, dairy"
                    colorClass="bg-orange-500/10 text-orange-400 border border-orange-500/20"
                  />
                  {prefs.allergies?.length > 0 && (
                    <p className="text-[10px] text-orange-400 font-bold uppercase tracking-widest mt-3 flex items-center gap-1">
                      <AlertTriangle size={10} /> We will strictly avoid these.
                    </p>
                  )}
                </Section>

                {prefs.feedback?.length > 0 && (
                  <Section icon={<User size={16} />} title="AI Insights">
                    <ul className="space-y-3">
                      {prefs.feedback.map((f, i) => (
                        <li key={i} className="text-sm font-medium text-[#a8a19c] bg-white/5 p-3 rounded-xl border border-white/5">
                          {f}
                        </li>
                      ))}
                    </ul>
                  </Section>
                )}
              </>
            )}
          </div>

          {/* Footer Save */}
          {prefs && (
            <div className="p-6 shrink-0 border-t border-white/10 bg-[#1a1714]/80 backdrop-blur-xl">
              <button
                onClick={handleSave}
                disabled={saving || saved}
                className={`w-full py-4 rounded-full font-black text-xs tracking-widest uppercase flex items-center justify-center gap-2 transition-all duration-300 ${
                  saved
                    ? "bg-green-500 text-white shadow-lg"
                    : "bg-gradient-to-r from-[#dfc18b] to-[#a37c35] text-[#1a1714] shadow-[0_10px_20px_rgba(223,193,139,0.2)] hover:scale-[1.02]"
                }`}
              >
                {saved ? (
                  <><CheckCircle2 size={16} /> Data Synced</>
                ) : saving ? (
                  <><div className="w-4 h-4 border-2 border-[#1a1714] border-t-transparent rounded-full animate-spin" /> Syncing</>
                ) : (
                  <><Save size={16} /> Save Memory Matrix</>
                )}
              </button>
            </div>
          )}
        </motion.div>
      </div>
    </AnimatePresence>
  );
};

export default ProfileDrawer;
