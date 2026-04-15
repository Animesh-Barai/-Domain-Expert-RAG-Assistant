'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { AuthCard } from '@/components/auth/AuthCard';
import { InputField, AuthButton } from '@/components/ui/InputField';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();
  const { login, isLoading, error } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      router.push('/'); // Redirect to dashboard/home
    } catch (err) {
      // Error handled by store
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#09090b] p-6 selection:bg-indigo-500/30">
      <AuthCard 
        title="Aura" 
        subtitle="Sign in to your cognitive assistant"
      >
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-4">
            <InputField
              label="Email Address"
              placeholder="name@example.com"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <InputField
              label="Password"
              placeholder="••••••••"
              showToggle
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-xs py-3 px-4 rounded-xl">
              {error}
            </div>
          )}

          <div className="pt-2">
            <AuthButton isLoading={isLoading}>
              Sign In
            </AuthButton>
          </div>

          <p className="text-center text-xs text-zinc-500">
            Don&apos;t have an account?{' '}
            <Link 
              href="/register" 
              className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
            >
              Create an account
            </Link>
          </p>
        </form>
      </AuthCard>
    </div>
  );
}
