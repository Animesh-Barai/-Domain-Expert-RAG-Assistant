'use client';

import React, { useState, useCallback } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { useDocumentStore } from '@/store/useDocumentStore';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const DropZone = () => {
  const { uploadDocument, isUploading, error } = useDocumentStore();
  const [isDragActive, setIsDragActive] = useState(false);

  const onDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      try {
        await uploadDocument(file);
      } catch (err) {
        // Error handled in store
      }
    }
  }, [uploadDocument]);

  const onFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      try {
        await uploadDocument(e.target.files[0]);
      } catch (err) {
        // Error handled in store
      }
    }
  };

  return (
    <div className="w-full space-y-4">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragActive(true); }}
        onDragLeave={() => setIsDragActive(false)}
        onDrop={onDrop}
        className={cn(
          "relative border-2 border-dashed rounded-3xl p-12 transition-all duration-500 flex flex-col items-center text-center space-y-4 group overflow-hidden",
          isDragActive 
            ? "border-indigo-500 bg-indigo-500/5 scale-[1.01]" 
            : "border-zinc-800 bg-[#0e0e10] hover:border-zinc-700",
          isUploading && "opacity-60 cursor-not-allowed border-indigo-500/30"
        )}
      >
        {/* Animated Background Shimmer */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden opacity-20">
          <div className="w-full h-full bg-gradient-to-r from-transparent via-indigo-500/10 to-transparent -translate-x-full group-hover:animate-shimmer" />
        </div>

        <div className={cn(
          "w-16 h-16 rounded-2xl flex items-center justify-center transition-all duration-300",
          isDragActive ? "bg-indigo-500 text-white" : "bg-zinc-800 text-zinc-500"
        )}>
          {isUploading ? (
            <div className="w-8 h-8 border-2 border-zinc-600 border-t-white rounded-full animate-spin" />
          ) : (
            <Upload size={32} className={cn(isDragActive && "animate-pulse")} />
          )}
        </div>

        <div className="space-y-1 relative z-10">
          <h3 className="text-sm font-bold text-zinc-200 uppercase tracking-widest">
            {isUploading ? "Ingesting Fragment..." : "Intelligence Sync"}
          </h3>
          <p className="text-xs text-zinc-500">
            {isDragActive ? "Release to begin sync" : "Drag PDF fragments or click to browse"}
          </p>
        </div>

        <input
          type="file"
          accept=".pdf"
          disabled={isUploading}
          onChange={onFileChange}
          className="absolute inset-0 opacity-0 cursor-pointer"
        />

        {/* Status Indicators */}
        <AnimatePresence>
          {error && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="absolute bottom-4 flex items-center gap-2 text-[10px] font-bold text-red-400 bg-red-500/10 px-3 py-1.5 rounded-full border border-red-500/20"
            >
              <AlertCircle size={12} />
              {error}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <p className="text-[10px] text-zinc-600 font-medium text-center italic">
        Aura currently processes PDF vectors exclusively • Max 25MB per fragment
      </p>
    </div>
  );
};
