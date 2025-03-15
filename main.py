import json
import pdf2final_list
import dictToPpt
import text2audio

result = pdf2final_list.process("common types of birds in seattle for birding")

enriched_outline = result["enriched_outline"]

text = result["speech_text"]

dictToPpt.dictToPpt(enriched_outline)
print("*"*18)
# text2audio.text_to_speech(text)