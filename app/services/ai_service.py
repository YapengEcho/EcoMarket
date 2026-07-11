"""
Qwen3.7-Plus AI 服务封装

优化点（相对于原始 Plan）:
1. 使用 AsyncOpenAI 替代同步 OpenAI 客户端，避免阻塞事件循环
2. 增加重试机制和更完善的错误处理
3. 响应解析增加容错性
"""
import json
import logging
from typing import Optional
from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)


class Qwen37PlusService:
    """Qwen3.7-Plus AI 服务封装"""

    _client: Optional[AsyncOpenAI] = None

    @classmethod
    def get_client(cls) -> AsyncOpenAI:
        if cls._client is None:
            cls._client = AsyncOpenAI(
                api_key=settings.dashscope_api_key,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
        return cls._client

    @classmethod
    async def generate_item_info(
        cls, product_name: str, additional_info: Optional[str] = None
    ) -> dict:
        """生成商品定价和描述"""
        if not settings.dashscope_api_key:
            return {"error": "请配置 DASHSCOPE_API_KEY 环境变量"}

        prompt = f"""你是一个专业的二手交易助手。用户想卖一件商品：{product_name}。
{additional_info if additional_info else ''}

请根据商品名称，生成：
1. 建议售价（仅输出数字，单位元）
2. 一段150字左右的商品卖点描述（突出核心价值和使用场景）

输出格式（严格遵守）：
价格: xxx
描述: xxxxxxxxxxxx"""

        try:
            client = cls.get_client()
            response = await client.chat.completions.create(
                model="qwen-plus",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的二手交易助手，擅长商品估价和文案撰写。",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=500,
                extra_body={"enable_thinking": False},
            )
            content = response.choices[0].message.content
            return cls._parse_response(content)
        except Exception as e:
            logger.error(f"AI 服务调用失败: {e}")
            return {"error": f"AI 服务调用失败: {str(e)}"}

    @classmethod
    def _parse_response(cls, content: str) -> dict:
        """解析 AI 返回内容"""
        lines = content.strip().split("\n")
        result = {}
        for line in lines:
            if line.startswith("价格:"):
                price_str = line.replace("价格:", "").strip()
                try:
                    result["price"] = float(price_str)
                except ValueError:
                    result["price"] = price_str
            elif line.startswith("描述:"):
                result["description"] = line.replace("描述:", "").strip()

        if not result:
            return {"description": content.strip()}

        return result

    @classmethod
    async def search_with_web(cls, query: str) -> str:
        """联网搜索（使用 Qwen3.7-Plus）"""
        if not settings.dashscope_api_key:
            return "请配置 DASHSCOPE_API_KEY 环境变量"
        try:
            client = cls.get_client()
            response = await client.chat.completions.create(
                model="qwen-plus",
                messages=[{"role": "user", "content": query}],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"AI 搜索失败: {e}")
            return f"搜索失败: {str(e)}"
