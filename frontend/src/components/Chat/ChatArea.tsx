import React from 'react';
import { Layout } from 'antd';
import ModelSelector from './ModelSelector';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const { Content } = Layout;

interface ChatAreaProps {
  sidebarCollapsed?: boolean;
}

const ChatArea: React.FC<ChatAreaProps> = ({ sidebarCollapsed = false }) => {
  return (
    <Layout style={{ height: '100vh', background: 'white' }}>
      <ModelSelector sidebarCollapsed={sidebarCollapsed} />
      
      <Content style={{ 
        position: 'relative',
        height: 'calc(100vh - 60px)', // Subtract header height
        overflow: 'hidden'
      }}>
        <MessageList />
        <MessageInput />
      </Content>
    </Layout>
  );
};

export default ChatArea;
