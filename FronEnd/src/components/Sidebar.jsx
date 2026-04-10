import { useState, useEffect } from "react";
import { getAllChatsAPI, deleteChatAPI } from "../services/api";

export default function Sidebar({ currentChatId, onSelectChat, onNewChat, onChatsRefresh }) {
  const [chats, setChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Load all chats when component mounts or when refresh is needed
  useEffect(() => {
    loadChats();
  }, [onChatsRefresh]);

  const loadChats = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await getAllChatsAPI();
      setChats(res.data.chats || []);
    } catch (err) {
      console.error("Failed to load chats:", err);
      setError("Failed to load chats");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteChat = async (e, chatId) => {
    e.stopPropagation();
    
    if (!window.confirm("Delete this chat?")) return;

    try {
      await deleteChatAPI(chatId);
      // Refresh the chat list
      await loadChats();
      // If deleted chat was selected, clear selection
      if (currentChatId === chatId) {
        onSelectChat(null);
      }
    } catch (err) {
      console.error("Failed to delete chat:", err);
      alert("Failed to delete chat");
    }
  };

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full shadow-lg">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onNewChat}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-2 px-4 rounded-lg font-medium hover:opacity-90 transition-opacity duration-200 flex items-center justify-center space-x-2"
        >
          <span>+ New Chat</span>
        </button>
      </div>

      {/* Chat List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {loading ? (
          <div className="text-gray-500 text-sm text-center py-4">Loading chats...</div>
        ) : error ? (
          <div className="text-red-500 text-sm text-center py-4">{error}</div>
        ) : chats.length === 0 ? (
          <div className="text-gray-500 text-sm text-center py-4">No chats yet. Create one!</div>
        ) : (
          chats.map((chat) => (
            <div
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className={`p-3 rounded-lg cursor-pointer transition-all duration-200 group ${
                currentChatId === chat.id
                  ? "bg-gradient-to-r from-blue-100 to-purple-100 border-l-4 border-blue-500"
                  : "hover:bg-gray-100 border-l-4 border-transparent"
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-sm font-medium text-gray-800 truncate group-hover:text-gray-900">
                    {chat.title}
                  </h3>
                  <p className="text-xs text-gray-500 mt-1">
                    {new Date(chat.created_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  onClick={(e) => handleDeleteChat(e, chat.id)}
                  className="ml-2 opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-700 transition-opacity duration-200 p-1"
                  title="Delete chat"
                >
                  ✕
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
