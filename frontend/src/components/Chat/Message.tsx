import React from 'react';
import { Card, Typography, Space, Button, Tooltip } from 'antd';
import { UserOutlined, RobotOutlined, CopyOutlined, RedoOutlined } from '@ant-design/icons';
import { Message as MessageType } from '../../types';
import { useChat } from '../../contexts';

const { Text, Paragraph } = Typography;

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  const { regenerateMessage } = useChat();
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
  };

  const handleRegenerate = () => {
    regenerateMessage(message.id);
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div 
      className="message-item"
      style={{ 
        display: 'flex', 
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px'
      }}>
      <div style={{ 
        maxWidth: '70%',
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        alignItems: 'flex-start',
        gap: '8px'
      }}>
        {/* Avatar */}
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          backgroundColor: isUser ? '#1890ff' : '#52c41a',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '14px',
          flexShrink: 0,
          marginTop: '4px'
        }}>
          {isUser ? <UserOutlined /> : <RobotOutlined />}
        </div>

        {/* Message Content */}
        <Card
          size="small"
          className="message-bubble"
          style={{
            backgroundColor: isUser ? '#1890ff' : '#f6f6f6',
            border: 'none',
            borderRadius: '12px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}
          bodyStyle={{
            padding: '12px 16px',
            color: isUser ? 'white' : '#262626'
          }}
        >
          <div>
            <Paragraph 
              style={{ 
                margin: 0,
                color: isUser ? 'white' : '#262626',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}
            >
              {message.content}
            </Paragraph>
            
            <div style={{ 
              marginTop: '8px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <Text 
                style={{ 
                  fontSize: '11px',
                  color: isUser ? 'rgba(255,255,255,0.7)' : '#8c8c8c'
                }}
              >
                {formatTime(message.created_at)}
                {message.tool_used && message.tool_used !== 'none' && (
                  <span style={{ marginLeft: '8px' }}>
                    • {message.tool_used}
                  </span>
                )}
              </Text>
              
              <Space size="small">
                <Tooltip title="Copy message">
                  <Button
                    type="text"
                    size="small"
                    icon={<CopyOutlined />}
                    onClick={handleCopy}
                    style={{
                      color: isUser ? 'rgba(255,255,255,0.7)' : '#8c8c8c',
                      border: 'none',
                      padding: '2px 4px'
                    }}
                  />
                </Tooltip>
                
                {!isUser && (
                  <Tooltip title="Regenerate response">
                    <Button
                      type="text"
                      size="small"
                      icon={<RedoOutlined />}
                      onClick={handleRegenerate}
                      style={{
                        color: '#8c8c8c',
                        border: 'none',
                        padding: '2px 4px'
                      }}
                    />
                  </Tooltip>
                )}
              </Space>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Message;
