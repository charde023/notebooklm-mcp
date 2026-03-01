import asyncio
import os
import argparse
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from pptx import Presentation
from pptx.util import Pt
from notebooklm.auth import extract_cookies_from_storage, fetch_tokens, AuthTokens
from notebooklm.client import NotebookLMClient
import json

# Windows asyncio 버그 해결 (필수)
import sys
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def get_notebooklm_client():
    storage_path = Path.home() / ".notebooklm" / "storage_state.json"
    if not storage_path.exists():
        raise FileNotFoundError(f"Missing {storage_path}. Please login using the notebooklm CLI first.")
    state = json.loads(storage_path.read_text())
    cookies = extract_cookies_from_storage(state)
    csrf, session_id = await fetch_tokens(cookies)
    auth = AuthTokens(cookies=cookies, csrf_token=csrf, session_id=session_id)
    return NotebookLMClient(auth)

async def generate_slide_deck_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [SlideDeck] 네이티브 슬라이드 생성 큐에 등록...")
    return await client.artifacts.generate_slide_deck(
        nb_id, 
        language="ko", 
        instructions=instructions_text if instructions_text else "비즈니스 전문가를 위한 심층 보고서 형식으로 구체적인 데이터와 주요 인용구를 포함해 상세하게 작성해주세요."
    )

async def generate_podcast_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [Podcast] 오디오 오버뷰(팟캐스트) 생성 큐에 등록...")
    return await client.artifacts.generate_audio(
        nb_id, 
        language="ko", 
        instructions=instructions_text if instructions_text else "전문적이고 분석적인 뉴스 브리핑 톤으로 남녀가 교차 진행하며, 단순히 뉴스의 사실만 읽지 말고 산업에 미치는 파급력과 전망까지 깊게 토론(Deep Dive)해 주세요."
    )

async def generate_infographic_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [Infographic] 인포그래픽 생성 큐에 등록...")
    # generate_infographic은 Enum 파라미터 호환성 문제로 인해 안전하게 기본 파라미터만 전달합니다.
    return await client.artifacts.generate_infographic(nb_id, language="ko")

async def generate_video_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [Video] 비디오 개요 생성 큐에 등록...")
    return await client.artifacts.generate_video(nb_id, language="ko", instructions=instructions_text)
    
async def generate_report_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [Report] 보고서 생성 큐에 등록...")
    # generate_report는 instructions 대신 custom_prompt 매개변수를 사용
    return await client.artifacts.generate_report(nb_id, language="ko", custom_prompt=instructions_text)

async def generate_study_guide_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [StudyGuide] 스터디 가이드 생성 큐에 등록...")
    # generate_study_guide는 지시문 커스텀을 지원하지 않음
    return await client.artifacts.generate_study_guide(nb_id, language="ko")

async def generate_quiz_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [Quiz] 퀴즈 생성 큐에 등록...")
    # generate_quiz는 language 매개변수를 지원하지 않음
    return await client.artifacts.generate_quiz(nb_id, instructions=instructions_text)

async def generate_flashcards_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [Flashcards] 플래시카드 생성 큐에 등록...")
    # generate_flashcards는 language 매개변수를 지원하지 않음
    return await client.artifacts.generate_flashcards(nb_id, instructions=instructions_text)

async def generate_data_table_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [DataTable] 데이터 표 생성 큐에 등록...")
    return await client.artifacts.generate_data_table(nb_id, language="ko", instructions=instructions_text)

async def generate_mind_map_task(client, nb_id, instructions_text: str, topic: str = ""):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] [MindMap] 마인드맵 생성 큐에 등록...")
    # generate_mind_map은 추가 매개변수를 지원하지 않음
    return await client.artifacts.generate_mind_map(nb_id)

# 미디어 키 -> 함수 맵핑 딕셔너리
TASK_MAP = {
    "slide_deck": generate_slide_deck_task,
    "audio": generate_podcast_task,
    "video": generate_video_task,
    "infographic": generate_infographic_task,
    "report": generate_report_task,
    "study_guide": generate_study_guide_task,
    "quiz": generate_quiz_task,
    "flashcards": generate_flashcards_task,
    "data_table": generate_data_table_task,
    "mind_map": generate_mind_map_task
}


