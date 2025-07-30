import { useEffect, useState, useRef } from "react";
import { FaPaperPlane, FaRobot } from "react-icons/fa";

// Spinner for loading
const Spinner = () => (
  <div className="w-5 h-5 border-2 border-t-transparent border-white rounded-full animate-spin"></div>
);
const formatTime = (timestamp) => {
  if (!timestamp) return "";
  return new Date(timestamp).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
};

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isChatOpen, setIsChatOpen] = useState(false);
  const textRef = useRef("");
  const inputRef = useRef(null);
  const chatContainerRef = useRef(null);

  const toggleChat = () => {
    setIsChatOpen(!isChatOpen);
  };

  // Load saved messages
  useEffect(() => {
    const saved = localStorage.getItem("chat");
    if (saved) setMessages(JSON.parse(saved));
  }, []);

  // Save messages to local storage
  useEffect(() => {
    localStorage.setItem("chat", JSON.stringify(messages));
  }, [messages]);

  // Initial greeting (only once)
  useEffect(() => {
    if (isChatOpen && messages.length === 0) {
      const alreadyGreeted = localStorage.getItem("greeted");
      if (!alreadyGreeted) {
        setMessages([
          {
            role: "bot",
            content:
              "Hello! Welcome back to Merry's Way ☕ What can I get you today?",
            timestamp: new Date(),
          },
        ]);
        localStorage.setItem("greeted", "true");
      }
    }
  }, [isChatOpen]);

  // Auto-scroll chat window
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop =
        chatContainerRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = async () => {
    let message = textRef.current.trim();
    if (!message) return;

    const userMessage = {
      content: message,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    textRef.current = "";
    if (inputRef.current) inputRef.current.value = "";
    setIsTyping(true);

    try {
      const response = await fetch(
        "https://coffee-shop-chatbot.onrender.com/chat",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_input: message,
            user_id: "1",
          }),
        }
      );

      if (!response.ok)
        throw new Error(`HTTP error! status: ${response.status}`);

      const data = await response.json();
      setIsTyping(false);

      setMessages((prev) => [
        ...prev,
        {
          content: data.response,
          role: "bot",
          timestamp: new Date(),
        },
      ]);
    } catch (err) {
      console.error("Error sending message:", err);
      setIsTyping(false);
      console.log("err", err);
      setMessages((prev) => [
        ...prev,
        {
          content: "⚠️ Oops! Something went wrong. Please try again.",
          role: "bot",
          timestamp: new Date(),
        },
      ]);
    }
  };

  // Format time

  return (
    <>
      {!isChatOpen && (
        <button
          onClick={toggleChat}
          className="fixed bottom-6 right-6 bg-[#4B3832] text-white p-4 rounded-full shadow-lg hover:bg-[#3a2d27] transition z-50"
        >
          <FaRobot size={24} />
        </button>
      )}

      <div
        className={`fixed bottom-0 inset-x-4 sm:right-6 sm:inset-x-auto w-full sm:w-1/3 h-[80vh] sm:h-[500px] bg-[#fefcf9] shadow-2xl rounded-t-xl transform ${
          isChatOpen ? "translate-y-0" : "translate-y-full"
        } transition-transform duration-300 ease-in-out z-40 flex flex-col border border-[#d1beab]`}
      >
        {/* Header */}
        <div className="flex justify-between items-center p-4 bg-[#4B3832] text-white rounded-t-xl">
          <h2 className="text-lg font-semibold">Coffee Chatbot</h2>
          <button
            onClick={toggleChat}
            className="text-white text-xl hover:text-[#d1beab]"
          >
            ×
          </button>
        </div>

        {/* Chat Area */}
        <div
          ref={chatContainerRef}
          className="flex-grow overflow-y-auto p-4 space-y-3 bg-[#fefcf9] scrollbar-thin scrollbar-thumb-[#d1beab] scrollbar-track-[#fefcf9]"
        >
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-4 py-2 max-w-[80%] text-sm rounded-lg shadow-md relative ${
                  msg.role === "user"
                    ? "bg-[#4B3832] text-white rounded-br-none"
                    : "bg-[#d1beab] text-[#4B3832] rounded-bl-none"
                }`}
              >
                <div className="whitespace-pre-wrap">{msg.content}</div>
                <div className="text-[10px] text-right mt-1 opacity-60">
                  {formatTime(msg.timestamp)}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="p-2 max-w-xs bg-[#d1beab] text-[#4B3832] rounded-2xl shadow animate-pulse">
                Typing...
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t flex items-center space-x-2 bg-[#f5efe6] rounded-b-xl">
          <input
            ref={inputRef}
            type="text"
            placeholder="Type a message..."
            className="flex-grow p-2 rounded-full border border-gray-300 text-[#4B3832] bg-[#fffaf3]"
            onChange={(e) => (textRef.current = e.target.value)}
            onBlur={() => (textRef.current = inputRef.current?.value || "")}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
          />
          <button
            disabled={isTyping}
            onClick={handleSendMessage}
            className={`p-2 rounded-full ${
              isTyping ? "bg-gray-400" : "bg-[#4B3832] hover:bg-[#3a2d27]"
            } text-white flex items-center justify-center`}
          >
            {isTyping ? <Spinner /> : <FaPaperPlane size={20} />}
          </button>
        </div>
      </div>
    </>
  );
};

export default Chatbot;
