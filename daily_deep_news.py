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

import sys
import io

# Windows asyncio 버그 해결 (필수) 및 터미널 인코딩 에러 방지
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding='utf-8')
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding='utf-8')

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
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [SlideDeck] 네이티브 슬라이드 생성 큐에 등록...")
    return await client.artifacts.generate_slide_deck(
        nb_id, 
        language="ko", 
        instructions=instructions_text if instructions_text else "비즈니스 전문가를 위한 심층 보고서 형식으로 구체적인 데이터와 주요 인용구를 포함해 상세하게 작성해주세요."
    )

async def generate_podcast_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [Podcast] 오디오 오버뷰(팟캐스트) 생성 큐에 등록...")
    return await client.artifacts.generate_audio(
        nb_id, 
        language="ko", 
        instructions=instructions_text if instructions_text else "전문적이고 분석적인 뉴스 브리핑 톤으로 남녀가 교차 진행하며, 단순히 뉴스의 사실만 읽지 말고 산업에 미치는 파급력과 전망까지 깊게 토론(Deep Dive)해 주세요."
    )

async def generate_infographic_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [Infographic] 인포그래픽 생성 큐에 등록...")
    # Enum 파라미터는 생략하되, 프롬프트(instructions)는 전달하여 정상 생성되도록 수정
    return await client.artifacts.generate_infographic(nb_id, language="ko", instructions=instructions_text)

async def generate_video_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [Video] 비디오 개요 생성 큐에 등록...")
    return await client.artifacts.generate_video(nb_id, language="ko", instructions=instructions_text)
    
async def generate_report_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [Report] 보고서 생성 큐에 등록...")
    # generate_report는 instructions 대신 custom_prompt 매개변수를 사용
    return await client.artifacts.generate_report(nb_id, language="ko", custom_prompt=instructions_text)

async def generate_study_guide_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [StudyGuide] 스터디 가이드 생성 큐에 등록...")
    # generate_study_guide는 지시문 커스텀을 지원하지 않음
    return await client.artifacts.generate_study_guide(nb_id, language="ko")

async def generate_quiz_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [Quiz] 퀴즈 생성 큐에 등록...")
    # generate_quiz는 language 매개변수를 지원하지 않음
    return await client.artifacts.generate_quiz(nb_id, instructions=instructions_text)

async def generate_flashcards_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [Flashcards] 플래시카드 생성 큐에 등록...")
    # generate_flashcards는 language 매개변수를 지원하지 않음
    return await client.artifacts.generate_flashcards(nb_id, instructions=instructions_text)

async def generate_data_table_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [DataTable] 데이터 표 생성 큐에 등록...")
    return await client.artifacts.generate_data_table(nb_id, language="ko", instructions=instructions_text)

