'use client';

import React, { useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  showToggle?: boolean;
}

export const InputField = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, showToggle, type, className, ...props }, ref) => {
    const [isVisible, setIsVisible] = useState(false);
    const inputType = showToggle ? (isVisible ? 'text' : 'password') : type;

    return (
      <div className="w-full space-y-1.5">
        {label && (
          <label className="text-xs font-medium text-zinc-400 uppercase tracking-widest ml-1">
            {label}
          </label>
        )}
        <div className="relative group">
          <input
            {...props}
            type={inputType}
            ref={ref}
            className={cn(
              "w-full bg-zinc-900/50 border border-zinc-800 text-zinc-100 px-4 py-3 rounded-xl",
              "focus:outline-none focus:ring-1 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all duration-200",
              "placeholder:text-zinc-600",
              error && "border-red-500/50 focus:ring-red-500/50 focus:border-red-500/50",
              className
            )}
          />
          {showToggle && (
            <button
              type="button"
              onClick={() => setIsVisible(!isVisible)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300 transition-colors"
            >
              {isVisible ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          )}
        </div>
        {error && <p className="text-[10px] text-red-400 font-medium ml-1">{error}</p>}
      </div>
    );
  }
);

InputField.displayName = "InputField";

export const AuthButton = ({ 
  children, 
  isLoading, 
  variant = 'primary',
  className,
  ...props 
}: { 
  children: React.ReactNode; 
  isLoading?: boolean;
  variant?: 'primary' | 'secondary';
  className?: string;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) => {
  return (
    <button
      {...props}
      disabled={isLoading || props.disabled}
      className={cn(
        "w-full py-3.5 px-6 rounded-xl font-semibold transition-all duration-300 flex items-center justify-center gap-2",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        variant === 'primary' && "bg-gradient-to-br from-indigo-500 to-indigo-700 text-white shadow-lg shadow-indigo-500/20 hover:scale-[1.02] active:scale-[0.98]",
        variant === 'secondary' && "bg-zinc-800 text-zinc-100 hover:bg-zinc-700 border border-zinc-700",
        className
      )}
    >
      {isLoading ? (
        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      ) : children}
    </button>
  );
};
