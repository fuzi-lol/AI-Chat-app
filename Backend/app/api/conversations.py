from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.middleware.auth_middleware import get_current_active_user
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.conversation import (
    Conversation as ConversationSchema,
    ConversationCreate,
    ConversationUpdate,
    ConversationWithMessages
)
from app.schemas.chat import Message as MessageSchema
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("/", response_model=List[ConversationSchema])
def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all conversations for the current user with pagination."""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(
        Conversation.updated_at.desc()
    ).offset(skip).limit(limit).all()
    
    return conversations


@router.post("/", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED)
def create_conversation(
    conversation: ConversationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new conversation."""
    db_conversation = Conversation(
        user_id=current_user.id,
        title=conversation.title
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


@router.get("/{conversation_id}", response_model=ConversationWithMessages)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation with all its messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get messages for this conversation
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    # Convert to schema
    conversation_dict = {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "langfuse_session_id": conversation.langfuse_session_id,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "messages": [MessageSchema.from_orm(msg) for msg in messages]
    }
    
    return ConversationWithMessages(**conversation_dict)


@router.get("/{conversation_id}/messages", response_model=List[MessageSchema])
def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get messages for a specific conversation with pagination."""
    # Verify user owns the conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(
        Message.created_at.asc()
    ).offset(skip).limit(limit).all()
    
    return [MessageSchema.from_orm(msg) for msg in messages]


@router.put("/{conversation_id}", response_model=ConversationSchema)
def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a conversation (e.g., change title)."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Update fields if provided
    if conversation_update.title is not None:
        conversation.title = conversation_update.title
    
    db.commit()
    db.refresh(conversation)
    return conversation


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a conversation and all its messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Delete all messages in the conversation (cascade should handle this)
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    
    # Delete the conversation
    db.delete(conversation)
    db.commit()
    
    return None


@router.delete("/{conversation_id}/messages/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(
    conversation_id: int,
    message_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a specific message from a conversation."""
    # Verify user owns the conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Find and delete the message
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.conversation_id == conversation_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    db.delete(message)
    db.commit()
    
    return None


@router.get("/{conversation_id}/export")
def export_conversation(
    conversation_id: int,
    format: str = Query("json", regex="^(json|markdown)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Export a conversation in JSON or Markdown format."""
    # Verify user owns the conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
    
    # Get all messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    if format == "json":
        return {
            "conversation": {
                "id": conversation.id,
                "title": conversation.title,
                "created_at": conversation.created_at.isoformat(),
                "updated_at": conversation.updated_at.isoformat(),
                "langfuse_session_id": conversation.langfuse_session_id
            },
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "tool_used": msg.tool_used,
                    "langfuse_trace_id": msg.langfuse_trace_id,
                    "metadata": msg.message_metadata,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in messages
            ]
        }
    
    elif format == "markdown":
        markdown_content = f"# {conversation.title or f'Conversation {conversation.id}'}\n\n"
        markdown_content += f"**Created:** {conversation.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        markdown_content += f"**Updated:** {conversation.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        markdown_content += "---\n\n"
        
        for msg in messages:
            role_emoji = "🧑" if msg.role == "user" else "🤖" if msg.role == "assistant" else "⚙️"
            role_title = msg.role.title()
            
            markdown_content += f"## {role_emoji} {role_title}\n\n"
            markdown_content += f"{msg.content}\n\n"
            
            if msg.tool_used and msg.tool_used != "none":
                markdown_content += f"*Tool used: {msg.tool_used}*\n\n"
            
            markdown_content += f"*{msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            markdown_content += "---\n\n"
        
        return {
            "content": markdown_content,
            "filename": f"conversation_{conversation_id}.md"
        }
