'use client';

import React from 'react';
import { motion } from 'framer-motion';

export const AuthCard = ({ 
  children, 
  title, 
  subtitle 
}: { 
  children: React.ReactNode; 
  title: string; 
  subtitle?: string;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="w-full max-w-md p-8 glass-panel rounded-3xl relative overflow-hidden group shadow-2xl shadow-indigo-500/5"
    >
      {/* Decorative Glow */}
      <div className="absolute -top-24 -right-24 w-48 h-48 bg-indigo-500/10 blur-[80px] rounded-full group-hover:bg-indigo-500/15 transition-colors duration-500" />
      
      <div className="space-y-6 relative z-10">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold tracking-tight text-white gradient-text">
            {title}
          </h1>
          {subtitle && (
            <p className="text-sm text-zinc-400">
              {subtitle}
            </p>
          )}
        </div>

        <div className="space-y-4">
          {children}
        </div>
      </div>
    </motion.div>
  );
};
