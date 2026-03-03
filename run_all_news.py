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
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 총 {len(topics)}개의 주제(Topic)에 대해 데일리 {search_type} 뉴스 파이프라인 병렬 처리를 시작합니다. (최대 3개 동시 실행)")
    print("="*60)
    
    # API Rate Limit 및 과부하 방지를 위해 동시에 최대 3개까지만 병렬 실행하도록 제한
    sem = asyncio.Semaphore(3)

    async def run_with_semaphore(idx, topic):
        short_topic = topic.replace('\n', ' ').strip()
        if len(short_topic) > 30:
            short_topic = short_topic[:30] + "..."
            
        async with sem:
            print(f"\n▶ [{idx+1}/{len(topics)}] 주제 처리 시작: '{short_topic}'")
            return await daily_deep_news.run_news_flow(topic, instructions, search_type)

    tasks = []
    for idx, topic in enumerate(topics):
        tasks.append(run_with_semaphore(idx, topic))
        
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 모든 주제의 제한적 병렬 처리(Semaphore)를 대기합니다...")
    
    # asyncio.gather를 사용하여 모든 작업을 병렬로 실행하되, 내부 Semaphore에 의해 최대 3개씩 끊어서 알아서 처리됨
    gathered_results = await asyncio.gather(*tasks, return_exceptions=True)
    results = list(zip(topics, gathered_results))
            
    # 전체 요약 출력
    print("\n" + "="*60)
    for idx, (topic, result) in enumerate(results, 1):
        short_topic = topic.replace('\n', ' ').strip()
        if len(short_topic) > 30:
            short_topic = short_topic[:30] + "..."
            
        if isinstance(result, Exception):
            print(f"[!] '{short_topic}' 실행 중 에러 발생: {result}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] '{short_topic}' 완료!")
            
    print("="*60)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 스케줄링된 모든 주제의 순차 작업이 마무리되었습니다.")

if __name__ == "__main__":
    if sys.platform == 'win32':
        import sys
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(run_all_topics())
