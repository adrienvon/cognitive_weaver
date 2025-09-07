import asyncio
from src.cognitive_weaver.config import load_config
from src.cognitive_weaver.ai_inference import AIInferenceEngine

async def test_ai_connection():
    # 加载配置
    config = load_config('config.yaml')
    print(f"AI Provider: {config.ai_model.provider}")
    print(f"Model: {config.ai_model.model_name}")
    print(f"API Key: {config.ai_model.api_key[:10]}..." if config.ai_model.api_key else "No API key")
    print(f"Base URL: {config.ai_model.base_url}")
    
    # 初始化AI引擎
    ai_engine = AIInferenceEngine(config)
    
    if ai_engine.client is None:
        print("AI client is None - running in mock mode")
        return
    
    print("AI client initialized successfully")
    
    # 测试简单的API调用
    try:
        print("Testing simple API call...")
        response = await ai_engine.generate_response("Hello, can you respond with just 'OK'?")
        print(f"AI Response: {response}")
    except Exception as e:
        print(f"API call failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai_connection())
