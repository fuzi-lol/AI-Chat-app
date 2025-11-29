import React, { useState } from 'react';
import { Layout, Button } from 'antd';
import { MenuOutlined } from '@ant-design/icons';
import { Sidebar } from '../components/Sidebar';
import { ChatArea } from '../components/Chat';
import { ChatProvider } from '../contexts';

const ChatPage: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <ChatProvider>
      <Layout style={{ minHeight: '100vh' }}>
        <Sidebar 
          collapsed={sidebarCollapsed} 
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
        
        <Layout style={{ 
          marginLeft: sidebarCollapsed ? 0 : 280,
          transition: 'margin-left 0.2s'
        }}>
          {/* Show toggle button when sidebar is collapsed */}
          {sidebarCollapsed && (
            <Button
              type="primary"
              icon={<MenuOutlined />}
              onClick={() => setSidebarCollapsed(false)}
              style={{
                position: 'fixed',
                top: '16px',
                left: '16px',
                zIndex: 200,
                borderRadius: '50%',
                width: '40px',
                height: '40px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
              }}
            />
          )}
          
          <ChatArea sidebarCollapsed={sidebarCollapsed} />
        </Layout>
      </Layout>
    </ChatProvider>
  );
};

export default ChatPage;
