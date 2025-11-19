import asyncio
import edge_tts

async def main():
    text = "你好，我是微软 Edge 的语音合成。"
    voice = "zh-CN-YunxiNeural"   # 男声
    output_file = "output.wav"

    tts = edge_tts.Communicate(text, voice)
    await tts.save(output_file)

    print("生成完毕:", output_file)

asyncio.run(main())
