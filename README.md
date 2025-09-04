# Cognitive Weaver (认知织网者)

AI驱动的Obsidian知识图谱结构化引擎

## 项目概述

Cognitive Weaver 是一个运行在本地的AI引擎，它能自动分析Obsidian笔记间的链接上下文，**智能地推断其逻辑关系，并以[[关系]]链接的形式将这种关系"固化"回笔记中**，从而将用户原本混乱的知识图谱，重构为一张结构清晰、可被分析的"认知地图"。

## 核心功能

- **自动关系抽取**: 分析Obsidian笔记间的链接上下文，推断逻辑关系
- **智能关系分类**: 支持8种预定义关系类型（支撑观点、反驳观点、举例说明等）
- **实时文件监控**: 监控Obsidian vault变化，自动处理新添加的链接
- **批量处理模式**: 支持对整个知识库进行一次性分析处理
- **安全备份机制**: 文件修改前自动创建备份，防止数据丢失
- **知识图谱构建**: 自动构建用户知识图谱，存储节点和关系数据
- **JSON数据导出**: 支持导出知识图谱数据为JSON格式进行分析

## 安装依赖

### 推荐使用虚拟环境

为了保持依赖隔离和项目一致性，建议使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 直接安装（不推荐）
```bash
pip install -r requirements.txt
```

## 快速开始

1. **设置虚拟环境**（推荐）：
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **复制配置文件**:
```bash
cp config.example.yaml config.yaml
```

3. **配置API密钥**: 在`config.yaml`中设置您的DeepSeek API密钥

4. **启动服务** (从项目根目录运行):
```bash
# 实时监控模式
python -m cognitive_weaver.cli start /path/to/your/obsidian/vault

# 批量处理模式
python -m cognitive_weaver.cli start /path/to/your/obsidian/vault --batch

# 处理特定文件夹
python -m cognitive_weaver.cli process-folder /path/to/your/folder

# 处理配置指定的文件夹
python -m cognitive_weaver.cli process-config-folders --config config.yaml

# 更新知识图谱（处理所有文件）
python -m cognitive_weaver.cli update-knowledge-graph /path/to/your/obsidian/vault

# 显示知识图谱统计信息
python -m cognitive_weaver.cli show-knowledge-graph

# 导出知识图谱为JSON文件
python -m cognitive_weaver.cli export-knowledge-graph

# 清空知识图谱数据
python -m cognitive_weaver.cli clear-knowledge-graph
```

## 调试指南

项目已配置调试支持，您可以在虚拟环境中使用以下方式进行调试：

```bash
# 确保在虚拟环境中
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 运行调试模式
python -m debugpy --listen 5678 -m cognitive_weaver.cli start /path/to/vault

# 或者使用IDE配置远程调试，连接到localhost:5678
```

## 配置说明

编辑`config.yaml`文件来自定义行为：

- `ai_model`: AI模型配置（支持DeepSeek、OpenAI等）
- `relations`: 关系类型配置
- `file_monitoring`: 文件监控设置
  - `folders_to_scan`: 要扫描的文件夹路径列表（例如：["folder1", "folder2/subfolder"]）
- `max_retries`: AI调用重试次数
- `backup_files`: 是否启用备份功能

## 项目结构

```
cognitive_weaver/
├── src/
│   └── cognitive_weaver/
│       ├── __init__.py          # 包初始化文件
│       ├── ai_inference.py      # AI推理引擎
│       ├── cli.py               # 命令行接口
│       ├── config.py            # 配置管理
│       ├── knowledge_graph.py   # 知识图谱模块（新增）
│       ├── monitor.py           # 文件监控
│       ├── parser.py            # 链接解析
│       └── rewriter.py          # 文件重写器
├── tests/
│   ├── test_full_pipeline.py    # 完整流程测试
│   ├── test_parser.py           # 解析器测试
│   └── test_data/
│       └── test_vault/          # 测试用的Obsidian vault
│           ├── 测试笔记.md      # 测试笔记文件
│           ├── 测试笔记.md.bak  # 备份文件
│           ├── 无意识.md        # 测试笔记文件
│           └── 无意识.md.bak    # 备份文件
├── config.example.yaml          # 示例配置文件
├── config.yaml                  # 用户配置文件（需创建）
├── knowledge_graph.json         # 知识图谱数据文件（自动生成）
├── README.md                    # 项目文档
└── requirements.txt             # Python依赖列表
```

## 文件作用详解

### 核心代码文件 (src/cognitive_weaver/)

