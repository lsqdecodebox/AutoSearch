import logging
import schedule
import time
import requests
import json
from datetime import datetime
import os
from typing import List, Dict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SearchAndSummarizeScheduler:
    def __init__(self):
        self.google_api_key = 'AIzaSyCC8wmMg4I4a-jOJPVRR0pZfnsODV0_TRE'
        self.google_cx = 'c60b1d18bfe1949ec'  # Google Custom Search Engine ID
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.running = False
        
    def google_search(self, query: str, num_results: int = 10) -> List[Dict]:
        """执行Google搜索"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.google_cx,
            'q': query,
            'num': num_results
        }
        
        # 配置代理
        proxies = {
            'http': 'http://localhost:7897',
            'https': 'http://localhost:7897'
        }
        
        try:
            response = requests.get(url, params=params, proxies=proxies)
            response.raise_for_status()
            results = response.json().get('items', [])
            return [{'title': item['title'], 'snippet': item['snippet'], 'link': item['link']} 
                   for item in results]
        except Exception as e:
            logger.error(f"Google搜索出错: {str(e)}")
            return []

    def summarize_with_ollama(self, text: str) -> str:
        """使用Ollama API进行文本总结"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "qwen3:30b",
                    "prompt": f"请总结以下内容，并引用来源，不要遗漏任何信息：\n{text}",
                    "stream": False
                }
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logger.error(f"Ollama API调用出错: {str(e)}")
            return ""

    def search_and_summarize_task(self, search_query: str):
        """执行搜索和总结任务"""
        logger.info(f"开始执行搜索任务，查询词: {search_query}")
        
        # 执行Google搜索
        search_results = self.google_search(search_query)
        if not search_results:
            logger.warning("未获取到搜索结果")
            return
        print(search_results)
        # 准备要总结的文本
        text_to_summarize = "\n".join([
            f"{index+1}. 标题: {result['title']}\n摘要: {result['snippet']}\n链接: {result['link']}\n"
            for index, result in enumerate(search_results)
        ])

        # 使用Ollama进行总结
        summary = self.summarize_with_ollama(text_to_summarize)
        
        # 保存结果
        self.save_results(search_query, search_results, summary)

    def save_results(self, query: str, search_results: List[Dict], summary: str):
        """保存搜索和总结结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = "search_results"
        
        # 创建结果目录
        os.makedirs(results_dir, exist_ok=True)
        
        # 保存结果到文件
        filename = f"{results_dir}/result_{timestamp}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'query': query,
                'timestamp': timestamp,
                'search_results': search_results,
                'summary': summary
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {filename}")

    def schedule_task(self, search_query: str, cron_expression: str):
        """设置定时任务"""

        time_str = datetime.now().strftime("%Y年%m月%d日")
        search_query = search_query.replace("今日", time_str)

        def parse_cron_to_schedule(cron_expr: str) -> tuple:
            # 解析cron表达式 "分 时 日 月 星期"
            minute, hour, day, month, day_of_week = cron_expr.split()
            
            if minute != "0" or hour == "*":
                logger.warning("Schedule库限制较多，建议使用整点调度")
            
            # Schedule只支持基础的时间调度，这里我们处理最常见的每天固定时间的情况
            if hour != "*" and minute == "0":
                schedule.every().day.at(f"{hour.zfill(2)}:00").do(
                    self.search_and_summarize_task, search_query
                )
                logger.info(f"已设置每天 {hour}:00 执行任务")
            else:
                logger.warning("不支持的cron表达式格式，将默认设置为每天早上8点执行")
                schedule.every().day.at("08:00").do(
                    self.search_and_summarize_task, search_query
                )

        parse_cron_to_schedule(cron_expression)
        logger.info(f"已设置定时任务，查询词: {search_query}, 调度表达式: {cron_expression}")

    def start(self):
        """启动调度器"""
        self.running = True
        logger.info("调度器已启动")
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def shutdown(self):
        """关闭调度器"""
        self.running = False
        logger.info("调度器已关闭")

if __name__ == "__main__":
    # 创建调度器实例
    scheduler = SearchAndSummarizeScheduler()

    time_str = datetime.now().strftime("%Y年%m月%d日")
    print(time_str)

    scheduler.search_and_summarize_task(f"{time_str}影响黄金价格的重大事件")
    
    # 设置示例任务 - 每天早上8点执行
    scheduler.schedule_task(
        search_query="今日影响黄金价格的重大事件",
        cron_expression="0 20 * * *"
    )
    
    try:
        # 启动调度器
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
