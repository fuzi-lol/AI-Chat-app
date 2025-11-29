// User types
export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

// Message types
export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  tool_used?: string;
  langfuse_trace_id?: string;
  message_metadata?: any;
  created_at: string;
}

export interface MessageCreate {
  message: string;
  conversation_id?: number;
  model?: string;
  tool_selection?: string;
}

// Conversation types
export interface Conversation {
  id: number;
  user_id: number;
  title?: string;
  langfuse_session_id?: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[];
}

// API Response types
export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ChatResponse {
  message: Message;
  conversation_id: number;
  langfuse_trace_id?: string;
}

export interface ModelInfo {
  name: string;
  size: number;
  modified_at: string;
  type: 'ollama' | 'tool';
}

export interface ModelsResponse {
  models: ModelInfo[];
  default_model: string;
}

// Context types
export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

export interface ChatContextType {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  availableModels: ModelInfo[];
  selectedModel: string;
  loading: boolean;
  loadingConversation: boolean;
  sendingMessage: boolean;
  sendMessage: (message: string) => Promise<void>;
  selectConversation: (conversationId: number) => Promise<void>;
  createNewConversation: () => void;
  deleteConversation: (conversationId: number) => Promise<void>;
  setSelectedModel: (model: string) => void;
  loadConversations: () => Promise<void>;
  regenerateMessage: (messageId: number) => Promise<void>;
}

// API Error type
export interface ApiError {
  detail: string;
  status_code?: number;
}
