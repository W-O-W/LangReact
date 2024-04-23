# 🦜️🔗 LangReact

⚡ 用 Planning Agent 来优化的大模型应用 ⚡
⚡ Build your LLM Application based on planning agent ⚡

## 🤔 What is LangReact?

**LangReact** 是一个配置化的 Planning Agent 应用开发工具，通过配置、插件能快速为你的 GPT 应用提供 Planning 能力。
- **配置化**: 通过 configure 快速构建你的 Planning Agent，无需对你的 AI 应用代码做任何更改
- **插件化**: 通过引入各种各样的工具插件，让你的 AI 应用快速具备使用工具的能力
- **多种 Planning Agent 实现**: 通过配置开启多种 Planning 功能：COT、Memory RAG、TOT、Reflection 等

## usage

### install

` pip install langreact`

### build your application
参考 demo 目录中的 create_qwen_chat_configure.py 和 create_a_chatbot.py

create_a_chatbot.py 创建一个 COT Planning 辅助的聊天机器人
create_qwen_chat_configure.py 应用的全局配置，包括 memory 服务器、PROMPT 等

# RoadMap

1. 提供 LangChain 应用装饰器，方便 LangChain 应用转换
2. 提供插件市场，并支持基于插件评分 Reranker
3. 提供 AI 数字人应用模版

# Contact

max_and_min@163.com
