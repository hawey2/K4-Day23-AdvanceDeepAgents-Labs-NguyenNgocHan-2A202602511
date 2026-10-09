# Survey about World Models

## TL;DR

World models in AI are internal representations that serve to understand and predict the environment [1][2][3]. They compress sensory inputs into latent variables for efficient planning and simulate future states to guide decision-making [1][3][4]. Architectures span multiple modalities and leverage diverse learning paradigms [4][5]. Applications range from robotics and autonomous driving to scientific modeling and education [4][5]. Recent advances include transformer-based models, hierarchical representations, and LLM-augmented reasoning architectures [6][7][8][9][10]. Key challenges remain in long-term prediction stability, sim-to-real gaps, and evaluation consistency [2][4][7].

## Background
World models in AI are internal representations that serve to understand and predict the environment. They compress sensory inputs into latent variables for efficient planning and simulate future states to guide decision-making. Architectures span multiple modalities and leverage diverse learning paradigms. Applications range from robotics and autonomous driving to scientific modeling and education. Recent advances include transformer-based models, hierarchical representations, and LLM-augmented reasoning architectures. Key challenges remain in long-term prediction stability, sim-to-real gaps, and evaluation consistency.

## Background
World models emerged as computational constructs enabling agents to build internal representations of their environments to support understanding, planning, and decision-making. Unlike classifiers or generators, world models simulate environment dynamics such as physics and causality, operating on sensor-based inputs. They are formally framed within agent-environment interaction models emphasizing modalities, asynchronous data streams, and locality of agent observation.

## Definitions and Core Concepts
World models serve two primary functions: constructing internally consistent representations of the environment and predicting future states to guide action. They utilize latent variables to capture essential information, enabling efficient planning and foresight. These models are functionally categorized as renderers (for observation synthesis), simulators (for state transition prediction), and planners (for action selection).

They differ significantly from large language models (LLMs), which operate on text and lack embodied physical understanding. Modern world models employ architectures like the Joint Embedding Predictive Architecture (JEPA), which integrates encoders, predictors, critics, and regularizers to minimize prediction error in latent space. Theoretical considerations highlight the importance of omnimodality, multidimensional asynchronicity, and locality in modeling from the agent’s perspective.

## Main Architectures and Applications
Architectural variants cover multiple input modalities including visual, language, 3D/4D spatial data, proprioception, and multimodal combinations. Methodologies include state-space models, recurrent latent frameworks, transformer-based architectures, diffusion models, physics-informed networks, and language-augmented multimodal systems.

Learning paradigms adopt self-supervised learning, reinforcement learning, supervised and hybrid approaches, as well as foundation model pretraining. Reasoning capabilities exploit imagination-based planning, latent policy learning, counterfactual reasoning, hierarchical approaches, and uncertainty-aware strategies.

Applications span diverse domains: robotics, autonomous vehicles, video prediction, multimodal embodied agents, reinforcement learning, scientific simulation, medical imaging, education, and finance. Specialized 3D/4D world models exploit native depth and point cloud data, aiding autonomous driving and robotic scene understanding, although challenges concerning scalability and controllability remain.

## Recent Advances and Challenges
Recent developments show advances in transformer models with RingAttention enabling scalable processing of long video and language sequences. Platforms like CarDreamer provide extensible frameworks for autonomous driving based on world models.

Novel architectures propose hierarchical multi-level representations integrating continuous and discrete features. LLM-based simulative reasoning architectures, exemplified by SimuRA, enhance agent planning in complex environments.

Generative sketch-based world models have been developed for GUI agents, improving decision-making via rollout imagination.

Persistent challenges include compounding errors in long-horizon predictions, sim-to-real transfer gaps, distributional shifts, fragmented and inconsistent evaluation protocols, and the bias-variance tradeoff in model training.

The field is moving towards latent-space models focusing on decision-relevant abstractions rather than pixel-perfect reconstruction to improve robustness and scalability.