async def generate_mind_map_task(client, nb_id, instructions_text: str, topic: str = ""):
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] [MindMap] 마인드맵 생성 큐에 등록...")
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
        
    
    short_topic = topic.replace('\n', ' ').strip()
    if len(short_topic) > 30:
        short_topic = short_topic[:30] + "..."
        
    def log(msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] {msg}")

    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # [수정] 한국어 키워드로 들어와도, 글로벌 영어 뉴스와 한국어 뉴스를 모두 깊게 탐색하도록 지시문(Prompt) 형태로 쿼리 변경
    query = f"Search for breaking news and major updates about '{topic}' published around {yesterday}. Please explicitly search across both English (global) and Korean news sources to gather comprehensive information."

    try:
        client = await get_notebooklm_client()
        async with client:
            # [수정됨] 매일 새 노트북의 이름이 "2026-02-28 - [AI Technology] Daily News"와 같이 날짜 최상단에 오도록 개선
            nb_title = f"{datetime.now().strftime('%Y-%m-%d')} - [{short_topic}] Daily News"
            log(f"클라이언트 연결 완료. '{nb_title}' 주제로 새로운 노트북 생성 중...")
            nb = await client.notebooks.create(nb_title)
            
            search_name = "패스트서치" if search_type == "fast" else "딥서치"
            
            # --- 0. Clean up old sources (False Positive 방지) ---
            log(f"🔎 노트북 초기화: '{search_name}' 전 기존 소스(과거 데이터)를 비웁니다...")
            try:
                old_sources = await client.sources.list(nb.id)
                if old_sources:
                    for old_s in old_sources:
                        await client.sources.delete(nb.id, old_s.id)
                    log(f"🧹 기존에 존재하던 소스 {len(old_sources)}개를 삭제하여 노트북을 깨끗하게 비웠습니다.")
                else:
                    log("✨ 기존 소스가 없습니다. 깨끗한 상태입니다.")
            except Exception as e:
                log(f"⚠️ 기존 소스 삭제 중 에러 발생 (무시하고 진행): {e}")

            # --- 1. Deep Research ---
            log(f"{search_name} 시작: '{query}'")
            try:
                start_result = await client.research.start(nb.id, query, "web", search_type)
            except Exception as e:
                log(f"❌ {search_name} 호출 중 에러/타임아웃 발생: {e}")
                return
            
            if not start_result:
                log(f"❌ {search_name} 시작 실패! (응답 없음)")
                return
                
            task_id = start_result["task_id"]
            
            status = None
            for i in range(120):
                status = await client.research.poll(nb.id)
                if status.get("status") == "completed":
                    break
                if (i * 5) > 0 and (i * 5) % 60 == 0:
                    log(f"{search_name} 진행 중... ({i*5}s 경과)")
                await asyncio.sleep(5)
                
            sources = status.get("sources", [])
            log(f"{search_name} 완료! 수집된 소스 {len(sources)}개 임포트 중...")
            
            if sources:
                # 소스 50개 제한
                selected_sources = sources[:50]
                try:
                    await client.research.import_sources(nb.id, task_id, selected_sources)
                    log("임포트 예약 완료. 백그라운드 소스 분석 완료를 대기합니다 (최대 3분)...")
                except Exception as e:
                    if "timed out" in str(e).lower() or "timeout" in str(e).lower():
                        log("⚠️ 소스 임포트 RPC 시간 초과 (서버 백그라운드에서 임포트가 계속 진행될 수 있습니다. 대기 모드로 진입합니다.)")
                        # 타임아웃 발생 시 서버 지연을 고려해 30초 정도 먼저 대기해 줍니다. 그래야 sources.list()가 0개로 뜨지 않습니다.
                        await asyncio.sleep(30)
                    else:
                        log(f"⚠️ 소스 임포트 중 에러 발생: {e} (일부 소스가 임포트 중일 수 있으므로 대기 모드로 진입합니다.)")
                        await asyncio.sleep(15)
                
                # 완전한 처리를 위한 Polling 대기 로직 (에러 소스 발생 시 자동 청소)
                for _ in range(36):
                    await asyncio.sleep(5)
                    curr_sources = await client.sources.list(nb.id)
                    
                    processing = [s for s in curr_sources if s.is_processing]
                    ready = [s for s in curr_sources if s.is_ready]
                    error = [s for s in curr_sources if s.is_error]
                    
                    # 처리중인 게 없고, 소스가 화면에 하나라도 나타났다면 완료로 간주
                    if not processing and len(curr_sources) > 0:
                        log(f"임포트/분석 대기 완료! (성공: {len(ready)}, 에러: {len(error)})")
                        break
                    
                    # 만약 서버 지연으로 아직 1개도 목록에 안 보인다면 (is_processing 조차 아님), 그냥 더 기다려줍니다.
                    if len(curr_sources) == 0:
                        elapsed = (_ + 1) * 5
                        log(f"서버 응답 지연 중... 데이터 마이그레이션을 기다립니다 ({elapsed}s 경과)")
                        continue
                    
                    elapsed = (_ + 1) * 5
                    if elapsed % 60 == 0:
                        log(f"소스 분석 진행 중... ({elapsed}s 경과, 준비됨: {len(ready)}, 처리중: {len(processing)})")
                
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
            media_keys = []
            tasks_to_run = []
            for media_key, info in instructions.items():
                if info.get("enabled", False) and media_key in TASK_MAP:
                    func = TASK_MAP[media_key]
                    tasks_to_run.append(func(client, nb.id, info.get("instruction", ""), topic))
                    media_keys.append(media_key)
            
            if tasks_to_run:
                log(f"요청된 미디어 작업: {', '.join(media_keys)}")
                # return_exceptions=True prevents one failed API call (e.g. rate limit on Video) from aborting the others
                statuses = await asyncio.gather(*tasks_to_run, return_exceptions=True)
                
                # Gate Check 2: Wait until all media are completely generated
                task_id_to_media = {}
                completed_media = []
                for s, m_key in zip(statuses, media_keys):
                    if isinstance(s, Exception):
                        log(f"[{m_key}] 미디어 큐 등록 실패 (API 오류): {s}")
                    elif hasattr(s, 'task_id'):
                        task_id_to_media[s.task_id] = m_key
                    elif isinstance(s, dict) and "note_id" in s:
                        completed_media.append(m_key)
                        log(f"[{m_key}] 미디어 생성 즉시 완료!")
                
                if task_id_to_media:
                    pending_tasks = list(task_id_to_media.keys())
                    log(f"⏳ [Gate 2 대기] 백그라운드 생성 대기중 (최대 30분): {', '.join(task_id_to_media.values())}")
                    for i in range(360): # 360 * 5s = 30 mins
                        await asyncio.sleep(5)
                        
                        for t_id in list(pending_tasks):
                            poll_res = await client.artifacts.poll_status(nb.id, t_id)
                            if poll_res.is_complete or poll_res.is_failed:
                                m_key = task_id_to_media[t_id]
                                status_str = "완료" if poll_res.is_complete else "실패"
                                log(f"[{m_key}] 미디어 생성 {status_str}!")
                                if poll_res.is_complete:
                                    completed_media.append(m_key)
                                pending_tasks.remove(t_id)
                                
                        if not pending_tasks:
                            log(f"✅ [Gate 2 통과] 모든 미디어 패키지 처리가 종료되었습니다! (최종 성공: {', '.join(completed_media)})")
                            break
                            
                        elapsed = (i + 1) * 5
                        if elapsed % 60 == 0:
                            pending_names = [task_id_to_media[t] for t in pending_tasks]
                            log(f"미디어 생성 진행 중... ({elapsed}s 경과, 남은 작업: {', '.join(pending_names)})")
                else:
                    log(f"✅ [Gate 2 통과] 모든 미디어 패키지 생성이 완료되었습니다! (최종 성공: {', '.join(completed_media)})")
            else:
                log(f"활성화된 미디어 작업이 없어 건너뜁니다.")

    except Exception as e:
        short_topic = topic.replace('\n', ' ').strip()
        if len(short_topic) > 30:
            short_topic = short_topic[:30] + "..."
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{short_topic}] 에러 발생: {e}")

async def main():
    parser = argparse.ArgumentParser(description="NotebookLM Deep Search & Media Automation")
    parser.add_argument("topic", type=str, nargs="?", default="AI Technology", help="검색할 주제")
    args = parser.parse_args()
    
    await run_news_flow(args.topic)

if __name__ == "__main__":
    asyncio.run(main())
