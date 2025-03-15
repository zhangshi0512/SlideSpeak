import gpt 
import pdf2final_list
import json
import speech_generator

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


def perSlideEnrich(topic: str, outline: str) -> dict:
    outline = json.loads(outline)
    for i, slide in enumerate(outline['slides']):
        # Temporarily remove visuals to reduce confusion in the prompt
        visual = slide.pop('visuals', None)

        enrichedSlide = gpt.gpt_summarise(
            system=textEnrichmentPrompt(), 
            text=f"topic: {topic}\n\n" + json.dumps(slide)
        ).replace("```json", "").replace("```", "")
        print(enrichedSlide)
        
        try: 
            enrichedSlide = json.loads(enrichedSlide)
        except json.JSONDecodeError:
            print(f"Warning: Slide {i} could not be enriched. Skipping.")
            enrichedSlide = {
                "title": slide['title'], 
                "content": [{"bulletPoint": content, "shortSubPoints": [], "details": []} for content in slide.get('content', [])]
            }
        if visual:
            enrichedSlide['visuals'] = visual 
        outline['slides'][i] = enrichedSlide
    return outline

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


def generateSlideSpeech(enriched_outline):
    for i, slide in enumerate(enriched_outline['slides']):
        simplified_content = []
        for item in slide['content']:
            details = item.get('details', [])
            details_text = ""
            if details:
                details_text = " ".join([d[:200] for d in details])
            simplified_content.append(f"{item['bulletPoint']} - {details_text}")

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
        print(enriched_outline['slides'][i])
    return enriched_outline
        

