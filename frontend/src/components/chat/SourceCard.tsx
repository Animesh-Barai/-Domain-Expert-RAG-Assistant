'use client';

import React from 'react';
import { FileText, ExternalLink, Zap } from 'lucide-react';
import { type Source } from '@/store/useChatStore';
import { useDocumentStore } from '@/store/useDocumentStore';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface SourceCardProps {
  source: Source;
}

export const SourceCard = ({ source }: SourceCardProps) => {
  const { openModal } = useDocumentStore();
  
  // Calculate a visual "relevance" width based on score
  const relevanceWidth = Math.min(Math.max(source.score * 100, 10), 100);

  return (
    <div className="group flex flex-col gap-2 p-3 rounded-2xl bg-zinc-900/30 border border-zinc-800/50 hover:border-indigo-500/30 hover:bg-zinc-800/40 transition-all duration-300">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg bg-zinc-800 text-zinc-500 group-hover:text-amber-500 transition-colors">
            <FileText size={14} />
          </div>
          <div className="min-w-0">
            <p className="text-[10px] font-bold text-zinc-300 truncate lowercase tracking-tighter">
              {source.filename}
            </p>
            <p className="text-[9px] text-zinc-600 font-mono">
              Fragment p.{source.page_number}
            </p>
          </div>
        </div>
        
        <button 
          onClick={openModal}
          className="p-1.5 rounded-lg text-zinc-600 hover:text-indigo-400 hover:bg-indigo-500/10 transition-all"
          title="Inspect Source"
        >
          <ExternalLink size={12} />
        </button>
      </div>

      {/* Relevance Meter */}
      <div className="space-y-1">
        <div className="flex items-center justify-between text-[8px] uppercase tracking-widest font-bold text-zinc-600">
          <span className="flex items-center gap-1">
            <Zap size={8} /> Relevance
          </span>
          <span>{Math.round(relevanceWidth)}%</span>
        </div>
        <div className="h-1 w-full bg-zinc-800 rounded-full overflow-hidden">
          <div 
            className="h-full bg-indigo-500 transition-all duration-1000 ease-out"
            style={{ width: `${relevanceWidth}%` }}
          />
        </div>
      </div>
    </div>
  );
};
