import { useEffect, useState, useRef } from "react";
import { MdAddCircle } from "react-icons/md";
import { FaSearch, FaTimes, FaStar } from "react-icons/fa";
import { useCart } from "../context/CartContext";
import { productsAPI } from "../services/api";

// ── Add-to-cart burst animation ───────────────────────────────────────────────
const CartBurst = ({ active }) => (
  <span className={`absolute inset-0 rounded-2xl pointer-events-none transition-all duration-300 ${
    active ? "ring-4 ring-[#4B3832] ring-opacity-40 scale-105" : ""
  }`} />
);

// ── Product Detail Modal ──────────────────────────────────────────────────────
const ProductModal = ({ product, onClose, onAdd, added }) => {
  if (!product) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative bg-[#fefcf9] rounded-3xl shadow-2xl max-w-md w-full overflow-hidden animate-fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Image */}
        <div className="relative h-56 overflow-hidden">
          <img
            src={product.image_url || "/images/Latte.jpg"}
            alt={product.name}
            className="w-full h-full object-cover"
            onError={(e) => { e.target.src = "/images/Latte.jpg"; }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />

          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-3 right-3 bg-white/90 text-[#4B3832] p-2 rounded-full hover:bg-white transition shadow"
          >
            <FaTimes size={14} />
          </button>

          {/* Rating badge */}
          {product.rating && (
            <div className="absolute bottom-3 left-4 flex items-center gap-1 bg-[#ffe8b3] text-[#4B3832] text-sm font-bold px-3 py-1 rounded-full shadow">
              <FaStar size={12} className="text-amber-500" />
              {product.rating}
            </div>
          )}
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="flex justify-between items-start mb-2">
            <div>
              <h2 className="text-2xl font-bold text-[#4B3832]">{product.name}</h2>
              <span className="text-sm text-[#9c7e6c] bg-[#f5efe6] px-2 py-0.5 rounded-full">
                {product.category}
              </span>
            </div>
            <span className="text-2xl font-bold text-[#b68d40]">₹{product.price?.toFixed(2)}</span>
          </div>

          {/* Description */}
          {product.description && (
            <p className="text-sm text-[#6b5245] mt-3 leading-relaxed">{product.description}</p>
          )}

          {/* Ingredients */}
          {product.ingredients?.length > 0 && (
            <div className="mt-4">
              <p className="text-xs font-semibold text-[#9c7e6c] uppercase tracking-wider mb-2">Ingredients</p>
              <div className="flex flex-wrap gap-1.5">
                {product.ingredients.map((ing, i) => (
                  <span key={i} className="text-xs bg-[#e8ddd0] text-[#4B3832] px-2.5 py-1 rounded-full">
                    {ing}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Add to cart button */}
          <button
            onClick={() => onAdd(product)}
            className={`mt-5 w-full py-3 rounded-xl font-semibold text-sm transition-all duration-200 flex items-center justify-center gap-2 ${
              added
                ? "bg-green-500 text-white scale-95"
                : "bg-[#4B3832] text-white hover:bg-[#3a2d27] active:scale-95"
            }`}
          >
            {added ? (
              <>✓ Added to order</>
            ) : (
              <><MdAddCircle size={20} /> Add to Order — ₹{product.price?.toFixed(2)}</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

// ── Main Menu ─────────────────────────────────────────────────────────────────
const Menu = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState(["All"]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [addedItems, setAddedItems] = useState({});   // name → bool for burst
  const [modalAdded, setModalAdded] = useState(false);
  const { addToCart } = useCart();
  const burstTimers = useRef({});

  const placeholders = ["Search for latte...", "Search for cappuccino...", "Search for espresso...", "Search for mocha..."];
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setPlaceholderIndex((p) => (p + 1) % placeholders.length), 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    productsAPI.getAll()
      .then((data) => {
        setProducts(data);
        setCategories(["All", ...new Set(data.map((p) => p.category).filter(Boolean))]);
      })
      .catch(() => setError("Failed to load menu. Please try again."))
      .finally(() => setLoading(false));
  }, []);

  const filtered = products.filter((p) => {
    const matchCat = selectedCategory === "All" || p.category === selectedCategory;
    const matchSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchCat && matchSearch;
  });

  const handleAdd = (product, fromModal = false) => {
    addToCart(product);

    // Burst animation on card
    setAddedItems((prev) => ({ ...prev, [product.name]: true }));
    if (burstTimers.current[product.name]) clearTimeout(burstTimers.current[product.name]);
    burstTimers.current[product.name] = setTimeout(() => {
      setAddedItems((prev) => ({ ...prev, [product.name]: false }));
    }, 700);

    // Modal added state
    if (fromModal) {
      setModalAdded(true);
      setTimeout(() => setModalAdded(false), 1200);
    }
  };

  const openModal = (product) => {
    setSelectedProduct(product);
    setModalAdded(false);
  };

  const closeModal = () => setSelectedProduct(null);

  if (loading) return (
    <div className="min-h-screen bg-[#F2E6D9] flex items-center justify-center">
      <div className="w-10 h-10 border-4 border-[#4B3832] border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-[#F2E6D9] flex items-center justify-center">
      <p className="text-red-500">{error}</p>
    </div>
  );

  return (
    <>
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: scale(0.95) translateY(8px); }
          to   { opacity: 1; transform: scale(1) translateY(0); }
        }
        .animate-fade-in { animation: fade-in 0.2s ease-out; }

        @keyframes pop {
          0%   { transform: scale(1); }
          40%  { transform: scale(1.22); }
          100% { transform: scale(1); }
        }
        .animate-pop { animation: pop 0.35s cubic-bezier(.36,.07,.19,.97); }

        @keyframes added-pill {
          0%   { opacity: 0; transform: translateY(4px) scale(0.9); }
          20%  { opacity: 1; transform: translateY(0) scale(1); }
          80%  { opacity: 1; }
          100% { opacity: 0; transform: translateY(-6px); }
        }
        .animate-added-pill { animation: added-pill 0.7s ease-out forwards; }
      `}</style>

      <div className="min-h-screen bg-[#F2E6D9] text-[#4B3832] px-4 py-6">

        {/* Search + Filter */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
          <div className="relative w-full md:w-1/2 max-w-md">
            <FaSearch className="absolute top-3.5 left-3 text-[#9c7e6c]" />
            <input
              type="text"
              placeholder={placeholders[placeholderIndex]}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 rounded-full bg-[#f5efe6] text-[#4B3832] placeholder-[#9c7e6c] border border-[#c8b09a] focus:outline-none focus:ring-2 focus:ring-[#4B3832] shadow-inner transition-all"
            />
          </div>

          <div className="flex flex-wrap justify-center gap-2">
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                  selectedCategory === cat
                    ? "bg-[#4B3832] text-white shadow-md"
                    : "bg-[#e0d3c0] text-[#4B3832] hover:bg-[#d1bfa5]"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Grid */}
        <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {filtered.length === 0 ? (
            <p className="col-span-full text-center text-[#9c7e6c]">No matching items found ☕</p>
          ) : (
            filtered.map((item) => {
              const isAdded = addedItems[item.name];
              return (
                <div
                  key={item.id}
                  className={`relative bg-[#fefcf9] border border-[#e5d6c6] shadow rounded-2xl overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-1 cursor-pointer ${
                    isAdded ? "ring-2 ring-[#4B3832]" : ""
                  }`}
                  onClick={() => openModal(item)}
                >
                  <CartBurst active={isAdded} />

                  <div className="relative">
                    <img
                      src={item.image_url || "/images/Latte.jpg"}
                      alt={item.name}
                      className="w-full h-48 object-cover"
                      onError={(e) => { e.target.src = "/images/Latte.jpg"; }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent" />
                    {item.rating && (
                      <div className="absolute top-2 right-2 flex items-center gap-1 bg-[#ffe8b3] text-[#4B3832] text-xs font-bold px-2 py-1 rounded-full shadow">
                        <FaStar size={10} className="text-amber-500" /> {item.rating}
                      </div>
                    )}
                  </div>

                  <div className="p-4">
                    <h3 className="text-base font-semibold leading-tight">{item.name}</h3>
                    <p className="text-xs text-[#9c7e6c] mt-0.5 mb-3">{item.category}</p>

                    {/* Description preview */}
                    {item.description && (
                      <p className="text-xs text-[#7a6255] leading-relaxed mb-3 line-clamp-2">
                        {item.description}
                      </p>
                    )}

                    <div className="flex justify-between items-center">
                      <p className="text-lg font-bold text-[#b68d40]">₹{item.price?.toFixed(2)}</p>

                      {/* Add button with animation */}
                      <div className="relative">
                        {isAdded && (
                          <span className="absolute -top-7 left-1/2 -translate-x-1/2 text-xs font-semibold text-white bg-[#4B3832] px-2 py-0.5 rounded-full whitespace-nowrap animate-added-pill pointer-events-none">
                            Added!
                          </span>
                        )}
                        <button
                          onClick={(e) => { e.stopPropagation(); handleAdd(item); }}
                          className={`transition-all duration-200 ${isAdded ? "text-green-600 animate-pop" : "text-[#4B3832] hover:text-[#3a2d27] hover:scale-110"}`}
                        >
                          <MdAddCircle size={32} />
                        </button>
                      </div>
                    </div>

                    <p className="text-xs text-[#9c7e6c] mt-2 hover:text-[#4B3832] transition-colors">
                      Tap for details →
                    </p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>

      {/* Product Detail Modal */}
      {selectedProduct && (
        <ProductModal
          product={selectedProduct}
          onClose={closeModal}
          onAdd={(p) => handleAdd(p, true)}
          added={modalAdded}
        />
      )}
    </>
  );
};

export default Menu;
