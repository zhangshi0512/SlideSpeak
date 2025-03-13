from pptx import Presentation
from pptx.slide import Slide
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
import win32com.client
import os
import re


### Helper method to preview the slide layouts available in a PowerPoint presentation
def previewSlideLayout():
    prs = Presentation()
    for i, layout in enumerate(prs.slide_layouts):
        print(f"Layout {i}:")
        for shape in layout.placeholders:
            print(f"  - Placeholder {shape.placeholder_format.idx}: {shape.name}")
        print("-" * 30)


def dictToPpt(inputDict: dict, speech_text=None):
    prs = Presentation() 

    # Add title slide
    addTitlePage(prs, inputDict["title"])

    # Process speech text into sections for speaker notes
    speech_sections = {}
    if speech_text:
        speech_sections = processSpecchIntoSections(speech_text, inputDict)

    # Add content slides
    for i, slide in enumerate(inputDict["slides"]):
        # Get the corresponding speech section for this slide if available
        slide_notes = speech_sections.get(slide["title"], "")
        addContentSlide(prs, slide, slide_notes)

    prs.save('PPT.pptx')

    print("Generation finished")

    # Uncomment if you want to use the shrinking functionality
    # shrinkTextInPowerpoint('PPT.pptx')


def processSpecchIntoSections(speech_text: str, inputDict: dict) -> dict:
    """
    Process the speech text and map sections to slide titles
    using explicit [SLIDE CHANGE] markers
    
    Args:
        speech_text: The entire speech text with [SLIDE CHANGE] markers
        inputDict: The presentation dictionary with slides
        
    Returns:
        A dictionary mapping slide titles to their corresponding speech sections
    """
    speech_sections = {}
    
    # Get all slide titles
    slide_titles = [slide["title"] for slide in inputDict["slides"]]
    
    # Split the speech by [SLIDE CHANGE] markers
    sections = speech_text.split("[SLIDE CHANGE]")
    
    # The first section is always for the first slide (introduction)
    if sections and slide_titles:
        speech_sections[slide_titles[0]] = sections[0].strip()
    
    # Map remaining sections to slides
    for i in range(1, min(len(sections), len(slide_titles))):
        speech_sections[slide_titles[i]] = sections[i].strip()
    
    # If we have more slides than sections, add empty notes for remaining slides
    for i in range(len(sections), len(slide_titles)):
        speech_sections[slide_titles[i]] = ""
    
    return speech_sections


### Helper method to add a title slide to the presentation, aka the first slide
### Take in the presentation object and the title: str of the presentation
def addTitlePage(prs: Presentation, title: str):
    # Presentation.slide_layouts[0] has the following layout (by default):
    #   - Placeholder 0: Title 1
    #   - Placeholder 1: Subtitle 2
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = title.strip()
    slide.placeholders[1].text = "Subtitle Placeholder"
    setTitlePageStyle(slide)

## Helper method to set the style for the title slide, aka the first slide
def setTitlePageStyle(slide: Slide):
    if slide.shapes.title:
        title_shape = slide.shapes.title
        font = title_shape.text_frame.paragraphs[0].font
        font.size = Pt(44)
        font.bold = True


