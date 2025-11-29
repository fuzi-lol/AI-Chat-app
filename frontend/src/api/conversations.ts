import apiClient from './client';
import { Conversation, ConversationWithMessages, Message } from '../types';

export const conversationsApi = {
  // Get all conversations for current user
  getConversations: async (): Promise<Conversation[]> => {
    const response = await apiClient.get<Conversation[]>('/conversations/');
    return response.data;
  },

  // Create new conversation
  createConversation: async (title?: string): Promise<Conversation> => {
    const response = await apiClient.post<Conversation>('/conversations/', {
      title: title || 'New Conversation',
    });
    return response.data;
  },

  // Get conversation with messages
  getConversation: async (conversationId: number): Promise<ConversationWithMessages> => {
    const response = await apiClient.get<ConversationWithMessages>(`/conversations/${conversationId}`);
    return response.data;
  },

  // Get messages for a conversation
  getMessages: async (conversationId: number): Promise<Message[]> => {
    const response = await apiClient.get<Message[]>(`/conversations/${conversationId}/messages`);
    return response.data;
  },

  // Update conversation title
  updateConversation: async (conversationId: number, title: string): Promise<Conversation> => {
    const response = await apiClient.put<Conversation>(`/conversations/${conversationId}`, {
      title,
    });
    return response.data;
  },

  // Delete conversation
  deleteConversation: async (conversationId: number): Promise<void> => {
    await apiClient.delete(`/conversations/${conversationId}`);
  },

  // Delete message
  deleteMessage: async (conversationId: number, messageId: number): Promise<void> => {
    await apiClient.delete(`/conversations/${conversationId}/messages/${messageId}`);
  },

  // Export conversation
  exportConversation: async (conversationId: number): Promise<any> => {
    const response = await apiClient.get(`/conversations/${conversationId}/export`);
    return response.data;
  },
};
