from typing import List

import sys, os, json
import experimentalGpt

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
sys.path.append(parent_dir)

import gpt



# only to make the prompt more readable 
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



# enrichh the entire outline, and generate the content of each slide with more content and details
# hard to output consistent JSON structure
def oneStepEnrich(outline: str) -> str:
    return experimentalGpt.gpt_summarise(system=oneStepEnrichmentPrompt(), text=outline)

# enrich the outline slide by slide, and generate the content of each slide with more content and details
def perSlideEnrich(topic: str, outline: str) -> dict:
    outline = json.loads(outline)
    for i, slide in enumerate(outline['slides']):
        # temporarily remove visuals for less confusing prompt
        visual = slide.pop('visuals', None)

        enrichedSlide = experimentalGpt.gpt_summarise(system=perSlideEnrichmentPrompt(), text=f"topic: {topic}\n\n" +json.dumps(slide))
        print(enrichedSlide)
        enrichedSlide = json.loads(enrichedSlide)
        if visual:
            enrichedSlide['visuals'] = visual
        outline['slides'][i] = enrichedSlide
    return outline





def process(topic: str):
    outlineText = experimentalGpt.gpt_summarise(system=initialOutlinePrompt(), text=topic)
    print(outlineText)
    
    # # # perSlideEnrich
    enrichedOutline = perSlideEnrich(topic, outlineText)
    print(enrichedOutline)
    

    # # oneStepEnrich
    # enrichedResultText = oneStepEnrich(outlineText)
    # print(enrichedResultText)
    # enrichedParsedResult = json.loads(enrichedResultText)


    return

    


process('The future of Artificial Intelligence with the introduction of quantum computing')