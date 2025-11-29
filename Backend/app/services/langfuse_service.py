from langfuse import Langfuse
from typing import Dict, Any, Optional, List
from app.config import settings
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)


class LangfuseService:
    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Langfuse client."""
        try:
            if settings.langfuse_public_key and settings.langfuse_secret_key:
                self.client = Langfuse(
                    public_key=settings.langfuse_public_key,
                    secret_key=settings.langfuse_secret_key,
                    host=settings.langfuse_host
                )
                logger.info("Langfuse client initialized successfully")
            else:
                logger.warning("Langfuse credentials not provided, tracing disabled")
        except Exception as e:
            logger.error(f"Failed to initialize Langfuse client: {e}")
            self.client = None

    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled and configured."""
        return self.client is not None

    def create_session(self, user_id: int, conversation_id: int) -> Optional[str]:
        """Create a new Langfuse session for a conversation."""
        if not self.is_enabled():
            return None

        try:
            session_id = f"conv_{conversation_id}_{uuid.uuid4().hex[:8]}"
            
            session = self.client.trace(
                id=session_id,
                name=f"Conversation {conversation_id}",
                user_id=str(user_id),
                metadata={
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "session_type": "chat_conversation"
                }
            )
            
            logger.info(f"Created Langfuse session: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create Langfuse session: {e}")
            return None

    def create_trace(
        self,
        session_id: Optional[str],
        user_message: str,
        model: str,
        tool_used: str = "none"
    ) -> Optional[str]:
        """Create a new trace for an LLM interaction."""
        if not self.is_enabled():
            return None

        try:
            trace_id = f"trace_{uuid.uuid4().hex}"
            
            trace = self.client.trace(
                id=trace_id,
                session_id=session_id,
                name=f"Chat with {model}",
                input=user_message,
                metadata={
                    "model": model,
                    "tool_used": tool_used,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Created Langfuse trace: {trace_id}")
            return trace_id
            
        except Exception as e:
            logger.error(f"Failed to create Langfuse trace: {e}")
            return None

    def log_search_span(
        self,
        trace_id: Optional[str],
        search_query: str,
        search_results: Dict[str, Any]
    ) -> Optional[str]:
        """Log a search operation as a span."""
        if not self.is_enabled() or not trace_id:
            return None

        try:
            span_id = f"search_{uuid.uuid4().hex[:8]}"
            
            span = self.client.span(
                id=span_id,
                trace_id=trace_id,
                name="Internet Search",
                input=search_query,
                output=search_results,
                metadata={
                    "tool": "tavily_search",
                    "results_count": len(search_results.get("results", [])),
                    "search_depth": search_results.get("search_metadata", {}).get("search_depth", "basic")
                }
            )
            
            logger.info(f"Logged search span: {span_id}")
            return span_id
            
        except Exception as e:
            logger.error(f"Failed to log search span: {e}")
            return None

    def log_llm_generation(
        self,
        trace_id: Optional[str],
        model: str,
        input_messages: List[Dict[str, str]],
        output_message: str,
        usage_data: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """Log an LLM generation as a span."""
        if not self.is_enabled() or not trace_id:
            return None

        try:
            generation_id = f"gen_{uuid.uuid4().hex[:8]}"
            
            # Format input for Langfuse
            formatted_input = []
            for msg in input_messages:
                formatted_input.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

            generation = self.client.generation(
                id=generation_id,
                trace_id=trace_id,
                name=f"LLM Generation - {model}",
                model=model,
                input=formatted_input,
                output=output_message,
                metadata={
                    "model_provider": "ollama",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            # Add usage data if available
            if usage_data:
                generation.update(
                    usage={
                        "input_tokens": usage_data.get("prompt_eval_count", 0),
                        "output_tokens": usage_data.get("eval_count", 0),
                        "total_tokens": (usage_data.get("prompt_eval_count", 0) + 
                                       usage_data.get("eval_count", 0))
                    },
                    metadata={
                        **generation.metadata,
                        "total_duration_ms": usage_data.get("total_duration", 0) / 1000000,  # Convert to ms
                        "load_duration_ms": usage_data.get("load_duration", 0) / 1000000,
                        "prompt_eval_duration_ms": usage_data.get("prompt_eval_duration", 0) / 1000000,
                        "eval_duration_ms": usage_data.get("eval_duration", 0) / 1000000
                    }
                )
            
            logger.info(f"Logged LLM generation: {generation_id}")
            return generation_id
            
        except Exception as e:
            logger.error(f"Failed to log LLM generation: {e}")
            return None

    def finalize_trace(
        self,
        trace_id: Optional[str],
        output_message: str,
        status: str = "success"
    ):
        """Finalize a trace with the final output."""
        if not self.is_enabled() or not trace_id:
            return

        try:
            trace = self.client.trace(id=trace_id)
            trace.update(
                output=output_message,
                metadata={
                    **trace.metadata,
                    "status": status,
                    "completed_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Finalized trace: {trace_id}")
            
        except Exception as e:
            logger.error(f"Failed to finalize trace: {e}")

    def log_agent_reasoning(
        self,
        trace_id: Optional[str],
        reasoning_steps: List[str],
        tool_calls: List[Dict[str, Any]],
        agent_decision: Dict[str, Any]
    ) -> Optional[str]:
        """Log agent reasoning and decision-making process."""
        if not self.is_enabled() or not trace_id:
            return None

        try:
            span_id = f"agent_{uuid.uuid4().hex[:8]}"
            
            span = self.client.span(
                id=span_id,
                trace_id=trace_id,
                name="Agent Reasoning",
                input={
                    "reasoning_steps": reasoning_steps,
                    "available_tools": [tool.get("name", "unknown") for tool in tool_calls]
                },
                output=agent_decision,
                metadata={
                    "agent_type": "react",
                    "tools_used": len(tool_calls),
                    "reasoning_steps_count": len(reasoning_steps),
                    "used_search": agent_decision.get("used_search", False)
                }
            )
            
            logger.info(f"Logged agent reasoning: {span_id}")
            return span_id
            
        except Exception as e:
            logger.error(f"Failed to log agent reasoning: {e}")
            return None

    def log_tool_call(
        self,
        trace_id: Optional[str],
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Dict[str, Any],
        execution_time_ms: Optional[float] = None
    ) -> Optional[str]:
        """Log individual tool call within agent execution."""
        if not self.is_enabled() or not trace_id:
            return None

        try:
            span_id = f"tool_{uuid.uuid4().hex[:8]}"
            
            metadata = {
                "tool_name": tool_name,
                "tool_type": "search" if "search" in tool_name.lower() else "unknown"
            }
            
            if execution_time_ms:
                metadata["execution_time_ms"] = execution_time_ms
            
            span = self.client.span(
                id=span_id,
                trace_id=trace_id,
                name=f"Tool: {tool_name}",
                input=tool_input,
                output=tool_output,
                metadata=metadata
            )
            
            logger.info(f"Logged tool call: {span_id}")
            return span_id
            
        except Exception as e:
            logger.error(f"Failed to log tool call: {e}")
            return None

    def log_error(
        self,
        trace_id: Optional[str],
        error_message: str,
        error_type: str = "unknown"
    ):
        """Log an error to a trace."""
        if not self.is_enabled() or not trace_id:
            return

        try:
            trace = self.client.trace(id=trace_id)
            trace.update(
                metadata={
                    **trace.metadata,
                    "status": "error",
                    "error_type": error_type,
                    "error_message": error_message,
                    "error_at": datetime.utcnow().isoformat()
                }
            )
            
            logger.info(f"Logged error to trace {trace_id}: {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to log error to trace: {e}")

    async def health_check(self) -> bool:
        """Check if Langfuse is healthy."""
        if not self.is_enabled():
            return False
            
        try:
            # Try to create a test trace
            test_trace = self.client.trace(
                name="health_check",
                metadata={"type": "health_check"}
            )
            return True
        except Exception as e:
            logger.error(f"Langfuse health check failed: {e}")
            return False


# Global instance
langfuse_service = LangfuseService()
