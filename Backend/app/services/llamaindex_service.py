import logging
from typing import List, Dict, Any, Optional, Tuple
from app.config import settings
import asyncio

logger = logging.getLogger(__name__)


class LlamaIndexService:
    def __init__(self):
        self.ollama_base_url = settings.ollama_base_url
        self.default_model = settings.ollama_default_model
        self.tavily_api_key = settings.tavily_api_key
        self.memory_buffer_size = getattr(settings, 'chat_memory_buffer_size', 20)
        
        # Initialize LLM
        self.llm = None
        self.agent = None
        self.tavily_tools = None
        self._initialized = False
        
        # Don't initialize components immediately to avoid import-time errors
    
    def _initialize_components(self):
        """Initialize LlamaIndex components."""
        try:
            # Import here to avoid import-time SSL issues
            from llama_index.llms.ollama import Ollama
            from llama_index.tools.tavily_research import TavilyToolSpec
            from llama_index.core.agent import ReActAgent
            
            # Initialize Ollama LLM
            # Note: LlamaIndex's Ollama wrapper uses /api/chat endpoint
            # Ensure Ollama is updated to a version that supports /api/chat
            # or the model is properly loaded
            try:
                self.llm = Ollama(
                    model=self.default_model,
                    base_url=self.ollama_base_url,
                    request_timeout=120.0
                )
                logger.info(f"Initialized Ollama LLM with model: {self.default_model} at {self.ollama_base_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Ollama LLM: {e}")
                raise Exception(f"Failed to initialize Ollama LLM. Make sure Ollama is running and model '{self.default_model}' is available. Error: {e}")
            
            # Initialize Tavily tools if API key is available
            if self.tavily_api_key:
                try:
                    tavily_spec = TavilyToolSpec(api_key=self.tavily_api_key)
                    self.tavily_tools = tavily_spec.to_tool_list()
                    logger.info(f"Initialized {len(self.tavily_tools)} Tavily tools")
                except Exception as e:
                    logger.warning(f"Failed to initialize Tavily tools: {e}")
                    self.tavily_tools = []
            else:
                logger.warning("Tavily API key not provided, search functionality will be limited")
                self.tavily_tools = []
            
            # Initialize ReAct agent with tools
            try:
                if self.tavily_tools:
                    self.agent = ReActAgent.from_tools(
                        self.tavily_tools,
                        llm=self.llm,
                        verbose=True,
                        max_iterations=5
                    )
                    logger.info("ReAct agent initialized with Tavily tools")
                else:
                    # Create agent without tools for fallback
                    self.agent = ReActAgent.from_tools(
                        [],
                        llm=self.llm,
                        verbose=True
                    )
                    logger.info("ReAct agent initialized without tools")
            except Exception as e:
                logger.error(f"Failed to create ReAct agent: {e}")
                # Try alternative initialization method
                try:
                    self.agent = ReActAgent(
                        tools=self.tavily_tools or [],
                        llm=self.llm,
                        verbose=True,
                        max_iterations=5
                    )
                    logger.info("ReAct agent initialized with alternative method")
                except Exception as e2:
                    logger.error(f"Alternative ReAct agent initialization also failed: {e2}")
                    # Set agent to None and use fallback logic
                    self.agent = None
                    logger.warning("Using fallback mode without ReAct agent")
                
        except Exception as e:
            logger.error(f"Failed to initialize LlamaIndex components: {e}")
            raise
    
    def _format_conversation_history(self, messages: List[Dict[str, str]]) -> List:
        """Convert conversation history to LlamaIndex ChatMessage format."""
        from llama_index.core.llms import ChatMessage, MessageRole
        
        chat_messages = []
        
        # Take the last N messages based on buffer size
        recent_messages = messages[-self.memory_buffer_size:] if len(messages) > self.memory_buffer_size else messages
        
        for msg in recent_messages:
            role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
            if msg["role"] == "system":
                role = MessageRole.SYSTEM
            
            chat_messages.append(ChatMessage(
                role=role,
                content=msg["content"]
            ))
        
        return chat_messages
    
    def _ensure_initialized(self):
        """Ensure components are initialized before use."""
        if not self._initialized:
            try:
                self._initialize_components()
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to initialize LlamaIndex components: {e}")
                raise

    async def generate_auto_response(
        self,
        prompt: str,
        conversation_history: List[Dict[str, str]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate response using auto mode where agent decides whether to use tools.
        
        Args:
            prompt: User's message
            conversation_history: Previous conversation messages
            model: Model to use (optional)
            
        Returns:
            Dict containing response, tool usage info, and reasoning
        """
        try:
            # Ensure components are initialized
            self._ensure_initialized()
            # Update model if specified and valid
            if model and model != self.default_model and model not in ["auto", "internet"]:
                self.llm.model = model
            
            # Format conversation history
            chat_history = []
            if conversation_history:
                chat_history = self._format_conversation_history(conversation_history)
            
            # Create memory buffer with conversation history
            from llama_index.core.memory import ChatMemoryBuffer
            memory = ChatMemoryBuffer.from_defaults(
                chat_history=chat_history,
                llm=self.llm
            )
            
            # Check if agent is available
            if self.agent is None:
                logger.warning("ReAct agent not available, using fallback response")
                return await self._fallback_response(prompt, conversation_history, model)
            
            # Update agent's memory
            self.agent.memory = memory
            
            # Generate response using the agent
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.agent.chat, prompt
            )
            
            # Extract information about tool usage
            tool_calls = []
            reasoning_steps = []
            
            # Check if agent used any tools
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for node in response.source_nodes:
                    if hasattr(node, 'metadata'):
                        tool_calls.append(node.metadata)
            
            # Get reasoning from agent's memory if available
            if hasattr(self.agent, 'memory') and hasattr(self.agent.memory, 'get_all'):
                recent_messages = self.agent.memory.get_all()
                for msg in recent_messages[-3:]:  # Get last few messages for reasoning
                    if "Thought:" in str(msg.content) or "Action:" in str(msg.content):
                        reasoning_steps.append(str(msg.content))
            
            return {
                "content": str(response),
                "model": model or self.default_model,
                "tool_calls": tool_calls,
                "reasoning_steps": reasoning_steps,
                "used_search": len(tool_calls) > 0,
                "agent_type": "react"
            }
            
        except Exception as e:
            logger.error(f"Error in auto response generation: {e}")
            error_msg = str(e)
            # Check if it's a 404 error (endpoint not found or model not available)
            if "404" in error_msg or "Not Found" in error_msg:
                logger.warning(f"LlamaIndex Ollama endpoint failed (404). This might mean:")
                logger.warning(f"  1. Ollama version doesn't support /api/chat endpoint")
                logger.warning(f"  2. Model '{model or self.default_model}' is not loaded in Ollama")
                logger.warning(f"  3. Ollama server is not running or misconfigured")
                logger.warning(f"Falling back to direct Ollama service...")
            # Fallback to direct Ollama service
            return await self._fallback_response(prompt, conversation_history, model)
    
    async def _fallback_response(
        self,
        prompt: str,
        conversation_history: List[Dict[str, str]] = None,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Fallback to direct Ollama service if LlamaIndex fails."""
        try:
            # Import ollama_service here to avoid circular imports
            from app.services.ollama_service import ollama_service
            
            # Use the direct Ollama service which uses /api/generate endpoint
            model_name = model if model and model not in ["auto", "internet"] else self.default_model
            
            logger.info(f"Using fallback Ollama service with model: {model_name}")
            
            # Convert conversation history format if needed
            history = conversation_history or []
            
            # Generate response using direct Ollama service
            response = await ollama_service.generate_response(
                prompt=prompt,
                conversation_history=history,
                model=model_name,
                system_message="You are a helpful AI assistant. Provide accurate and helpful responses."
            )
            
            return {
                "content": response.get("content", ""),
                "model": model_name,
                "tool_calls": [],
                "reasoning_steps": [],
                "used_search": False,
                "agent_type": "direct_ollama",
                "fallback": True
            }
            
        except Exception as e:
            logger.error(f"Fallback response generation failed: {e}")
            raise Exception(f"Failed to generate response: {e}")
    
    async def check_search_intent(self, prompt: str) -> bool:
        """
        Analyze if the prompt requires internet search.
        This is a simple heuristic - the ReAct agent will make the final decision.
        """
        search_indicators = [
            "current", "today", "now", "latest", "recent", "news",
            "weather", "stock", "price", "what's happening",
            "update", "2024", "2025", "this year", "this month"
        ]
        
        prompt_lower = prompt.lower()
        return any(indicator in prompt_lower for indicator in search_indicators)
    
    async def health_check(self) -> bool:
        """Check if LlamaIndex service is healthy."""
        try:
            # Ensure components are initialized
            self._ensure_initialized()
            
            # Test basic LLM functionality
            from llama_index.core.llms import ChatMessage, MessageRole
            test_message = ChatMessage(role=MessageRole.USER, content="Hello")
            response = await asyncio.get_event_loop().run_in_executor(
                None, self.llm.chat, [test_message]
            )
            return bool(response and response.message.content)
        except Exception as e:
            logger.error(f"LlamaIndex health check failed: {e}")
            return False
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        if self.tavily_tools:
            return [tool.metadata.name for tool in self.tavily_tools]
        return []
    
    def update_model(self, model_name: str):
        """Update the model used by the LLM."""
        try:
            self.llm.model = model_name
            self.default_model = model_name
            logger.info(f"Updated model to: {model_name}")
        except Exception as e:
            logger.error(f"Failed to update model: {e}")
            raise


# Global instance
llamaindex_service = LlamaIndexService()
