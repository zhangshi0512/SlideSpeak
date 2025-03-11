"""
Speech generator module for converting presentation outlines to TTS-ready speech scripts.
This module handles the conversion of presentation outlines to speech scripts optimized
for text-to-speech (TTS) systems.
"""

import json
import re
from typing import Dict, List, Union, Any

# Import the GPT module for text generation
from gpt import gpt_summarise


def generate_speech_introduction_prompt() -> str:
    """
    Returns the system prompt for generating speech introductions.
    """
    return """
    You are creating the introduction for a TTS-friendly speech.
    
    Generate an introduction that:
    1. Starts with "Hello everyone. Today, I will be presenting about [TITLE]."
    2. Briefly mentions the main sections you'll cover
    3. Sets the tone for the presentation
    4. Uses simple language suitable for text-to-speech systems
    5. Includes [PAUSE=1] markers for 1-second pauses at natural breaking points
    
    The introduction should be concise (3-5 sentences) and engaging.
    """


def generate_speech_section_prompt() -> str:
    """
    Returns the system prompt for generating speech sections.
    """
    return """
    You are creating a section of a TTS-friendly speech.
    
    Convert the slide content into natural, conversational speech that:
    1. Starts with "Let's discuss [SLIDE TITLE]."
    2. Explains the key points in a flowing, narrative style (not bullet points)
    3. Uses simple sentence structures for text-to-speech systems
    4. Includes [PAUSE=1] markers at natural breaking points
    
    The speech should sound natural when read aloud by a TTS system.
    """


def generate_speech_conclusion_prompt() -> str:
    """
    Returns the system prompt for generating speech conclusions.
    """
    return """
    You are creating the conclusion for a TTS-friendly speech.
    
    Generate a conclusion that:
    1. Summarizes the key points from the presentation
    2. Provides a closing thought or call to action
    3. Ends with exactly: "Thank you for your attention. [PAUSE=1] If you have any questions, I'd be happy to address them now."
    4. Uses simple language suitable for text-to-speech systems
    5. Includes [PAUSE=1] markers at natural breaking points
    
    The conclusion should be concise (3-5 sentences) and provide closure to the presentation.
    """


def outline_to_speech_chunked(enriched_outline: Dict[str, Any]) -> str:
    """
    Generate speech by processing the outline in chunks with state management.
    
    Args:
        enriched_outline (dict): The enriched presentation outline
        
    Returns:
        str: A formatted speech script optimized for TTS systems
    """
    # Extract title and basic information
    title = enriched_outline["title"]
    slide_titles = [slide["title"] for slide in enriched_outline["slides"]]
    
    # Step 1: Generate introduction with overall structure
    intro_prompt = f"""
    Title: {title}
    Main sections: {', '.join(slide_titles)}
    
    Create an introduction for this presentation that starts with "Hello everyone. Today, I will be presenting about {title}." Mention that you'll cover these main sections.
    """
    
    introduction = gpt_summarise(
        system=generate_speech_introduction_prompt(),
        text=intro_prompt
    )
    
    # Step 2: Process each slide individually
    sections = []
    for i, slide in enumerate(enriched_outline["slides"]):
        # Create a simplified version of the slide with only essential content
        simplified_content = []
        for item in slide["content"]:
            # For enriched slides with bulletPoint/details structure
            if isinstance(item, dict) and "bulletPoint" in item:
                # Include only first 1-2 details for each point to keep it manageable
                details = item.get("details", [])
                details_text = ""
                if details:
                    # Limit to first 2 details and max 200 chars each
                    details_text = " ".join([d[:200] for d in details[:2]])
                
                simplified_content.append(f"{item['bulletPoint']} - {details_text}")
            else:
                # For simple bullet point lists
                simplified_content.append(str(item)[:200])
        
        # Create a prompt for this specific slide
        slide_prompt = f"""
        Slide Title: {slide['title']}
        
        Key Points:
        - {" ".join(simplified_content[:5])}
        
        Convert this into a section of a speech with natural language. Use about 3-5 sentences. Do not start with Let's discuss, In natural language, it is indicated that there should be a beginning that carries over to the next.
        """
        
        # Generate the section text
        section_text = gpt_summarise(
            system=generate_speech_section_prompt(),
            text=slide_prompt
        )
        
        # Add transition except for the last slide
        if i < len(enriched_outline["slides"]) - 1:
            next_slide = enriched_outline["slides"][i+1]["title"]
            section_text += f" [PAUSE=1] Moving on to our next topic: {next_slide}. [SLIDE CHANGE]"
        
        sections.append(section_text)
    
    # Step 3: Generate conclusion
    conclusion_prompt = f"""
    Title: {title}
    Main sections covered: {', '.join(slide_titles)}
    
    Create a brief conclusion that summarizes these key points.
    """
    
    conclusion = gpt_summarise(
        system=generate_speech_conclusion_prompt(),
        text=conclusion_prompt
    )
    
    # Combine all parts
    full_speech = introduction + "\n\n" + "\n\n".join(sections) + "\n\n" + conclusion
    
    return full_speech


