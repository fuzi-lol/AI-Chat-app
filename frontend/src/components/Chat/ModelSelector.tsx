import React from 'react';
import { Select, Typography, Space } from 'antd';
import { RobotOutlined, GlobalOutlined } from '@ant-design/icons';
import { useChat } from '../../contexts';

const { Text } = Typography;
const { Option } = Select;

interface ModelSelectorProps {
  sidebarCollapsed?: boolean;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ sidebarCollapsed = false }) => {
  const { availableModels, selectedModel, setSelectedModel } = useChat();

  const getModelIcon = (modelType: string, modelName: string) => {
    if (modelName === 'internet' || modelType === 'tool') {
      return <GlobalOutlined style={{ color: '#52c41a' }} />;
    }
    return <RobotOutlined style={{ color: '#1890ff' }} />;
  };

  const getModelDescription = (modelName: string, modelType: string) => {
    if (modelName === 'internet') {
      return 'Internet Search';
    }
    if (modelType === 'ollama') {
      return 'AI Model';
    }
    return 'Tool';
  };

  return (
    <div style={{ 
      padding: '12px 24px',
      paddingLeft: sidebarCollapsed ? '72px' : '24px', // Extra space for toggle button when sidebar is collapsed
      borderBottom: '1px solid #f0f0f0',
      background: 'white',
      display: 'flex',
      alignItems: 'center',
      minHeight: '60px',
      transition: 'padding-left 0.2s'
    }}>
      <Space align="center" style={{ width: '100%' }}>
        <Text strong style={{ fontSize: '14px' }}>Model:</Text>
        <Select
          value={selectedModel}
          onChange={setSelectedModel}
          style={{ minWidth: 200 }}
          placeholder="Select a model"
        >
          {availableModels.map((model) => (
            <Option key={model.name} value={model.name}>
              <Space>
                {getModelIcon(model.type, model.name)}
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 500 }}>
                    {model.name}
                  </div>
                  <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                    {getModelDescription(model.name, model.type)}
                  </div>
                </div>
              </Space>
            </Option>
          ))}
        </Select>
      </Space>
    </div>
  );
};

export default ModelSelector;
