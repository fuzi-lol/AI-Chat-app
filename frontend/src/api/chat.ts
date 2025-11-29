import apiClient from './client';
import { MessageCreate, ChatResponse, ModelsResponse } from '../types';

export const chatApi = {
  // Send message and get AI response
  sendMessage: async (messageData: MessageCreate): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/chat/send', messageData);
    return response.data;
  },

  // Regenerate AI response for a message
  regenerateMessage: async (messageId: number, model?: string): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>('/chat/regenerate', {
      message_id: messageId,
      model,
    });
    return response.data;
  },

  // Get available models
  getModels: async (): Promise<ModelsResponse> => {
    const response = await apiClient.get<ModelsResponse>('/chat/models');
    return response.data;
  },
};
