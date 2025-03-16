import speech_generator  # Import the new speech generator module
import gpt
import json
import os
import re
from typing import Dict

def clean_json_output(text: str) -> str:
    """
    Clean the GPT output to produce valid JSON:
    - Remove markdown formatting (e.g. ```json and ```)
    - Extract the first JSON block using regex
    - Insert missing commas between adjacent string literals
    """
    # Remove markdown markers
    text = text.replace("```json", "").replace("```", "")
    # Extract the first JSON object (works even if there is extra text)
    match = re.search(r'\{.*\}', text, re.DOTALL)
    json_text = match.group(0) if match else text
    # Insert a comma between adjacent strings (e.g. "text1" "text2" -> "text1", "text2")
    json_text = re.sub(r'(")\s*(")', r'\1, \2', json_text)
    return json_text

def initialOutlinePrompt() -> str:
    return """I am giving you a topic.
    
Your task is to generate a **structured PowerPoint outline** based on the topic.
- The outline must be logically organized.
- Each slide should focus on one key idea.
- Use concise yet informative bullet points.
- If relevant, suggest visuals but avoid unnecessary ones.
- **Important:** The title of the outline must be exactly the input topic.
Format the output strictly as JSON in this structure:
{
    "title": "<Presentation Title>",
    "slides": [
        {
            "title": "<Slide Title>",
            "content": [
                "<Bullet point or short paragraph>",
                ...
            ],
            "visuals" (optional): "Suggestions for images, diagrams, etc."
        },
        ...
    ]
}
Validate the JSON format before finalizing.
"""

def textEnrichmentPrompt() -> str:
    return """
You are an expert assistant that enhances PowerPoint slides.
I provide you with a topic and a slide from an outline.
Enrich the slide by expanding bullet points into:
- A 'bulletPoint' field (the original text)
- A 'shortSubPoints' array with key ideas (brief)
- A 'details' array with examples or extra explanations
Format the response strictly as JSON in this structure:
{
    "title": "<Slide Title>",
    "content": [
        {
            "bulletPoint": "<Original bullet text>",
            "shortSubPoints": ["<Sub-point>", ...],
            "details": ["<Detail>", ...]
        },
        ...
    ]
}
Do not modify the slide title.
Ensure the output is valid JSON.
"""

def perSlideEnrich(topic: str, outline: str, device_type: str = "CPU") -> dict:
    # Clean and parse the initial outline
    try:
        cleaned_outline = clean_json_output(outline)
        outline = json.loads(cleaned_outline)
    except json.JSONDecodeError:
        print("Error: Could not parse outline JSON even after cleaning. Using empty structure.")
        outline = {"title": topic, "slides": []}
    # Enrich each slide
    for i, slide in enumerate(outline.get('slides', [])):
        visual = slide.pop('visuals', None)
        enrichedSlide = gpt.gpt_summarise(
            system=textEnrichmentPrompt(),
            text=f"topic: {topic}\n\nslides: {json.dumps(slide)}",
            device_type=device_type
        )
        enrichedSlide = clean_json_output(enrichedSlide)
        try:
            enrichedSlide = json.loads(enrichedSlide)
        except json.JSONDecodeError:
            print(f"Warning: Slide {i} could not be enriched. Skipping enrichment for this slide.")
            enrichedSlide = {
                "title": slide.get('title', f"Slide {i+1}"),
                "content": [{"bulletPoint": content, "shortSubPoints": [], "details": []} for content in slide.get('content', [])]
            }
        if visual:
            enrichedSlide['visuals'] = visual
        outline['slides'][i] = enrichedSlide
    return outline

def generateIntroSpeech(enriched_outline: dict, device_type: str = "CPU") -> dict:
    title = enriched_outline['title']
    slide_titles = [slide['title'] for slide in enriched_outline.get('slides', [])]
    intro_prompt = f"""
Title: {title}
Main sections: {', '.join(slide_titles)}
Create an introduction for this presentation that starts with "Hello everyone. Today, I will be presenting about {title}." Make sure the title exactly matches the input topic.
"""
    introduction = gpt.gpt_summarise(
        system=speech_generator.generate_speech_introduction_prompt(),
        text=intro_prompt,
        device_type=device_type
    )
    enriched_outline['introduction'] = introduction
    return enriched_outline

def generateSlideSpeech(enriched_outline: dict, device_type: str = "CPU") -> dict:
    for i, slide in enumerate(enriched_outline.get('slides', [])):
        simplified_content = []
        for item in slide.get('content', []):
            details = item.get('details', [])
            details_text = " ".join([d[:200] for d in details]) if details else ""
            bullet = item.get('bulletPoint', item if isinstance(item, str) else "")
            simplified_content.append(f"{bullet} - {details_text}")
        slide_prompt = f"""
Slide Title: {slide['title']}

Key Points:
- {" ".join(simplified_content[:5])}

Convert this into a natural language speech section (3-5 sentences).
"""
        section_text = gpt.gpt_summarise(
            system=speech_generator.generate_speech_section_prompt(),
            text=slide_prompt,
            device_type=device_type
        )
        enriched_outline['slides'][i]['speech'] = section_text
    return enriched_outline

def process(topic: str, device_type="CPU", use_chunking=True) -> Dict[str, any]:
    # Generate initial outline using the specified device type
    outlineText = gpt.gpt_summarise(
        system=initialOutlinePrompt(),
        text=topic,
        device_type=device_type
    )
    print("Initial outline generated.")
    print(outlineText)
    # Enrich each slide using the same device type
    enrichedOutline = perSlideEnrich(topic, outlineText, device_type=device_type)
    print("Outline enriched in bulk.")
    enrichedOutline = generateIntroSpeech(enrichedOutline, device_type=device_type)
    print("Introduction speech generated.")
    enrichedOutline = generateSlideSpeech(enrichedOutline, device_type=device_type)
    print("Slide speech generated.")
    speech_text = speech_generator.create_speech_from_enriched_outline(enrichedOutline)
    print("TTS-ready speech script generated.")
    speech_generator.save_speech_to_file(speech_text)
    return {"enriched_outline": enrichedOutline, "speech_text": speech_text}
