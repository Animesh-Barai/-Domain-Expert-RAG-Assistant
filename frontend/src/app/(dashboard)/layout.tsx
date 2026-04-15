'use client';

import React from 'react';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Sidebar } from '@/components/dashboard/Sidebar';
import { VaultModal } from '@/components/vault/VaultModal';
import { useDocumentStore } from '@/store/useDocumentStore';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isModalOpen, closeModal } = useDocumentStore();

  return (
    <ProtectedRoute>
      <div className="flex h-screen bg-[#09090b] text-zinc-100 overflow-hidden font-sans">
        {/* Persistent Floating Sidebar */}
        <Sidebar />
        
        {/* Main Workspace Area */}
        <main className="flex-1 relative flex flex-col min-w-0 bg-[#131315]">
          {children}
        </main>

        {/* Global Vault Modal */}
        <VaultModal isOpen={isModalOpen} onClose={closeModal} />
      </div>
    </ProtectedRoute>
  );
}
