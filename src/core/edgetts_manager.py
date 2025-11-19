import asyncio
import edge_tts
import os
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class EdgeTTSManager:
    def __init__(self, output_dir="output"):
        """
        初始化 EdgeTTSManager
        :param output_dir: 语音文件保存目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir = self.output_dir / "output_edgetts"
        
        self.voices = []
        self.voice_map = {}

    async def fetch_voices(self):
        """
        获取所有可用语音参数
        """
        self.voices = await edge_tts.list_voices()
        # 建立 voice_name -> voice_dict 映射
        self.voice_map = {v["ShortName"]: v for v in self.voices}
        return self.voices

    def list_voices(self):
        """
        返回已获取语音列表（ShortName, Gender, Locale）
        """
        return [v["ShortName"] for v in self.voices]

    def get_voice_styles(self, voice_name):
        """
        获取指定语音支持的风格
        """
        return self.voice_map.get(voice_name, {}).get("StyleList", [])

    def get_voice_roles(self, voice_name):
        """
        获取指定语音支持的角色
        """
        return self.voice_map.get(voice_name, {}).get("RolePlayList", [])

    async def generate_speech(self, text, voice="zh-CN-YunxiNeural"):
        """
        生成单条语音
        :param text: 文本
        :param file_name: 输出文件名，不填自动生成
        :param voice: 语音名称
        :return: 输出文件路径
        """
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            file_name = str(text)
            if not file_name.endswith(".wav"):
                file_name += ".wav"
            tts = edge_tts.Communicate(text, voice)
            output_path = self.output_dir / file_name
            await tts.save(output_path)
            logger.info(f"语音生成成功：{output_path}")
        except Exception as e:
            logger.error(f"单条语音生成失败：{e}")
            return None
        return output_path

    async def generate_batch(self, text_list, voice="zh-CN-YunxiNeural", max_concurrent=20):
        """
        批量生成语音，异步并发，限制并发数量
        :param text_list: 文本列表
        :param voice: 语音名称
        :param max_concurrent: 最大并发数
        :return: 文件夹路径 + 成功生成条数
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        try:
            async def sem_task(text):
                async with semaphore:
                    return await self.generate_speech(text, voice)

            tasks = [sem_task(text) for text in text_list]
            results = await asyncio.gather(*tasks)
            count = sum(1 for r in results if r is not None)
        except Exception as e:
            logger.error(f"多条语音生成失败：{e}")
            count = 0
        return self.output_dir, count
