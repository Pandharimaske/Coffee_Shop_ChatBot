import { useState, useEffect, useRef } from "react";
import { FaTimes, FaUser, FaEnvelope, FaMapMarkerAlt, FaHeart, FaThumbsDown, FaExclamationTriangle, FaSave, FaPlus, FaTrash } from "react-icons/fa";
import { MdEdit, MdCheckCircle } from "react-icons/md";
import { userAPI } from "../services/api";

// ── Tag input for lists (likes / dislikes / allergies) ───────────────────────
const TagInput = ({ tags, onChange, placeholder, color }) => {
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
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1.5">
        {tags.map((tag, i) => (
          <span key={i} className={`flex items-center gap-1 text-xs px-2.5 py-1 rounded-full font-medium ${color}`}>
            {tag}
            <button onClick={() => remove(i)} className="hover:opacity-70 transition">
              <FaTimes size={9} />
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && add()}
          placeholder={placeholder}
          className="flex-1 text-sm bg-[#f5efe6] border border-[#d4c0aa] rounded-lg px-3 py-1.5 text-[#4B3832] placeholder-[#9c7e6c] focus:outline-none focus:ring-1 focus:ring-[#4B3832]"
        />
        <button onClick={add} className="bg-[#4B3832] text-white px-2.5 rounded-lg hover:bg-[#3a2d27] transition">
          <FaPlus size={11} />
        </button>
      </div>
    </div>
  );
};

// ── Section wrapper ───────────────────────────────────────────────────────────
const Section = ({ icon, title, children }) => (
  <div className="bg-[#fefcf9] border border-[#e5d6c6] rounded-2xl p-4 space-y-3">
    <div className="flex items-center gap-2 text-[#4B3832]">
      <span className="text-[#b68d40]">{icon}</span>
      <h3 className="text-sm font-bold uppercase tracking-wider">{title}</h3>
    </div>
    {children}
  </div>
);

// ── Main Profile Drawer ───────────────────────────────────────────────────────
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

  // Close on click outside
  useEffect(() => {
    const handler = (e) => {
      if (drawerRef.current && !drawerRef.current.contains(e.target)) onClose();
    };
    setTimeout(() => document.addEventListener("mousedown", handler), 100);
    return () => document.removeEventListener("mousedown", handler);
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

  const avatar = (user.username || user.email)[0].toUpperCase();

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm z-40" />

      {/* Drawer */}
      <div
        ref={drawerRef}
        className="fixed top-0 right-0 h-full w-full max-w-sm bg-[#F2E6D9] z-50 shadow-2xl flex flex-col overflow-hidden"
        style={{ animation: "slideIn 0.25s ease-out" }}
      >
        <style>{`
          @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to   { transform: translateX(0); opacity: 1; }
          }
        `}</style>

        {/* Header */}
        <div className="bg-[#4B3832] text-white p-5 flex items-center gap-4 flex-shrink-0">
          <div className="w-14 h-14 rounded-full bg-[#b68d40] flex items-center justify-center text-2xl font-bold text-white shadow-lg">
            {avatar}
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-bold text-lg leading-tight truncate">
              {user.username || user.email.split("@")[0]}
            </p>
            <p className="text-[#c8b09a] text-xs truncate">{user.email}</p>
          </div>
          <button onClick={onClose} className="text-[#c8b09a] hover:text-white transition ml-auto">
            <FaTimes size={18} />
          </button>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">

          {/* Account info */}
          <Section icon={<FaUser size={14} />} title="Account">
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2 text-[#6b5245]">
                <FaEnvelope size={12} className="text-[#9c7e6c]" />
                <span className="truncate">{user.email}</span>
              </div>
              {user.id && (
                <div className="flex items-center gap-2 text-[#9c7e6c] text-xs">
                  <span>ID: {user.id.slice(0, 8)}…</span>
                </div>
              )}
            </div>
          </Section>

          {!prefs ? (
            <div className="flex justify-center py-8">
              <div className="w-8 h-8 border-4 border-[#4B3832] border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <>
              {/* Display name + location */}
              <Section icon={<MdEdit size={16} />} title="Profile">
                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-[#9c7e6c] font-medium mb-1 block">Display name</label>
                    <input
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      placeholder="What should we call you?"
                      className="w-full text-sm bg-[#f5efe6] border border-[#d4c0aa] rounded-lg px-3 py-2 text-[#4B3832] placeholder-[#9c7e6c] focus:outline-none focus:ring-1 focus:ring-[#4B3832]"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-[#9c7e6c] font-medium mb-1 block flex items-center gap-1">
                      <FaMapMarkerAlt size={10} /> Location
                    </label>
                    <input
                      value={editLocation}
                      onChange={(e) => setEditLocation(e.target.value)}
                      placeholder="e.g. Koregaon Park"
                      className="w-full text-sm bg-[#f5efe6] border border-[#d4c0aa] rounded-lg px-3 py-2 text-[#4B3832] placeholder-[#9c7e6c] focus:outline-none focus:ring-1 focus:ring-[#4B3832]"
                    />
                  </div>
                </div>
              </Section>

              {/* Likes */}
              <Section icon={<FaHeart size={13} />} title="Likes">
                <TagInput
                  tags={prefs.likes || []}
                  onChange={(val) => setPrefs({ ...prefs, likes: val })}
                  placeholder="e.g. oat milk, sweet"
                  color="bg-green-100 text-green-800"
                />
                <p className="text-xs text-[#9c7e6c]">The bot recommends based on these ☕</p>
              </Section>

              {/* Dislikes */}
              <Section icon={<FaThumbsDown size={13} />} title="Dislikes">
                <TagInput
                  tags={prefs.dislikes || []}
                  onChange={(val) => setPrefs({ ...prefs, dislikes: val })}
                  placeholder="e.g. cinnamon, very sweet"
                  color="bg-orange-100 text-orange-800"
                />
              </Section>

              {/* Allergies */}
              <Section icon={<FaExclamationTriangle size={13} />} title="Allergies">
                <TagInput
                  tags={prefs.allergies || []}
                  onChange={(val) => setPrefs({ ...prefs, allergies: val })}
                  placeholder="e.g. nuts, lactose"
                  color="bg-red-100 text-red-800"
                />
                <p className="text-xs text-[#9c7e6c]">These are never recommended to you 🚫</p>
              </Section>

              {/* Last order read-only */}
              {prefs.last_order && (
                <Section icon={<FaUser size={13} />} title="Last order">
                  <p className="text-sm text-[#6b5245]">{prefs.last_order}</p>
                </Section>
              )}

              {/* Feedback read-only */}
              {prefs.feedback?.length > 0 && (
                <Section icon={<FaUser size={13} />} title="Your feedback">
                  <ul className="space-y-1">
                    {prefs.feedback.map((f, i) => (
                      <li key={i} className="text-xs text-[#6b5245] border-l-2 border-[#b68d40] pl-2">{f}</li>
                    ))}
                  </ul>
                </Section>
              )}
            </>
          )}
        </div>

        {/* Save footer */}
        {prefs && (
          <div className="p-4 border-t border-[#d4c0aa] bg-[#f5efe6] flex-shrink-0">
            <button
              onClick={handleSave}
              disabled={saving}
              className={`w-full py-3 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
                saved
                  ? "bg-green-500 text-white"
                  : "bg-[#4B3832] text-white hover:bg-[#3a2d27] active:scale-95"
              }`}
            >
              {saved ? (
                <><MdCheckCircle size={18} /> Memory saved!</>
              ) : saving ? (
                <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Saving…</>
              ) : (
                <><FaSave size={15} /> Save preferences</>
              )}
            </button>
            <p className="text-center text-xs text-[#9c7e6c] mt-2">
              The chatbot learns from these automatically
            </p>
          </div>
        )}
      </div>
    </>
  );
};

export default ProfileDrawer;
