import React, { useState } from 'react';
import { List, Typography, Button, Popconfirm } from 'antd';
import { DeleteOutlined, MessageOutlined } from '@ant-design/icons';
import { Conversation } from '../../types';
import { useChat } from '../../contexts';

const { Text } = Typography;

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  onClick: () => void;
}

const ConversationItem: React.FC<ConversationItemProps> = ({
  conversation,
  isActive,
  onClick,
}) => {
  const { deleteConversation } = useChat();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    try {
      setIsDeleting(true);
      await deleteConversation(conversation.id);
    } catch (error) {
      // Error handled in context
    } finally {
      setIsDeleting(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString([], { weekday: 'short' });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <List.Item
      onClick={onClick}
      style={{
        cursor: 'pointer',
        padding: '12px 16px',
        borderRadius: '8px',
        margin: '4px 0',
        backgroundColor: isActive ? '#e6f7ff' : 'transparent',
        border: isActive ? '1px solid #1890ff' : '1px solid transparent',
        transition: 'all 0.2s ease',
      }}
      className="conversation-item"
    >
      <div style={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '4px' }}>
            <MessageOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
            <Text 
              strong={isActive}
              style={{ 
                fontSize: '14px',
                color: isActive ? '#1890ff' : '#262626'
              }}
              ellipsis={{ tooltip: conversation.title }}
            >
              {conversation.title || 'New Conversation'}
            </Text>
          </div>
          <Text 
            type="secondary" 
            style={{ fontSize: '12px' }}
          >
            {formatDate(conversation.updated_at)}
          </Text>
        </div>
        
        <Popconfirm
          title="Delete conversation"
          description="Are you sure you want to delete this conversation?"
          onConfirm={handleDelete}
          okText="Yes"
          cancelText="No"
          placement="topRight"
        >
          <Button
            type="text"
            size="small"
            icon={<DeleteOutlined />}
            loading={isDeleting}
            style={{ 
              opacity: 0.6,
              marginLeft: '8px'
            }}
            onClick={(e) => e.stopPropagation()}
          />
        </Popconfirm>
      </div>
    </List.Item>
  );
};

export default ConversationItem;
