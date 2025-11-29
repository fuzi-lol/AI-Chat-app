from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.middleware.auth_middleware import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.chat import ChatRequest, ChatResponse, RegenerateRequest, Message as MessageSchema
from app.services.ollama_service import ollama_service
from app.services.search_service import search_service
from app.services.langfuse_service import langfuse_service
from app.services.llamaindex_service import llamaindex_service
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send a message and get AI response."""
    try:
        # Get or create conversation
        if chat_request.conversation_id:
            conversation = db.query(Conversation).filter(
                Conversation.id == chat_request.conversation_id,
                Conversation.user_id == current_user.id
            ).first()
            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = Conversation(
                user_id=current_user.id,
                title=chat_request.message[:50] + "..." if len(chat_request.message) > 50 else chat_request.message
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
        
        # Create Langfuse session if not exists
        if not conversation.langfuse_session_id:
            session_id = langfuse_service.create_session(current_user.id, conversation.id)
            if session_id:
                conversation.langfuse_session_id = session_id
                db.commit()

        # Save user message
        user_message = Message(
            conversation_id=conversation.id,
            role="user",
            content=chat_request.message,
            tool_used=chat_request.tool_selection
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        # Create Langfuse trace
        # Use proper model name for Langfuse, not tool names
        trace_model = chat_request.model or settings.ollama_default_model
        if trace_model in ["auto", "internet"]:
            trace_model = settings.ollama_default_model
        
        trace_id = langfuse_service.create_trace(
            session_id=conversation.langfuse_session_id,
            user_message=chat_request.message,
            model=trace_model,
            tool_used=chat_request.tool_selection
        )

        # Get conversation history (last 10 messages)
        history_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.id < user_message.id  # Exclude the current user message
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        # Format conversation history
        conversation_history = []
        for msg in reversed(history_messages):  # Reverse to get chronological order
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Handle auto mode - let LlamaIndex agent decide whether to use tools
        if chat_request.model == "auto":
            try:
                # Ensure we use a valid Ollama model, not a tool name
                model_name = chat_request.model
                if not model_name or model_name in ["auto", "internet"]:
                    model_name = settings.ollama_default_model  # Use default Ollama model
                
                ai_response = await llamaindex_service.generate_auto_response(
                    prompt=chat_request.message,
                    conversation_history=conversation_history,
                    model=model_name
                )

                # Log agent reasoning in Langfuse
                langfuse_service.log_agent_reasoning(
                    trace_id=trace_id,
                    reasoning_steps=ai_response.get("reasoning_steps", []),
                    tool_calls=ai_response.get("tool_calls", []),
                    agent_decision={
                        "used_search": ai_response.get("used_search", False),
                        "agent_type": ai_response.get("agent_type", "react"),
                        "fallback": ai_response.get("fallback", False)
                    }
                )

                # Log individual tool calls if any
                for tool_call in ai_response.get("tool_calls", []):
                    langfuse_service.log_tool_call(
                        trace_id=trace_id,
                        tool_name=tool_call.get("tool_name", "unknown"),
                        tool_input=tool_call.get("input", {}),
                        tool_output=tool_call.get("output", {})
                    )

                # Save assistant message
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=ai_response["content"],
                    tool_used=chat_request.tool_selection,
                    langfuse_trace_id=trace_id,
                    message_metadata={
                        "model": ai_response["model"],
                        "agent_type": ai_response.get("agent_type", "react"),
                        "used_search": ai_response.get("used_search", False),
                        "tool_calls": ai_response.get("tool_calls", []),
                        "reasoning_steps": ai_response.get("reasoning_steps", []),
                        "fallback": ai_response.get("fallback", False)
                    }
                )
                db.add(assistant_message)
                db.commit()
                db.refresh(assistant_message)

                # Finalize Langfuse trace
                langfuse_service.finalize_trace(trace_id, ai_response["content"])

                return ChatResponse(
                    message=MessageSchema.from_orm(assistant_message),
                    conversation_id=conversation.id,
                    langfuse_trace_id=trace_id
                )

            except Exception as e:
                logger.error(f"Auto mode failed: {e}")
                langfuse_service.log_error(trace_id, str(e), "auto_mode_error")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Auto mode failed: {str(e)}"
                )

        # Handle internet search if requested - return search results directly without Ollama
        elif chat_request.tool_selection == "internet":
            try:
                search_results = await search_service.search(chat_request.message)
                search_context = search_service.format_search_results_for_llm(search_results)
                search_metadata = search_results
                    
                # Log search span in Langfuse
                langfuse_service.log_search_span(trace_id, chat_request.message, search_results)
                
                # Return search results directly without calling Ollama
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=search_context,
                    tool_used=chat_request.tool_selection,
                    langfuse_trace_id=trace_id,
                    message_metadata={
                        "search_results": search_metadata,
                        "source": "internet_search"
                    }
                )
                db.add(assistant_message)
                db.commit()
                db.refresh(assistant_message)

                # Finalize Langfuse trace
                langfuse_service.finalize_trace(trace_id, search_context)

                return ChatResponse(
                    message=MessageSchema.from_orm(assistant_message),
                    conversation_id=conversation.id,
                    langfuse_trace_id=trace_id
                )

            except Exception as e:
                logger.error(f"Search failed: {e}")
                langfuse_service.log_error(trace_id, str(e), "search_error")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Search failed: {str(e)}"
                )

        # Handle "none" tool selection - Generate AI response using Ollama directly
        else:  # This covers tool_selection == "none" and any other values
            prompt = chat_request.message
            try:
                ai_response = await ollama_service.generate_response(
                    prompt=prompt,
                    conversation_history=conversation_history,
                    model=chat_request.model,
                    system_message="You are a helpful AI assistant. Provide accurate and helpful responses."
                )

                # Log LLM generation in Langfuse
                input_messages = conversation_history + [{"role": "user", "content": prompt}]
                langfuse_service.log_llm_generation(
                    trace_id=trace_id,
                    model=ai_response["model"],
                    input_messages=input_messages,
                    output_message=ai_response["content"],
                    usage_data=ai_response
                )

                # Save assistant message
                assistant_message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=ai_response["content"],
                    tool_used=chat_request.tool_selection,
                    langfuse_trace_id=trace_id,
                    message_metadata={
                        "model": ai_response["model"],
                        "usage": {
                            "prompt_eval_count": ai_response.get("prompt_eval_count"),
                            "eval_count": ai_response.get("eval_count"),
                            "total_duration": ai_response.get("total_duration"),
                            "eval_duration": ai_response.get("eval_duration")
                        }
                    }
                )
                db.add(assistant_message)
                db.commit()
                db.refresh(assistant_message)

                # Finalize Langfuse trace
                langfuse_service.finalize_trace(trace_id, ai_response["content"])

                return ChatResponse(
                    message=MessageSchema.from_orm(assistant_message),
                    conversation_id=conversation.id,
                    langfuse_trace_id=trace_id
                )

            except Exception as e:
                logger.error(f"AI response generation failed: {e}")
                langfuse_service.log_error(trace_id, str(e), "llm_generation_error")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate AI response: {str(e)}"
                )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/regenerate", response_model=ChatResponse)
async def regenerate_message(
    regenerate_request: RegenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Regenerate an AI response for a specific message."""
    try:
        # Get the original message
        original_message = db.query(Message).filter(
            Message.id == regenerate_request.message_id
        ).first()
        
        if not original_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )

        # Verify user owns the conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == original_message.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Get the user message that prompted this response
        user_message = db.query(Message).filter(
            Message.conversation_id == original_message.conversation_id,
            Message.role == "user",
            Message.id < original_message.id
        ).order_by(Message.id.desc()).first()

        if not user_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot find original user message"
            )

        # Create new Langfuse trace for regeneration
        # Use proper model name for Langfuse, not tool names
        trace_model = regenerate_request.model or "llama3:latest"
        if trace_model in ["auto", "internet"]:
            trace_model = "llama3:latest"
        
        trace_id = langfuse_service.create_trace(
            session_id=conversation.langfuse_session_id,
            user_message=user_message.content,
            model=trace_model,
            tool_used=original_message.tool_used or "none"
        )

        # Get conversation history (excluding the original response)
        history_messages = db.query(Message).filter(
            Message.conversation_id == conversation.id,
            Message.id < user_message.id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        conversation_history = []
        for msg in reversed(history_messages):
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })

        # Handle auto mode regeneration
        if original_message.tool_used == "auto":
            try:
                # Ensure we use a valid Ollama model, not a tool name
                model_name = regenerate_request.model
                if not model_name or model_name in ["auto", "internet"]:
                    model_name = "llama3:latest"  # Use default Ollama model
                
                ai_response = await llamaindex_service.generate_auto_response(
                    prompt=user_message.content,
                    conversation_history=conversation_history,
                    model=model_name
                )

                # Log agent reasoning in Langfuse
                langfuse_service.log_agent_reasoning(
                    trace_id=trace_id,
                    reasoning_steps=ai_response.get("reasoning_steps", []),
                    tool_calls=ai_response.get("tool_calls", []),
                    agent_decision={
                        "used_search": ai_response.get("used_search", False),
                        "agent_type": ai_response.get("agent_type", "react"),
                        "fallback": ai_response.get("fallback", False)
                    }
                )

                # Create new assistant message
                new_message = Message(
                    conversation_id=conversation.id,
                    role="assistant",
                    content=ai_response["content"],
                    tool_used=original_message.tool_used,
                    langfuse_trace_id=trace_id,
                    message_metadata={
                        "model": ai_response["model"],
                        "regenerated_from": original_message.id,
                        "agent_type": ai_response.get("agent_type", "react"),
                        "used_search": ai_response.get("used_search", False),
                        "tool_calls": ai_response.get("tool_calls", []),
                        "reasoning_steps": ai_response.get("reasoning_steps", []),
                        "fallback": ai_response.get("fallback", False)
                    }
                )
                db.add(new_message)
                db.commit()
                db.refresh(new_message)

                # Finalize Langfuse trace
                langfuse_service.finalize_trace(trace_id, ai_response["content"])

                return ChatResponse(
                    message=MessageSchema.from_orm(new_message),
                    conversation_id=conversation.id,
                    langfuse_trace_id=trace_id
                )

            except Exception as e:
                logger.error(f"Auto mode regeneration failed: {e}")
                langfuse_service.log_error(trace_id, str(e), "auto_mode_regeneration_error")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Auto mode regeneration failed: {str(e)}"
                )

        # If original message used internet search, return search results without Ollama
        elif original_message.tool_used == "internet":
            search_metadata = None
            search_context = original_message.content  # Reuse the search results content
            
            if original_message.message_metadata:
                search_metadata = original_message.message_metadata.get("search_results")
            
            # Create new assistant message with same search results
            new_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=search_context,
                tool_used=original_message.tool_used,
                langfuse_trace_id=trace_id,
                message_metadata={
                    "search_results": search_metadata,
                    "regenerated_from": original_message.id,
                    "source": "internet_search"
                }
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            # Finalize Langfuse trace
            langfuse_service.finalize_trace(trace_id, search_context)

            return ChatResponse(
                message=MessageSchema.from_orm(new_message),
                conversation_id=conversation.id,
                langfuse_trace_id=trace_id
            )

        # Generate new AI response using Ollama (for "none" tool selection and other cases)
        else:  # This covers tool_used == "none" and any other values
            prompt = user_message.content
            ai_response = await ollama_service.generate_response(
                prompt=prompt,
                conversation_history=conversation_history,
                model=regenerate_request.model,
                system_message="You are a helpful AI assistant. Provide accurate and helpful responses."
            )

            # Log LLM generation in Langfuse
            input_messages = conversation_history + [{"role": "user", "content": prompt}]
            langfuse_service.log_llm_generation(
                trace_id=trace_id,
                model=ai_response["model"],
                input_messages=input_messages,
                output_message=ai_response["content"],
                usage_data=ai_response
            )

            # Create new assistant message
            new_message = Message(
                conversation_id=conversation.id,
                role="assistant",
                content=ai_response["content"],
                tool_used=original_message.tool_used,
                langfuse_trace_id=trace_id,
                message_metadata={
                    "model": ai_response["model"],
                    "regenerated_from": original_message.id,
                    "usage": {
                        "prompt_eval_count": ai_response.get("prompt_eval_count"),
                        "eval_count": ai_response.get("eval_count"),
                        "total_duration": ai_response.get("total_duration"),
                        "eval_duration": ai_response.get("eval_duration")
                    }
                }
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            # Finalize Langfuse trace
            langfuse_service.finalize_trace(trace_id, ai_response["content"])

            return ChatResponse(
                message=MessageSchema.from_orm(new_message),
                conversation_id=conversation.id,
                langfuse_trace_id=trace_id
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Regenerate endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/models")
async def get_available_models():
    """Get list of available Ollama models and tools."""
    try:
        models = await ollama_service.list_models()
        ollama_models = [
            {
                "name": model["name"],
                "size": model.get("size", 0),
                "modified_at": model.get("modified_at", ""),
                "type": "ollama"
            }
            for model in models
        ]
        
        # Add tool options
        tool_options = [
            {
                "name": "auto",
                "size": 0,
                "modified_at": "",
                "type": "tool",
                "description": "AI automatically decides when to use internet search"
            },
            {
                "name": "internet",
                "size": 0,
                "modified_at": "",
                "type": "tool",
                "description": "Direct internet search"
            }
        ]
        
        return {
            "models": ollama_models + tool_options,
            "default_model": "auto",
            "default_ollama_model": ollama_service.default_model
        }
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get available models: {str(e)}"
        )
