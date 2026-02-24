import { useState, useEffect, useRef } from "react";
import { userAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";

const TAGS = {
  likes: { label: "Likes", color: "bg-green-100 text-green-800 border-green-200" },
  dislikes: { label: "Dislikes", color: "bg-red-100 text-red-800 border-red-200" },
  allergies: { label: "Allergies", color: "bg-amber-100 text-amber-800 border-amber-200" },
};

const TagInput = ({ field, values, onChange, color }) => {
  const [input, setInput] = useState("");

  const add = () => {
    const val = input.trim();
    if (val && !values.includes(val)) {
      onChange([...values, val]);
    }
    setInput("");
  };

  const remove = (v) => onChange(values.filter((x) => x !== v));

  return (
    <div>
      <div className="flex flex-wrap gap-1.5 mb-2 min-h-[28px]">
        {values.map((v) => (
          <span key={v} className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full border font-medium ${color}`}>
            {v}
            <button onClick={() => remove(v)} className="hover:opacity-60 leading-none">×</button>
          </span>
        ))}
        {values.length === 0 && <span className="text-xs text-[#9c7e6c] italic">None added</span>}
      </div>
      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && add()}
          placeholder={`Add ${field}...`}
          className="flex-1 text-xs px-3 py-1.5 rounded-lg border border-[#d4c4b0] bg-[#faf7f3] focus:outline-none focus:ring-1 focus:ring-[#4B3832] placeholder-[#b0977e]"
        />
        <button
          onClick={add}
          className="text-xs px-3 py-1.5 bg-[#4B3832] text-white rounded-lg hover:bg-[#3a2d27] transition"
        >
          Add
        </button>
      </div>
    </div>
  );
};

export default function UserProfilePanel({ onClose }) {
  const { user, logout } = useAuth();
  const panelRef = useRef(null);

  const [prefs, setPrefs] = useState({ name: "", likes: [], dislikes: [], allergies: [], location: "" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  // Close on outside click
  useEffect(() => {
    const handler = (e) => {
      if (panelRef.current && !panelRef.current.contains(e.target)) onClose();
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, [onClose]);

  // Load preferences
  useEffect(() => {
    userAPI.getPreferences()
      .then((data) => setPrefs({
        name: data.name || "",
        likes: data.likes || [],
        dislikes: data.dislikes || [],
        allergies: data.allergies || [],
        location: data.location || "",
      }))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      await userAPI.updatePreferences(prefs);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      console.error("Save failed", e);
    } finally {
      setSaving(false);
    }
  };

  const avatar = (user?.username || user?.email || "U")[0].toUpperCase();

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 z-40" />

      {/* Panel */}
      <div
        ref={panelRef}
        className="absolute right-0 top-14 z-50 w-80 bg-[#fefcf9] border border-[#e5d6c6] rounded-2xl shadow-2xl overflow-hidden animate-slide-down"
        style={{ animation: "slideDown 0.18s ease-out" }}
      >
        <style>{`
          @keyframes slideDown {
            from { opacity: 0; transform: translateY(-8px) scale(0.97); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
          }
        `}</style>

        {/* Header */}
        <div className="bg-[#4B3832] px-5 py-4 flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#b68d40] flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
            {avatar}
          </div>
          <div className="overflow-hidden">
            <p className="text-white font-semibold text-sm truncate">{user?.username || user?.email?.split("@")[0]}</p>
            <p className="text-[#c8a882] text-xs truncate">{user?.email}</p>
          </div>
        </div>

        {/* Body */}
        <div className="p-4 max-h-[70vh] overflow-y-auto space-y-4">
          {loading ? (
            <div className="flex justify-center py-6">
              <div className="w-6 h-6 border-2 border-[#4B3832] border-t-transparent rounded-full animate-spin" />
            </div>
          ) : (
            <>
              {/* Display name */}
              <div>
                <label className="text-xs font-semibold text-[#9c7e6c] uppercase tracking-wider">Display Name</label>
                <input
                  value={prefs.name}
                  onChange={(e) => setPrefs({ ...prefs, name: e.target.value })}
                  placeholder="How should we call you?"
                  className="mt-1.5 w-full text-sm px-3 py-2 rounded-lg border border-[#d4c4b0] bg-[#faf7f3] focus:outline-none focus:ring-1 focus:ring-[#4B3832] text-[#4B3832] placeholder-[#b0977e]"
                />
              </div>

              {/* Location */}
              <div>
                <label className="text-xs font-semibold text-[#9c7e6c] uppercase tracking-wider">Location</label>
                <input
                  value={prefs.location}
                  onChange={(e) => setPrefs({ ...prefs, location: e.target.value })}
                  placeholder="e.g. Koregaon Park"
                  className="mt-1.5 w-full text-sm px-3 py-2 rounded-lg border border-[#d4c4b0] bg-[#faf7f3] focus:outline-none focus:ring-1 focus:ring-[#4B3832] text-[#4B3832] placeholder-[#b0977e]"
                />
              </div>

              {/* Memory fields */}
              {Object.entries(TAGS).map(([field, { label, color }]) => (
                <div key={field}>
                  <label className="text-xs font-semibold text-[#9c7e6c] uppercase tracking-wider">{label}</label>
                  <div className="mt-1.5">
                    <TagInput
                      field={label.toLowerCase()}
                      values={prefs[field]}
                      onChange={(v) => setPrefs({ ...prefs, [field]: v })}
                      color={color}
                    />
                  </div>
                </div>
              ))}

              {/* Memory tip */}
              <p className="text-[10px] text-[#9c7e6c] bg-[#f5efe6] rounded-lg px-3 py-2 leading-relaxed">
                💡 These preferences help the chatbot personalise recommendations and avoid ingredients you dislike or are allergic to.
              </p>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-[#e5d6c6] px-4 py-3 flex gap-2">
          <button
            onClick={save}
            disabled={saving || loading}
            className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
              saved
                ? "bg-green-500 text-white"
                : "bg-[#4B3832] text-white hover:bg-[#3a2d27] disabled:opacity-50"
            }`}
          >
            {saved ? "✓ Saved!" : saving ? "Saving…" : "Save Changes"}
          </button>
          <button
            onClick={logout}
            className="px-4 py-2 rounded-lg text-sm font-medium text-red-600 border border-red-200 hover:bg-red-50 transition"
          >
            Logout
          </button>
        </div>
      </div>
    </>
  );
}