def process_text_content_chunked(content_text: str, topic: str = "") -> str:
    """
    Process text content by identifying sections and processing them sequentially.
    
    Args:
        content_text (str): The presentation content text
        topic (str): Optional topic to provide context
        
    Returns:
        str: A formatted speech script optimized for TTS systems
    """
    # Try to extract a title if not provided
    if not topic:
        # Look for a title pattern like "### Title" or "Title\n---"
        title_match = re.search(r'#{1,6}\s+([^\n]+)|([^\n]+)\n[=\-]{3,}', content_text)
        if title_match:
            topic = next((g for g in title_match.groups() if g), "Presentation")
    
    # Find sections using common markdown patterns
    section_pattern = r'#{2,4}\s+([^\n]+)|\n([^\n]+)\n[=\-]{3,}'
    section_matches = re.finditer(section_pattern, content_text)
    
    sections = []
    last_pos = 0
    section_titles = []
    
    for match in section_matches:
        section_title = next((g for g in match.groups() if g), "")
        section_titles.append(section_title.strip())
        
        # If this isn't the first match, capture the content of the previous section
        if last_pos > 0:
            section_content = content_text[last_pos:match.start()].strip()
            sections.append({"title": section_titles[-2], "content": section_content})
        
        last_pos = match.end()
    
    # Add the last section
    if last_pos > 0 and section_titles:
        section_content = content_text[last_pos:].strip()
        sections.append({"title": section_titles[-1], "content": section_content})
    
    # If no sections were found, treat the entire content as one section
    if not sections:
        sections = [{"title": topic or "Main Content", "content": content_text}]
    
    # Step 1: Generate introduction
    intro_prompt = f"""
    Title: {topic}
    Main sections: {', '.join([s['title'] for s in sections])}
    
    Create an introduction for this presentation.
    """
    
    introduction = gpt_summarise(
        system=generate_speech_introduction_prompt(),
        text=intro_prompt
    )
    
    # Step 2: Process each section
    speech_sections = []
    for i, section in enumerate(sections):
        # Limit content length to avoid overwhelming the model
        content_preview = section['content'][:1000]
        
        section_prompt = f"""
        Section: {section['title']}
        
        Content preview:
        {content_preview}
        
        Convert this into a natural-sounding speech section of about 3-5 sentences.
        """
        
        section_text = gpt_summarise(
            system=generate_speech_section_prompt(),
            text=section_prompt
        )
        
        # Add transition except for the last section
        if i < len(sections) - 1:
            next_section = sections[i+1]["title"]
            section_text += f" [PAUSE=1] Moving on to our next topic: {next_section}. [SLIDE CHANGE]"
        
        speech_sections.append(section_text)
    
    # Step 3: Generate conclusion
    conclusion_prompt = f"""
    Title: {topic}
    Main sections covered: {', '.join([s['title'] for s in sections])}
    
    Create a brief conclusion.
    """
    
    conclusion = gpt_summarise(
        system=generate_speech_conclusion_prompt(),
        text=conclusion_prompt
    )
    
    # Combine all parts
    full_speech = introduction + "\n\n" + "\n\n".join(speech_sections) + "\n\n" + conclusion
    
    return full_speech


def outline_to_speech(content: Union[Dict[str, Any], str], use_chunking: bool = True) -> str:
    """
    Convert presentation content to a TTS-ready speech script.
    
    Args:
        content: Can be either a JSON outline or a presentation text
        use_chunking: Whether to use chunked processing (for smaller LLMs) or direct processing (for larger LLMs)
        
    Returns:
        str: A formatted speech script optimized for TTS systems
    """
    # For direct processing with larger LLMs
    if not use_chunking:
        # Convert content to string if it's a dictionary
        if isinstance(content, dict):
            content_str = json.dumps(content)
        else:
            content_str = str(content)
        
        # Use direct method (suitable for larger LLMs)
        direct_prompt = """
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
        
        speech_text = gpt_summarise(system=direct_prompt, text=content_str)
        return speech_text
    
    # For chunked processing with smaller LLMs
    else:
        # Determine the type of content and use appropriate processing
        if isinstance(content, dict):
            # Process JSON outline using chunked method
            return outline_to_speech_chunked(content)
        else:
            # Process text content using text chunking method
            content_str = str(content)
            return process_text_content_chunked(content_str)


def save_speech_to_file(speech_text: str, filename: str = "presentation_speech.md") -> None:
    """
    Save the generated TTS-ready speech script to a markdown file.
    
    Args:
        speech_text (str): The speech content
        filename (str): The filename to save to (default: presentation_speech.md)
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(speech_text)
    print(f"TTS-ready speech script saved to {filename}")


def process_existing_content(content_text: str, topic: str = "", use_chunking: bool = True) -> str:
    """
    Process existing presentation content and generate a TTS-ready speech script.
    
    Args:
        content_text (str): The presentation content text
        topic (str): Optional topic to provide context
        use_chunking (bool): Whether to use chunked processing (for smaller LLMs) or direct processing (for larger LLMs)
        
    Returns:
        str: TTS-ready speech script
    """
    # Add topic context if provided
    if topic:
        content_with_context = f"Topic: {topic}\n\n{content_text}"
    else:
        content_with_context = content_text
    
    # Process with selected method
    if use_chunking:
        speech_text = process_text_content_chunked(content_with_context)
        print("TTS-ready speech script generated from existing content using chunked processing.")
    else:
        # Use direct method for larger LLMs
        speech_text = outline_to_speech(content_with_context, use_chunking=False)
        print("TTS-ready speech script generated from existing content using direct processing.")
    
    # Save speech script to file
    save_speech_to_file(speech_text)
    
    return speech_text


if __name__ == "__main__":
    # Simple example usage
    demo_outline = {
        "title": "Introduction to Speech Generation",
        "slides": [
            {
                "title": "What is TTS?",
                "content": [
                    {"bulletPoint": "Definition of TTS", "details": ["Text-to-Speech converts written text to spoken words"]}
                ]
            },
            {
                "title": "Benefits of TTS",
                "content": [
                    {"bulletPoint": "Accessibility", "details": ["Helps visually impaired users"]}
                ]
            }
        ]
    }
    
    # Generate speech from the demo outline
    speech = outline_to_speech(demo_outline)
    save_speech_to_file(speech, "demo_speech.md")
    print("Demo speech generated and saved to demo_speech.md")