import React from 'react';
import { Layout, Button, Typography, Avatar, Space, List, Divider, Dropdown, MenuProps } from 'antd';
import { PlusOutlined, UserOutlined, LogoutOutlined, SettingOutlined, MenuOutlined } from '@ant-design/icons';
import { useAuth, useChat } from '../../contexts';
import ConversationItem from './ConversationItem';

const { Sider } = Layout;
const { Title, Text } = Typography;

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const { user, logout } = useAuth();
  const { 
    conversations, 
    currentConversation, 
    createNewConversation, 
    selectConversation
  } = useChat();

  const handleNewChat = () => {
    createNewConversation();
  };

  const handleConversationClick = (conversationId: number) => {
    selectConversation(conversationId);
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: 'Profile',
      disabled: true,
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: 'Settings',
      disabled: true,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: logout,
    },
  ];

  return (
    <Sider
      width={280}
      collapsed={collapsed}
      collapsedWidth={0}
      style={{
        background: '#fafafa',
        borderRight: '1px solid #f0f0f0',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        zIndex: 100,
      }}
    >
      <div style={{ 
        height: '100%', 
        display: 'flex', 
        flexDirection: 'column',
        padding: '16px'
      }}>
        {/* Header with Toggle */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '16px' 
        }}>
          <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
            AI Chat App
          </Title>
          <Button
            type="text"
            icon={<MenuOutlined />}
            onClick={onToggle}
            style={{
              color: '#8c8c8c',
              padding: '4px',
              height: 'auto',
              width: 'auto',
              minWidth: 'auto'
            }}
            size="small"
          />
        </div>

        {/* New Chat Button */}
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={handleNewChat}
          style={{ 
            marginBottom: '16px',
            height: '40px',
            borderRadius: '8px'
          }}
          block
        >
          New Chat
        </Button>

        <Divider style={{ margin: '0 0 16px 0' }} />

        {/* Conversations List */}
        <div style={{ flex: 1, overflow: 'hidden' }}>
          <Text type="secondary" style={{ fontSize: '12px', marginBottom: '8px', display: 'block' }}>
            Recent Conversations
          </Text>
          
          <div style={{ height: 'calc(100vh - 200px)', overflowY: 'auto' }}>
            {conversations.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                padding: '20px',
                color: '#8c8c8c'
              }}>
                <Text type="secondary">No conversations yet</Text>
              </div>
            ) : (
              <List
                dataSource={conversations}
                renderItem={(conversation) => (
                  <ConversationItem
                    key={conversation.id}
                    conversation={conversation}
                    isActive={currentConversation?.id === conversation.id}
                    onClick={() => handleConversationClick(conversation.id)}
                  />
                )}
                style={{ padding: 0 }}
              />
            )}
          </div>
        </div>

        {/* User Profile */}
        <div style={{ marginTop: 'auto', paddingTop: '16px' }}>
          <Divider style={{ margin: '0 0 16px 0' }} />
          <Dropdown menu={{ items: userMenuItems }} placement="topRight">
            <div style={{ 
              cursor: 'pointer',
              padding: '8px',
              borderRadius: '8px',
              transition: 'background-color 0.2s',
            }}
            className="user-profile-dropdown"
            >
              <Space>
                <Avatar 
                  size="small" 
                  icon={<UserOutlined />}
                  style={{ backgroundColor: '#1890ff' }}
                />
                <div>
                  <Text strong style={{ fontSize: '14px' }}>
                    {user?.email?.split('@')[0] || 'User'}
                  </Text>
                  <br />
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    {user?.email}
                  </Text>
                </div>
              </Space>
            </div>
          </Dropdown>
        </div>
      </div>
    </Sider>
  );
};

export default Sidebar;