async def run_news_flow(topic: str, instructions: dict = None, search_type: str = "deep"):
    if instructions is None:
        instructions = {}
        
    def log(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] {msg}")

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # [수정] 한국어 키워드로 들어와도, 글로벌 영어 뉴스와 한국어 뉴스를 모두 깊게 탐색하도록 지시문(Prompt) 형태로 쿼리 변경
    query = f"Search for breaking news and major updates about '{topic}' published around {yesterday}. Please explicitly search across both English (global) and Korean news sources to gather comprehensive information."

    try:
        client = await get_notebooklm_client()
        async with client:
            # [수정됨] 매일 새 노트북의 이름이 "2026-02-28 - [AI Technology] Daily News"와 같이 날짜 최상단에 오도록 개선
            nb_title = f"{datetime.now().strftime('%Y-%m-%d')} - [{topic}] Daily News"
            log(f"클라이언트 연결 완료. '{nb_title}' 주제로 새로운 노트북 생성 중...")
            nb = await client.notebooks.create(nb_title)
            
            search_name = "패스트서치" if search_type == "fast" else "딥서치"
            
            # --- 1. Deep Research ---
            log(f"{search_name} 시작: '{query}'")
            start_result = await client.research.start(nb.id, query, "web", search_type)
            
            if not start_result:
                log(f"{search_name} 시작 실패!")
                return
                
            task_id = start_result["task_id"]
            
            status = None
            for i in range(120):
                status = await client.research.poll(nb.id)
                if status.get("status") == "completed":
                    break
                log(f"{search_name} 진행 중... ({i*5}s 경과)")
                await asyncio.sleep(5)
                
            sources = status.get("sources", [])
            log(f"{search_name} 완료! 수집된 소스 {len(sources)}개 임포트 중...")
            
            if sources:
                # 소스 50개 제한
                selected_sources = sources[:50]
                await client.research.import_sources(nb.id, task_id, selected_sources)
                log("임포트 예약 완료. 백그라운드 소스 분석 완료를 대기합니다 (최대 3분)...")
                
                # 완전한 처리를 위한 Polling 대기 로직 (에러 소스 발생 시 자동 청소)
                for _ in range(36):
                    await asyncio.sleep(5)
                    curr_sources = await client.sources.list(nb.id)
                    
                    processing = [s for s in curr_sources if s.is_processing]
                    ready = [s for s in curr_sources if s.is_ready]
                    error = [s for s in curr_sources if s.is_error]
                    
                    if not processing and len(curr_sources) > 0:
                        log(f"임포트/분석 대기 완료! (성공: {len(ready)}, 에러: {len(error)})")
                        break
                    
                    if _ % 3 == 0:
                        log(f"소스 분석 진행 중... (준비됨: {len(ready)}, 처리중: {len(processing)})")
                
                # 타임아웃 종료 후, 백엔드에서 읽지 못한 Failed(Error) 소스들 완전 삭제
                curr_sources = await client.sources.list(nb.id)
                error_sources = [s for s in curr_sources if s.is_error]
                for err_s in error_sources:
                    try:
                        await client.sources.delete(nb.id, err_s.id)
                    except Exception:
                        pass
                
                if error_sources:
                    log(f"분석에 실패한(Error) {len(error_sources)}개의 소스 목록에서 제거했습니다.")
                
                # 게이트 체크 1: 사용 가능한 소스가 있는지 엄격히 확인
                final_sources = await client.sources.list(nb.id)
                final_ready = [s for s in final_sources if s.is_ready]
                if not final_ready:
                    log(f"❌ 정상적으로 분석 완료된 소스가 없어 미디어 생성을 중단합니다.")
                    return
                log(f"✅ [Gate 1 통과] 총 {len(final_ready)}개의 정상 소스로 미디어 생성을 시작합니다.")

            else:
                log("수집된 뉴스가 없습니다.")
                return

            # --- 2. 미디어 동시 병렬 생성 (SlideDeck, Podcast, Infographic 등 전부 통합 지원) ---
            log(f"미디어 동시 생성 작업 시작 (커스텀 지시문 반영)...")
            
            tasks_to_run = []
            for media_key, info in instructions.items():
                if info.get("enabled", False) and media_key in TASK_MAP:
                    func = TASK_MAP[media_key]
                    tasks_to_run.append(func(client, nb.id, info.get("instruction", ""), topic))
            
            if tasks_to_run:
                statuses = await asyncio.gather(*tasks_to_run)
                log(f"{len(tasks_to_run)}개의 미디어 생성 작업 시작 요청이 완료되었습니다.")
                
                # Gate Check 2: Wait until all media are completely generated
                task_ids = []
                for s in statuses:
                    if hasattr(s, 'task_id'):
                        task_ids.append(s.task_id)
                    # For MindMap which returns a dict: {"note_id": ...} instead of GenerationStatus
                    elif isinstance(s, dict) and "note_id" in s:
                        # MindMap is immediately completed usually when it returns NoteID
                        pass
                
                if task_ids:
                    log(f"⏳ [Gate 2 대기] 전체 미디어(진행중 {len(task_ids)}개) 생성 완료를 기다립니다 (최대 30분)...")
                    for i in range(360): # 360 * 5s = 30 mins
                        await asyncio.sleep(5)
                        all_done = True
                        for t_id in task_ids:
                            poll_res = await client.artifacts.poll_status(nb.id, t_id)
                            if not poll_res.is_complete and not poll_res.is_failed:
                                all_done = False
                                break
                        if all_done:
                            log(f"✅ [Gate 2 통과] 모든 미디어 패키지 생성이 완료되었습니다!")
                            break
                        if i > 0 and i % 12 == 0:
                            log(f"미디어 배경 생성 진행 중... ({(i)*5}초 경과)")
                else:
                    log(f"즉시 완료된 미디어들 처리 완료.")
            else:
                log(f"활성화된 미디어 작업이 없어 건너뜁니다.")

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{topic}] 에러 발생: {e}")

async def main():
    parser = argparse.ArgumentParser(description="NotebookLM Deep Search & Media Automation")
    parser.add_argument("topic", type=str, nargs="?", default="AI Technology", help="검색할 주제")
    args = parser.parse_args()
    
    await run_news_flow(args.topic)

if __name__ == "__main__":
    asyncio.run(main())
