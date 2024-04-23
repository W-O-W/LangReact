# 🦜️🔗 LangReact

⚡ 用 Planning Agent 来优化的大模型应用 ⚡
⚡ Build your LLM Application based on planning agent ⚡

## 🤔 What is LangReact?

**LangReact** 是一个配置化的 Planning Agent 应用开发工具，通过配置和插件能快速为你的 GPT 应用提供 Planning 能力。
- **配置化**: 通过 configure 快速构建你的 Planning Agent，无需对你的 AI 应用代码做任何更改
- **插件化**: 通过引入各种各样的工具插件，让你的 AI 应用快速具备使用工具的能力
- **多种 Planning Agent 实现**: 通过配置开启多种 Planning 功能：COT、Memory RAG、TOT、Reflection 等

## usage

### install

` pip install langreact`

### build your application
参考 demo 目录中的 create_a_chatbot.py 创建一个 COT Planning 辅助的聊天机器人
执行这个 demo：
`DASHSCOPE_API_KEY=XXXX python3 -m demo.create_a_chatbot`

创建和使用一个应用的基本流程：
1. 继承 ApplicationPlugin 创建一个自己的 LLM 应用
2. 从 demo 中拷贝 default.py 来创建一个新的应用配置文件，例如 demo/qwen_chat_configure.py
3. 修改配置中的 MEMORY_INDEX_URI 来引入你的日志 RAG 索引，如果仅仅测试可以执行 demo/simple_milvus_server 中的 start_default_server 方法，创建一个临时的索引
4. （可选）根据需要修改配置中的 PROMPT 来定制你自己的 planning agent
5. 通过 Flow 创建应用的数据流，赋予你的 LLM 应用 Planning 能力
6. 通过 Flow.invoke 来调用你的 LLM 应用

# RoadMap

1. 提供 LangChain 应用装饰器，方便 LangChain 应用转换
2. 提供插件市场，并支持基于插件评分 Reranker
3. 提供 AI 数字人应用模版

# Contact

max_and_min@163.com

