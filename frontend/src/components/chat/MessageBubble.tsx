'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { Copy, Check, Database } from 'lucide-react';
import { SourceCard } from './SourceCard';
import { type Source } from '@/store/useChatStore';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  sources?: Source[];
}

export const MessageBubble = ({ role, content, isStreaming, sources }: MessageBubbleProps) => {
  const isUser = role === 'user';
  const [copied, setCopied] = React.useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={cn(
        "flex w-full mb-10",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      <div className={cn(
        "max-w-[95%] sm:max-w-[85%] rounded-[32px] px-8 py-7 relative group transition-all duration-500",
        isUser 
          ? "bg-gradient-to-br from-indigo-500/90 to-indigo-700/90 text-white shadow-xl shadow-indigo-500/10 rounded-tr-none border border-white/10" 
          : "bg-surface-container/30 ghost-border ambient-shadow text-zinc-200 rounded-tl-none"
      )}>
        {/* Aura Identity Indicator */}
        {!isUser && (
          <div className="flex items-center gap-2 mb-6">
            <div className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-pulse shadow-[0_0_10px_rgba(129,140,248,0.5)]" />
            <span className="tracking-label text-zinc-500">Neural Sync Active</span>
          </div>
        )}

        <div className={cn(
          "text-[15px] leading-relaxed prose prose-invert max-w-none prose-headings:text-indigo-300 prose-headings:tracking-display prose-headings:mt-8 prose-headings:mb-4",
          isUser ? "text-indigo-50" : "text-zinc-200"
        )}>
          {!isUser && isStreaming && content === '' ? (
            <div className="flex items-center gap-3 text-indigo-400 font-mono text-[10px] uppercase tracking-[0.3em] my-4">
              <span className="animate-pulse">Synthesizing intelligence shards</span>
              <div className="flex gap-1.5">
                <span className="w-1 h-1 rounded-full bg-indigo-500 animate-bounce [animation-delay:-0.3s]" />
                <span className="w-1 h-1 rounded-full bg-indigo-500 animate-bounce [animation-delay:-0.15s]" />
                <span className="w-1 h-1 rounded-full bg-indigo-500 animate-bounce" />
              </div>
            </div>
          ) : (
            <div className={cn(!isUser && "space-y-6")}>
              {!isUser && !content.includes('##') && (
                <div className="flex items-center gap-2 mb-2 opacity-50">
                  <Database size={10} className="text-zinc-500" />
                  <span className="text-[9px] uppercase tracking-widest font-bold text-zinc-500">Neural Discovery Shard</span>
                </div>
              )}
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  // ... existing h2 decorator ...
                h2({ children }) {
                  const label = String(children);
                  const iconMatch = label.toLowerCase();
                  let Icon = Database;
                  if (iconMatch.includes('risk')) Icon = () => <span className="text-amber-500">⚠️</span>;
                  if (iconMatch.includes('alpha') || iconMatch.includes('result')) Icon = () => <span className="text-indigo-400">⚡</span>;
                  if (iconMatch.includes('model') || iconMatch.includes('method')) Icon = () => <span className="text-emerald-400">🧬</span>;

                  return (
                    <div className="flex flex-col gap-1 mt-10 mb-4 group/section">
                      <div className="flex items-center gap-2">
                        <div className="p-1 rounded bg-zinc-800/50 border border-zinc-700/50 group-hover/section:border-indigo-500/30 transition-colors">
                          <Icon />
                        </div>
                        <h2 className="text-xs uppercase tracking-[0.2em] font-bold text-indigo-300 m-0">{children}</h2>
                      </div>
                      <div className="h-[1px] w-full bg-gradient-to-r from-indigo-500/20 via-indigo-500/5 to-transparent mt-2" />
                    </div>
                  );
                },
                code({ node, inline, className, children, ...props }: any) {
                  // ... existing code ...
                  const match = /language-(\w+)/.exec(className || '');
                  const lang = match ? match[1] : '';
                  
                  return !inline ? (
                    <div className="relative my-8 rounded-2xl overflow-hidden border border-zinc-800 group/code">
                      <div className="flex items-center justify-between px-4 py-2 bg-zinc-900/80 border-b border-zinc-800">
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">{lang || 'shard'}</span>
                        <button
                          onClick={() => handleCopy(String(children))}
                          className="text-zinc-500 hover:text-indigo-400 transition-colors"
                        >
                          {copied ? <Check size={14} /> : <Copy size={14} />}
                        </button>
                      </div>
                      <SyntaxHighlighter
                        style={vscDarkPlus}
                        language={lang}
                        PreTag="div"
                        customStyle={{
                          margin: 0,
                          padding: '1.5rem',
                          background: '#0e0e10',
                          fontSize: '0.85rem',
                          lineHeight: '1.6',
                        }}
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    </div>
                  ) : (
                    <code className="bg-zinc-800/80 text-indigo-300 px-1.5 py-0.5 rounded-md text-[0.85em] font-mono border border-zinc-700/50" {...props}>
                      {children}
                    </code>
                  );
                },
                table({ children }) {
                  return (
                    <div className="my-8 overflow-x-auto rounded-2xl border border-zinc-800/80 shadow-inner shadow-black/20">
                      <table className="w-full border-collapse text-left text-[13px]">
                        {children}
                      </table>
                    </div>
                  );
                },
                th({ children }) {
                  return <th className="bg-zinc-900/80 p-4 font-bold border-b border-zinc-800 text-indigo-400 uppercase tracking-wider">{children}</th>;
                },
                td({ children }) {
                  return <td className="p-4 border-b border-zinc-800/40 text-zinc-400">{children}</td>;
                }
              }}
            >
              {content}
            </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Intelligence Shards (Citations) */}
        {!isUser && sources && sources.length > 0 && (
          <div className="mt-8 pt-6 border-t border-zinc-800/50 space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-700">
            <div className="flex items-center gap-2 text-zinc-500">
              <Database size={12} />
              <span className="text-[9px] uppercase tracking-[0.2em] font-bold">Intelligence Shards Retrieved</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {sources.map((source, idx) => (
                <SourceCard key={source.id || idx} source={source} />
              ))}
            </div>
          </div>
        )}

        {/* Streaming Shimmer */}
        {isStreaming && !isUser && (
          <div className="absolute inset-0 pointer-events-none rounded-[32px] overflow-hidden">
            <div className="w-full h-full bg-gradient-to-r from-transparent via-white/[0.02] to-transparent -translate-x-full animate-shimmer" />
          </div>
        )}
      </div>
    </motion.div>
  );
};
