'use client';

import React from 'react';
import { FileText, Trash2, CheckCircle2, Loader2, AlertCircle, Cpu } from 'lucide-react';
import { useDocumentStore, type Document, type DocumentStatus } from '@/store/useDocumentStore';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const statusConfig: Record<DocumentStatus, { label: string, color: string, icon: any }> = {
  PENDING: { label: 'In Queue', color: 'text-zinc-500 bg-zinc-500/10', icon: Loader2 },
  PROCESSING: { label: 'Analyzing', color: 'text-indigo-400 bg-indigo-500/10', icon: Cpu },
  COMPLETED: { label: 'Indexed', color: 'text-emerald-400 bg-emerald-500/10', icon: CheckCircle2 },
  FAILED: { label: 'Failed', color: 'text-red-400 bg-red-500/10', icon: AlertCircle },
};

export const DocumentItem = ({ doc }: { doc: Document }) => {
  const { deleteDocument } = useDocumentStore();
  const config = statusConfig[doc.status];
  const Icon = config.icon;

  const fileSize = (doc.file_size / (1024 * 1024)).toFixed(2);

  return (
    <div className="group relative bg-[#1c1b1d] border border-zinc-800/50 rounded-2xl p-4 flex items-center gap-4 hover:border-zinc-700/50 transition-all duration-300 shadow-lg shadow-black/20">
      <div className="w-12 h-12 rounded-xl bg-zinc-900 flex items-center justify-center text-zinc-500 group-hover:text-indigo-400 transition-colors">
        <FileText size={24} />
      </div>

      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-semibold text-zinc-200 truncate">{doc.filename}</h4>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-tighter">{fileSize} MB</span>
          <span className="text-zinc-700">•</span>
          <div className={cn(
            "flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-widest",
            config.color
          )}>
            <Icon size={10} className={cn(doc.status === 'PROCESSING' && "animate-spin")} />
            {config.label}
          </div>
        </div>
      </div>

      <button
        onClick={() => deleteDocument(doc.id)}
        className="opacity-0 group-hover:opacity-100 p-2 text-zinc-600 hover:text-red-400 transition-all rounded-lg hover:bg-red-500/10"
      >
        <Trash2 size={18} />
      </button>
    </div>
  );
};
