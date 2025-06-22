# 定时搜索和总结框架

这是一个Python定时调度框架，用于自动执行Google搜索和使用Ollama进行内容总结的任务。

## 功能特点

- 支持定时执行搜索任务
- 使用Google Custom Search API进行信息搜索
- 使用Ollama API进行内容总结
- 自动保存搜索结果和总结到JSON文件
- 灵活的定时配置（支持cron表达式）

## 环境要求

- Python 3.7+
- 安装的依赖包（见requirements.txt）
- Google Custom Search API密钥
- 运行中的Ollama服务

## 安装

1. 克隆代码库
2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 环境变量配置

在运行之前，需要设置以下环境变量：

- `GOOGLE_API_KEY`: Google API密钥
- `GOOGLE_CX`: Google Custom Search Engine ID
- `OLLAMA_URL`: Ollama服务的URL（默认为http://localhost:11434）

可以通过export命令设置：
```bash
export GOOGLE_API_KEY="你的Google API密钥"
export GOOGLE_CX="你的Search Engine ID"
export OLLAMA_URL="http://localhost:11434"
```

## 使用方法

1. 基本使用：
```python
from schedule_search import SearchAndSummarizeScheduler

scheduler = SearchAndSummarizeScheduler()

# 设置定时任务（每天早上8点执行）
scheduler.schedule_task(
    search_query="你的搜索关键词",
    cron_expression="0 8 * * *"
)

# 启动调度器
scheduler.start()
```

2. 直接运行脚本：
```bash
python schedule_search.py
```

## Cron表达式示例

- 每天早上8点：`0 8 * * *`
- 每小时执行：`0 * * * *`
- 每周一早上9点：`0 9 * * 1`
- 每月1号中午12点：`0 12 1 * *`

## 结果输出

搜索结果和总结将保存在`search_results`目录下，文件名格式为：`result_YYYYMMDD_HHMMSS.json` 