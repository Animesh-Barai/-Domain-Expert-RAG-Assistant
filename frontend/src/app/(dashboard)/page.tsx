'use client';

import React from 'react';
import { ChatFeed } from '@/components/chat/ChatFeed';
import { AuraInput } from '@/components/chat/AuraInput';
import { useChatStore } from '@/store/useChatStore';

export default function WorkspacePage() {
  const { sendMessage, isStreaming, activeChatId, createChat } = useChatStore();

  const handleSendMessage = async (content: string) => {
    let currentId = activeChatId;

    // If no active chat, create one automatically on first message
    if (!currentId) {
      const newChat = await createChat(content.substring(0, 30) + '...');
      currentId = newChat.id;
    }

    await sendMessage(content, true);
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Workspace Header - Glassmorphic overlay */}
      <header className="h-16 flex items-center px-8 border-b border-zinc-800/50 bg-[#131315]/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-glow shadow-emerald-500/50" />
          <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-zinc-400">Sync Pipeline Active</h2>
        </div>
      </header>

      {/* Chat Messages */}
      <ChatFeed />

      {/* Input Area */}
      <AuraInput onSend={handleSendMessage} isLoading={isStreaming} />
    </div>
  );
}
