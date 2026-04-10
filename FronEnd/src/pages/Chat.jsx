import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { sendMessageAPI, createChatAPI, getMessagesAPI } from "../services/api";
import { useAuth } from "../context/AuthContext";
import Sidebar from "../components/Sidebar";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentChatId, setCurrentChatId] = useState(null);
  const [showNewChatDialog, setShowNewChatDialog] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState("");
  const [chatsRefresh, setChatsRefresh] = useState(0);
  const [loadingMessages, setLoadingMessages] = useState(false);

  const { logout } = useAuth();
  const navigate = useNavigate();
  const bottomRef = useRef(null);

  // Auto scroll to bottom whenever messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load messages when currentChatId changes
  useEffect(() => {
    if (currentChatId) {
      loadMessages(currentChatId);
    } else {
      setMessages([]);
    }
  }, [currentChatId]);

  const loadMessages = async (chatId) => {
    try {
      setLoadingMessages(true);
      const res = await getMessagesAPI(chatId);
      const apiMessages = res.data.messages || [];
      // Transform API messages to UI format
      const uiMessages = apiMessages.map((msg) => ({
        sender: msg.role === "user" ? "user" : "bot",
        text: msg.content
      }));
      setMessages(uiMessages);
    } catch (err) {
      console.error("Failed to load messages:", err);
      setMessages([]);
    } finally {
      setLoadingMessages(false);
    }
  };

  const handleNewChat = () => {
    setNewChatTitle("");
    setShowNewChatDialog(true);
  };

  const handleCreateChat = async () => {
    if (!newChatTitle.trim()) {
      alert("Please enter a chat title");
      return;
    }

    try {
      const res = await createChatAPI(newChatTitle);
      const newChatId = res.data.chat_id;
      
      // Close dialog and reset
      setShowNewChatDialog(false);
      setNewChatTitle("");
      
      // Refresh chat list and select new chat
      setChatsRefresh((prev) => prev + 1);
      setCurrentChatId(newChatId);
    } catch (err) {
      console.error("Failed to create chat:", err);
      alert("Failed to create chat. Please try again.");
    }
  };

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !currentChatId) return;

    const userMessage = input.trim();
    setInput("");

    // Show user message immediately
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setLoading(true);

    try {
      const res = await sendMessageAPI(currentChatId, userMessage);
      const botReply = res.data.reply;
      setMessages((prev) => [...prev, { sender: "bot", text: botReply }]);
    } catch (err) {
      console.error("Chat API error:", err);
      const errorMessage = err.response?.data?.detail || err.message || "Something went wrong. Please try again.";
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: errorMessage },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-purple-50 to-pink-100 flex">
      {/* Sidebar */}
      <Sidebar
        currentChatId={currentChatId}
        onSelectChat={setCurrentChatId}
        onNewChat={handleNewChat}
        onChatsRefresh={chatsRefresh}
      />

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="bg-white shadow-lg border-b border-gray-200 p-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
              🤖
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-800">AI Assistant</h3>
              <p className="text-sm text-gray-500">{currentChatId ? "Chat active" : "Select a chat to start"}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors duration-200 font-medium"
          >
            Logout
          </button>
        </div>

        {/* Messages Area */}
        {currentChatId ? (
          <>
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-transparent to-gray-50">
              {loadingMessages ? (
                <div className="text-center text-gray-500 py-4">Loading messages...</div>
              ) : messages.length === 0 ? (
                <div className="text-center text-gray-500 py-4">Start the conversation!</div>
              ) : (
                messages.map((msg, i) => (
                  <div
                    key={i}
                    className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl shadow-sm ${
                        msg.sender === "user"
                          ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-br-sm"
                          : "bg-white text-gray-800 border border-gray-200 rounded-bl-sm"
                      }`}
                    >
                      <p className="text-sm leading-relaxed">{msg.text}</p>
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="flex justify-start animate-pulse">
                  <div className="bg-white text-gray-800 px-4 py-3 rounded-2xl rounded-bl-sm border border-gray-200 shadow-sm">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-sm text-gray-500">AI is thinking...</span>
                    </div>
                  </div>
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white border-t border-gray-200 p-4">
              <form onSubmit={handleSend} className="flex space-x-3">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    placeholder="Type your message here..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={loading}
                    className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 bg-gray-50 disabled:bg-gray-100"
                  />
                  <button
                    type="button"
                    className="absolute right-2 top-2 text-gray-400 hover:text-gray-600 transition-colors duration-200"
                  >
                    😊
                  </button>
                </div>
                <button
                  type="submit"
                  disabled={loading || !input.trim()}
                  className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-500 text-white px-6 py-3 rounded-full font-medium transition-all duration-200 transform hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
                >
                  {loading ? "..." : "Send"}
                </button>
              </form>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <div className="text-6xl mb-4">💬</div>
              <h2 className="text-2xl font-semibold text-gray-800 mb-2">No Chat Selected</h2>
              <p className="text-gray-600">Select a chat from the sidebar or create a new one to get started</p>
            </div>
          </div>
        )}
      </div>

      {/* New Chat Dialog */}
      {showNewChatDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Create New Chat</h2>
            <input
              type="text"
              placeholder="Enter chat title..."
              value={newChatTitle}
              onChange={(e) => setNewChatTitle(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleCreateChat()}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-4"
              autoFocus
            />
            <div className="flex space-x-3">
              <button
                onClick={() => setShowNewChatDialog(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors duration-200"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateChat}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:opacity-90 transition-opacity duration-200"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}