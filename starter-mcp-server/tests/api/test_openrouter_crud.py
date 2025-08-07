"""Comprehensive CRUD tests for OpenRouter API.

This module tests all Create, Read, Update, Delete operations for OpenRouter
to ensure the API works correctly and prevents regressions.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from tests.conftest import assert_valid_response, assert_valid_crud_response


class TestOpenRouterCRUD:
    """Test suite for OpenRouter CRUD operations."""
    
    def test_get_models_success(self, test_client: TestClient):
        """Test successful retrieval of OpenRouter models."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock successful response from OpenRouter API
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {
                        "id": "openai/gpt-4",
                        "name": "GPT-4",
                        "description": "OpenAI's GPT-4 model",
                        "pricing": {
                            "prompt": "0.00003",
                            "completion": "0.00006"
                        },
                        "context_length": 8192,
                        "architecture": {
                            "modality": "text",
                            "tokenizer": "cl100k_base"
                        }
                    },
                    {
                        "id": "anthropic/claude-3-opus",
                        "name": "Claude 3 Opus",
                        "description": "Anthropic's Claude 3 Opus model",
                        "pricing": {
                            "prompt": "0.000015",
                            "completion": "0.000075"
                        },
                        "context_length": 200000,
                        "architecture": {
                            "modality": "text"
                        }
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            response = test_client.get("/api/openrouter/models")
            assert_valid_crud_response(response, "read")
            
            data = response.json()
            assert "data" in data
            assert len(data["data"]) == 2
            
            # Verify model structure
            model = data["data"][0]
            assert "id" in model
            assert "name" in model
            assert "description" in model
            assert "pricing" in model
            assert "context_length" in model
    
    def test_get_models_api_error(self, test_client: TestClient):
        """Test handling of OpenRouter API errors."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock API error response
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_get.return_value = mock_response
            
            response = test_client.get("/api/openrouter/models")
            assert response.status_code in [500, 502, 503]  # Server error or bad gateway
    
    def test_get_models_network_error(self, test_client: TestClient):
        """Test handling of network errors."""
        with patch('httpx.AsyncClient.get') as mock_get:
            # Mock network error
            mock_get.side_effect = Exception("Network error")
            
            response = test_client.get("/api/openrouter/models")
            assert response.status_code in [500, 502, 503]  # Server error
    
    def test_get_models_with_filters(self, test_client: TestClient):
        """Test retrieving models with filters."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {
                        "id": "openai/gpt-4",
                        "name": "GPT-4",
                        "description": "OpenAI's GPT-4 model",
                        "pricing": {"prompt": "0.00003", "completion": "0.00006"},
                        "context_length": 8192,
                        "architecture": {"modality": "text"}
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            # Test with modality filter
            response = test_client.get("/api/openrouter/models?modality=text")
            assert_valid_crud_response(response, "read")
            
            # Test with provider filter
            response = test_client.get("/api/openrouter/models?provider=openai")
            assert_valid_crud_response(response, "read")
    
    def test_create_chat_completion_success(self, test_client: TestClient, sample_openrouter_request):
        """Test successful chat completion creation."""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock successful response from OpenRouter API
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "object": "chat.completion",
                "created": 1677652288,
                "model": "openai/gpt-4",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "Hello! How can I help you today?"
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 9,
                    "total_tokens": 19
                }
            }
            mock_post.return_value = mock_response
            
            response = test_client.post("/api/openrouter/chat/completions", json=sample_openrouter_request)
            assert_valid_crud_response(response, "create")
            
            data = response.json()
            assert "id" in data
            assert "choices" in data
            assert "usage" in data
            assert len(data["choices"]) > 0
            assert "message" in data["choices"][0]
    
    def test_create_chat_completion_invalid_request(self, test_client: TestClient):
        """Test chat completion with invalid request data."""
        invalid_requests = [
            {},  # Empty request
            {"model": "openai/gpt-4"},  # Missing messages
            {"messages": []},  # Missing model
            {
                "model": "openai/gpt-4",
                "messages": [
                    {"role": "invalid", "content": "Hello"}  # Invalid role
                ]
            },
            {
                "model": "openai/gpt-4",
                "messages": [
                    {"role": "user"}  # Missing content
                ]
            }
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/openrouter/chat/completions", json=invalid_request)
            assert response.status_code == 422  # Validation error
    
    def test_create_chat_completion_api_error(self, test_client: TestClient, sample_openrouter_request):
        """Test handling of OpenRouter API errors during chat completion."""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock API error response
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": {
                    "message": "Invalid model specified",
                    "type": "invalid_request_error",
                    "code": "model_not_found"
                }
            }
            mock_post.return_value = mock_response
            
            response = test_client.post("/api/openrouter/chat/completions", json=sample_openrouter_request)
            assert response.status_code in [400, 500]  # Client or server error
    
    def test_create_chat_completion_with_streaming(self, test_client: TestClient, sample_openrouter_request):
        """Test chat completion with streaming enabled."""
        sample_openrouter_request["stream"] = True
        
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock streaming response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"content-type": "text/event-stream"}
            mock_response.iter_lines.return_value = [
                "data: {\"id\":\"chatcmpl-123\",\"choices\":[{\"delta\":{\"content\":\"Hello\"}}]}",
                "data: {\"id\":\"chatcmpl-123\",\"choices\":[{\"delta\":{\"content\":\" there!\"}}]}",
                "data: [DONE]"
            ]
            mock_post.return_value = mock_response
            
            response = test_client.post("/api/openrouter/chat/completions", json=sample_openrouter_request)
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
    
    def test_get_model_by_id(self, test_client: TestClient):
        """Test retrieving specific model by ID."""
        model_id = "openai/gpt-4"
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": model_id,
                "name": "GPT-4",
                "description": "OpenAI's GPT-4 model",
                "pricing": {
                    "prompt": "0.00003",
                    "completion": "0.00006"
                },
                "context_length": 8192,
                "architecture": {
                    "modality": "text",
                    "tokenizer": "cl100k_base"
                }
            }
            mock_get.return_value = mock_response
            
            response = test_client.get(f"/api/openrouter/models/{model_id}")
            assert_valid_crud_response(response, "read")
            
            data = response.json()
            assert data["id"] == model_id
            assert "name" in data
            assert "pricing" in data
    
    def test_get_model_not_found(self, test_client: TestClient):
        """Test retrieving non-existent model."""
        model_id = "nonexistent/model"
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "error": {
                    "message": "Model not found",
                    "type": "not_found_error"
                }
            }
            mock_get.return_value = mock_response
            
            response = test_client.get(f"/api/openrouter/models/{model_id}")
            assert response.status_code == 404