- **__init__.py**: Python包初始化文件，标识cognitive_weaver为一个Python包
- **ai_inference.py**: AI推理引擎核心，负责调用AI模型分析笔记间的逻辑关系，支持多种关系类型推断
- **cli.py**: 命令行接口，提供start命令用于启动实时监控或批量处理模式，以及知识图谱管理命令
- **config.py**: 配置管理模块，处理配置文件的加载、验证和提供配置访问接口
- **knowledge_graph.py**: 知识图谱模块，管理用户知识图谱的构建、存储和查询
- **monitor.py**: 文件系统监控模块，使用watchdog库监听Obsidian vault的文件变化事件，自动更新知识图谱
- **parser.py**: 链接解析器，提取Markdown文件中的双链链接，分析链接上下文
- **rewriter.py**: 文件重写器，负责安全地修改笔记文件，添加推断出的关系链接

### 测试文件 (tests/)

- **test_full_pipeline.py**: 完整流程集成测试，验证从解析到重写的整个工作流
- **test_parser.py**: 解析器单元测试，专门测试链接解析功能
- **test_data/test_vault/**: 包含测试用的Obsidian笔记文件，用于各种测试场景

### 配置文件

- **config.example.yaml**: 示例配置文件，展示所有可配置选项和默认值
- **config.yaml**: 用户实际使用的配置文件（需要从示例复制并修改）
- **knowledge_graph.json**: 自动生成的知识图谱数据文件，包含所有节点和关系信息

### 其他文件

- **README.md**: 项目文档，包含安装、使用说明和项目信息
- **requirements.txt**: Python依赖包列表，用于pip安装

## 支持的关系类型

- `支撑观点` - 一个观点支持另一个观点
- `反驳观点` - 一个观点反驳另一个观点  
- `举例说明` - 用例子说明概念
- `定义概念` - 定义某个概念
- `属于分类` - 属于某个分类或类别
- `包含部分` - 包含某个组成部分
- `引出主题` - 引出或过渡到某个主题
- `简单提及` - 简单提及或引用

## 使用示例

### 关系链接处理

处理前的笔记内容：
```markdown
无意识不会在乎事实如何，无意识只在乎[[感受]]。
```

处理后的笔记内容：
```markdown
无意识不会在乎事实如何，无意识只在乎[[感受]]。 [[支撑观点]]
```

### 知识图谱数据

知识图谱自动构建的数据结构（存储在knowledge_graph.json中）：
```json
{
  "nodes": [
    {
      "id": "感受",
      "title": "感受",
      "file_path": "/path/to/感受.md",
      "content_snippet": "感受是人类情感体验的核心...",
      "created_at": "2024-01-15T10:30:00",
      "updated_at": "2024-01-15T10:30:00"
    },
    {
      "id": "无意识",
      "title": "无意识",
      "file_path": "/path/to/无意识.md", 
      "content_snippet": "无意识不会在乎事实如何...",
      "created_at": "2024-01-15T10:35:00",
      "updated_at": "2024-01-15T10:35:00"
    }
  ],
  "edges": [
    {
      "source": "无意识",
      "target": "感受",
      "relationship": "支撑观点",
      "context": "无意识不会在乎事实如何，无意识只在乎感受",
      "created_at": "2024-01-15T10:35:00"
    }
  ]
}
```

## 开发路线图

- [x] 核心引擎开发（CLI框架、监控、解析、推理、重写）
- [x] 知识图谱功能（节点管理、关系存储、JSON导出）
- [ ] 功能增强与优化（配置文件、批量处理、备份机制）
- [ ] Obsidian插件集成（图形化界面）
- [ ] 高级分析功能（认知分析报告、可视化展示）

## 知识图谱功能详解

Cognitive Weaver现在包含完整的知识图谱功能，能够自动构建和维护用户的知识结构：

### 数据结构
- **节点 (Nodes)**: 表示笔记文件，包含标题、文件路径、内容片段等信息
- **边 (Edges)**: 表示笔记间的关系，包含源节点、目标节点、关系类型和上下文

### 自动构建
知识图谱在以下情况下自动更新：
- 实时监控模式下检测到文件变化
- 批量处理模式下处理整个知识库
- 使用`update-knowledge-graph`命令显式更新

### 数据持久化
知识图谱数据自动保存到`knowledge_graph.json`文件中，支持：
- 增量更新（只添加新的节点和关系）
- JSON格式导出用于外部分析
- 数据清空和重新构建

### 使用场景
1. **知识发现**: 分析笔记间的关联模式
2. **内容分析**: 识别核心概念和热门话题
3. **学习追踪**: 跟踪知识构建过程和时间线
4. **外部集成**: 导出数据到其他分析工具

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目！