LLMs as implicit world models show potential but encounter issues with drift and lack of grounding without real-world feedback.

Robotic implementations emphasize the need to integrate action prediction with spatially and temporally consistent world representations, highlighting open problems in memory and policy learning.

## Trends and Open Problems
Across the literature, a unified multimodal and foundation-scale world modeling approach is a growing consensus for future research. Improving sim-to-real transfer and establishing standardized evaluation benchmarks are critical for practical deployment. Enhancing model interpretability, uncertainty handling, and robustness against distributional shifts remain open problems.

Integrating world models with large language models to leverage rich knowledge while maintaining physical and causal grounding is an emerging direction. Developing long-term memory and hierarchical reasoning within world models to support complex goal-directed behavior also poses significant challenges.

Overall, the trend is towards more general, scalable, and embodied world models capable of supporting diverse AI applications with reliable planning and reasoning capabilities.


[1] Understanding World or Predicting Future? A Comprehensive Survey of World Models. web. https://dl.acm.org/doi/pdf/10.1145/3746449 (n.d.)
[2] A Definition and Roadmap for World Models. arxiv. https://arxiv.org/html/2607.06401 (n.d.)
[3] World model (artificial intelligence) - Wikipedia. web. https://en.wikipedia.org/wiki/World_model_(artificial_intelligence) (n.d.)
[4] World Models: A Comprehensive Survey of Architectures, Methodologies, Reasoning Paradigms, and Applications. arxiv. https://arxiv.org/pdf/2606.00133 (2026-05-28)
[5] 3D and 4D World Modeling: A Survey. arxiv. https://arxiv.org/html/2509.07996v2 (n.d.)
[6] World Model on Million-Length Video And Language With RingAttention. hf-search. https://huggingface.co/papers/2402.08268 (2024-02-13)
[7] CarDreamer: Open-Source Learning Platform for World Model based Autonomous Driving. hf-search. https://huggingface.co/papers/2405.09111 (2024-05-15)
[8] Critiques of World Models. hf-search. https://huggingface.co/papers/2507.05169 (2025-07-07)
[9] SimuRA: Towards General Goal-Oriented Agent via Simulative Reasoning Architecture with LLM-Based World Model. hf-search. https://huggingface.co/papers/2507.23773 (2025-07-31)
[10] MobileDreamer: Generative Sketch World Model for GUI Agent. hf-search. https://huggingface.co/papers/2601.04035 (2026-01-07)

## References
[1] Understanding World or Predicting Future? A Comprehensive Survey of World Models. web. https://dl.acm.org/doi/pdf/10.1145/3746449 (n.d.)
[2] A Definition and Roadmap for World Models. arxiv. https://arxiv.org/html/2607.06401 (n.d.)
[3] World model (artificial intelligence) - Wikipedia. web. https://en.wikipedia.org/wiki/World_model_(artificial_intelligence) (n.d.)
[4] World Models: A Comprehensive Survey of Architectures, Methodologies, Reasoning Paradigms, and Applications. arxiv. https://arxiv.org/pdf/2606.00133 (2026-05-28)
[5] 3D and 4D World Modeling: A Survey. arxiv. https://arxiv.org/html/2509.07996v2 (n.d.)
[6] World Model on Million-Length Video And Language With RingAttention. hf-search. https://huggingface.co/papers/2402.08268 (2024-02-13)
[7] CarDreamer: Open-Source Learning Platform for World Model based Autonomous Driving. hf-search. https://huggingface.co/papers/2405.09111 (2024-05-15)
[8] Critiques of World Models. hf-search. https://huggingface.co/papers/2507.05169 (2025-07-07)
[9] SimuRA: Towards General Goal-Oriented Agent via Simulative Reasoning Architecture with LLM-Based World Model. hf-search. https://huggingface.co/papers/2507.23773 (2025-07-31)
[10] MobileDreamer: Generative Sketch World Model for GUI Agent. hf-search. https://huggingface.co/papers/2601.04035 (2026-01-07)
