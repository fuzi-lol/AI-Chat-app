import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class OllamaService:
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.default_model = settings.ollama_default_model
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(120.0),
            limits=httpx.Limits(max_keepalive_connections=10)
        )

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def list_models(self) -> List[Dict[str, Any]]:
        """List all available models in Ollama."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()
            return data.get("models", [])
        except httpx.RequestError as e:
            logger.error(f"Error connecting to Ollama: {e}")
            raise Exception(f"Failed to connect to Ollama: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e}")
            raise Exception(f"Ollama API error: {e}")

    async def pull_model(self, model_name: str) -> bool:
        """Pull a model to Ollama."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/pull",
                json={"name": model_name}
            )
            response.raise_for_status()
            return True
        except httpx.RequestError as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"Error pulling model {model_name}: {e}")
            return False

    async def check_model_exists(self, model_name: str) -> bool:
        """Check if a model exists in Ollama."""
        try:
            models = await self.list_models()
            model_names = [model["name"] for model in models]
            return model_name in model_names
        except Exception as e:
            logger.warning(f"Could not check if model exists: {e}")
            return False

    def format_conversation_history(self, messages: List[Dict[str, str]], max_messages: int = 10) -> List[Dict[str, str]]:
        """Format conversation history for Ollama, keeping last N messages."""
        # Take the last max_messages messages
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        formatted_messages = []
        for msg in recent_messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted_messages

    async def generate_response(
        self,
        prompt: str,
        conversation_history: List[Dict[str, str]] = None,
        model: Optional[str] = None,
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a response from Ollama."""
        if model == 'auto':
            model_name = self.default_model
        else:
            model_name = model
        
        # Optionally check if model exists, but don't block if check fails
        try:
            if not await self.check_model_exists(model_name):
                logger.info(f"Model {model_name} not found, attempting to pull...")
                # if not await self.pull_model(model_name):
                #     logger.warning(f"Could not pull model {model_name}, but will attempt to use it anyway")
        except Exception as e:
            logger.warning(f"Model check failed: {e}. Proceeding anyway...")

        # Prepare messages
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add conversation history
        if conversation_history:
            formatted_history = self.format_conversation_history(conversation_history)
            messages.extend(formatted_history)
        
        # Add current user message
        messages.append({"role": "user", "content": prompt})

        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=120.0
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "content": data.get("response", ""),
                "model": model_name,
                "total_duration": data.get("total_duration"),
                "load_duration": data.get("load_duration"),
                "prompt_eval_count": data.get("prompt_eval_count"),
                "prompt_eval_duration": data.get("prompt_eval_duration"),
                "eval_count": data.get("eval_count"),
                "eval_duration": data.get("eval_duration")
            }
            
        except httpx.RequestError as e:
            logger.error(f"Error generating response: {e}")
            error_msg = str(e)
            if "Connection refused" in error_msg or "Connect" in error_msg:
                raise Exception(f"Cannot connect to Ollama at {self.base_url}. Make sure Ollama is running.")
            raise Exception(f"Failed to generate response: {error_msg}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama API error: {e.response.status_code} - {e.response.text}")
            try:
                error_detail = e.response.json()
                error_msg = error_detail.get("error", e.response.text)
            except:
                error_msg = e.response.text
            raise Exception(f"Ollama API error (Status {e.response.status_code}): {error_msg}")

    async def health_check(self) -> bool:
        """Check if Ollama is healthy."""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False


# Global instance
ollama_service = OllamaService()
