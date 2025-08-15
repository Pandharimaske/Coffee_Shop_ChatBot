import { useState } from "react";
import { Link } from "react-router-dom"; // Use if you're using React Router for navigation
import {
  FaHome,
  FaConciergeBell,
  FaShoppingCart,
  FaComment,
} from "react-icons/fa"; // Importing icons from react-icons

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(true);

  const toggleSidebar = () => setIsOpen(!isOpen);

  return (
    <div className="flex bg-red-300">
      <div
        className={`bg-gray-800 text-white w-64 h-full fixed top-0 left-0 transition-all duration-300 ${
          isOpen
            ? "transform-none opacity-100 visible"
            : "-translate-x-full opacity-0 invisible"
        } ${isOpen ? "pointer-events-auto" : "pointer-events-none"}`}
      >
        <div className="flex justify-between items-center p-4">
          <h2 className="text-xl font-bold">Coffee Shop</h2>
          <button onClick={toggleSidebar} className="text-2xl text-white">
            {isOpen ? "×" : "≡"}
          </button>
        </div>
        <nav>
          <ul>
            <li className="hover:bg-gray-700 p-4 flex items-center">
              <FaHome size={20} className="mr-3" />
              <Link to="/home" className="block">
                Home
              </Link>
            </li>
            <li className="hover:bg-gray-700 p-4 flex items-center">
              <FaConciergeBell size={20} className="mr-3" />
              <Link to="/menu" className="block">
                Menu
              </Link>
            </li>
            <li className="hover:bg-gray-700 p-4 flex items-center">
              <FaShoppingCart size={20} className="mr-3" />
              <Link to="/order" className="block">
                Order
              </Link>
            </li>
            <li className="hover:bg-gray-700 p-4 flex items-center">
              <FaComment size={20} className="mr-3" />
              <Link to="/chatroom" className="block">
                Chatroom
              </Link>
            </li>
          </ul>
        </nav>
      </div>
      {/* Main content */}
      <div className={`transition-all ml-64 w-full ${isOpen ? "" : "ml-20"}`}>
        {/* Your main content will go here */}
      </div>
    </div>
  );
};

export default Sidebar;
