"use client";

import { useState } from "react";

interface SidebarProps {
  onNewChat: () => void;
}

interface Conversation {
  id: string;
  title: string;
  time: string;
}

export function Sidebar({ onNewChat }: SidebarProps) {
  const [conversations, setConversations] = useState<Conversation[]>([
    { id: "1", title: "Product Inventory Query", time: "2 hours ago" },
    { id: "2", title: "Customer Support Analysis", time: "Yesterday" },
    { id: "3", title: "Sales Data Review", time: "2 days ago" },
  ]);

  const handleDeleteConversation = (id: string) => {
    setConversations((prev) => prev.filter((conv) => conv.id !== id));
  };

  return (
    <aside className="w-64 bg-nvidia-dark border-r border-nvidia-border flex flex-col h-screen relative z-20">
      {/* Header / New Chat */}
      <div className="p-4">
        <button
          onClick={onNewChat}
          className="w-full flex items-center gap-3 bg-nvidia-dark-surface hover:bg-nvidia-dark-elevated border border-nvidia-border hover:border-nvidia-green/30 text-nvidia-text font-medium px-4 py-3 rounded-lg transition-all duration-200 group"
        >
          <div className="p-1 rounded bg-nvidia-green/10 text-nvidia-green group-hover:bg-nvidia-green group-hover:text-nvidia-dark transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          </div>
          <span className="text-sm">New Chat</span>
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto px-2 space-y-1 custom-scrollbar">
        <div className="px-4 py-2 text-xs font-semibold text-nvidia-text-muted uppercase tracking-wider opacity-60">
          Recent
        </div>

        {conversations.map((conv) => (
          <div
            key={conv.id}
            className="group relative w-full px-3 py-2.5 rounded-lg hover:bg-nvidia-dark-surface transition-colors duration-200 cursor-pointer"
            onClick={() => console.log("Selected conversation:", conv.id)}
          >
            <div className="flex items-center justify-between gap-2">
              <div className="flex-1 min-w-0">
                <h3 className="text-nvidia-text text-sm truncate group-hover:text-white transition-colors">
                  {conv.title}
                </h3>
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteConversation(conv.id);
                }}
                className="opacity-0 group-hover:opacity-100 text-nvidia-text-muted hover:text-nvidia-red p-1 rounded hover:bg-nvidia-red/10 transition-all"
                aria-label="Delete conversation"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* User Profile / Footer */}
      <div className="p-4 border-t border-nvidia-border bg-nvidia-dark">
        <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-nvidia-dark-surface transition-colors cursor-pointer">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-nvidia-green to-nvidia-green-hover flex items-center justify-center text-nvidia-dark font-bold text-xs shadow-lg shadow-nvidia-green/20">
            AI
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-nvidia-text text-sm font-medium truncate">
              Retail Agent
            </p>
            <p className="text-nvidia-text-muted text-xs truncate opacity-70">
              NVIDIA Enterprise
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
