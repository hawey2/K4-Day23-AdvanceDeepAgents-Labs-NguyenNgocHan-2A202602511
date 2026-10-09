# Survey about Efficient Inference and Small Language Models

## TL;DR
This survey explores efficient inference techniques and the design of small language models (SLMs) optimized for resource-constrained environments. It covers pruning, quantization, distillation, and architectural optimizations for efficient inference. Small models focus on efficient deployment through dynamic query routing, modular backbones, and safety alignment, particularly excelling in agentic workloads. Challenges include balancing latency, accuracy, vocabulary size, and hardware constraints. The survey outlines current trends and open problems related to integrating multiple efficiency techniques, hardware-aware design, and trustworthy deployment.

## Background
Language models have grown immensely in size and capability, posing challenges in deployment, especially for latency-sensitive and resource-constrained applications. Efficient inference techniques help mitigate the computational and memory costs of these models. Small language models offer competitive performance with advantages in cost, latency, energy efficiency, and deployment flexibility, particularly on edge devices. This survey examines methods, design principles, and challenges encountered in this growing area.

## Methods and Techniques for Efficient Inference
Efficient inference in language models employs multiple methods aimed at reducing computational resources while maintaining performance. Pruning reduces parameters or network connections to shrink model size. Quantization lowers numerical precision of weights and activations, trading some accuracy for faster computation and memory savings. Knowledge distillation transfers learned knowledge from larger teachers to smaller student models, preserving capabilities amidst compression. Architecture search and optimizations identify subnetworks that balance efficiency and accuracy.

Notable approaches combine these techniques, such as Fast DistilBERT, which integrates hardware-aware pruning, distillation, quantization, and custom runtime engines to enhance CPU throughput [1]. Training-free architecture search frameworks optimize subnets for inference speed and memory, preserving model fidelity [2]. Contemporary model compression surveys highlight the systematic use of compression and system-level optimization [3]. Integrated refinement frameworks use quantization combined with adaptation and data distillation to compress models for downstream tasks [4]. Leveraging abstract concepts from large models can improve small model performance dynamically [5].

## Design and Capabilities of Small Language Models
Small language models are increasingly designed for efficient inference and specialized agentic tasks. Techniques include dynamic query routing that switches between local small models and full cloud models based on input uncertainty and safety checks, optimizing latency under resource constraints [6]. Safety alignment strategies activate reasoning modules only for adversarial inputs, thereby reducing overhead [7].

Architectural advances include smaller backbone networks combined with modular components such as vision modules to enable multimodal capabilities at reduced cost [8]. Small LMs have shown strong performance in agentic workloads requiring tool use, function calls, and retrieval-augmented generation, providing better latency, cost-effectiveness, and energy use relative to large counterparts [9]. Additionally, some small generative AI models show competitive understanding of specific applications like malware detection, offering efficient deployment possibilities [10].

## Challenges, Trade-offs, and Limitations
Balancing various factors is central to challenges in efficient inference and small language model design. Optimizing architecture affects inference latency and memory use considerably, with vocabulary size especially impacting memory and runtime efficiency [11][12]. Quantization can effectively reduce decode latency but risks precision degradation, notably with longer input contexts [11][12].

Trade-offs include latency versus accuracy and memory footprint versus vocabulary size. Fine-tuning large models to meet domain needs remains costly and not always suitable for small-model deployment [13][14]. Privacy concerns drive the use of local models but are constrained by computational limits. Hardware heterogeneity necessitates hardware-software co-design approaches to achieve performance targets [11][13][15][14].

## Trends and Open Problems
An emerging trend is the composite usage of multiple efficient inference strategies, leveraging pruning, quantization, distillation, and architectural search synergistically. Hardware-aware optimizations and custom runtimes gain importance for latency and energy efficiency.

Future challenges include refining quantization to minimize precision loss, creating architectures balancing vocabulary size and context length, and advancing trustworthy and secure small model deployment. Innovations in hardware and software co-design remain critical to pushing small models closer to large model flexibility.

Open problems also involve enhancing adaptability with minimal fine-tuning costs and bridging performance gaps in complex tasks through architectural and training innovations.

## References
[1] Fast DistilBERT on CPUs. hf-search. https://huggingface.co/papers/2211.07715 (2022-10-27)
[2] Search for Efficient Large Language Models. hf-search. https://huggingface.co/papers/2409.17372 (2024-09-25)
[3] Contemporary Model Compression on Large Language Models Inference. hf-search. https://huggingface.co/papers/2409.01990 (2024-09-03)
[4] Advancing Model Refinement: Muon-Optimized Distillation and Quantization for LLM Deployment. hf-search. https://huggingface.co/papers/2601.09865 (2026-01-14)
[5] Can abstract concepts from LLM improve SLM performance?. hf-search. https://huggingface.co/papers/2512.19069 (2025-12-22)
[6] SWARM-LLM: Collaborative Inference for Edge-based Small Language Models. hf-search. https://huggingface.co/papers/2606.14711 (2026-04-22)
[7] EASE: Practical and Efficient Safety Alignment for Small Language Models. hf-search. https://huggingface.co/papers/2511.06512 (2025-11-09)
[8] TinyGPT-V: Efficient Multimodal Large Language Model via Small Backbones. hf-search. https://huggingface.co/papers/2312.16862 (2023-12-28)
[9] Small Language Models for Agentic Systems: A Survey of Architectures, Capabilities, and Deployment Trade offs. hf-search. https://huggingface.co/papers/2510.03847 (2025-10-04)
[10] Can Small GenAI Language Models Rival Large Language Models in Understanding Application Behavior?. hf-search. https://huggingface.co/papers/2511.12576 (2025-11-16)
[11] Demystifying Small Language Models for Edge Deployment. hf-daily. https://aclanthology.org/anthology-files/anthology-files/pdf/acl/2025.acl-long.718.pdf (N.d.)
[12] Small Language Models: Survey, Measurements, and Insights. hf-daily. https://arxiv.org/abs/2409.15790 (2025-02-26)
[13] A Comprehensive Survey of Small Language Models in the Era of Large Language Models. hf-daily. https://dl.acm.org/doi/10.1145/3768165 (2025-11-24)
[14] Challenges, Trade-offs, and Limitations of Efficient Inference and Small LMs (Web page). web. https://aclanthology.org/2025.smalllm.survey.pdf (N.d.)
[15] A Survey on Small Language Models in the Era of Large Language Models. hf-daily. https://dl.acm.org/doi/10.1145/3711896.3736563 (2025-08-03)