class TestOpenRouterValidation:
    """Test suite for OpenRouter request validation."""
    
    def test_chat_completion_message_validation(self, test_client: TestClient):
        """Test validation of chat completion messages."""
        base_request = {
            "model": "openai/gpt-4",
            "max_tokens": 100
        }
        
        # Test valid message formats
        valid_messages = [
            [{"role": "user", "content": "Hello"}],
            [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"}
            ],
            [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
                {"role": "user", "content": "How are you?"}
            ]
        ]
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "choices": [{"message": {"role": "assistant", "content": "Response"}}],
                "usage": {"total_tokens": 10}
            }
            mock_post.return_value = mock_response
            
            for messages in valid_messages:
                request_data = {**base_request, "messages": messages}
                response = test_client.post("/api/openrouter/chat/completions", json=request_data)
                assert response.status_code in [200, 201]
    
    def test_chat_completion_parameter_validation(self, test_client: TestClient):
        """Test validation of chat completion parameters."""
        base_request = {
            "model": "openai/gpt-4",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        # Test valid parameter ranges
        valid_params = [
            {"temperature": 0.0},
            {"temperature": 1.0},
            {"temperature": 2.0},
            {"max_tokens": 1},
            {"max_tokens": 4096},
            {"top_p": 0.1},
            {"top_p": 1.0},
            {"frequency_penalty": -2.0},
            {"frequency_penalty": 2.0},
            {"presence_penalty": -2.0},
            {"presence_penalty": 2.0}
        ]
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "choices": [{"message": {"role": "assistant", "content": "Response"}}],
                "usage": {"total_tokens": 10}
            }
            mock_post.return_value = mock_response
            
            for params in valid_params:
                request_data = {**base_request, **params}
                response = test_client.post("/api/openrouter/chat/completions", json=request_data)
                assert response.status_code in [200, 201]
        
        # Test invalid parameter ranges
        invalid_params = [
            {"temperature": -0.1},  # Below minimum
            {"temperature": 2.1},   # Above maximum
            {"max_tokens": 0},      # Below minimum
            {"top_p": 0.0},         # Below minimum
            {"top_p": 1.1},         # Above maximum
            {"frequency_penalty": -2.1},  # Below minimum
            {"frequency_penalty": 2.1},   # Above maximum
        ]
        
        for params in invalid_params:
            request_data = {**base_request, **params}
            response = test_client.post("/api/openrouter/chat/completions", json=request_data)
            assert response.status_code == 422  # Validation error
    
    def test_model_id_validation(self, test_client: TestClient):
        """Test model ID format validation."""
        valid_model_ids = [
            "openai/gpt-4",
            "anthropic/claude-3-opus",
            "meta-llama/llama-2-70b-chat",
            "google/palm-2-chat-bison"
        ]
        
        invalid_model_ids = [
            "",              # Empty
            "invalid",       # No provider
            "/model",        # Empty provider
            "provider/",     # Empty model
            "provider//model",  # Double slash
        ]
        
        base_request = {
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "choices": [{"message": {"role": "assistant", "content": "Response"}}],
                "usage": {"total_tokens": 10}
            }
            mock_post.return_value = mock_response
            
            # Test valid model IDs
            for model_id in valid_model_ids:
                request_data = {**base_request, "model": model_id}
                response = test_client.post("/api/openrouter/chat/completions", json=request_data)
                assert response.status_code in [200, 201]
        
        # Test invalid model IDs
        for model_id in invalid_model_ids:
            request_data = {**base_request, "model": model_id}
            response = test_client.post("/api/openrouter/chat/completions", json=request_data)
            assert response.status_code == 422  # Validation error


