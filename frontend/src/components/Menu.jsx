import { useEffect, useState } from "react";
import menuItems from "../data/menu_items.json";
import { MdAddCircle } from "react-icons/md";
import { FaSearch } from "react-icons/fa";
import { useCart } from "../context/CartContext";

const Menu = () => {
  const [products, setProducts] = useState([]);
  const [shownProducts, setShownProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [searchTerm, setSearchTerm] = useState("");
  const { addToCart } = useCart();
  // Placeholder animation
  const placeholders = [
    "Search for latte",
    "Search for cappuccino",
    "Search for espresso",
    "Search for mocha",
    "Search for americano",
  ];
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % placeholders.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const uniqueCategories = [
      "All",
      ...new Set(menuItems.map((item) => item.category)),
    ];
    setCategories(uniqueCategories);
    setProducts(menuItems);
    setShownProducts(menuItems);
  }, []);

  useEffect(() => {
    let filtered = [...products];
    if (selectedCategory !== "All") {
      filtered = filtered.filter((item) => item.category === selectedCategory);
    }
    if (searchTerm.trim()) {
      filtered = filtered.filter((item) =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    setShownProducts(filtered);
  }, [selectedCategory, searchTerm, products]);

  const handleAddToCart = (item) => {
    console.log("Added to cart:", item.name);
    // Future: update context or state
    addToCart(item);
  };

  return (
    <div className="min-h-screen bg-[#F2E6D9] text-[#4B3832] px-4 py-6">
      {/* Search + Categories */}
      <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        {/* Search Input */}
        <div className="relative w-full md:w-1/2 max-w-md">
          <FaSearch className="absolute top-3.5 left-3 text-[#4B3832]" />
          <input
            type="text"
            placeholder={placeholders[placeholderIndex]}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-3 rounded-full bg-[#f5efe6] text-[#4B3832] placeholder-[#9c7e6c] border border-[#4B3832] focus:outline-none shadow-inner transition-all"
          />
        </div>

        {/* Category Filter Buttons */}
        <div className="flex flex-wrap justify-center md:justify-end gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                selectedCategory === cat
                  ? "bg-[#4B3832] text-white"
                  : "bg-[#e0d3c0] text-[#4B3832] hover:bg-[#d1bfa5]"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Product Grid */}
      <div className="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 transition-all">
        {shownProducts.length === 0 ? (
          <p className="col-span-full text-center text-[#9c7e6c]">
            No matching items found ☕
          </p>
        ) : (
          shownProducts.map((item, index) => (
            <div
              key={index}
              className="bg-[#fefcf9] border border-[#e5d6c6] shadow rounded-2xl overflow-hidden transition-transform hover:scale-105 duration-300"
            >
              <div className="relative">
                <img
                  src={`/images/${item.image_path}`}
                  alt={`Coffee - ${item.name}`}
                  className="w-full h-48 object-cover"
                />
                <div className="absolute top-2 right-2 bg-[#ffe8b3] text-[#4B3832] text-xs font-bold px-2 py-1 rounded-full shadow-md">
                  ⭐ {item.rating}
                </div>
              </div>

              <div className="p-4">
                <h3 className="text-lg font-semibold">{item.name}</h3>
                <p className="text-sm text-[#9c7e6c] mb-2">{item.category}</p>

                <div className="flex justify-between items-center">
                  <p className="text-lg font-bold text-[#b68d40]">
                    ${item.price.toFixed(2)}
                  </p>
                  <button
                    onClick={() => handleAddToCart(item)}
                    className="text-[#4B3832] hover:text-[#3a2d27] transition-transform hover:scale-110"
                  >
                    <MdAddCircle size={32} />
                  </button>
                </div>

                <button className="mt-2 text-sm text-[#4B3832] hover:underline">
                  See Details...
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Menu;