if __name__ == "__main__":
    topic = "Edge AI vs. Cloud AI: The Battle for the Future of Computing"
    # # ### Generate initial outline
    outlineText = gpt.gpt_summarise(system=pdf2final_list.initialOutlinePrompt(), text=topic)
    print(outlineText)
    print("Initial outline generated.")

    enrichedOutline = perSlideEnrich(topic, outlineText)
    print("Outline enriched slide by slide.")
        
    # print("*" * 30)
    # print(enrichedOutline)

    # example saved output 
    # enrichedOutline = {'title': 'Edge AI vs. Cloud AI: The Battle for the Future of Computing', 'slides': [{'title': 'Introduction to Edge and Cloud AI', 'content': [{'bulletPoint': 'Definition of Edge AI - processing data locally on device or near the source.', 'shortSubPoints': ['Local computation', 'Near-source processing'], 'details': ['Edge AI processes data directly on devices such as smartphones, IoT sensors, and wearables without relying on remote servers.', 'This approach reduces latency by minimizing data transfer time to and from cloud services.', 'Examples include real-time monitoring in healthcare (e.g., smartwatches) or industrial automation (e.g., factory floor sensors).']}, {'bulletPoint': 'Definition of Cloud AI - leveraging remote servers for computation, storage, and analytics.', 'shortSubPoints': ['Remote processing', 'Scalability'], 'details': ['Cloud AI involves sending data to remote server clusters for processing, which provides high computational power and flexibility.', 'This model supports complex analytics that require significant resources, such as machine learning models with large datasets.', 'Examples include big data analysis in financial services or predictive maintenance in manufacturing.']}, {'bulletPoint': 'Key benefits and use cases of both approaches.', 'shortSubPoints': ['Reduced latency', 'Scalability', 'Resource allocation'], 'details': ['Edge AI reduces latency, ensuring faster response times critical for applications like autonomous vehicles or real-time gaming.', 'Cloud AI offers scalability, allowing businesses to handle increased data processing demands without adding physical infrastructure.', 'Resource allocation in Edge AI is more efficient as devices can manage their own computing needs, reducing energy consumption and network bandwidth usage.']}]}, {'title': 'Advantages of Edge AI', 'content': [{'bulletPoint': 'Low latency: Immediate responses without waiting for cloud processing.', 'shortSubPoints': ['Faster decision-making', 'Real-time application support'], 'details': ['Edge AI processes data closer to the source, reducing the time between receiving a command and executing it. This is crucial for applications like autonomous vehicles, where delay could be life-threatening.', 'For example, in healthcare, edge AI can enable real-time analysis of patient data by medical devices, leading to immediate diagnosis and treatment.']}, {'bulletPoint': 'Reduced data transmission: Lower bandwidth usage by handling tasks locally.', 'shortSubPoints': ['Conserves network resources', 'Supports remote areas with limited connectivity'], 'details': ['By processing data at the edge, devices generate less data that needs to be sent over a network. This is particularly beneficial for IoT devices and smart cities where large volumes of data are generated.', 'In regions with poor internet infrastructure or high network congestion, edge AI can ensure smooth operation without relying on cloud services.']}, {'bulletPoint': 'Enhanced privacy: Sensitive data is processed on the device, minimizing risk of exposure.', 'shortSubPoints': ['Protects user privacy', 'Compliance with regulations'], 'details': ['Edge AI ensures that personal and sensitive data remains on the local device, reducing the likelihood of data breaches or unauthorized access.', 'This is especially important for industries like finance and healthcare, where strict regulatory compliance is required.']}]}, {'title': 'Advantages of Cloud AI', 'content': [{'bulletPoint': 'Scalability and flexibility: Resources can be easily adjusted based on demand.', 'shortSubPoints': ['Flexible resource allocation', 'Elastic scaling for varying workloads'], 'details': ['In cloud AI, users can quickly scale up or down computing resources as needed, ensuring optimal performance without underutilizing or over-provisioning hardware.', 'For instance, during peak traffic periods in a chatbot service, additional computational power can be seamlessly added to handle increased load.', 'This flexibility allows companies to focus on their core business rather than managing physical infrastructure.']}, {'bulletPoint': 'High computational power: Access to powerful servers for complex tasks.', 'shortSubPoints': ['Powerful server infrastructure', 'Handling of complex computations'], 'details': ['Cloud AI provides access to some of the most advanced and powerful computing resources available, which are essential for running sophisticated machine learning models or large-scale data processing tasks.', 'Examples include deep learning frameworks like TensorFlow and PyTorch being run on high-end GPU clusters in the cloud.', 'The ability to use these powerful servers allows developers and researchers to achieve breakthroughs that might be impractical with local hardware.']}, {'bulletPoint': 'Cost-effectiveness: Pay-as-you-go pricing models.', 'shortSubPoints': ['Pay-per-use model', 'No fixed investment in hardware'], 'details': ['Cloud AI services typically operate on a pay-as-you-go basis, where users only pay for the resources they consume, eliminating the need for significant upfront capital investments in servers and other infrastructure.', 'This cost structure is particularly advantageous for startups or projects with fluctuating resource needs, as it reduces financial risk and allows for greater innovation without large initial outlays.', 'Additionally, cloud providers often offer discounted rates for long-term contracts, making it an economically viable option even for larger scale deployments.']}]}, {'title': 'Use Cases and Applications', 'content': [{'bulletPoint': 'Edge AI - Autonomous vehicles, smart homes, wearable technology, IoT devices.', 'shortSubPoints': ['Autonomous vehicles for real-time decision-making', 'Smart homes for efficient resource management', 'Wearable tech for personalized health monitoring', 'IoT devices for enhanced connectivity and response speed'], 'details': ['Autonomous vehicles rely on edge AI for real-time processing of sensor data, enabling safe driving in various conditions.', 'In smart homes, edge AI optimizes energy consumption by analyzing local data from sensors without sending it to the cloud.', 'Wearable technology benefits from edge AI through personalized health insights and continuous monitoring, reducing data transmission needs.', 'IoT devices use edge AI for rapid response times and low latency in industrial settings, enhancing operational efficiency.']}, {'bulletPoint': 'Cloud AI - Data analysis, machine learning model training, large-scale data processing.', 'shortSubPoints': ['Big data analytics for business intelligence', 'Machine learning model development and tuning', 'Scalable data processing for cloud-based services'], 'details': ['Cloud AI enables big data analytics by leveraging powerful computing resources to process extensive datasets, providing valuable insights for businesses.', 'For machine learning, the cloud offers vast computational power needed for training complex models on large datasets, ensuring high accuracy and performance.', 'Large-scale data processing in the cloud supports scalable services that can handle millions of users or petabytes of data without compromising performance.']}]}, {'title': 'Challenges of Edge AI', 'content': [{'bulletPoint': 'Limited computational power and storage capacity compared to cloud solutions.', 'shortSubPoints': ['Computers at the edge often have limited processing capabilities', 'Smaller form factors limit storage space'], 'details': ['Edge devices like smartphones and IoT sensors typically come with less powerful CPUs and smaller RAM capacities, making them unsuitable for complex computational tasks.', 'For instance, a typical smartphone has an A-series or Snapdragon processor, which is significantly less powerful than the servers used in cloud computing environments.']}, {'bulletPoint': 'Security concerns: Local device can be vulnerable if not properly secured.', 'shortSubPoints': ['Local data breaches are more likely', 'Malware risks on edge devices'], 'details': ['Edge devices can store sensitive user information, and a security breach at the edge could expose this data to cyber threats.', 'The limited processing power of these devices makes it harder for them to run sophisticated security checks like those found in cloud environments.', 'Malware targeting IoT devices is on the rise, with edge devices being particularly vulnerable due to their wide distribution and often outdated software.']}]}, {'title': 'Challenges of Cloud AI', 'content': [{'bulletPoint': 'Latency issues: Data transmission delays can affect real-time applications.', 'shortSubPoints': ['Data travel time to cloud servers adds latency', 'Real-time responsiveness compromised'], 'details': ['In scenarios requiring immediate processing, such as autonomous driving or surgical robots, even a few milliseconds of delay can be critical.', 'Latency is exacerbated by long distances between the user and the server, especially in remote locations.']}, {'bulletPoint': 'High dependency on network connectivity: Poor internet connection can disrupt services.', 'shortSubPoints': ['Internet reliability crucial for cloud AI operations', 'Service availability depends on network conditions'], 'details': ['Cloud AI applications require a stable and fast Internet connection to function correctly, making them susceptible to outages during network failures.', 'Users in areas with unreliable or slow internet might experience frequent disruptions or service interruptions.']}]}, {'title': 'Hybrid Approach - Combining Edge and Cloud AI', 'content': [{'bulletPoint': 'Overview of hybrid solutions that leverage both edge and cloud capabilities.', 'shortSubPoints': ['Balancing local processing with remote computing', 'Efficient use of resources by combining both methods'], 'details': ['Hybrid AI approaches integrate the strengths of Edge AI and Cloud AI to optimize performance, reduce latency, and minimize bandwidth usage. For example, in autonomous vehicles, real-time decision-making can be handled locally at the edge (Edge AI) while complex data analysis is offloaded to a cloud server for more computing power.', 'This approach allows for a flexible deployment model that can adapt based on the specific requirements of the application, such as mission-critical operations where latency cannot be tolerated or scenarios requiring extensive data processing.']}, {'bulletPoint': 'Benefits of a balanced approach: Optimizing between local processing and remote computing.', 'shortSubPoints': ['Enhanced performance through optimized resource allocation', 'Reduced latency by reducing dependency on cloud connectivity'], 'details': ['By leveraging the strengths of both edge and cloud, hybrid solutions can significantly enhance overall system performance. For instance, Edge AI provides quick response times for real-time data processing while Cloud AI offers scalable resources for handling large-scale computations.', 'Reducing latency is crucial in applications like smart cities or healthcare where timely decisions are essential. For example, emergency medical equipment could process critical patient data locally and instantly send summaries to the cloud for further analysis by specialists, ensuring immediate action can be taken.']}]}, {'title': 'Future Trends in AI Computing', 'content': [{'bulletPoint': 'Integration with 5G networks - Enhancing real-time communication and speed.', 'shortSubPoints': ['Faster data transfer rates', 'Reduced latency'], 'details': ['5G technology significantly reduces the time it takes for devices to communicate, enabling faster AI processing. For instance, a typical 5G network can provide speeds up to 20 Gbps, compared to 1-2 Gbps with 4G. This improvement is crucial for real-time applications like autonomous vehicles and remote surgeries.', 'Enhanced speed in 5G networks leads to quicker data analysis and response times, which are vital in AI systems requiring immediate decision-making capabilities.']}, {'bulletPoint': 'Advancements in quantum computing - Potential breakthroughs in computational efficiency.', 'shortSubPoints': ['Increased processing power', 'Solving complex problems faster'], 'details': ['Quantum computers can process information using qubits, which can exist in multiple states simultaneously. This allows them to solve certain types of problems much faster than classical computers, such as simulating chemical reactions or optimizing large-scale systems.', 'Potential applications include drug discovery, financial modeling, and complex system simulations where current computing power is insufficient.']}, {'bulletPoint': 'Ethical considerations and regulatory frameworks.', 'shortSubPoints': ['Bias detection', 'Privacy concerns'], 'details': ['As AI systems become more prevalent, ensuring they are free from bias is critical. This involves using diverse training data and regular audits to identify and mitigate biases in algorithms.', 'Regulatory bodies like the European Union’s General Data Protection Regulation (GDPR) and California Consumer Privacy Act (CCPA) enforce strict rules on how companies handle personal data, emphasizing the need for robust privacy protections in AI systems.']}]}, {'title': 'Conclusion', 'content': [{'bulletPoint': 'Summary of key points: Edge, cloud, and hybrid approaches each have unique advantages and limitations.', 'shortSubPoints': ['Edge computing processes data locally for faster response times and reduced latency.', 'Cloud computing offers scalability, storage, and advanced processing power with centralized management.', 'Hybrid solutions combine the benefits of both by leveraging local resources while still connecting to cloud services.'], 'details': ['Edge computing is ideal for real-time applications like autonomous vehicles or industrial IoT where latency can impact performance critically.', 'Cloud AI excels in scenarios requiring massive data storage and processing, such as deep learning models training on large datasets.', 'Hybrid approaches allow businesses to balance between local and remote computing resources, optimizing costs and performance.']}, {'bulletPoint': 'The future likely involves a mix of strategies to leverage the strengths of both methods.', 'shortSubPoints': ['Integration of edge and cloud for optimal resource utilization', 'Dynamic workload distribution'], 'details': ['As technology advances, we will see more seamless integration between edge and cloud computing. This includes real-time data processing at the edge with periodic updates to models stored in the cloud.', 'Future systems may dynamically distribute workloads based on current network conditions, compute requirements, or user preferences, ensuring efficiency and responsiveness.']}]}]}
    
    enrichedOutline = generateIntroSpeech(enrichedOutline)
    enrichedOutline = generateSlideSpeech(enrichedOutline)