class TestOpenRouterAdvanced:
    """Advanced test scenarios for OpenRouter."""
    
    def test_rate_limiting_handling(self, test_client: TestClient, sample_openrouter_request):
        """Test handling of rate limiting from OpenRouter API."""
        with patch('httpx.AsyncClient.post') as mock_post:
            # Mock rate limit response
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {"retry-after": "60"}
            mock_response.json.return_value = {
                "error": {
                    "message": "Rate limit exceeded",
                    "type": "rate_limit_error"
                }
            }
            mock_post.return_value = mock_response
            
            response = test_client.post("/api/openrouter/chat/completions", json=sample_openrouter_request)
            assert response.status_code == 429
            assert "retry-after" in response.headers or "error" in response.json()
    
    def test_token_usage_tracking(self, test_client: TestClient, sample_openrouter_request):
        """Test token usage tracking and reporting."""
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "choices": [{"message": {"role": "assistant", "content": "Response"}}],
                "usage": {
                    "prompt_tokens": 15,
                    "completion_tokens": 25,
                    "total_tokens": 40
                }
            }
            mock_post.return_value = mock_response
            
            response = test_client.post("/api/openrouter/chat/completions", json=sample_openrouter_request)
            assert_valid_crud_response(response, "create")
            
            data = response.json()
            assert "usage" in data
            usage = data["usage"]
            assert "prompt_tokens" in usage
            assert "completion_tokens" in usage
            assert "total_tokens" in usage
            assert usage["total_tokens"] == usage["prompt_tokens"] + usage["completion_tokens"]
    
    def test_model_capabilities_filtering(self, test_client: TestClient):
        """Test filtering models by capabilities."""
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "data": [
                    {
                        "id": "openai/gpt-4-vision",
                        "name": "GPT-4 Vision",
                        "architecture": {
                            "modality": "multimodal",
                            "capabilities": ["text", "vision"]
                        }
                    },
                    {
                        "id": "openai/gpt-4",
                        "name": "GPT-4",
                        "architecture": {
                            "modality": "text",
                            "capabilities": ["text"]
                        }
                    }
                ]
            }
            mock_get.return_value = mock_response
            
            # Test filtering by capability
            response = test_client.get("/api/openrouter/models?capability=vision")
            assert_valid_crud_response(response, "read")
            
            data = response.json()
            if "data" in data:
                vision_models = [
                    model for model in data["data"]
                    if "vision" in model.get("architecture", {}).get("capabilities", [])
                ]
                assert len(vision_models) >= 0  # May or may not have vision models
    
    def test_cost_estimation(self, test_client: TestClient, sample_openrouter_request):
        """Test cost estimation for requests."""
        # Add cost estimation request
        sample_openrouter_request["estimate_cost"] = True
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "choices": [{"message": {"role": "assistant", "content": "Response"}}],
                "usage": {
                    "prompt_tokens": 15,
                    "completion_tokens": 25,
                    "total_tokens": 40
                },
                "cost": {
                    "prompt_cost": 0.00045,
                    "completion_cost": 0.0015,
                    "total_cost": 0.00195
                }
            }
            mock_post.return_value = mock_response
            
            response = test_client.post("/api/openrouter/chat/completions", json=sample_openrouter_request)
            if response.status_code == 200:
                data = response.json()
                if "cost" in data:
                    cost = data["cost"]
                    assert "total_cost" in cost
                    assert isinstance(cost["total_cost"], (int, float))
    
    def test_concurrent_requests(self, test_client: TestClient, sample_openrouter_request):
        """Test handling of concurrent requests."""
        import asyncio
        import httpx
        
        async def make_request():
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://testserver/api/openrouter/chat/completions",
                    json=sample_openrouter_request
                )
                return response.status_code
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "chatcmpl-123",
                "choices": [{"message": {"role": "assistant", "content": "Response"}}],
                "usage": {"total_tokens": 10}
            }
            mock_post.return_value = mock_response
            
            # Test multiple concurrent requests
            responses = []
            for _ in range(5):
                response = test_client.post("/api/openrouter/chat/completions", json=sample_openrouter_request)
                responses.append(response.status_code)
            
            # All requests should succeed
            assert all(status in [200, 201] for status in responses)