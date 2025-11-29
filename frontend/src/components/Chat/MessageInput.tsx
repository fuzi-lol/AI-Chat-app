import React, { useState } from 'react';
import { Input, Button, Space } from 'antd';
import { SendOutlined } from '@ant-design/icons';
import { useChat } from '../../contexts';

const { TextArea } = Input;

const MessageInput: React.FC = () => {
  const [message, setMessage] = useState('');
  const { sendMessage, sendingMessage, loadingConversation } = useChat();

  const handleSend = async () => {
    if (!message.trim() || sendingMessage || loadingConversation) return;

    const messageToSend = message.trim();
    setMessage('');
    
    try {
      await sendMessage(messageToSend);
    } catch (error) {
      // Error is handled in context
      setMessage(messageToSend); // Restore message on error
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{
      position: 'absolute',
      bottom: 0,
      left: 0,
      right: 0,
      background: 'white',
      borderTop: '1px solid #f0f0f0',
      padding: '16px 24px',
      zIndex: 10
    }}>
      <Space.Compact style={{ width: '100%' }}>
        <TextArea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={loadingConversation ? "Loading conversation..." : "Type your message here... (Press Enter to send, Shift+Enter for new line)"}
          autoSize={{ minRows: 1, maxRows: 4 }}
          style={{ 
            resize: 'none',
            borderRadius: '8px 0 0 8px'
          }}
          disabled={sendingMessage || loadingConversation}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSend}
          loading={sendingMessage || loadingConversation}
          disabled={!message.trim() || loadingConversation}
          style={{ 
            height: 'auto',
            minHeight: '32px',
            borderRadius: '0 8px 8px 0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          Send
        </Button>
      </Space.Compact>
    </div>
  );
};

export default MessageInput;
