# Cognitive Weaver (认知织网者)
## 下一阶段：MOFA框架迁移技术规划
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

# 关键词自动链接处理（推荐功能）
python -m cognitive_weaver.cli process-keywords /path/to/your/folder

# 更新知识图谱（处理所有文件）
python -m cognitive_weaver.cli update-knowledge-graph /path/to/your/obsidian/vault

# 显示知识图谱统计信息
python -m cognitive_weaver.cli show-knowledge-graph

# 导出知识图谱为JSON文件
python -m cognitive_weaver.cli export-knowledge-graph

# 清空知识图谱数据
python -m cognitive_weaver.cli clear-knowledge-graph
```

## 关键词自动链接工作流程详解

### 核心功能：`process-keywords` 命令

`process-keywords` 是 Cognitive Weaver 的核心功能之一，它能够智能地分析文件夹中的所有笔记，自动识别相似的概念并为它们创建 Obsidian 双链链接。

#### 使用方法
```bash
python -m cognitive_weaver.cli process-keywords "tests/精神分析"
```

#### 完整工作流程

##### 1. **命令解析与初始化** (`cli.py`)
- 验证目标文件夹路径的有效性
- 加载配置文件（`config.yaml` 或 `config.example.yaml`）
- 初始化核心组件：VaultMonitor、KeywordExtractor、AIInferenceEngine

##### 2. **文件扫描与过滤** (`monitor.py`)
- 递归扫描指定文件夹中的所有 `.md` 文件
- 自动过滤备份文件（`.bak`）和配置中指定的忽略模式
- 输出：`Found X markdown files in the folder`

##### 3. **智能关键词提取** (`keyword_extractor.py`)
对每个 Markdown 文件执行以下操作：

**文本预处理**：
- 逐行读取文件内容
- 跳过已包含 `[[]]` 格式链接的行（避免重复处理）
- 移除标点符号和特殊字符

**中文关键词提取算法**：
- 使用正则表达式 `[\u4e00-\u9fff\w]+` 提取中文字符和单词
- 智能分割策略：
  - 短词语（≤4字符）：直接作为候选关键词
  - 长词语（>4字符）：使用滑动窗口提取2-3字符的有意义片段
- 停用词过滤：排除"的"、"了"、"在"、"是"等无意义词汇
- 质量控制：过滤数字、单字符和包含停用词的组合

**上下文提取**：
- 为每个关键词提取周围的上下文文本
- 包含前后行的部分内容以提供语义环境
- 输出：`Found X potential keywords across Y files`

##### 4. **AI驱动的相似性分析** (`ai_inference.py`)

**初始分组**：
- 按标准化形式（转小写）对关键词进行初步聚类
- 只处理出现多次的关键词组（避免单次出现的噪音）

**AI语义验证**：
对每个候选关键词组执行以下分析：
- 构建详细的分析提示，包含：
  - 关键词本身
  - 出现的上下文
  - 所在文件名
- 发送给AI模型进行语义相似性判断
- AI提示示例：
```
你是一位心理学知识图谱专家，擅长识别中文心理学概念之间的语义相似性。

请分析以下关键词是否指向同一个心理学概念或实体：
关键词: '攻击性', 上下文: '攻击性是人格的重要组成部分', 文件: 攻击性与力比多.md
关键词: '攻击性', 上下文: '一个人的疾病是攻击性投注出了问题', 文件: 疾病分析.md

如果这些关键词确实指向同一个心理学概念，回复"是"，否则回复"否"。
```
- 输出：`Found X groups of similar keywords`

##### 5. **自动链接生成** (`rewriter.py`)

**安全文件操作**：
- 为每个要修改的文件自动创建 `.bak` 备份
- 使用原子操作确保文件完整性

**链接插入算法**：
- 在文件中定位关键词的精确位置
- 将关键词转换为 `[[关键词]]` 格式
- 保持原文件的格式、缩进和结构不变
- 避免重复链接（跳过已有链接的行）

**处理示例**：
```markdown
# 处理前
攻击性是人格的重要组成部分，它与力比多共同作用。

# 处理后  
[[攻击性]]是人格的重要组成部分，它与[[力比多]]共同作用。
```

##### 6. **知识图谱更新** (`knowledge_graph.py`)
- 将新创建的概念链接添加到知识图谱
- 更新节点（概念）和边（关系）信息
- 自动保存到 `user_knowledge_graph.json` 文件

#### 实际执行示例

```bash
$ python -m cognitive_weaver.cli process-keywords "tests/精神分析"

Processing keywords for folder: c:\Users\baoba\Desktop\cognitive_weaver\tests\精神分析
Found 16 markdown files in the folder
Found 966 potential keywords across 16 files
Found 95 groups of similar keywords
Linking 3 occurrences of '攻击性'
Linking 2 occurrences of '力比多'  
Linking 4 occurrences of '母亲'
Linking 2 occurrences of '防御'
Linking 3 occurrences of '焦虑'
...
Keyword linking completed.
```

#### 技术特点

1. **智能而非机械**：使用AI语义分析而非简单的字符串匹配
2. **安全可靠**：自动备份机制，防止数据丢失
3. **批量高效**：一次处理整个文件夹的所有笔记
4. **Obsidian兼容**：生成标准的 `[[]]` 双链链接格式
5. **上下文感知**：考虑关键词的使用语境进行智能判断
6. **专业优化**：针对特定领域（如心理学）进行概念识别优化

#### 适用场景

- **学术研究**：自动识别和链接相关的学术概念
- **知识整理**：将散乱的笔记转换为结构化的知识网络
- **概念梳理**：发现笔记中的重复概念并建立关联
- **知识图谱构建**：为 Obsidian 知识库自动建立概念关系网络

这个工作流程的核心价值在于将人工的概念识别和链接工作自动化，让用户能够专注于内容创作，而由系统负责维护知识结构的一致性和完整性。

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
