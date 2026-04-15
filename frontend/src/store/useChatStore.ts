import { create } from 'zustand';
import api from '@/lib/api-client';

export interface Source {
  id: string;
  filename: string;
  page_number: string | number;
  score: number;
}

export interface Message {
  id: string;
  chat_id: string;
  content: string;
  role: 'user' | 'assistant';
  created_at: string;
  sources?: Source[];
}

interface Chat {
  id: string;
  title: string;
  created_at: string;
}

interface ChatState {
  chats: Chat[];
  messages: Message[];
  activeChatId: string | null;
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;

  // Actions
  fetchChats: () => Promise<void>;
  createChat: (title: string) => Promise<Chat>;
  fetchMessages: (chatId: string) => Promise<void>;
  sendMessage: (content: string, stream?: boolean) => Promise<void>;
  clearMessages: () => void;
  setError: (error: string | null) => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  messages: [],
  activeChatId: null,
  isLoading: false,
  isStreaming: false,
  error: null,

  fetchChats: async () => {
    set({ isLoading: true });
    try {
      const response = await api.get('/chats/');
      set({ chats: response.data, isLoading: false });
    } catch (error: any) {
      set({ error: 'Failed to load synchronies', isLoading: false });
    }
  },

  createChat: async (title) => {
    set({ isLoading: true });
    try {
      const response = await api.post('/chats/', { title });
      set((state) => ({ 
        chats: [response.data, ...state.chats], 
        isLoading: false,
        activeChatId: response.data.id,
        messages: []
      }));
      return response.data;
    } catch (error: any) {
      set({ error: 'Failed to initialize sync', isLoading: false });
      throw error;
    }
  },

  fetchMessages: async (chatId) => {
    set({ isLoading: true, activeChatId: chatId });
    try {
      const response = await api.get(`/chats/${chatId}/messages`);
      set({ messages: response.data, isLoading: false });
    } catch (error: any) {
      set({ error: 'Failed to retrieve message logs', isLoading: false });
    }
  },

  sendMessage: async (content, stream = true) => {
    const { activeChatId } = get();
    if (!activeChatId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      chat_id: activeChatId,
      content,
      role: 'user',
      created_at: new Date().toISOString()
    };

    set((state) => ({ 
      messages: [...state.messages, userMessage],
      isStreaming: true,
      error: null
    }));

    if (!stream) {
      try {
        const response = await api.post(`/chats/${activeChatId}/messages`, { content });
        set((state) => ({ 
          messages: [...state.messages, response.data],
          isStreaming: false 
        }));
      } catch (error: any) {
        set({ error: 'Aura failed to respond', isStreaming: false });
      }
      return;
    }

    try {
      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/chats/${activeChatId}/messages?stream=true`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ content })
      });

      if (!response.ok) throw new Error('Stream failed');

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      let assistantMessage: Message = {
        id: 'streaming-assistant',
        chat_id: activeChatId,
        content: '',
        role: 'assistant',
        created_at: new Date().toISOString(),
        sources: []
      };

      set((state) => ({ messages: [...state.messages, assistantMessage] }));

      while (true) {
        const { done, value } = await reader!.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.replace('data: ', '').trim();
            if (dataStr === '[DONE]') continue;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.type === 'metadata' && data.sources) {
                // Store sources for the current message
                assistantMessage.sources = data.sources;
              } else if (data.chunk) {
                assistantMessage.content += data.chunk;
              } else if (data.error) {
                throw new Error(data.error);
              }

              // Update the message in state
              set((state) => ({
                messages: state.messages.map(msg => 
                  msg.id === 'streaming-assistant' ? { ...assistantMessage } : msg
                )
              }));

            } catch (e) {
              console.error('SSE Parse Error', e);
            }
          }
        }
      }

      set({ isStreaming: false });
      get().fetchMessages(activeChatId);

    } catch (error: any) {
      set({ error: 'The neural void disconnected', isStreaming: false });
    }
  },

  clearMessages: () => set({ messages: [], activeChatId: null }),
  setError: (error) => set({ error }),
}));
