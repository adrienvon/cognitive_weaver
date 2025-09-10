import asyncio
import signal
from src.cognitive_weaver.config import load_config
from src.cognitive_weaver.ai_inference import AIInferenceEngine

async def test_with_timeout():
    try:
        # 加载配置
        config = load_config('config.yaml')
        print(f"AI Provider: {config.ai_model.provider}")
        
        # 初始化AI引擎
        ai_engine = AIInferenceEngine(config)
        
        if ai_engine.client is None:
            print("AI client is None - running in mock mode")
            return
        
        print("AI client initialized successfully")
        print("Testing API call with 10 second timeout...")
        
        # 测试简单的API调用，带超时
        response = await asyncio.wait_for(
            ai_engine.generate_response("Hello, respond with just 'OK'"),
            timeout=10.0
        )
        print(f"AI Response: {response}")
        
    except asyncio.TimeoutError:
        print("API call timed out after 10 seconds")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_with_timeout())
