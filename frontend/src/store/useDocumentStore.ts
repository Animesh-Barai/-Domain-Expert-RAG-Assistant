import { create } from 'zustand';
import api from '@/lib/api-client';

export type DocumentStatus = 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';

export interface Document {
  id: string;
  filename: string;
  file_size: number;
  status: DocumentStatus;
  created_at: string;
}

interface DocumentState {
  documents: Document[];
  isLoading: boolean;
  isUploading: boolean;
  isModalOpen: boolean;
  error: string | null;

  // Actions
  fetchDocuments: () => Promise<void>;
  uploadDocument: (file: File) => Promise<Document>;
  deleteDocument: (id: string) => Promise<void>;
  pollStatus: (id: string) => void;
  openModal: () => void;
  closeModal: () => void;
  setError: (error: string | null) => void;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  documents: [],
  isLoading: false,
  isUploading: false,
  isModalOpen: false,
  error: null,

  fetchDocuments: async () => {
    set({ isLoading: true });
    try {
      const response = await api.get('/documents/');
      set({ documents: response.data, isLoading: false });
    } catch (error: any) {
      set({ error: 'System failure: could not retrieve document vaults', isLoading: false });
    }
  },

  uploadDocument: async (file: File) => {
    set({ isUploading: true, error: null });
    
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      const err = 'Aura only accepts specialized PDF fragments.';
      set({ error: err, isUploading: false });
      throw new Error(err);
    }

    if (file.size > 25 * 1024 * 1024) {
      const err = 'Intelligence fragment exceeds 25MB limit.';
      set({ error: err, isUploading: false });
      throw new Error(err);
    }

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const newDoc = response.data;
      set((state) => ({ 
        documents: [newDoc, ...state.documents], 
        isUploading: false 
      }));

      get().pollStatus(newDoc.id);
      return newDoc;
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Ingestion failure';
      set({ error: message, isUploading: false });
      throw error;
    }
  },

  deleteDocument: async (id: string) => {
    try {
      await api.delete(`/documents/${id}`);
      set((state) => ({
        documents: state.documents.filter(doc => doc.id !== id)
      }));
    } catch (error: any) {
      set({ error: 'Failed to purge document fragment' });
    }
  },

  pollStatus: (id: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/documents/${id}`);
        const updatedDoc = response.data;

        set((state) => ({
          documents: state.documents.map(doc => 
            doc.id === id ? updatedDoc : doc
          )
        }));

        if (updatedDoc.status === 'COMPLETED' || updatedDoc.status === 'FAILED') {
          clearInterval(interval);
        }
      } catch (e) {
        clearInterval(interval);
      }
    }, 3000);
  },

  openModal: () => set({ isModalOpen: true }),
  closeModal: () => set({ isModalOpen: false }),
  setError: (error) => set({ error }),
}));
