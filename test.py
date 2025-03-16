import gpt 
import pdf2final_list
import json
import speech_generator
import re

def clean_json_output(text: str) -> str:
    text = text.replace("```json", "").replace("```", "")
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1:
        text = text[start:end+1]
    text = re.sub(r'(")\s*(")', r'\1, \2', text)
    return text

def perSlideEnrich(topic: str, outline: str) -> dict:
    try:
        cleaned_outline = clean_json_output(outline)
        outline = json.loads(cleaned_outline)
    except json.JSONDecodeError:
        print("Error: Could not parse outline JSON even after cleaning. Using empty structure.")
        outline = {"title": "Presentation", "slides": []}
    for i, slide in enumerate(outline.get('slides', [])):
        visual = slide.pop('visuals', None)
        enrichedSlide = gpt.gpt_summarise(
            system=textEnrichmentPrompt(), 
            text=f"topic: {topic}\n\n" + json.dumps(slide)
        )
        enrichedSlide = clean_json_output(enrichedSlide)
        try: 
            enrichedSlide = json.loads(enrichedSlide)
        except json.JSONDecodeError:
            print(f"Warning: Slide {i} could not be enriched. Skipping.")
            enrichedSlide = {
                "title": slide.get('title', 'Slide ' + str(i+1)), 
                "content": [{"bulletPoint": content, "shortSubPoints": [], "details": []} for content in slide.get('content', [])]
            }
        if visual:
            enrichedSlide['visuals'] = visual 
        outline['slides'][i] = enrichedSlide
    return outline

def textEnrichmentPrompt():
    return """
    You are an expert assistant that enhances PowerPoint slides by expanding on key points while keeping the content structured and concise.

    I am providing you with a topic, and a structured PowerPoint outline for a single slide.

    Your task is to **enrich** the provided slide content where necessary by:
    - Expanding each bullet point with **more details, examples, or explanations** into the details list.
    - Breaking down complex ideas into **shorter sub-points** that can fit into a Powerpoint slide.
    - Keeping the response clear, structured, and presentation friendly

    Strictly format the response as JSON with the following structure:
    {
        "title": "<Slide Title>",
        "content": [
            {
                "bulletPoint": "<Original Bullet Points>",
                "shortSubPoints": [
                    "Condensed key idea for PowerPoint",
                    "Another brief sub-point",
                    "Further clarification if needed"
                ],
                "details": [
                    "Detailed explanation or examples"
                ]
            }
        ]
    }

    **Important:**  
    - Validate the output format before finalizing.  
    - Do not change the original slide structure or reword titles.  
    - Maintain a structured and informative tone.
    - Ensure the summary remains slide-friendly (short and digestible).
    """

if __name__ == "__main__":
    topic = "kfc and macdonald in china"
    outlineText = gpt.gpt_summarise(system=pdf2final_list.initialOutlinePrompt(), text=topic)
    print("Initial outline generated.")
    print(outlineText)

    enrichedOutline = perSlideEnrich(topic, outlineText)
    print("Outline enriched slide by slide.")
    print(enrichedOutline)
