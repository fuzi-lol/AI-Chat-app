import React from 'react';
import { RobotOutlined } from '@ant-design/icons';

const TypingIndicator: React.FC = () => {
  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'flex-start',
      marginBottom: '16px'
    }}>
      <div style={{ 
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'flex-start',
        gap: '8px'
      }}>
        {/* Avatar */}
        <div style={{
          width: '32px',
          height: '32px',
          borderRadius: '50%',
          backgroundColor: '#52c41a',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontSize: '14px',
          flexShrink: 0,
          marginTop: '4px'
        }}>
          <RobotOutlined />
        </div>

        {/* Typing Bubble */}
        <div style={{
          backgroundColor: '#f6f6f6',
          borderRadius: '12px',
          padding: '12px 16px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          display: 'flex',
          alignItems: 'center',
          gap: '4px'
        }}>
          <div className="typing-dots">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
