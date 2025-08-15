import { Routes, Route, Link } from "react-router-dom";
import Menu from "./components/Menu";
import Order from "./components/Order";
import Home from "./components/Home";
import Chatbot from "./components/Chatbot";

// Temporary Login Component
const Login = () => <div className="p-4">Login Page</div>;

function App() {
  return (
    <div className="bg-[#d1beab] min-h-screen text-[#4B3832] relative">
      {/* Header Navbar */}
      <header className="bg-[#c69c6f] shadow-2xl">
        <div className="flex justify-between items-center px-6 py-4 max-w-7xl mx-auto">
          <div className="text-2xl font-bold text-[#4B3832]">Coffee Shop</div>
          <nav className="space-x-6">
            <Link
              to="/menu"
              className="text-[#4B3832] hover:text-[#3a2d27] font-medium"
            >
              Menu
            </Link>
            <Link
              to="/order"
              className="text-[#4B3832] hover:text-[#3a2d27] font-medium"
            >
              Order
            </Link>
            <Link
              to="/login"
              className="text-[#4B3832] hover:text-[#3a2d27] font-medium"
            >
              Login
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/menu" element={<Menu />} />
          <Route path="/order" element={<Order />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </main>

      {/* Chatbot Component with floating button */}
      <Chatbot />
    </div>
  );
}

export default App;
