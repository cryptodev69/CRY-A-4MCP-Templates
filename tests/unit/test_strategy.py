from src.cry_a_4mcp.crawl4ai.extraction_strategies.base import LLMExtractionStrategy

class TestStrategy(LLMExtractionStrategy):
    SCHEMA = {
        "type": "object",
        "properties": {
            "test_field": {"type": "string"}
        }
    }
    
    INSTRUCTION = "This is a test strategy for extraction."
    
    def extract(self, content, **kwargs):
        return {"test_field": "This is a test result"}