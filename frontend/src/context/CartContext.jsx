import { createContext, useContext, useState, useEffect, useRef } from "react";
import { ordersAPI, productsAPI } from "../services/api";
import { useAuth } from "./AuthContext";

const CartContext = createContext();

export const useCart = () => useContext(CartContext);

export const CartProvider = ({ children }) => {
  const { user } = useAuth();
  const [cartItems, setCartItems] = useState([]);
  const syncTimer = useRef(null);   // debounce timer
  const latestItems = useRef([]);   // always holds latest cart for sync

  // Load active order from backend when user logs in
  useEffect(() => {
    if (!user) {
      setCartItems([]);
      latestItems.current = [];
      return;
    }
    // Load cart + enrich with product images in one go
    Promise.all([ordersAPI.getActive(), productsAPI.getAll()])
      .then(([order, products]) => {
        if (!order.items?.length) return;
        const imageMap = Object.fromEntries(products.map((p) => [p.name, p.image_url]));
        const loaded = order.items.map((i) => ({
          name: i.name,
          price: i.per_unit_price,
          quantity: i.quantity,
          total_price: i.total_price,
          image_url: imageMap[i.name] || null,
        }));
        setCartItems(loaded);
        latestItems.current = loaded;
      })
      .catch(() => {});
  }, [user]);

  // Debounced sync — waits 400ms after last change then pushes to backend
  const scheduleSync = (items) => {
    latestItems.current = items;
    if (syncTimer.current) clearTimeout(syncTimer.current);
    syncTimer.current = setTimeout(async () => {
      if (!user) return;
      try {
        if (latestItems.current.length === 0) {
          await ordersAPI.clearActive();
        } else {
          await ordersAPI.updateActive(
            latestItems.current.map((i) => ({
              name: i.name,
              quantity: i.quantity,
              per_unit_price: i.price ?? i.per_unit_price,
            }))
          );
        }
      } catch (e) {
        console.error("Order sync failed:", e.message);
      }
    }, 400);
  };

  const addToCart = (product) => {
    setCartItems((prev) => {
      const existing = prev.find((item) => item.name === product.name);
      const updated = existing
        ? prev.map((item) =>
            item.name === product.name
              ? { ...item, quantity: item.quantity + 1 }
              : item
          )
        : [...prev, { ...product, quantity: 1 }];
      scheduleSync(updated);
      return updated;
    });
  };

  const removeFromCart = (name) => {
    setCartItems((prev) => {
      const updated = prev.filter((item) => item.name !== name);
      scheduleSync(updated);
      return updated;
    });
  };

  const updateCartItem = (product, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(product.name);
      return;
    }
    setCartItems((prev) => {
      const updated = prev.map((item) =>
        item.name === product.name ? { ...item, quantity: newQuantity } : item
      );
      scheduleSync(updated);
      return updated;
    });
  };

  const clearCart = () => {
    setCartItems([]);
    scheduleSync([]);
  };

  // Pull latest order from backend and sync into cart — called after bot responds
  const refreshCart = async () => {
    if (!user) return;
    try {
      const [order, products] = await Promise.all([ordersAPI.getActive(), productsAPI.getAll()]);
      const imageMap = Object.fromEntries(products.map((p) => [p.name, p.image_url]));
      const loaded = (order.items || []).map((i) => ({
        name: i.name,
        price: i.per_unit_price,
        quantity: i.quantity,
        total_price: i.total_price,
        image_url: imageMap[i.name] || null,
      }));
      setCartItems(loaded);
      latestItems.current = loaded;
    } catch {}
  };

  return (
    <CartContext.Provider value={{ cartItems, addToCart, removeFromCart, updateCartItem, clearCart, refreshCart }}>
      {children}
    </CartContext.Provider>
  );
};
