'use client';

import React, { useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ChatFeed } from '@/components/chat/ChatFeed';
import { AuraInput } from '@/components/chat/AuraInput';
import { useChatStore } from '@/store/useChatStore';

export default function ChatSessionPage() {
  const { id } = useParams();
  const { fetchMessages, activeChatId, sendMessage, isStreaming } = useChatStore();

  useEffect(() => {
    if (id && typeof id === 'string') {
      fetchMessages(id);
    }
  }, [id, fetchMessages]);

  const handleSendMessage = async (content: string) => {
    await sendMessage(content, true);
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Session Header */}
      <header className="h-16 flex items-center px-8 border-b border-zinc-800/50 bg-[#131315]/80 backdrop-blur-md sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-indigo-500 shadow-glow shadow-indigo-500/50" />
          <h2 className="text-xs font-bold uppercase tracking-[0.2em] text-zinc-400">Sync Session Verified</h2>
        </div>
      </header>

      {/* Chat Messages */}
      <ChatFeed />

      {/* Input Area */}
      <AuraInput onSend={handleSendMessage} isLoading={isStreaming} />
    </div>
  );
}
