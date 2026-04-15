'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { AuthCard } from '@/components/auth/AuthCard';
import { InputField, AuthButton } from '@/components/ui/InputField';
import Link from 'next/link';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error } = useAuthStore();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError(null);

    if (password !== confirmPassword) {
      setLocalError('Passwords do not match');
      return;
    }

    try {
      await register(email, password);
      router.push('/'); // Redirect after auto-login
    } catch (err) {
      // Error handled by store
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#09090b] p-6 selection:bg-indigo-500/30">
      <AuthCard 
        title="Forge Identity" 
        subtitle="Begin your journey with Aura"
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
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <InputField
                label="Password"
                placeholder="••••••••"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <InputField
                label="Confirm"
                placeholder="••••••••"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
              />
            </div>
          </div>

          {(error || localError) && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-400 text-xs py-3 px-4 rounded-xl">
              {error || localError}
            </div>
          )}

          <div className="pt-2">
            <AuthButton isLoading={isLoading}>
              Create Account
            </AuthButton>
          </div>

          <p className="text-center text-xs text-zinc-500">
            Already a member?{' '}
            <Link 
              href="/login" 
              className="text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
            >
              Sign In
            </Link>
          </p>
        </form>
      </AuthCard>
    </div>
  );
}
