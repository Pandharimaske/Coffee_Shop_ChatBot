import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="bg-gradient-to-br from-[#F2E6D9] to-[#FFF8F0] min-h-screen flex flex-col items-center justify-center px-4 py-12">
      {/* Hero content */}
      <div className="max-w-7xl w-full flex flex-col md:flex-row items-center justify-between space-y-10 md:space-y-0">
        {/* Left Side Text */}
        <div className="md:w-1/2 space-y-6 text-center md:text-left">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-bold text-[#4B3832]">
            Your Personal Coffee Shop Assistant
          </h1>
          <p className="text-[#4B3832] text-base sm:text-lg">
            Order seamlessly, ask menu details, and get personalised
            recommendations instantly.
          </p>

          <div className="flex flex-row flex-wrap justify-center md:justify-start gap-4">
            <button className="bg-[#4B3832] text-white px-6 py-3 rounded-full shadow hover:bg-[#3a2d27] transition">
              Try Chatbot
            </button>
            <Link to={"/menu"}>
              <button className="border-2 border-[#4B3832] text-[#4B3832] px-6 py-3 rounded-full hover:bg-[#4B3832] hover:text-white transition">
                Explore Menu
              </button>
            </Link>
          </div>
        </div>

        {/* Right Side Image */}
        <div className="md:w-1/2 flex justify-center">
          <img
            src="/images/cappuccino.jpg"
            alt="Coffee Shop Chatbot"
            className="w-64 sm:w-80 md:w-[400px] rounded-xl shadow-xl"
          />
        </div>
      </div>
    </div>
  );
};

export default Home;
