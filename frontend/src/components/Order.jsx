import { useState, useEffect } from "react";
import { useCart } from "../context/CartContext";
import { useNavigate } from "react-router-dom";

const PLATFORM_FEE = 4;
const DISCOUNT_RATE = 0.1;
const PROMO_CODE = "SUMMER10";

const Order = () => {
  const { cartItems, removeFromCart, updateCartItem } = useCart();
  const [promoCode, setPromoCode] = useState("");
  const [originalTotal, setOriginalTotal] = useState(0);
  const [discountAmount, setDiscountAmount] = useState(0);
  const [total, setTotal] = useState(0);
  const [discountApplied, setDiscountApplied] = useState(false);
  const navigate = useNavigate();

  const calculateTotals = (items, isDiscountApplied) => {
    const subtotal = items.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    );
    const discount = isDiscountApplied ? subtotal * DISCOUNT_RATE : 0;
    const grandTotal = subtotal - discount + PLATFORM_FEE;

    setOriginalTotal(subtotal);
    setDiscountAmount(discount);
    setTotal(grandTotal);
  };

  // Recalculate totals whenever cart changes or discount status changes
  useEffect(() => {
    calculateTotals(cartItems, discountApplied);
  }, [cartItems, discountApplied]);

  const handleQuantityChange = (item, newQuantity) => {
    if (newQuantity < 1) {
      removeFromCart(item.name);
      return;
    }

    updateCartItem(item, newQuantity);

    const updatedCart = cartItems.map((cartItem) =>
      cartItem.name === item.name
        ? { ...cartItem, quantity: newQuantity }
        : cartItem
    );

    calculateTotals(updatedCart, discountApplied);
  };

  const applyDiscount = () => {
    if (promoCode === PROMO_CODE && !discountApplied) {
      setDiscountApplied(true);
    } else if (discountApplied) {
      alert("Promo code already applied");
    } else {
      alert("Invalid promo code");
    }
  };

  return (
    <>
      <div className="min-h-screen bg-[#F2E6D9] text-[#4B3832] px-6 py-8">
        <h2 className="text-3xl font-bold mb-8">Your Order</h2>

        {cartItems.length === 0 ? (
          <div className="text-center">
            <p className="mb-4 text-lg">
              Your cart is empty. Start adding items from our menu!
            </p>
            <button
              onClick={() => navigate("/menu")}
              className="mt-4 bg-[#4B3832] hover:bg-[#3a2d27] text-white py-2 px-6 rounded-full transition"
            >
              Go to Menu
            </button>
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row justify-between gap-6">
            {/* Cart Items */}
            <div className="flex-1 space-y-6">
              {cartItems.map((item, idx) => (
                <div
                  key={idx}
                  className="flex items-center bg-white border border-gray-300 rounded-md p-4 shadow-sm"
                >
                  <img
                    src={`/images/${item.image_path}`}
                    alt={item.name}
                    className="w-20 h-20 object-cover rounded mr-4"
                  />
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold">{item.name}</h3>
                    <div className="flex items-center mt-2">
                      <button
                        onClick={() =>
                          handleQuantityChange(item, item.quantity - 1)
                        }
                        className="bg-gray-200 text-black px-2 py-1 rounded hover:bg-gray-300"
                      >
                        -
                      </button>
                      <span className="px-3">{item.quantity}</span>
                      <button
                        onClick={() =>
                          handleQuantityChange(item, item.quantity + 1)
                        }
                        className="bg-gray-200 text-black px-2 py-1 rounded hover:bg-gray-300"
                      >
                        +
                      </button>
                    </div>
                    <div className="mt-2 text-sm">
                      <span className="text-gray-500 line-through mr-2">
                        ₹{(item.price * 1.5).toFixed(2)}
                      </span>
                      <span className="text-green-600 font-semibold">
                        ₹{(item.price * item.quantity).toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Summary Box */}
            <div className="bg-white border border-gray-300 p-6 rounded-lg shadow-md w-full max-w-sm sticky top-6 self-start">
              <h4 className="text-xl font-semibold mb-4">PRICE DETAILS</h4>
              <div className="flex justify-between mb-2">
                <span>Price ({cartItems.length} items)</span>
                <span>₹{originalTotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between mb-2 text-green-600">
                <span>Discount</span>
                <span>-₹{discountAmount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span>Platform Fee</span>
                <span>₹{PLATFORM_FEE}</span>
              </div>
              <hr className="my-4" />
              <div className="flex justify-between text-lg font-bold">
                <span>Total Amount</span>
                <span>₹{total.toFixed(2)}</span>
              </div>
              <p className="text-green-600 mt-2 font-medium">
                You will save ₹{discountAmount.toFixed(2)} on this order
              </p>

              {/* Promo Code */}
              <div className="flex gap-2 mt-4">
                <input
                  type="text"
                  value={promoCode}
                  onChange={(e) => setPromoCode(e.target.value)}
                  placeholder="Promo Code"
                  className="flex-grow p-3 rounded-md border border-gray-400 text-black placeholder-gray-500 focus:outline-none"
                  disabled={discountApplied}
                />
                <button
                  onClick={applyDiscount}
                  disabled={discountApplied}
                  className={`px-5 rounded-md text-white font-medium transition ${
                    discountApplied
                      ? "bg-gray-400 cursor-not-allowed"
                      : "bg-[#4B3832] hover:bg-[#3a2d27]"
                  }`}
                >
                  Apply
                </button>
              </div>

              <button
                className="mt-6 w-full bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-md font-semibold transition"
                onClick={() => alert("Order Placed!")}
              >
                PLACE ORDER
              </button>

              <button
                onClick={() => navigate("/menu")}
                className="mt-4 w-full bg-[#b68d40] hover:bg-[#a37b2c] text-white py-3 rounded-md font-semibold transition"
              >
                Add More Items
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default Order;
