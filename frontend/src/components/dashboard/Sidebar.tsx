'use client';

import React, { useEffect } from 'react';
import { Plus, MessageSquare, Settings, LogOut, Database } from 'lucide-react';
import { useChatStore } from '@/store/useChatStore';
import { useAuthStore } from '@/store/useAuthStore';
import { useDocumentStore } from '@/store/useDocumentStore';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const Sidebar = () => {
  const { chats, fetchChats, createChat, isLoading } = useChatStore();
  const { openModal } = useDocumentStore();
  const { user, logout } = useAuthStore();
  const params = useParams();
  const router = useRouter();

  useEffect(() => {
    fetchChats();
  }, [fetchChats]);

  const handleNewChat = async () => {
    try {
      const chat = await createChat('New Intelligence Sync');
      router.push(`/chat/${chat.id}`);
    } catch (err) {
      console.error('Failed to create chat', err);
    }
  };

  return (
    <aside className="w-72 h-full flex flex-col bg-[#1c1b1d] border-r border-zinc-800/50 relative z-20">
      {/* App Branding */}
      <div className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-indigo-700 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <span className="text-white font-bold text-sm">A</span>
          </div>
          <span className="text-xl font-bold tracking-tight gradient-text">Aura</span>
        </div>
      </div>

      {/* New Chat Button */}
      <div className="px-4 mb-4">
        <button
          onClick={handleNewChat}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700/50 rounded-xl transition-all group"
        >
          <Plus size={18} className="text-indigo-400 group-hover:scale-110 transition-transform" />
          <span className="text-sm font-medium text-zinc-300">New Sync</span>
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto px-4 py-2 space-y-1 custom-scrollbar">
        <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-3 ml-2">Recent Synchronies</p>
        
        {chats.length === 0 && !isLoading && (
          <p className="text-xs text-zinc-600 italic ml-2">No active sessions...</p>
        )}

        {chats.map((chat) => {
          const isActive = params.id === chat.id;
          return (
            <Link 
              key={chat.id} 
              href={`/chat/${chat.id}`}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all group relative",
                isActive ? "bg-indigo-500/10 text-indigo-300" : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200"
              )}
            >
              <MessageSquare size={16} className={cn(isActive ? "text-indigo-400" : "text-zinc-500 group-hover:text-zinc-400")} />
              <span className="text-sm font-medium truncate">{chat.title}</span>
              {isActive && (
                <motion.div 
                  layoutId="active-pill"
                  className="absolute left-0 w-1 h-4 bg-indigo-500 rounded-full"
                />
              )}
            </Link>
          );
        })}
      </div>

      {/* Vault Trigger */}
      <div className="px-4 mb-4">
        <button
          onClick={openModal}
          className="w-full flex items-center gap-3 px-4 py-3 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 border border-transparent hover:border-zinc-800 rounded-xl transition-all"
        >
          <Database size={18} className="text-indigo-400" />
          <span className="text-xs font-bold uppercase tracking-widest">Intelligence Vault</span>
        </button>
      </div>

      {/* User Actions */}
      <div className="p-4 bg-zinc-900/30 border-t border-zinc-800/50">
        <div className="flex items-center gap-3 mb-4 px-2">
          <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-[10px] font-bold text-zinc-400">
            {user?.email?.substring(0, 2).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-zinc-200 truncate">{user?.email}</p>
            <p className="text-[10px] text-zinc-500">Explorer</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          <button className="flex items-center justify-center py-2 px-3 rounded-lg bg-zinc-800/50 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition-colors">
            <Settings size={16} />
          </button>
          <button 
            onClick={() => logout()}
            className="flex items-center justify-center py-2 px-3 rounded-lg bg-zinc-800/50 text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
};
