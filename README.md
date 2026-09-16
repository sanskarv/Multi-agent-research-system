# 🔬 The Research Desk

> **An AI-powered multi-agent research system that transforms a topic into a structured research report.**

The Research Desk uses a **four-agent AI pipeline built with LangChain**. Each agent performs a specialized task — searching, reading, writing, and critically reviewing — before delivering a finished research report.

---

## ✨ Features

- 🔎 **Search Agent** — Finds recent and relevant sources from the web.
- 📖 **Reader Agent** — Selects relevant sources and extracts useful information.
- ✍️ **Writer Agent** — Combines research into a structured report.
- 🧐 **Critic Agent** — Reviews the generated report and identifies gaps or weak points.
- 🔗 **Multi-Agent Pipeline** — Agents work sequentially, with each stage feeding the next.
- ⚡ **Live Research Progress** — Track the research process as the agents work.
- 📄 **Structured Reports** — Generates reports containing an introduction, key findings, conclusion, and sources.
- 🎨 **Simple Web Interface** — Enter a topic and start research with a single click.

---

## 🖥️ Application

### The Research Desk

Give it a topic and let the AI agents research it for you.

Example topics:

- **LLM agents in 2026**
- **CRISPR gene editing**
- **Fusion energy progress**

The application processes the topic through the complete research pipeline and returns a finished report.

---
<img width="1919" height="902" alt="image" src="https://github.com/user-attachments/assets/2b0b70cf-ad64-452b-b748-916f7ff3a6fd" />

## 🏗️ How It Works

The system follows a sequential four-agent architecture:

```text
                         ┌──────────────────┐
                         │   Research Topic │
                         └────────┬─────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │      🔎 Search Agent     │
                    │                         │
                    │ Finds relevant and      │
                    │ recent web sources      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      📖 Reader Agent     │
                    │                         │
                    │ Reads and extracts      │
                    │ useful information      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      ✍️ Writer Agent     │
                    │                         │
                    │ Creates a structured    │
                    │ research report         │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │      🧐 Critic Agent     │
                    │                         │
                    │ Reviews the report and  │
                    │ identifies weaknesses   │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │    📄 Final Report       │
                    │                         │
                    │ Introduction            │
                    │ Key Findings            │
                    │ Conclusion              │
                    │ Sources                  │
                    └─────────────────────────┘
