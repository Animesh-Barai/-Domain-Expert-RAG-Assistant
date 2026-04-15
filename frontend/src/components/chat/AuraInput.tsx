'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Loader2 } from 'lucide-react';
import { useDocumentStore } from '@/store/useDocumentStore';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface AuraInputProps {
  onSend: (content: string) => void;
  isLoading?: boolean;
}

export const AuraInput = ({ onSend, isLoading }: AuraInputProps) => {
  const [content, setContent] = useState('');
  const { openModal } = useDocumentStore();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (content.trim() && !isLoading) {
      onSend(content.trim());
      setContent('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'inherit';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = `${Math.min(scrollHeight, 200)}px`;
    }
  }, [content]);

  return (
    <div className="w-full max-w-4xl mx-auto px-4 pb-8 pt-2">
      <div className={cn(
        "relative flex items-end gap-2 bg-[#0e0e10] border border-zinc-800/50 rounded-2xl p-2 transition-all duration-300",
        "focus-within:border-indigo-500/50 focus-within:ring-1 focus-within:ring-indigo-500/50 shadow-2xl shadow-black/50"
      )}>
        <button 
          onClick={openModal}
          title="Open Intelligence Vault"
          className="p-2.5 text-zinc-500 hover:text-indigo-400 transition-colors"
        >
          <Paperclip size={20} />
        </button>

        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Query the neural void..."
          className="flex-1 bg-transparent border-none text-zinc-200 placeholder:text-zinc-600 resize-none py-2.5 outline-none text-sm max-h-[200px] custom-scrollbar"
          rows={1}
        />

        <button
          onClick={handleSend}
          disabled={!content.trim() || isLoading}
          className={cn(
            "p-2.5 rounded-xl transition-all duration-300",
            content.trim() && !isLoading 
              ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/20 hover:scale-105 active:scale-95" 
              : "bg-zinc-800 text-zinc-500 cursor-not-allowed"
          )}
        >
          {isLoading ? <Loader2 size={18} className="animate-spin" /> : <Send size={18} />}
        </button>
      </div>
      <p className="text-[10px] text-zinc-600 text-center mt-3 tracking-tight uppercase">
        Encrypted Sync Active • Domain Expert Protocol v1.0
      </p>
    </div>
  );
};
