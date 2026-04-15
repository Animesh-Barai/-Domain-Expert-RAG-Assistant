'use client';

import React, { useEffect, useRef } from 'react';
import { MessageBubble } from './MessageBubble';
import { useChatStore } from '@/store/useChatStore';
import { motion, AnimatePresence } from 'framer-motion';

export const ChatFeed = () => {
  const { messages, isStreaming } = useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-8 animate-in fade-in duration-700">
        <div className="space-y-4 max-w-md">
          <h2 className="text-4xl font-bold tracking-tighter text-white gradient-text">Neural Workspace</h2>
          <p className="text-zinc-500 text-sm leading-relaxed">
            The void is open. Aura is ready to ingest and analyze your domain knowledge with high-precision RAG protocols.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl">
          {[
            "Analyze current project architecture...",
            "Identify security bottlenecks in v1.0",
            "Synthesize RAG optimization strategy",
            "Explore neural sync possibilities"
          ].map((prompt, idx) => (
            <button 
              key={idx}
              className="p-4 rounded-2xl bg-[#201f22] border border-zinc-800/50 text-zinc-400 text-xs font-medium hover:border-indigo-500/50 hover:text-indigo-300 transition-all text-left group"
            >
              <span className="opacity-0 group-hover:opacity-100 mr-2 text-indigo-500 transition-opacity">→</span>
              {prompt}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-0 relative">
      <div className="pulse-ribbon sticky top-0 z-10" />
      
      <div className="flex-1 overflow-y-auto custom-scrollbar px-4 sm:px-8 py-10 space-y-2">
        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="popLayout">
            {messages.map((msg, idx) => (
              <MessageBubble 
                key={msg.id || idx} 
                role={msg.role} 
                content={msg.content} 
                sources={msg.sources}
                isStreaming={isStreaming && idx === messages.length - 1}
              />
            ))}
          </AnimatePresence>
          <div ref={bottomRef} className="h-8" />
        </div>
      </div>
    </div>
  );
};