# Helper method, Add content of slide object inside slides from the inputDictp
# The input slideDict should shape like this:
# {
#   "title": str,
#   "content":[
#      {
#        "bulletPoint": str,
#        "details": [str, str, ...]
#      }, ... 
#   ]
# } 
def addContentSlide(prs: Presentation, slideDict: dict, speaker_notes=""):
    # Presentation.slide_layouts[0] has the following layout (by default):
    #   - Placeholder 0: Title 1
    #   - Placeholder 1: Content Placeholder 2
    #   - Placeholder 10: Date Placeholder 3
    #   - Placeholder 11: Footer Placeholder 4
    #   - Placeholder 12: Slide Number Placeholder 5
    
    # Create the first slide for this topic
    currentSlide = addLayout1(prs, slideDict["title"])
    contentTextFrame = currentSlide.placeholders[1].text_frame
    wordCount = 0
    
    # First, add speaker notes to the first slide
    if speaker_notes and hasattr(currentSlide, 'notes_slide'):
        notes_slide = currentSlide.notes_slide
        notes_textframe = notes_slide.notes_text_frame
        
        # Clean up the notes by removing special markers for TTS
        clean_notes = re.sub(r'\[PAUSE=\d+\]', '', speaker_notes)
        clean_notes = re.sub(r'\[SLIDE CHANGE\]', '', clean_notes)
        
        notes_textframe.text = clean_notes.strip()
    
    # Then add content, potentially creating additional slides if needed
    for content in slideDict["content"]:
        newContentWordCount = len(content["bulletPoint"].split()) + sum([len(detail.split()) for detail in content["details"]])
        
        # If content is too large, create a new slide
        if wordCount != 0 and wordCount + newContentWordCount > 120:
            currentSlide = addLayout1(prs, slideDict["title"])
            contentTextFrame = currentSlide.placeholders[1].text_frame
            wordCount = 0
            
            # No speaker notes for additional slides with the same title
        
        p = contentTextFrame.add_paragraph()
        p.text = content["bulletPoint"]
        p.level = 0
        p.font.size = Pt(22)

        for detail in content["details"]:
            p = contentTextFrame.add_paragraph()
            detail = detail.strip()[2:] if detail.strip().startswith("- ") else detail.strip()
            p.text = detail
            p.level = 1
            p.font.size = Pt(18)

        wordCount += newContentWordCount


def addLayout1(prs: Presentation, title: str) -> Slide:
    """ Add a slide with layout 1 (title and content) to the presentation. """
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = title.strip()
    slide.shapes.title.text_frame.paragraphs[0].font.bold = True
    slide.shapes.title.text_frame.paragraphs[0].font.size = Pt(40)
    slide.shapes.title.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT

    contentTextFrame = slide.placeholders[1].text_frame
    contentTextFrame.clear()
    contentTextFrame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    contentTextFrame.fit_text()
    # Remove the default empty paragraph
    if len(contentTextFrame.paragraphs) > 0:
        contentTextFrame.paragraphs[0]._element.getparent().remove(contentTextFrame.paragraphs[0]._element)

    return slide


def shrinkTextInPowerpoint(file_path: str) -> None:
    try:
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        powerpoint.Visible = True

        presentation = powerpoint.Presentations.Open(os.path.abspath(file_path))

        for slide in presentation.Slides:
            for shape in slide.Shapes:
                if shape.HasTextFrame:
                    text_frame = shape.TextFrame
                    text_range = text_frame.TextRange
                    print(f"Found text frame with text : {text_range.Text}")

                    shrinkHappened = shrinkText(text_frame)
                    if shrinkHappened:
                        adjustFirstLineFontSize(text_frame)
        
        presentation.Save()
        presentation.Close()
        powerpoint.Quit()
    except Exception as e:
        print(f"Error: {e}")

def shrinkText(textFrame) -> bool:
    textRange = textFrame.TextRange
    shrunk = False
    while textRange.BoundHeight > textFrame.Parent.Height and textRange.Font.Size > 10:
        textRange.Font.Size -= 1
        shrunk = True
        print(f"Shrunk text to {textRange.Font.Size}")
    return shrunk

def adjustFirstLineFontSize(textFrame) -> None:
    textRange = textFrame.TextRange
    textContent = textRange.Text.strip()
    lines = textContent.split("\n")

    if lines:
        firstLine = lines[0]
        restText = "\n".join(lines[1:])
        textRange.Text = firstLine + "\n" + restText
        textRange.Words(1, len(firstLine)).Font.Size += 2

if __name__ == "__main__":
    import json
    # This is a test to demonstrate speaker notes functionality
    with open("./output/enriched_outline.json", "r", encoding="utf-8") as file:
        test_dict = json.load(file)
    
    with open("./output/presentation_speech.md", "r", encoding="utf-8") as file:
        test_speech = file.read()
    
    dictToPpt(test_dict, test_speech)