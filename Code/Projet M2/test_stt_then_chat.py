from Source.Activities.stt_whisper import WhisperSTT
from Source.Activities.llm_chat import LocalTinyLlamaChat

stt = WhisperSTT(language="en", record_seconds=4)
bot = LocalTinyLlamaChat()

print("Speak now (4s)...")
text = stt.listen_once()
print("STT:", text if text else "[nothing detected]")

if text:
    print("BOT:", bot.reply(text))
