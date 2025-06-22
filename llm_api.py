

import requests
from typing import List, Dict
import re   


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url

    def chat_completions_create(self, model: str, messages: List[Dict[str, str]], temperature: float = 0.8) -> Dict:
        """
        使用Ollama API创建聊天完成
        """
        data = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "seed": 101,
                "temperature": temperature
            },
        }
        print("______chat_completions_create______")    
        print("=====request data=====\n", data)
        response = requests.post(f"{self.base_url}/api/chat", json=data)
        response.raise_for_status()
        result = response.json()
        print("=====response data=====\n", result)
        return self.get_raw_text(result)
         
    def get_raw_text(self, result: Dict) -> str:
        return result["message"]["content"]

    def transform_response_to_openai_format(self, result: Dict) -> Dict:
        # 转换为与OpenAI API类似的格式
        return {
            "choices": [{
                "message": {
                    "content": result["message"]["content"]
                }
            }]
        }
        
    def remove_think_tags(self, text: str) -> str:
        """
        移除文本中的思维链部分（<think>标签之间的内容）
        :param text: 包含思维链的原始文本
        :return: 移除思维链后的文本
        
        示例:
        输入: "这是开头<think>这是思维过程</think>这是结论"
        输出: "这是开头这是结论"
        """
        
        # 使用非贪婪模式匹配<think>标签及其内容
        pattern = r'<think>.*?</think>'
        # 移除所有匹配到的内容
        cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
        # 移除可能产生的多余空行
        cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text)
        return cleaned_text.strip()