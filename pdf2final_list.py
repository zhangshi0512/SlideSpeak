import speech_generator  # Import the new speech generator module
import gpt
from typing import List
import sys
import os
import json

cur_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(cur_dir)
sys.path.append(parent_dir)


# Only to make the prompt more readable
def initialOutlinePrompt() -> str:
    return """I am giving you a topic. 
    
    Yout task is to generate a **structured PowerPoint outline** based on the topic.

    - Ensure the outline is **logically organized** with a clear flow of information.  
    - Each slide should focus on **one key idea** to maintain clarity.  
    - Use **concise yet informative** bullet points or short paragraphs for each slide.  
    - If relevant, suggest visuals that enhance understanding, but **avoid unnecessary visuals.**  
    - The total number of slides should be determined **dynamically**, based on the depth required for the topic.  
    
    Strictly format the response as JSON with the following structure:
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

    **Important:**  
    - Validate the output format before finalizing. 
    """


def textEnrichmentPrompt() -> str:
    return """
    You are an expert assistant that enhances PowerPoint slides by expanding on key points while keeping the content structured and concise.

    I am providing you with a topic, and a structured PowerPoint outline with multiple slides.

    Your task is to **enrich** the content of **each slide** in the provided outline where necessary by:
    - Expanding each bullet point with **more details, examples, or explanations** into the details list.
    - Breaking down complex ideas into **shorter sub-points** that can fit into a Powerpoint slide.
    - Keeping the response clear, structured, and presentation friendly

    Strictly format the response as JSON for **a list of slides**, where each element is in the following structure:
    [
        {
            "title": "<Slide Title>",
            "content": [
                {
                    "bulletPoint": "<Original Bullet Points>",
                    "shortSubPoints": [
                        "Condensed key idea for PowerPoint",
                        "Another brief sub-point",
                        "Further clarification if needed",
                        ...
                    ],
                    "details": [
                        "Detailed explanation or examples",
                        ...
                    ]
                }, 
                ...
            ]
        },
        ...
    ]

    **Important:**  
    - Validate the output format before finalizing.  
    - Do not change the original slide structure or reword titles.  
    - Maintain a structured and informative tone.
    - Ensure the summary remains slide-friendly (short and digestible).
    """

# Updated version of per slide enrichment from test.py


def perSlideEnrich(topic: str, outline: str) -> dict:
    try:
        outline = json.loads(outline.replace("```json", "").replace("```", ""))
    except json.JSONDecodeError:
        print("Error: Could not parse outline JSON. Using empty structure.")
        outline = {"title": "Presentation", "slides": []}

    # Prepare slides for bulk enrichment
    slides_for_enrichment = []
    for i, slide in enumerate(outline['slides']):
        visual = slide.pop('visuals', None)  # Remove visuals temporarily
        slides_for_enrichment.append(slide)

    try:
        enrichedSlidesJson = gpt.gpt_summarise(
            system=textEnrichmentPrompt(),
            text=f"topic: {topic}\n\nslides: {json.dumps(slides_for_enrichment)}"
        ).replace("```json", "").replace("```", "")

        try:
            enrichedSlides = json.loads(enrichedSlidesJson)
            for i, enrichedSlide in enumerate(enrichedSlides):
                # Restore visuals if they exist
                if 'visuals' in outline['slides'][i]:
                    enrichedSlide['visuals'] = outline['slides'][i]['visuals']
                outline['slides'][i] = enrichedSlide
        except json.JSONDecodeError:
            print(f"Warning: Could not parse enriched slides JSON. Skipping enrichment.")
    except Exception as e:
        print(f"Error enriching slides: {str(e)}")

    return outline

# Generate introduction speech for the presentation


def generateIntroSpeech(enriched_outline):
    title = enriched_outline['title']
    slide_titles = [slide['title'] for slide in enriched_outline['slides']]
    intro_prompt = f"""
    Title: {title}
    Main sections: {', '.join(slide_titles)}
    
    Create an introduction for this presentation that starts with "Hello everyone. Today, I will be presenting about {title}." Mention that you'll cover these main sections.
    """

    introduction = gpt.gpt_summarise(
        system=speech_generator.generate_speech_introduction_prompt(),
        text=intro_prompt
    )
    enriched_outline['introduction'] = introduction
    return enriched_outline

# Generate speech for each slide


def generateSlideSpeech(enriched_outline):
    for i, slide in enumerate(enriched_outline['slides']):
        simplified_content = []
        for item in slide['content']:
            details = item.get('details', [])
            details_text = ""
            if details:
                details_text = " ".join([d[:200] for d in details])
            # Get bulletPoint with fallback
            bullet_point_text = item.get('bulletPoint', '')
            simplified_content.append(
                f"{bullet_point_text} - {details_text}")

        slide_prompt = f"""
        Slide Title: {slide['title']}
        
        Key Points:
        - {" ".join(simplified_content[:5])}
        
        Convert this into a section of a speech with natural language. Use about 3-5 sentences. Do not start with Let's discuss, In natural language, it is indicated that there should be a beginning that carries over to the next.
        """
        section_text = gpt.gpt_summarise(
            system=speech_generator.generate_speech_section_prompt(),
            text=slide_prompt
        )
        enriched_outline['slides'][i]['speech'] = section_text

    return enriched_outline


def process(topic: str, use_chunking=True):
    # Generate initial outline
    outlineText = gpt.gpt_summarise(system=initialOutlinePrompt(), text=topic)
    print("Initial outline generated.")
    print(outlineText)

    # Enrich content slide by slide
    enrichedOutline = perSlideEnrich(topic, outlineText)
    print("Outline enriched in bulk.")  # Modified print statement

    # Add speech introduction to the enriched outline
    enrichedOutline = generateIntroSpeech(enrichedOutline)
    print("Introduction speech generated.")

    # Add speech for each slide
    enrichedOutline = generateSlideSpeech(enrichedOutline)
    print("Slide speech generated.")

    # Convert enriched outline to TTS-ready speech script
    speech_text = speech_generator.create_speech_from_enriched_outline(
        enrichedOutline)
    print("TTS-ready speech script generated.")

    # Save speech script to file
    speech_generator.save_speech_to_file(speech_text)

    # Return the enriched outline and generated speech script
    return {
        "enriched_outline": enrichedOutline,
        "speech_text": speech_text
    }


if __name__ == "__main__":
    # Simple example of processing a topic
    topic = "AI Acceleration on Edge Devices: A Deep Dive into NPUs, TPUs, and GPUs"
    print(f"Generating presentation and speech for topic: '{topic}'")

    # Default: Use chunked processing for smaller LLMs
    result = process(topic)
