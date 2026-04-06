import { useEffect, useState, useRef } from "react";
import { Plus, Search, X, Star, ChevronRight, Check, Minus } from "lucide-react";
import { useCart } from "../context/CartContext";
import { productsAPI } from "../services/api";
import { motion, AnimatePresence } from "framer-motion";

const ProductModal = ({ product, onClose, onAdd, added }) => {
  const [qty, setQty] = useState(1);

  if (!product) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-md overflow-y-auto"
        onClick={onClose}
      >
        <div className="min-h-[100dvh] flex items-center justify-center p-4 w-full cursor-pointer pointer-events-none">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="relative bg-[#1a1714] border border-white/10 rounded-[2rem] shadow-2xl max-w-md w-full overflow-hidden cursor-default pointer-events-auto my-8"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="relative h-64 overflow-hidden">
              <motion.img
                layoutId={`img-${product.id}`}
                src={product.image_url || "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&q=80&w=600&h=600"}
                alt={product.name}
                className="w-full h-full object-cover mix-blend-luminosity hover:mix-blend-normal transition-all duration-700"
                onError={(e) => { e.target.src = "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&q=80&w=600&h=600"; }}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#1a1714] to-transparent opacity-80" />
              
              <button
                onClick={onClose}
                className="absolute top-4 right-4 bg-black/40 text-white p-2 text-xs rounded-full hover:bg-white border border-white/20 hover:text-black transition backdrop-blur-md"
              >
                <X size={16} />
              </button>
              {product.rating && (
                <div className="absolute bottom-4 left-6 flex items-center gap-1.5 bg-[#dfc18b] text-[#1a1714] text-xs font-bold px-3 py-1 rounded-full shadow-lg">
                  <Star size={12} fill="currentColor" />
                  {product.rating}
                </div>
              )}
            </div>

            <div className="p-8">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <motion.h2 layoutId={`title-${product.id}`} className="text-3xl font-black text-white tracking-tighter">{product.name}</motion.h2>
                  <span className="text-xs text-[#a37c35] font-bold tracking-widest uppercase mt-1 block">
                    {product.category}
                  </span>
                </div>
                <span className="text-2xl font-bold text-[#dfc18b]">₹{product.price?.toFixed(2)}</span>
              </div>

              {product.description && (
                <p className="text-sm text-[#a8a19c] mt-4 leading-relaxed">{product.description}</p>
              )}

              {product.ingredients?.length > 0 && (
                <div className="mt-6">
                  <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-3">Ingredients</p>
                  <div className="flex flex-wrap gap-2">
                    {product.ingredients.map((ing, i) => (
                      <span key={i} className="text-xs border border-white/10 text-[#a8a19c] px-3 py-1.5 rounded-full">
                        {ing}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="mt-8 border-t border-white/5 pt-6">
                <h3 className="text-[10px] font-bold text-white/40 uppercase tracking-widest mb-3">Quantity</h3>
                <div className="flex items-center gap-3">
                  <button onClick={() => setQty(Math.max(1, qty - 1))} className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white flex items-center justify-center transition focus:outline-none">
                    <Minus size={16} />
                  </button>
                  <span className="w-8 text-center font-black text-xl text-white">{qty}</span>
                  <button onClick={() => setQty(qty + 1)} className="w-10 h-10 rounded-full bg-white/5 hover:bg-white/10 border border-white/10 text-white flex items-center justify-center transition focus:outline-none">
                    <Plus size={16} />
                  </button>
                </div>
              </div>

              <button
                onClick={() => onAdd({ ...product, quantity: qty })}
                className={`mt-8 w-full py-4 rounded-2xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 relative overflow-hidden ${
                  added
                    ? "bg-green-500 text-white scale-95"
                    : "bg-gradient-to-r from-[#dfc18b] to-[#a37c35] text-[#1a1714] shadow-[0_10px_30px_rgba(223,193,139,0.2)] hover:scale-[1.02]"
                }`}
              >
                {added ? (
                  <><Check size={18} /> Added to order</>
                ) : (
                  <><Plus size={18} /> Add {qty} to Order — ₹{(product.price * qty).toFixed(2)}</>
                )}
              </button>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </AnimatePresence>
  );
};

const Menu = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState(["All"]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [modalAdded, setModalAdded] = useState(false);
  const { addToCart } = useCart();

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

  const handleAdd = (productObj) => {
    // Check if the productObj already has a quantity (passed from the modal)
    // If it doesn't, default to 1 (when clicking "+" on the grid)
    const productToAdd = productObj.quantity !== undefined ? productObj : { ...productObj, quantity: 1 };
    
    addToCart(productToAdd);
    setModalAdded(true);
    setTimeout(() => setModalAdded(false), 1200);
  };

  if (loading) return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="w-10 h-10 border-2 border-[#dfc18b] border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error) return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <p className="text-red-500">{error}</p>
    </div>
  );

  return (
    <div className="space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 mb-8 mt-4">
        <div className="space-y-4">
           <h1 className="text-4xl md:text-5xl font-black text-white tracking-tighter">
             The <span className="text-gradient-gold">Collection</span>
           </h1>
           <p className="text-[#a8a19c] max-w-sm text-sm">Finely crafted espresso beverages, artisan pastries, and seasonal reserves.</p>
        </div>
        
        <div className="w-full md:w-auto relative group">
          <Search className="absolute top-3.5 left-4 text-[#a8a19c] group-focus-within:text-[#dfc18b] transition-colors" size={18} />
          <input
            type="text"
            placeholder="Search menu..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full md:w-64 pl-12 pr-4 py-3 rounded-full bg-white/5 border border-white/10 text-white placeholder-[#a8a19c] focus:outline-none focus:border-[#dfc18b]/50 focus:ring-1 focus:ring-[#dfc18b]/50 focus:bg-white/10 transition-all font-medium text-sm border focus:ring-opacity-50 !outline-none"
          />
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 mb-12">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-6 py-2 rounded-full text-[10px] font-bold tracking-widest uppercase transition-all duration-300 border ${
              selectedCategory === cat
                ? "bg-[#dfc18b] text-[#1a1714] border-[#dfc18b]"
                : "bg-transparent text-[#a8a19c] border-white/10 hover:border-white/30 hover:text-white lg:hover:w-auto"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Masonry-style Grid */}
      <motion.div layout className="grid gap-6 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 pb-20">
        <AnimatePresence>
          {filtered.length === 0 && (
            <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="col-span-full text-center text-[#a8a19c] py-20">
              No matching items found ☕
            </motion.p>
          )}
          {filtered.map((item) => (
            <motion.div
              layout
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ duration: 0.3 }}
              key={item.id}
              className="group glass-card glass-card-hover rounded-[2rem] overflow-hidden cursor-pointer flex flex-col"
              onClick={() => {
                setSelectedProduct(item);
              }}
            >
              <div className="relative h-56 overflow-hidden">
                <motion.img
                  layoutId={`img-${item.id}`}
                  src={item.image_url || "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&q=80&w=600&h=600"}
                  alt={item.name}
                  className="w-full h-full object-cover mix-blend-luminosity group-hover:mix-blend-normal group-hover:scale-110 transition-all duration-700"
                  onError={(e) => { e.target.src = "https://images.unsplash.com/photo-1541167760496-1628856ab772?auto=format&fit=crop&q=80&w=600&h=600"; }}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#1a1714] via-transparent to-transparent opacity-90" />
              </div>

              <div className="p-6 flex-grow flex flex-col justify-between relative -mt-[4.5rem] bg-gradient-to-t from-[#1a1714] to-transparent">
                <div>
                  <motion.h3 layoutId={`title-${item.id}`} className="text-xl font-bold text-white tracking-tight leading-tight mb-2 drop-shadow-md">{item.name}</motion.h3>
                  <p className="text-[9px] text-[#dfc18b] font-bold tracking-[0.2em] uppercase mb-4 opacity-80">{item.category}</p>
                </div>
                
                <div className="flex justify-between items-end mt-4">
                  <p className="text-lg font-bold text-[#dfc18b]">₹{item.price?.toFixed(2)}</p>
                  <button className="w-10 h-10 rounded-full bg-white/10 border border-white/20 flex items-center justify-center text-white group-hover:bg-[#dfc18b] group-hover:text-[#1a1714] transition-all hover:scale-110">
                    <Plus size={18} />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </motion.div>

      {/* Modal */}
      <ProductModal
        product={selectedProduct}
        onClose={() => setSelectedProduct(null)}
        onAdd={(p) => handleAdd(p)}
        added={modalAdded}
      />
    </div>
  );
};

export default Menu;
