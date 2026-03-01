import json
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import importlib.util

# daily_deep_news.py 의존성 주입
import daily_deep_news

CONFIG_FILE = Path(__file__).parent / "config.json"

async def run_all_topics():
    if not CONFIG_FILE.exists():
        print("config.json 파일이 없습니다. 기본 [AI Technology] 주제 1개만 실행합니다.")
        await daily_deep_news.run_news_flow("AI Technology")
        return

    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        
    topics = config.get("topics", ["AI Technology"])
    instructions = config.get("media", {})
    search_type = config.get("search_type", "deep") # 기본값 deep
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 총 {len(topics)}개의 주제(Topic)에 대해 데일리 {search_type} 뉴스 파이프라인 병렬 처리를 시작합니다.")
    print("="*60)
    
    tasks = []
    for idx, topic in enumerate(topics, 1):
        print(f"\n▶ [{idx}/{len(topics)}] 주제 큐에 추가: '{topic}'")
        tasks.append(daily_deep_news.run_news_flow(topic, instructions, search_type))
        
    # Execute all topics concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for idx, (topic, result) in enumerate(zip(topics, results), 1):
        if isinstance(result, Exception):
            print(f"[!] '{topic}' 실행 중 에러 발생: {result}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] '{topic}' 완료!")
            
    print("="*60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 스케줄링된 모든 주제의 병렬 작업이 마무리되었습니다.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        import sys
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(run_all_topics())
