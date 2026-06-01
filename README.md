# Marketing Orchestrator 🚀

An AI-Powered, stateless operational budget orchestrator built with **FastAPI**, **Cube.js**, **PostgreSQL (Supabase)**, and **React (Vite)**. 

This platform bridges semantic analytical data querying with asynchronous operational writebacks, enabling an LLM-driven copilot to safely evaluate property performance and execute real-time budget synchronization.

*   💻 **Live Frontend (Vercel):** [https://marketing-orchestrator-chi.vercel.app](https://marketing-orchestrator-chi.vercel.app/)
*   ⚙️ **Live API (Hugging Face Spaces):** [https://rbrodbeck-marketing-orchestrator.hf.space](https://rbrodbeck-marketing-orchestrator.hf.space)

---

## 🏗️ System Architecture

This project is built using a secure, stateless, and cloud-decoupled multi-tier architecture:

```mermaid
graph TD
    User([User Browser]) -->|HTTPS Port 443| Vercel[Vercel Frontend UI]
    User -->|HTTPS Port 443| HF[Hugging Face Space Gateway]
    
    subgraph Hugging Face Space Container
        HF -->|Public Port 7860| FastAPI[FastAPI Gateway]
        FastAPI -->|Private Localhost Port 4000| CubeJS[CubeJS Semantic Server]
    end
    
    CubeJS -->|PostgreSQL SSL Port 5432| Supabase[(Supabase Cloud Database)]
    FastAPI -->|Secure HTTPS| OpenAI[OpenAI API]