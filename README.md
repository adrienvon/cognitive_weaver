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

## 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

1. **复制配置文件**:
```bash
cp config.example.yaml config.yaml
```

2. **配置API密钥**: 在`config.yaml`中设置您的DeepSeek API密钥

3. **启动服务** (从项目根目录运行):
```bash
# 实时监控模式
python -m cognitive_weaver.cli start /path/to/your/obsidian/vault

# 批量处理模式
python -m cognitive_weaver.cli start /path/to/your/obsidian/vault --batch

# 处理特定文件夹
python -m cognitive_weaver.cli process-folder /path/to/your/folder

# 处理配置指定的文件夹
python -m cognitive_weaver.cli process-config-folders --config config.yaml
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
├── README.md                    # 项目文档
└── requirements.txt             # Python依赖列表
```

## 文件作用详解

### 核心代码文件 (src/cognitive_weaver/)

- **__init__.py**: Python包初始化文件，标识cognitive_weaver为一个Python包
- **ai_inference.py**: AI推理引擎核心，负责调用AI模型分析笔记间的逻辑关系，支持多种关系类型推断
- **cli.py**: 命令行接口，提供start命令用于启动实时监控或批量处理模式
- **config.py**: 配置管理模块，处理配置文件的加载、验证和提供配置访问接口
- **monitor.py**: 文件系统监控模块，使用watchdog库监听Obsidian vault的文件变化事件
- **parser.py**: 链接解析器，提取Markdown文件中的双链链接，分析链接上下文
- **rewriter.py**: 文件重写器，负责安全地修改笔记文件，添加推断出的关系链接

### 测试文件 (tests/)

- **test_full_pipeline.py**: 完整流程集成测试，验证从解析到重写的整个工作流
- **test_parser.py**: 解析器单元测试，专门测试链接解析功能
- **test_data/test_vault/**: 包含测试用的Obsidian笔记文件，用于各种测试场景

### 配置文件

- **config.example.yaml**: 示例配置文件，展示所有可配置选项和默认值
- **config.yaml**: 用户实际使用的配置文件（需要从示例复制并修改）

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

处理前的笔记内容：
```markdown
无意识不会在乎事实如何，无意识只在乎[[感受]]。
```

处理后的笔记内容：
```markdown
无意识不会在乎事实如何，无意识只在乎[[感受]]。 [[支撑观点]]
```

## 开发路线图

- [x] 核心引擎开发（CLI框架、监控、解析、推理、重写）
- [ ] 功能增强与优化（配置文件、批量处理、备份机制）
- [ ] Obsidian插件集成（图形化界面）
- [ ] 高级分析功能（认知分析报告）

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来帮助改进这个项目！
