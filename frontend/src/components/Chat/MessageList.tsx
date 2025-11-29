import React, { useEffect, useRef } from 'react';
import { Empty } from 'antd';
import { MessageOutlined } from '@ant-design/icons';
import { useChat } from '../../contexts';
import Message from './Message';
import TypingIndicator from './TypingIndicator';

const MessageList: React.FC = () => {
  const { messages, sendingMessage, currentConversation } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!currentConversation && messages.length === 0) {
    return (
      <div style={{ 
        height: '100%', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        flexDirection: 'column',
        padding: '40px'
      }}>
        <Empty
          image={<MessageOutlined style={{ fontSize: '64px', color: '#d9d9d9' }} />}
          description={
            <div style={{ textAlign: 'center' }}>
              <h3 style={{ color: '#595959', marginBottom: '8px' }}>
                Welcome to AI Chat App
              </h3>
              <p style={{ color: '#8c8c8c', margin: 0 }}>
                Start a new conversation or select an existing one from the sidebar
              </p>
            </div>
          }
        />
      </div>
    );
  }

  return (
    <div style={{ 
      height: '100%', 
      overflowY: 'auto',
      padding: '16px 24px',
      paddingBottom: '80px' // Space for input area
    }}>
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      
      {sendingMessage && <TypingIndicator />}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
