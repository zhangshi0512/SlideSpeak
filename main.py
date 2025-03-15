import pdf2final_list
import dictToPpt
# import text2audio_pyttsx3
import json

result = pdf2final_list.process("Coca-Cola's use of Cloud Computing")

enriched_outline = result["enriched_outline"]
speech_text = result["speech_text"]
# 定义文件路径
outline_path = "./output/enriched_outline.json"
speech_text_path = "./output/presentation_speech.md"

# 保存 enriched_outline 到 JSON 文件
with open(outline_path, "w", encoding="utf-8") as file:
    json.dump(enriched_outline, file, ensure_ascii=False, indent=4)

# 保存 speech_text 到文本文件
with open(speech_text_path, "w", encoding="utf-8") as file:
    file.write(speech_text)

# Pass the speech_text to dictToPpt to include it in speaker notes
dictToPpt.dictToPpt(enriched_outline, speech_text)
print("*"*18)
# text2audio_pyttsx3.text_to_speech(speech_text)
