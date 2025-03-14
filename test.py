import gpt 
import pdf2final_list
import json

exampleOutline = """{
    "title": "Edge AI vs. Cloud AI: The Battle for the Future of Computing",
    "slides": [
        {
            "title": "Introduction to Edge and Cloud AI",
            "content": [
                "Definition of Edge AI (processing data locally on devices) vs. Cloud AI (processing data in remote servers)",
                "Brief history and evolution of both technologies"
            ],
            "visuals": "Conceptual diagram showing the difference between edge and cloud computing"
        },
        {
            "title": "Advantages of Edge AI",
            "content": [
                "Lower latency, critical for real-time applications like autonomous vehicles or remote medical devices",
                "Enhanced privacy with data processing on-device (e.g., facial recognition)",
                "Reduced bandwidth usage and lower costs in scenarios where large volumes of data are generated locally"
            ]
        },
        {
            "title": "Advantages of Cloud AI",
            "content": [
                "Scalability and flexibility for handling varying workloads and computing needs",
                "Cost-effectiveness for businesses without the need to invest heavily in local hardware",
                "Access to advanced AI models and services that may not be available on edge devices"
            ]
        },
        {
            "title": "Trade-offs Between Edge and Cloud",
            "content": [
                "Balancing between privacy, security, and computational power",
                "Network dependency for cloud AI; potential issues with unreliable internet connections",
                "Complexity in managing hybrid systems that combine both edge and cloud computing"
            ]
        },
        {
            "title": "Applications of Edge AI and Cloud AI",
            "content": [
                "Edge AI: Autonomous vehicles, smart homes, wearables, industrial IoT (IIoT)",
                "Cloud AI: Large-scale data analytics, enterprise resource planning (ERP), machine learning model training"
            ]
        },
        {
            "title": "Future Trends in Edge and Cloud Computing",
            "content": [
                "Advancements in 5G networks enhancing edge computing capabilities",
                "Increased focus on fog computing as an intermediate layer between the cloud and device",
                "Integration of AI into both edge and cloud to optimize performance and decision-making"
            ]
        },
        {
            "title": "Conclusion: The Synergy Between Edge and Cloud",
            "content": [
                "Both technologies are complementary rather than competitive, with a growing trend towards hybrid approaches",
                "Future developments will likely see more seamless integration of edge and cloud computing to leverage their respective strengths"
            ]
        }
    ]
}
"""

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
                "summary": "<Concise version for PowerPoint>",
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
    }

    **Important:**  
    - Validate the output format before finalizing.  
    - Do not change the original slide structure or reword titles.  
    - Maintain a structured and informative tone.
    - Ensure the summary remains slide-friendly (short and digestible).
    """



if __name__ == "__main__":
    topic = "Edge AI vs. Cloud AI: The Battle for the Future of Computing"

    # ### Generate initial outline
    # outlineText = gpt.gpt_summarise(system=pdf2final_list.initialOutlinePrompt(), text=topic)
    # print(outlineText)
    # print("Initial outline generated.")

    # ### Enrich
    # outline = json.loads(outlineText)
    outline = json.loads(exampleOutline)
    print("Outline valid JSON")
    
    for i, slide in enumerate(outline['slides']):
        print(slide)
        visual = slide.pop('visuals', None)

        enrichedSlide = gpt.gpt_summarise(system=textEnrichmentPrompt(), text=f"topic: {topic}\n\n" + json.dumps(slide)).replace("```json", "").replace("```", "")
        print(enrichedSlide)

        enrichedSlide = json.loads(enrichedSlide)
        if visual:
            enrichedSlide['visuals'] = visual
        outline['slides'][i] = enrichedSlide
        
    # print("*" * 30)
    # print(outline)
