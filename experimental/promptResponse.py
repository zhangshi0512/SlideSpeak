from typing import List
import sys, os, json
import experimentalGpt

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
sys.path.append(parent_dir)

import gpt

# Only to make the prompt more readable
def initialOutlinePrompt() -> str: 
    return """I am giving you a topic. 
    
    Yout task is to generate a **structured PowerPoint outline** based on the topic.

    - Ensure the outline is **logically organized** with a clear flow of information.  
    - Each slide should focus on **one key idea** to maintain clarity.  
    - Use **concise yet informative** bullet points or short paragraphs for each slide.  
    - If relevant, suggest visuals that enhance understanding, but **avoid unnecessary visuals.**  
    - The total number of slides should be determined **dynamically**, based on the depth required for the topic.  
    
    Format the response as JSON with the following structure: 
    {
        "title": "<Presentation Title>",
        "slides": [
            {
                "title": "<Slide Title>",
                "content": [
                    "<Bullet points or short paragraphs expanding on the slide's topic>",
                    ...
                ],
                "visuals" (optional): "Relevant suggestions for images, diagrams, or charts, if they add value. Otherwise, exclude this field."
            },
            ...
        ]
    }
    """

def oneStepEnrichmentPrompt() -> str:
    return """
    You are an expert assistant that enhances PowerPoint slides by expanding on key points while keeping the content structured, clear, and concise.

    I am providing you with a structured PowerPoint outline. 

    Your task is to **enrich** the slides by expanding each bullet point with more details, ensuring completeness and relevance.

    - **Each slide in the input must be included in the output. Do not omit any slides.**  
    - **Each bullet point must have at least one detailed expansion, unless it is already fully detailed.**  
    - Add **sub-points** where appropriate to provide context or explanation.  
    - Provide **brief but meaningful examples** when helpful.  
    - Ensure the content remains **concise, structured, and useful for a presentation.**  
    - **Do not add unnecessary visuals** unless they are explicitly mentioned in the input.  

    **Output Format: Strict JSON**
    Ensure the response follows this exact structure:
    {
        "title": "<Presentation Title>",
        "slides": [
            {
                "title": "<Slide Title>",
                "content": [
                    {
                        "bulletPoint": "Main bullet point",
                        "details": [
                            "Expanded explanation or examples",
                            "Further breakdown if needed"
                        ]
                    }, 
                    ...
                ],
                "visuals" (optional): "Include only if it exists in the input."
            },
            ...
        ]
    }

    **Important:**  
    - Validate the output format before finalizing.  
    - Do not change the original slide structure or reword titles.  
    - Maintain a structured and informative tone.  
    """

def perSlideEnrichmentPrompt() -> str:
    return """
    You are an expert assistant that enhances PowerPoint slides by expanding on key points while keeping the content structured and concise.

    I am providing you with a topic, and a structured PowerPoint outline for a single slide.

    Your task is to **enrich** the provided slide content where necessary by:
    - Expanding each bullet point with **more details, examples, or explanations**.
    - Breaking down complex ideas into **sub-points** where relevant. 

    Keep responses **clear and presentation-friendly**.

    Strictly format the response as JSON with the following structure:
    {
        "title": "<Slide Title>",
        "content": [
            {
                "bulletPoint": "<Original Bullet Points>",
                "details": [
                    "Detailed explanation or examples",
                    ...
                ]
            }, 
            ...
        ]
    }

    **Important:**  
    - Validate the output format before finalizing.  
    - Do not change the original slide structure or reword titles.  
    - Maintain a structured and informative tone.  
    """

