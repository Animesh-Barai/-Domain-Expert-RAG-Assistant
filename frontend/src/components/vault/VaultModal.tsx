'use client';

import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Cpu, Database, Info } from 'lucide-react';
import { DropZone } from './DropZone';
import { DocumentItem } from './DocumentItem';
import { useDocumentStore } from '@/store/useDocumentStore';

interface VaultModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const VaultModal = ({ isOpen, onClose }: VaultModalProps) => {
  const { documents, fetchDocuments, isLoading } = useDocumentStore();

  useEffect(() => {
    if (isOpen) {
      fetchDocuments();
    }
  }, [isOpen, fetchDocuments]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
          />

          {/* Modal Content */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative w-full max-w-2xl bg-[#131315] border border-zinc-800 rounded-[32px] shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
          >
            {/* Header */}
            <div className="p-8 border-b border-zinc-800/50 flex items-center justify-between bg-gradient-to-b from-zinc-900/50 to-transparent">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <Database size={20} className="text-indigo-400" />
                  <h2 className="text-2xl font-bold tracking-tight text-white gradient-text">Intelligence Vault</h2>
                </div>
                <p className="text-xs text-zinc-500 uppercase tracking-widest font-medium">Domain Expertise Repository</p>
              </div>
              <button
                onClick={onClose}
                className="p-2 rounded-xl bg-zinc-800/50 text-zinc-500 hover:text-zinc-200 hover:bg-zinc-800 transition-all"
              >
                <X size={20} />
              </button>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-8 custom-scrollbar space-y-10">
              {/* Upload Section */}
              <section className="space-y-4">
                <div className="flex items-center gap-2 text-zinc-400">
                  <Cpu size={16} />
                  <span className="text-xs font-bold uppercase tracking-tighter">New Ingestion</span>
                </div>
                <DropZone />
              </section>

              {/* Document List */}
              <section className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-zinc-400">
                    <Database size={16} />
                    <span className="text-xs font-bold uppercase tracking-tighter">Current Fragments</span>
                  </div>
                  <span className="text-[10px] bg-zinc-800 text-zinc-500 px-2 py-0.5 rounded-full font-bold">
                    {documents.length} Units
                  </span>
                </div>

                <div className="space-y-3">
                  {isLoading && documents.length === 0 ? (
                    <div className="py-20 flex flex-col items-center justify-center space-y-4">
                      <div className="w-8 h-8 border-2 border-indigo-500/20 border-t-indigo-500 rounded-full animate-spin" />
                      <p className="text-[10px] text-zinc-500 uppercase tracking-[0.2em]">Accessing Data Shards...</p>
                    </div>
                  ) : documents.length === 0 ? (
                    <div className="py-20 border border-dashed border-zinc-800 rounded-2xl flex flex-col items-center justify-center opacity-40">
                      <Info size={40} className="text-zinc-700 mb-2" />
                      <p className="text-sm italic text-zinc-600">No active fragments indexed.</p>
                    </div>
                  ) : (
                    documents.map((doc) => (
                      <DocumentItem key={doc.id} doc={doc} />
                    ))
                  )}
                </div>
              </section>
            </div>

            {/* Footer */}
            <div className="p-4 bg-zinc-900/30 border-t border-zinc-800/50 text-center">
              <p className="text-[9px] text-zinc-600 uppercase tracking-widest">
                Deep Mind RAG Protocol • All fragments are vector-encrypted
              </p>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};
