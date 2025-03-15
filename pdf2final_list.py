from typing import List
import sys, os, json
import gpt

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
sys.path.append(parent_dir)

import gpt
import speech_generator  # Import the new speech generator module

# Only to make the prompt more readable 
def initialOutlinePrompt() -> str: 
    return """I am giving you a topic. 
    
    Yout task is to generate a **structured PowerPoint outline** based on the topic.

    - Ensure the outline is **logically organized** with a clear flow of information.  
    - Each slide should focus on **one key idea** to maintain clarity.  
    - Use **concise yet informative** bullet points or short paragraphs for each slide. For each slide, words must not overflow.  
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

# need somehow make model align with the output format 
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
    - "content" can have less than 2 to 4 elements. If there are more than three elements make sure in that case "details" must have at most two elements
    - **each** string in "details" must be informative concise with less than 30 words, "details" should have less than 3 elements.

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

# Enrich the entire outline in one step
def oneStepEnrich(outline: str) -> str:
    return gpt.gpt_summarise(system=oneStepEnrichmentPrompt(), text=outline)

# Enrich content slide by slide
def perSlideEnrich(topic: str, outline: str) -> dict:
    outline = json.loads(outline)
    for i, slide in enumerate(outline['slides']):
        # Temporarily remove visuals to reduce confusion in the prompt
        visual = slide.pop('visuals', None)

        enrichedSlide = gpt.gpt_summarise(system=perSlideEnrichmentPrompt(), text=f"topic: {topic}\n\n" + json.dumps(slide))
        #print(enrichedSlide)
        enrichedSlide = json.loads(enrichedSlide)
        if visual:
            enrichedSlide['visuals'] = visual
        outline['slides'][i] = enrichedSlide
    return outline

def process(topic: str, use_chunking=True):
    # Generate initial outline
    outlineText = gpt.gpt_summarise(system=initialOutlinePrompt(), text=topic)
    with open("./output/testData.json", "w", encoding="utf-8") as file:
        formatted = json.loads(outlineText)
        json.dump(formatted, file, indent=4)
    print("Initial outline generated and saved.")
    
    # Enrich content slide by slide
    enrichedOutline = perSlideEnrich(topic, outlineText)
    with open("./output/detailed.json", "w") as file:
        json.dump(enrichedOutline, file, indent=4)
    print("Outline enriched slide by slide and saved.")
    
    # Convert enriched outline to TTS-ready speech script using the speech_generator module
    speech_text = speech_generator.outline_to_speech(enrichedOutline, use_chunking=use_chunking)
    print(f"TTS-ready speech script generated using {'chunked' if use_chunking else 'direct'} processing.")
    
    # Save speech script to file
    speech_generator.save_speech_to_file(speech_text)
    
    # Return the enriched outline and generated speech script
    return {
        "enriched_outline": enrichedOutline,
        "speech_text": speech_text
    }

if __name__ == "__main__":
    # Simple example of processing a topic
    topic = "Coca-Cola's use of Cloud Computing"
    print(f"Generating presentation and speech for topic: '{topic}'")
    
    # Default: Use chunked processing for smaller LLMs
    result = process(topic)
    
    # # Preview the result
    # print("\nSpeech preview (first 300 characters):")
    # print("-" * 50)
    # print(result["speech_text"][:300] + "..." if len(result["speech_text"]) > 300 else result["speech_text"])
    # print("-" * 50)
    
    # To use the direct processing method for larger LLMs, you would call:
    # result = process(topic, use_chunking=False)