def generate_speech_prompt() -> str:
    return """
    You are an expert speech writer who creates TTS-optimized speech scripts.
    
    Your task is to transform the provided content into a speech script specifically formatted for text-to-speech (TTS) systems.
    
    STRICT FORMAT REQUIREMENTS (you must follow these exactly):
    
    1. Start with the exact greeting: "Hello everyone. Today, I will be presenting about [TOPIC]. In this presentation, I will cover [LIST 3-5 KEY SECTIONS]."
    
    2. For each section or slide, begin with: "Let's discuss [SECTION TITLE]." followed by the content in natural conversational language.
    
    3. Between sections, add the transition: "[PAUSE=1] Moving on to our next topic. [SLIDE CHANGE]"
    
    4. Include precise pause indicators: "[PAUSE=1]" for 1-second pauses, "[PAUSE=2]" for 2-second pauses.
    
    5. End with exactly: "Thank you for your attention. [PAUSE=1] If you have any questions, I'd be happy to address them now. [PAUSE=2]"
    
    IMPORTANT LANGUAGE GUIDELINES:
    - Use simple, clear sentences that work well for TTS
    - Avoid complex words or terms that might be mispronounced
    - Break down complex concepts into shorter, digestible statements
    - Use natural transitions between ideas
    
    The final output should read as a continuous speech that a TTS system could read without awkward phrasing or unclear structure.
    """

# Convert outline to TTS-ready speech script
def outline_to_speech(enriched_outline: dict) -> str:
    """
    Convert an enriched presentation outline to a TTS-ready speech script.
    
    Args:
        enriched_outline (dict): The enriched outline in JSON format
        
    Returns:
        str: A formatted speech script optimized for TTS systems
    """
    # Convert dictionary to JSON string if needed
    if isinstance(enriched_outline, dict):
        outline_json = json.dumps(enriched_outline)
    else:
        outline_json = enriched_outline
    
    # Generate the speech script using LLM
    speech_text = experimentalGpt.gpt_summarise(system=generate_speech_prompt(), text=outline_json)
    
    return speech_text

# Save speech script to file
def save_speech_to_file(speech_text: str, filename: str = "presentation_speech.md"):
    """
    Save the generated TTS-ready speech script to a markdown file.
    
    Args:
        speech_text (str): The speech content
        filename (str): The filename to save to (default: presentation_speech.md)
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(speech_text)
    print(f"TTS-ready speech script saved to {filename}")

# Enrich the entire outline in one step
def oneStepEnrich(outline: str) -> str:
    return experimentalGpt.gpt_summarise(system=oneStepEnrichmentPrompt(), text=outline)

# Enrich content slide by slide
def perSlideEnrich(topic: str, outline: str) -> dict:
    outline = json.loads(outline)
    for i, slide in enumerate(outline['slides']):
        # Temporarily remove visuals to reduce confusion in the prompt
        visual = slide.pop('visuals', None)

        enrichedSlide = experimentalGpt.gpt_summarise(system=perSlideEnrichmentPrompt(), text=f"topic: {topic}\n\n" + json.dumps(slide))
        print(enrichedSlide)
        enrichedSlide = json.loads(enrichedSlide)
        if visual:
            enrichedSlide['visuals'] = visual
        outline['slides'][i] = enrichedSlide
    return outline

def process(topic: str):
    # Generate initial outline
    outlineText = experimentalGpt.gpt_summarise(system=initialOutlinePrompt(), text=topic)
    print("Initial outline generated.")
    
    # Enrich content slide by slide
    enrichedOutline = perSlideEnrich(topic, outlineText)
    print("Outline enriched slide by slide.")
    
    # Convert enriched outline to TTS-ready speech script
    speech_text = outline_to_speech(enrichedOutline)
    print("TTS-ready speech script generated.")
    
    # Save speech script to file
    save_speech_to_file(speech_text)
    
    # Return the enriched outline and generated speech script
    return {
        "enriched_outline": enrichedOutline,
        "speech_text": speech_text
    }

if __name__ == "__main__":
    import json

    # 读取 JSON 文件
    with open("./outline.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 假设 outline_to_speech 需要传入 JSON 数据
    speech_text = outline_to_speech(json_data)
    save_speech_to_file(speech_text)
    print("TTS-ready speech script generated.")