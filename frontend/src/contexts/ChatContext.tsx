import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Conversation, Message, ModelInfo, ChatContextType } from '../types';
import { chatApi, conversationsApi } from '../api';
import { message as antdMessage } from 'antd';

const ChatContext = createContext<ChatContextType | undefined>(undefined);

interface ChatProviderProps {
  children: ReactNode;
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [availableModels, setAvailableModels] = useState<ModelInfo[]>([]);
  const [selectedModel, setSelectedModel] = useState<string>('');
  const [loading] = useState(false);
  const [loadingConversation, setLoadingConversation] = useState(false);
  const [sendingMessage, setSendingMessage] = useState(false);

  // Load initial data
  useEffect(() => {
    loadConversations();
    loadModels();
  }, []);

  const loadModels = async (): Promise<void> => {
    try {
      const modelsResponse = await chatApi.getModels();
      setAvailableModels(modelsResponse.models);
      setSelectedModel(modelsResponse.default_model);
    } catch (error: any) {
      console.error('Failed to load models:', error);
      antdMessage.error('Failed to load available models');
    }
  };

  const loadConversations = async (): Promise<void> => {
    try {
      const conversationsList = await conversationsApi.getConversations();
      setConversations(conversationsList);
    } catch (error: any) {
      console.error('Failed to load conversations:', error);
      antdMessage.error('Failed to load conversations');
    }
  };

  const selectConversation = async (conversationId: number): Promise<void> => {
    try {
      // Clear messages immediately to prevent showing old messages
      setMessages([]);
      setLoadingConversation(true);
      
      // Try to find conversation in local state first
      let conversation = conversations.find(c => c.id === conversationId);
      
      // If not found in local state, fetch it directly from API
      if (!conversation) {
        const conversationWithMessages = await conversationsApi.getConversation(conversationId);
        conversation = {
          id: conversationWithMessages.id,
          user_id: conversationWithMessages.user_id,
          title: conversationWithMessages.title,
          langfuse_session_id: conversationWithMessages.langfuse_session_id,
          created_at: conversationWithMessages.created_at,
          updated_at: conversationWithMessages.updated_at,
        };
        // Update conversations list with the fetched conversation
        setConversations(prev => {
          const exists = prev.find(c => c.id === conversationId);
          if (exists) {
            return prev.map(c => c.id === conversationId ? conversation! : c);
          }
          return [...prev, conversation!];
        });
      }
      
      // Set current conversation before loading messages
      setCurrentConversation(conversation);
      
      // Load messages for this conversation
      const conversationMessages = await conversationsApi.getMessages(conversationId);
      
      // Only set messages if we're still on the same conversation (prevent race conditions)
      setMessages(conversationMessages);
      
    } catch (error: any) {
      console.error('Failed to load conversation:', error);
      antdMessage.error('Failed to load conversation');
      // Clear state on error
      setCurrentConversation(null);
      setMessages([]);
    } finally {
      setLoadingConversation(false);
    }
  };

  const createNewConversation = (): void => {
    setCurrentConversation(null);
    setMessages([]);
  };

  const sendMessage = async (messageContent: string): Promise<void> => {
    if (!messageContent.trim()) return;
    
    // Prevent sending message while conversation is loading
    if (loadingConversation) {
      antdMessage.warning('Please wait for the conversation to load');
      return;
    }

    // Determine conversation_id - use current conversation if available
    const conversationId = currentConversation?.id;
    
    // Add optimistic message so user sees their message immediately
    // This works for both existing and new conversations
    const optimisticMessage: Message = {
      id: Date.now(), // Temporary ID
      conversation_id: conversationId || 0, // Will be updated when conversation is created
      role: 'user',
      content: messageContent,
      created_at: new Date().toISOString(),
    };
    setMessages(prev => [...prev, optimisticMessage]);

    try {
      setSendingMessage(true);

      // Send message to API
      const response = await chatApi.sendMessage({
        message: messageContent,
        conversation_id: conversationId,
        model: selectedModel,
        tool_selection: selectedModel === 'internet' ? 'internet' : selectedModel === 'auto' ? 'auto' : 'none',
      });

      // Update current conversation if it was created
      if (!currentConversation) {
        // Fetch the newly created conversation directly from API
        const newConversationData = await conversationsApi.getConversation(response.conversation_id);
        const newConversation: Conversation = {
          id: newConversationData.id,
          user_id: newConversationData.user_id,
          title: newConversationData.title,
          langfuse_session_id: newConversationData.langfuse_session_id,
          created_at: newConversationData.created_at,
          updated_at: newConversationData.updated_at,
        };
        
        // Update conversations list
        setConversations(prev => {
          const exists = prev.find(c => c.id === response.conversation_id);
          if (exists) {
            return prev.map(c => c.id === response.conversation_id ? newConversation : c);
          }
          return [newConversation, ...prev];
        });
        
        // Set current conversation
        setCurrentConversation(newConversation);
        
        // Update messages: replace optimistic message with actual user message and add assistant response
        setMessages(prev => {
          // Replace optimistic message with actual user message (with correct conversation_id)
          const updatedMessages = prev.map(m => 
            m.id === optimisticMessage.id
              ? {
                  ...optimisticMessage,
                  id: Date.now() - 1,
                  conversation_id: response.conversation_id,
                }
              : m
          );
          // Add assistant response
          return [...updatedMessages, response.message];
        });
      } else {
        // Update messages with actual response
        // The optimistic user message is already in the messages array, so we just add the assistant response
        setMessages(prev => {
          // Update optimistic message with correct conversation_id if needed, then add assistant response
          const updatedMessages = prev.map(m => 
            m.id === optimisticMessage.id && m.conversation_id === 0
              ? { ...m, conversation_id: response.conversation_id }
              : m
          );
          return [...updatedMessages, response.message];
        });
      }

    } catch (error: any) {
      console.error('Failed to send message:', error);
      antdMessage.error(error.detail || 'Failed to send message');
      
      // Remove optimistic message on error
      if (optimisticMessage) {
        setMessages(prev => prev.filter(m => m.id !== optimisticMessage!.id));
      }
    } finally {
      setSendingMessage(false);
    }
  };

  const regenerateMessage = async (messageId: number): Promise<void> => {
    try {
      setSendingMessage(true);
      const response = await chatApi.regenerateMessage(messageId, selectedModel);
      
      // Replace the message with the regenerated one
      setMessages(prev => prev.map(m => 
        m.id === messageId ? response.message : m
      ));
      
      antdMessage.success('Message regenerated successfully');
    } catch (error: any) {
      console.error('Failed to regenerate message:', error);
      antdMessage.error(error.detail || 'Failed to regenerate message');
    } finally {
      setSendingMessage(false);
    }
  };

  const deleteConversation = async (conversationId: number): Promise<void> => {
    try {
      await conversationsApi.deleteConversation(conversationId);
      setConversations(prev => prev.filter(c => c.id !== conversationId));
      
      // If deleted conversation was current, clear it
      if (currentConversation?.id === conversationId) {
        setCurrentConversation(null);
        setMessages([]);
      }
      
      antdMessage.success('Conversation deleted successfully');
    } catch (error: any) {
      console.error('Failed to delete conversation:', error);
      antdMessage.error(error.detail || 'Failed to delete conversation');
    }
  };

  const value: ChatContextType = {
    conversations,
    currentConversation,
    messages,
    availableModels,
    selectedModel,
    loading,
    loadingConversation,
    sendingMessage,
    sendMessage,
    selectConversation,
    createNewConversation,
    deleteConversation,
    setSelectedModel,
    loadConversations,
    regenerateMessage,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
