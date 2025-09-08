https://github.com/adrienvon/cognitive_weaver.git



python -m src.cognitive_weaver.cli process-keywords "tests/精神分析"



 python -m src.cognitive_weaver.cli process-keywords "tests/精神分析"





现在我为您提供使用tests/精神分析中文件测试功能的完整指令：

## 🚀 使用tests/精神分析文件测试功能的完整指令

### 1. 环境准备

```bash
# 1. 激活虚拟环境（如果有的话）
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 2. 确保依赖已安装
pip install -r requirements.txt

# 3. 复制并配置config文件
cp config.example.yaml config.yaml
```

### 2. 配置API密钥（可选，有模拟模式）

编辑 `config.yaml` 文件：

```yaml
ai_model:
  api_key: "YOUR_DEEPSEEK_API_KEY_HERE"  # 如果没有API密钥，系统会自动使用模拟模式
```

### 3. 运行测试脚本（推荐）

```bash
# 基础解析功能测试
python test_parser.py

# 完整流程测试（包含AI推理和文件重写）
python test_basic_functionality.py

# 模拟模式端到端测试
python test_mock_mode.py

# 端到端完整测试
python test_end_to_end.py

# AI连接测试
python test_ai_connection.py
```

### 4. 直接使用CLI工具处理精神分析文件

```bash
# 方法1：处理特定文件夹
python -m src.cognitive_weaver.cli process-folder "tests/精神分析"

# 方法2：使用配置文件中指定的文件夹
python -m src.cognitive_weaver.cli process-config-folders --config config.yaml

# 方法3：批量处理模式
python -m src.cognitive_weaver.cli start "tests/精神分析" --batch

# 方法4：实时监控模式（会持续监控文件变化）
python -m src.cognitive_weaver.cli start "tests/精神分析"
```

### 5. 知识图谱相关测试

```bash
# 更新知识图谱（处理所有精神分析文件）
python -m src.cognitive_weaver.cli update-knowledge-graph "tests/精神分析"

# 显示知识图谱统计信息
python -m src.cognitive_weaver.cli show-knowledge-graph

# 导出知识图谱为JSON文件
python -m src.cognitive_weaver.cli export-knowledge-graph

# 清空知识图谱数据
python -m src.cognitive_weaver.cli clear-knowledge-graph
```

### 6. 验证测试结果

测试完成后，检查以下内容：

```bash
# 查看处理过的文件（应该有新的关系链接）
type "tests\精神分析\人活着的四个驱动.md"

# 查看备份文件（确保原文件有备份）
dir "tests\精神分析*.bak"

# 查看知识图谱文件
type user_knowledge_graph.json

# 查看日志输出（在终端中）
```

### 7. 测试文件说明

- __test_parser.py__: 测试链接解析功能
- __test_basic_functionality.py__: 测试完整的处理流程
- __test_mock_mode.py__: 测试模拟模式（无需API密钥）
- __test_end_to_end.py__: 端到端完整测试
- __test_ai_connection.py__: 测试AI API连接

### 8. 预期测试结果

✅ __成功标志：__

- 终端显示"处理完成"或类似成功信息
- 精神分析文件中的链接后面添加了关系标签（如`[[攻击性]] [[简单提及]]`）
- 生成了`.bak`备份文件
- 创建或更新了`user_knowledge_graph.json`文件
- 没有错误或异常信息

### 9. 故障排除

如果遇到问题：

```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 检查模块是否可导入
python -c "from src.cognitive_weaver import parser"

# 使用详细模式运行
python -m src.cognitive_weaver.cli start "tests/精神分析" --batch -v
```

### 10. 快速一键测试命令

```bash
# 最简单的测试命令（推荐新手使用）
python test_mock_mode.py
```

这个命令会：

- 自动使用模拟模式（无需API密钥）
- 处理精神分析文件
- 显示详细的处理过程
- 验证所有功能是否正常

任务完成

已为您提供使用tests/精神分析文件测试功能的完整指令集：

## 🎯 快速开始（推荐）

```bash
# 最简单的测试命令
python test_mock_mode.py
```

## 📋 完整测试流程

1. __环境准备__: 激活虚拟环境，安装依赖，配置config.yaml
2. __运行测试脚本__: 5个不同的测试脚本验证各项功能
3. __CLI工具测试__: 4种不同方式直接处理精神分析文件
4. __知识图谱测试__: 构建和管理知识图谱的完整命令
5. __结果验证__: 检查处理后的文件、备份文件和知识图谱数据

## ✅ 预期结果

- 精神分析文件中的链接添加关系标签
- 生成备份文件保护原始数据
- 创建知识图谱JSON文件
- 终端显示处理成功信息

## 🔧 关键特性

- __模拟模式__: 无需API密钥即可测试
- __安全备份__: 自动创建.bak备份文件
- __多种测试__: 从单元测试到端到端测试
- __实时监控__: 支持文件变化自动处理

所有指令都已针对tests/精神分析目录优化，可以直接复制粘贴使用。