import customtkinter as ctk
from tkinter import messagebox
import json
import os
import subprocess
from pathlib import Path
import threading
from datetime import datetime

ctk.set_appearance_mode("Dark")

# Color Palette (다크 & 네온 민트 모던 테마)
APP_BG = "#121212"    # 최상단 어두운 배경
PANEL_BG = "#1E1E1E"  # 콘텐츠 창 배경
TEXT_MAIN = "#FFFFFF" # 메인 텍스트 (흰색)
TEXT_SUB = "#A0A0A0"  # 서브 텍스트 (회색)
BORDER_COLOR = "#333333" # 세련된 라인 
ACCENT_MINT = "#1DF0A1" # 네온 민트 (메인 포인트)
ACCENT_HOVER = "#15CF89"
BTN_DARK = "#2C2C2E"    # 일반 다크 버튼
BTN_DARK_HOVER = "#3A3A3C"

# 폰트 세팅 (모던 산세리프)
FONT_FAMILY = "Malgun Gothic"
FONT_TITLE = (FONT_FAMILY, 26, "bold")
FONT_H1 = (FONT_FAMILY, 22, "bold")
FONT_H2 = (FONT_FAMILY, 16, "bold")
FONT_NORM = (FONT_FAMILY, 14)
FONT_BOLD = (FONT_FAMILY, 14, "bold")

CONFIG_FILE = Path(__file__).parent / "config.json"
RUN_SCRIPT = Path(__file__).parent / "run_all_news.py"
BAT_WRAPPER = Path(__file__).parent / "run_scheduled_news.bat"
LOGIN_HELPER = Path(__file__).parent / "gui_login_helper.py"
UV_EXE = str(Path.home() / ".local" / "bin" / "uv.exe")

MEDIA_INFO = {
    "slide_deck": {
        "title": "슬라이드 브리핑", 
        "opts": ["자세히", "보통", "요약"], 
        "prompts": {
            "자세히": "비즈니스 전문가를 위한 심층 보고서 형식으로 구체적인 데이터, 통계자료, 주요 인용구를 모두 포함해 상세하고 깊이 있는 슬라이드 덱을 작성해주세요.",
            "보통": "주요 핵심 내용과 흐름을 중심으로, 누구나 이해하기 쉽고 짜임새 있는 표준 길이의 슬라이드 덱을 구성해주세요.",
            "요약": "바쁜 경영진을 위해 핵심 결론, 요점, 시사점만 필터링하여 매우 짧고 간결한 슬라이드로 요약해주세요."
        }
    },
    "audio": {
        "title": "오디오 개요(팟캐스트)", 
        "opts": ["길게", "보통", "짧게"], 
        "prompts": {
            "길게": "전문적이고 분석적인 뉴스 브리핑 톤으로 남녀가 교차 진행하며, 단순 사실 전달을 넘어 산업에 미치는 파급력, 향후 전망, 다양한 시각까지 깊게 토론(Deep Dive)하는 긴 팟캐스트 스크립트를 작성해주세요.",
            "보통": "출퇴근길에 편하게 들을 수 있는 친근한 톤으로 주요 뉴스 이슈의 맥락과 핵심을 짚어주는 표준 길이의 오디오 스크립트를 작성해주세요.",
            "짧게": "가장 중요한 헤드라인과 결론만 1~2분 내로 핵심만 바짝 짚어주는 아주 텐션 높고 짧은 오디오 브리핑을 작성해주세요."
        }
    },
    "video": {
        "title": "비디오 개요", 
        "opts": ["길게", "보통", "짧게"], 
        "prompts": {
            "길게": "시각적 자료 설명과 함께 상세한 배경, 분석, 전문가 인터뷰 컨셉이 포함된 매우 상세하고 긴 비디오 스크립트 형태의 개요를 작성해주세요.",
            "보통": "유튜브 인포테인먼트 영상처럼 시각적으로 매력적이고 핵심 정보를 잘 전달할 수 있는 표준 길이의 비디오 스크립트를 작성해주세요.",
            "짧게": "숏폼(쇼츠/릴스)에 적합하게, 1분 이내로 핵심만 강렬하게 전달하는 빠른 호흡의 아주 짧은 비디오 텍스트 개요를 작성해주세요."
        }
    },
    "infographic": {
        "title": "핵심 인포그래픽", 
        "opts": ["상세히", "보통", "요약"], 
        "prompts": {
            "상세히": "오늘 뉴스의 중심이 되는 트렌드 변화, 세부 통계 지표, 관련 기업 동향, 향후 타임라인까지 모두 꼼꼼하게 분해하여 다채로운 인포그래픽 구조로 요약해주세요.",
            "보통": "주요 통계와 핵심 인사이트를 눈에 잘 띄게, 대중이 이해하기 쉬운 직관적인 구조의 기사 인포그래픽으로 작성해주세요.",
            "요약": "숫자로 보는 주요 팩트 3가지와 핵심 결론 1줄만 들어가는, 아주 심플하고 임팩트 있는 요약 인포그래픽을 만들어주세요."
        }
    },
    "report": {
        "title": "브리핑 분석 보고서", 
        "opts": ["상세히", "보통", "요약"], 
        "prompts": {
            "상세히": "서론, 본론(다각도 분석 및 데이터 증명), 결론 및 정책적/경제적 시사점까지 완벽히 갖춘 논문 혹은 리서치 센터 수준의 두꺼운 종합 분석 브리핑 문서를 작성해주세요.",
            "보통": "핵심 사항, 주요 배경, 향후 전망을 균형 있게 다룬 표준적인 실무진용 브리핑 보고서를 작성해주세요.",
            "요약": "딱 1페이지(One Pager) 분량으로 현황, 문제점, 결론 파트만 짧은 글머리 기호(Bullet Points)로 극강의 요약을 해주세요."
        }
    },
    "data_table": {
        "title": "데이터 분석 표", 
        "opts": ["상세히", "보통", "요약"], 
        "prompts": {
            "상세히": "기사에 등장하는 모든 수치, 연도별 추이, 기업별 실적 비교, 증감률 등 추출할 수 있는 모든 데이터를 찾아내어 매우 복잡하고 상세한 다차원 데이터 표(테이블)로 완벽 정리해주세요.",
            "보통": "독자가 주요 통계와 핵심 지표를 한눈에 비교할 수 있도록 핵심 항목 중심으로 깔끔한 데이터 표를 생성해주세요.",
            "요약": "가장 중요한 핵심 지표 2~3가지만 추려서 모바일에서도 보기 편한 심플한 미니 표 형태로 요약해주세요."
        }
    },
    "mind_map": {
        "title": "논리 마인드맵", 
        "opts": ["상세히", "보통", "핵심만"], 
        "prompts": {
            "상세히": "메인 테마부터 3~4단계 깊이의 하위 서브 토픽, 파생 효과, 관련 인물까지 모두 가지치기하여 거대한 마인드맵 텍스트 형태로 시각화해주세요.",
            "보통": "주요 뉴스 테마를 중심으로 서브 토픽, 핵심 내용들을 1~2단계로 연결한 표준 마인드맵 구조로 작성해주세요.",
            "핵심만": "중심 주제 아래에 핵심 키워드 3~5개만 방사형으로 뻗어 나가는 아주 직관적이고 심플한 마인드맵을 구성해주세요."
        }
    },
    "study_guide": {
        "title": "스터디 가이드", 
        "opts": ["심층", "보통", "핵심만"], 
        "prompts": {
            "심층": "이 주제를 전공하는 대학원생 수준으로, 고난이도 개념 증명, 상세한 배경사, 토론거리 및 심화 학습 가이드를 매우 디테일하게 구성해주세요.",
            "보통": "일반 학생이나 주니어가 뉴스의 맥락을 이해할 수 있도록 친절한 개념 설명, 용어 해설, 이해도 확인 가이드로 구성해주세요.",
            "핵심만": "시험 직전 암기노트처럼 벼락치기에 필요한 핵심 개념과 한 줄 요약, 필수 암기 용어만 극도로 요약한 가이드를 만들어주세요."
        }
    },
    "quiz": {
        "title": "지식 확인 퀴즈", 
        "opts": ["어렵게 (10개)", "보통 (5개)", "쉽게 (3개)"], 
        "prompts": {
            "어렵게 (10개)": "전문가 수준의 디테일을 묻는 고난이도 함정 문제와 구체적 수치를 묻는 퀴즈 10개를 내고, 오답 이유까지 상세하게 해설해주세요.",
            "보통 (5개)": "독자들이 주요 내용을 제대로 이해했는지 확인하기 좋은 난이도의 객관식/주관식 퀴즈 5개와 정답 해설을 구성해주세요.",
            "쉽게 (3개)": "글만 읽으면 누구나 맞출 수 있는 아주 기초적인 상식 수준의 쉬운 퀴즈 3개와 심플한 정답을 제시해주세요."
        }
    },
    "flashcards": {
        "title": "핵심 암기 플래시카드", 
        "opts": ["많이 (15개)", "보통 (10개)", "적게 (5개)"], 
        "prompts": {
            "많이 (15개)": "뉴스에 등장하는 모든 고유명사, 숫자, 기술 용어를 총망라하여 앞면(단어)-뒷면(상세설명) 구성의 암기용 플래시카드 15개 세트를 꽉 채워 작성해주세요.",
            "보통 (10개)": "뉴스에서 꼭 기억해야 할 주요 키워드와 개념 10개를 모아, 빠르게 복습할 수 있는 표준 암기용 플래시카드 세트를 작성해주세요.",
            "적게 (5개)": "이 뉴스를 읽고 절대 까먹으면 안 되는 초핵심 필수 키워드 딱 5개만 골라서 빠르고 강력한 플래시카드 세트를 만들어주세요."
        }
    }
}

DEFAULT_CONFIG = {
    "topics": ["AI Technology"],
    "schedule_time": "05:00",
    "media": {
        "slide_deck": {"enabled": True, "option": "보통", "instruction": MEDIA_INFO["slide_deck"]["prompts"]["보통"]},
        "audio": {"enabled": True, "option": "보통", "instruction": MEDIA_INFO["audio"]["prompts"]["보통"]},
        "infographic": {"enabled": True, "option": "상세히", "instruction": MEDIA_INFO["infographic"]["prompts"]["상세히"]}
    }
}

def parse_time_to_ampm(time_str):
    try:
        h, m = map(int, time_str.split(':'))
        ampm = "오후" if h >= 12 else "오전"
        disp_h = h % 12
        if disp_h == 0: disp_h = 12
        return ampm, str(disp_h), f"{m:02d}"
    except:
        return "오전", "5", "00"

def format_ampm_to_time(ampm, h_str, m_str):
    h = int(h_str)
    m = int(m_str)
    if ampm == "오후" and h != 12: h += 12
    if ampm == "오전" and h == 12: h = 0
    return f"{h:02d}:{m:02d}"

class NewsManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("NotebookLM 데일리 뉴스 매니저")
        # 1화면에 들어오도록 세로 좀 줄이고 가로를 대폭 넓힘 (좌/우 2열 배치)
        self.geometry("1450x880")
        self.configure(fg_color=APP_BG)
        
        # Grid 1x2 설정: 왼쪽은 고정 크기(기본 컨텐츠 크기 유지), 오른쪽만 확장됨
        self.grid_columnconfigure(0, weight=0, minsize=480) # Left Column (Fixed Width 약간 넓힘)
        self.grid_columnconfigure(1, weight=1)              # Right Column (Expandable)
        self.grid_rowconfigure(0, weight=1)
        
        self.config_data = self.load_config()
        self.media_widgets = {}   # 미디어별 동적 위젯 객체 저장용 { "slide": {"checkbox_var", "frame", "seg_btn", "textbox"} }
        
        self.create_left_panel()
        self.create_right_panel()
        
        self.populate_topics()
        self.refresh_media_panels()
        
    def load_config(self):
        conf = DEFAULT_CONFIG.copy()
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    conf["topics"] = data.get("topics", conf["topics"])
                    conf["schedule_time"] = data.get("schedule_time", conf["schedule_time"])
                    
                    # 마이그레이션 (과거 instructions -> 신규 media)
                    if "media" not in data:
                        conf["media"] = {}
                        old_inst = data.get("instructions", {})
                        for k in ["slide_deck", "audio", "infographic"]:
                            old_k = "slide" if k == "slide_deck" else k
                            if old_k in old_inst:
                                conf["media"][k] = {
                                    "enabled": True, 
                                    "option": MEDIA_INFO[k]["opts"][1], 
                                    "instruction": old_inst[k]
                                }
                    else:
                        conf["media"] = data["media"]
            except:
                pass
                
        # 신규 프롬프트 시스템용 마이그레이션 (기존에 수정한 적 없는 프롬프트면 새 버전으로 덮어쓰기)
        for k in conf["media"]:
            if k in MEDIA_INFO:
                opt = conf["media"][k].get("option", MEDIA_INFO[k]["opts"][1])
                curr_inst = conf["media"][k].get("instruction", "")
                
                # 만약 기존 저장된 프롬프트가 구버전의 default_inst와 똑같거나 비어있거나 테스트용 짧은 문구라면, 
                # 새로운 다이나믹 프롬프트로 강제 업데이트 해줍니다.
                legacy_defaults = [
                    "비즈니스 전문가를 위한 심층 보고서 형식으로 구체적인 데이터와 주요 인용구를 포함해 상세하게 작성해주세요.",
                    "전문적이고 분석적인 뉴스 브리핑 톤으로 남녀가 교차 진행하며, 단순히 뉴스의 사실만 읽지 말고 산업에 미치는 파급력과 전망까지 깊게 토론(Deep Dive)해 주세요.",
                    "시각적으로 매력적이고 핵심 정보를 잘 전달할 수 있는 비디오 스크립트 형태의 개요를 작성해주세요.",
                    "오늘 뉴스의 가장 핵심이 되는 트렌드 변화, 통계 지표, 그리고 관련 기업들의 동향을 한눈에 들어오는 구조로 꼼꼼하게 요약해주세요.",
                    "주요 핵심 사항과 함께 뉴스의 배경, 시사점을 포함한 종합적인 브리핑 문서를 작성해주세요.",
                    "뉴스 기사에 등장하는 주요 통계치, 기업 실적, 지표 등을 추출하여 한눈에 비교할 수 있는 데이터 표(테이블) 형태로 정리해주세요.",
                    "주요 뉴스 테마를 중심으로 서브 토픽, 파생 효과들을 가지치기하듯 연결한 마인드맵 텍스트 구조로 핵심 개념들을 시각적으로 맵핑해주세요.",
                    "이 내용을 처음 배우는 학생이나 실무자를 위한 친절한 설명, 용어 해설, 그리고 이해도를 확인하는 스터디 가이드를 만들어주세요.",
                    "이 뉴스 주제에 대해 독자들이 내용을 제대로 이해했는지 확인할 수 있는 핵심 퀴즈와 정답 해설을 구성해주세요.",
                    "뉴스에서 꼭 기억해야 할 주요 키워드와 개념들의 핵심만 모아서 빠르게 복습할 수 있는 암기용 플래시카드 세트를 작성해주세요.",
                    "테스트"
                ]
                
                if not curr_inst or curr_inst in legacy_defaults or len(curr_inst.strip()) < 10:
                    conf["media"][k]["instruction"] = MEDIA_INFO[k]["prompts"].get(opt, MEDIA_INFO[k]["prompts"][MEDIA_INFO[k]["opts"][1]])

        return conf

    def save_config(self):
        ampm = self.combo_ampm.get()
        hh = self.combo_h.get()
        mm = self.combo_m.get()
        self.config_data["schedule_time"] = format_ampm_to_time(ampm, hh, mm)
        self.config_data["search_type"] = self.search_type_var.get()
        
        new_media = {}
        # 미디어 설정 저장
        for key, widgets in self.media_widgets.items():
            is_enabled = widgets["checkbox_var"].get()
            
            # 체크되어 위젯이 화면에 있을 때만 값을 읽고, 아닐 경우 기존 config 값을 유지하거나 기본값 사용
            if is_enabled and widgets["textbox"] is not None and widgets["textbox"].winfo_exists() and widgets["seg_btn"] is not None and widgets["seg_btn"].winfo_exists():
                selected_opt = widgets["seg_btn"].get() if widgets["seg_btn"].get() else MEDIA_INFO[key]["opts"][1]
                instruction = widgets["textbox"].get("0.0", "end").strip()
            else:
                conf_media = self.config_data.get("media", {}).get(key, {})
                selected_opt = conf_media.get("option", MEDIA_INFO[key]["opts"][1])
                default_prompt = MEDIA_INFO[key]["prompts"].get(selected_opt, MEDIA_INFO[key]["prompts"][MEDIA_INFO[key]["opts"][1]])
                instruction = conf_media.get("instruction", default_prompt)
            
            new_media[key] = {
                "enabled": is_enabled,
                "option": selected_opt,
                "instruction": instruction
            }
            
        self.config_data["media"] = new_media
            
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.config_data, f, ensure_ascii=False, indent=4)
            
    def run_login(self):
        self.btn_login.configure(state="disabled", text="⏳ 팝업 구동 중...")
        def _login_thread():
            try:
                cmd = [UV_EXE, "run", str(LOGIN_HELPER)]
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                result = subprocess.run(cmd, text=True, capture_output=True, startupinfo=startupinfo)
                if result.returncode == 0:
                    messagebox.showinfo("로그인 완료", "구글 계정 연동(토큰 갱신)이 성공적으로 완료되었습니다!")
                    self.btn_login.configure(state="normal", text="🔗 계정 연동 완료", text_color=ACCENT_MINT, border_color=ACCENT_MINT)
                else:
                    messagebox.showerror("로그인 실패", f"로그인 창이 닫혔거나 에러가 발생했습니다.\n{result.stderr}")
                    self.btn_login.configure(state="normal", text="❌ 계정 미연동 (클릭)", text_color="#FF4C4C", border_color="#FF4C4C")
            except Exception as e:
                messagebox.showerror("실행 에러", f"로그인 헬퍼 실행 중 에러가 발생했습니다: {e}")
                self.btn_login.configure(state="normal", text="❌ 계정 미연동 (클릭)", text_color="#FF4C4C", border_color="#FF4C4C")
        threading.Thread(target=_login_thread, daemon=True).start()

    # 좌측 패널: 타이틀, 로그인, 주제목록, 스케줄러, 저장
    def create_left_panel(self):
        pad_x = 15
        
        self.left_scroll = ctk.CTkFrame(self, fg_color=APP_BG)
        self.left_scroll.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        lbl_title = ctk.CTkLabel(self.left_scroll, text="NotebookLM News Manager", 
                                 font=FONT_TITLE, text_color=TEXT_MAIN)
        lbl_title.pack(pady=(15, 10), padx=pad_x, anchor="w")
        
        # 0. 계정 로그인 구역 및 검색 속도 구역 (나란히 배치)
        top_ctrl_frame = ctk.CTkFrame(self.left_scroll, corner_radius=15, fg_color=PANEL_BG)
        top_ctrl_frame.pack(fill="x", padx=pad_x, pady=8)
        
        # 계정 연동 상태 확인 로직
        storage_path = Path.home() / ".notebooklm" / "storage_state.json"
        is_logged_in = storage_path.exists()
        login_text = "🔗 계정 연동 완료" if is_logged_in else "❌ 계정 미연동 (클릭)"
        login_color = ACCENT_MINT if is_logged_in else "#FF4C4C"
        
        self.btn_login = ctk.CTkButton(top_ctrl_frame, text=login_text, height=36, 
                                       font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                                       fg_color="transparent", text_color=login_color, hover_color=BTN_DARK_HOVER,
                                       border_width=1, border_color=login_color, corner_radius=8, command=self.run_login)
        self.btn_login.pack(side="left", padx=(15, 5), pady=15, expand=True, fill="x")

        self.search_type_var = ctk.StringVar(value=self.config_data.get("search_type", "deep"))
        search_seg = ctk.CTkSegmentedButton(top_ctrl_frame, values=["fast", "deep"], variable=self.search_type_var, font=FONT_NORM, selected_color=ACCENT_MINT, selected_hover_color=ACCENT_HOVER, unselected_color=BTN_DARK, unselected_hover_color=BTN_DARK_HOVER, text_color=TEXT_MAIN, corner_radius=8, height=36, width=110)
        search_seg.pack(side="right", padx=(0, 15), pady=15)

        # 1. 주제(Topic) 구역
        topic_frame = ctk.CTkFrame(self.left_scroll, corner_radius=15, fg_color=PANEL_BG)
        topic_frame.pack(fill="x", padx=pad_x, pady=8)
        
        hdr_frame = ctk.CTkFrame(topic_frame, fg_color="transparent")
        hdr_frame.pack(fill="x", padx=15, pady=(15, 0))
        
        ctk.CTkLabel(hdr_frame, text="📌 수집할 뉴스 주제", font=FONT_H2, text_color=TEXT_MAIN).pack(side="left")
        ctk.CTkLabel(hdr_frame, text="※ 자동 번역 검색", font=FONT_BOLD, text_color=TEXT_SUB).pack(side="right")
        
        input_frame = ctk.CTkFrame(topic_frame, fg_color="transparent")
        input_frame.pack(fill="x", padx=15, pady=5)
        self.topic_entry = ctk.CTkTextbox(input_frame, height=80, wrap="word", font=FONT_NORM, fg_color=BTN_DARK, border_width=1, border_color=BORDER_COLOR, text_color=TEXT_MAIN, corner_radius=8)
        self.topic_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        # Insert placeholder manually (CTkTextbox has no placeholder_text natively without binding tricks, but we just leave it blank)
        
        btn_wrapper = ctk.CTkFrame(input_frame, fg_color="transparent")
        btn_wrapper.pack(side="left", fill="y")
        ctk.CTkButton(btn_wrapper, text="✚ 추가", width=70, height=80, font=FONT_BOLD, text_color=APP_BG, fg_color=ACCENT_MINT, hover_color=ACCENT_HOVER, corner_radius=8, command=self.add_topic).pack(side="top", expand=True)
        
        self.scroll_topics = ctk.CTkScrollableFrame(topic_frame, height=130, fg_color=APP_BG, corner_radius=10, scrollbar_button_color=BORDER_COLOR)
        self.scroll_topics.pack(fill="x", padx=15, pady=(10, 15))

        # (단독 리서치 강도 프레임은 삭제됨)

        # 2. 스케줄러 등록 구역
        sched_frame = ctk.CTkFrame(self.left_scroll, corner_radius=15, fg_color=PANEL_BG)
        sched_frame.pack(fill="x", padx=pad_x, pady=8)
        
        ctk.CTkLabel(sched_frame, text="⏰ 일일 스케줄 실행 시간", font=FONT_H2, text_color=TEXT_MAIN).pack(anchor="w", padx=15, pady=(15, 5))
        
        cb_frame = ctk.CTkFrame(sched_frame, fg_color="transparent")
        cb_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ampm_val, h_val, m_val = parse_time_to_ampm(self.config_data.get("schedule_time", "05:00"))
        
        combo_font = ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold")
        self.combo_ampm = ctk.CTkComboBox(cb_frame, values=["오전", "오후"], width=80, height=36, font=combo_font, dropdown_font=FONT_NORM, fg_color=BTN_DARK, text_color=TEXT_MAIN, border_color=BORDER_COLOR, button_color=BORDER_COLOR, button_hover_color=BTN_DARK_HOVER, corner_radius=8)
        self.combo_ampm.set(ampm_val)
        self.combo_ampm.pack(side="left", padx=(0, 5))
        
        self.combo_h = ctk.CTkComboBox(cb_frame, values=[str(i) for i in range(1, 13)], width=70, height=36, font=combo_font, dropdown_font=FONT_NORM, fg_color=BTN_DARK, text_color=TEXT_MAIN, border_color=BORDER_COLOR, button_color=BORDER_COLOR, button_hover_color=BTN_DARK_HOVER, corner_radius=8)
        self.combo_h.set(h_val)
        self.combo_h.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(cb_frame, text="시", font=combo_font, text_color=TEXT_MAIN).pack(side="left", padx=(0, 10))
        
        min_opts = [f"{i:02d}" for i in range(0, 60, 10)]
        self.combo_m = ctk.CTkComboBox(cb_frame, values=min_opts, width=70, height=36, font=combo_font, dropdown_font=FONT_NORM, fg_color=BTN_DARK, text_color=TEXT_MAIN, border_color=BORDER_COLOR, button_color=BORDER_COLOR, button_hover_color=BTN_DARK_HOVER, corner_radius=8)
        self.combo_m.set(m_val)
        self.combo_m.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(cb_frame, text="분", font=combo_font, text_color=TEXT_MAIN).pack(side="left")

        # 3. 저장 및 윈도우 스케줄러 등록 액션
        save_frame = ctk.CTkFrame(self.left_scroll, fg_color="transparent")
        save_frame.pack(fill="x", padx=pad_x, pady=(10, 5))
        
        ctk.CTkLabel(save_frame, text="※ 스케줄 실행을 위해선 지정된 시간에 PC가 켜져 있어야 합니다", font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"), text_color=TEXT_SUB).pack(anchor="w", pady=(0, 5), padx=5)
        
        save_btn = ctk.CTkButton(save_frame, text="✅ 모든 설정 및 스케줄 저장하기", height=45, font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"), text_color=TEXT_MAIN, fg_color=BTN_DARK, hover_color=BTN_DARK_HOVER, border_width=1, border_color=BORDER_COLOR, corner_radius=10, command=self.save_and_schedule)
        save_btn.pack(fill="x", pady=(0, 10))
        
        run_now_btn = ctk.CTkButton(save_frame, text="▶ 지금 바로 뉴스 생성", height=50, font=ctk.CTkFont(family=FONT_FAMILY, size=16, weight="bold"), text_color="#121212", fg_color=ACCENT_MINT, hover_color=ACCENT_HOVER, corner_radius=12, command=self.run_now)
        run_now_btn.pack(fill="x", pady=(0, 20)) # 추가 하단 패딩 확보

    # 우측 패널: 전체 미디어 체크박스 및 동적 프롬프트 설정창
    def create_right_panel(self):
        self.right_scroll = ctk.CTkScrollableFrame(self, fg_color=APP_BG, scrollbar_button_color=BORDER_COLOR)
        self.right_scroll.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        hdr_frame = ctk.CTkFrame(self.right_scroll, fg_color="transparent")
        hdr_frame.pack(fill="x", padx=20, pady=(25, 20))
        
        ctk.CTkLabel(hdr_frame, text="⚙️ 생성할 미디어 종류 및 상세 설정", font=FONT_H1, text_color=TEXT_MAIN).pack(side="left")
        
        btn_frame = ctk.CTkFrame(hdr_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(btn_frame, text="전체 선택", width=80, height=30, font=FONT_BOLD, text_color=APP_BG, fg_color=ACCENT_MINT, hover_color=ACCENT_HOVER, corner_radius=6, command=self.select_all_media).pack(side="left", padx=(0, 5))
        ctk.CTkButton(btn_frame, text="전체 해제", width=80, height=30, font=FONT_BOLD, text_color=TEXT_MAIN, fg_color=BTN_DARK, hover_color=BTN_DARK_HOVER, corner_radius=6, command=self.deselect_all_media).pack(side="left")
        
        # 체크박스들을 담을 최상단 박스
        chk_box_frame = ctk.CTkFrame(self.right_scroll, corner_radius=15, fg_color=PANEL_BG)
        chk_box_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Grid layout for checkboxes
        chk_grid = ctk.CTkFrame(chk_box_frame, fg_color="transparent")
        chk_grid.pack(padx=20, pady=20, fill="x")
        
        # 체크박스 변수 및 상태 저장 구조 초기화
        for i, (key, info) in enumerate(MEDIA_INFO.items()):
            # 기존 config 에 있으면 그 상태, 없으면 기본 off
            conf_media = self.config_data.get("media", {}).get(key, {})
            is_enabled = conf_media.get("enabled", False)
            if key in ["slide_deck", "audio", "infographic"] and "media" not in self.config_data:
                # 초기 버전 호환성
                is_enabled = True
                    
            var = ctk.BooleanVar(value=is_enabled)
            
            # 체크박스 토글 시 하단 프롬프트 패널 리프레시 호출
            chk = ctk.CTkCheckBox(chk_grid, text=info["title"], variable=var, font=FONT_BOLD, text_color=TEXT_MAIN, fg_color=ACCENT_MINT, hover_color=ACCENT_HOVER, border_color=BORDER_COLOR, checkmark_color="#121212", corner_radius=6, command=self.refresh_media_panels)
            # 10개 항목이므로 2열 배치: 0,1,2,3,4 줄에 2칸씩
            row = i // 2
            col = i % 2
            chk.grid(row=row, column=col, sticky="w", padx=15, pady=8)
            
            # 딕셔너리에 예약
            self.media_widgets[key] = {
                "checkbox_var": var,
                "frame": None,
                "seg_btn": None,
                "textbox": None
            }
            
        # 프롬프트 동적 렌더링 컨테이너
        self.dynamic_panels_container = ctk.CTkFrame(self.right_scroll, fg_color="transparent")
        self.dynamic_panels_container.pack(fill="both", expand=True, padx=20, pady=5)
        self.dynamic_panels_container.grid_columnconfigure(0, weight=1, uniform="col")
        self.dynamic_panels_container.grid_columnconfigure(1, weight=1, uniform="col")
        
    def select_all_media(self):
        for key in MEDIA_INFO.keys():
            self.media_widgets[key]["checkbox_var"].set(True)
        self.refresh_media_panels()
        
    def deselect_all_media(self):
        for key in MEDIA_INFO.keys():
            self.media_widgets[key]["checkbox_var"].set(False)
        self.refresh_media_panels()

    def refresh_media_panels(self):
        # 1. 모든 동적 패널 제거
        for widget in self.dynamic_panels_container.winfo_children():
            widget.destroy()
            
        # 2. 체크된 항목들만 패널 생성
        active_idx = 0
        for key, info in MEDIA_INFO.items():
            widgets = self.media_widgets[key]
            if widgets["checkbox_var"].get():
                panel = ctk.CTkFrame(self.dynamic_panels_container, corner_radius=15, fg_color=PANEL_BG)
                row = active_idx // 2
                col = active_idx % 2
                panel.grid(row=row, column=col, sticky="nsew", padx=10, pady=10)
                active_idx += 1
                
                widgets["frame"] = panel
                
                # 상단 헤더 (제목 + 세그먼트 버튼)
                hdr = ctk.CTkFrame(panel, fg_color="transparent")
                hdr.pack(fill="x", padx=20, pady=(20, 10))
                
                ctk.CTkLabel(hdr, text=info["title"], font=FONT_H2, text_color=TEXT_MAIN).pack(side="left")
                
                # 세그먼트 버튼 (짧게/보통/자세히 등)
                conf_media = self.config_data.get("media", {}).get(key, {})
                selected_opt = conf_media.get("option", info["opts"][1])
                
                def on_seg_change(new_val, target_key=key, target_txt=None):
                    if target_txt:
                        new_prompt = MEDIA_INFO[target_key]["prompts"].get(new_val, "")
                        target_txt.delete("0.0", "end")
                        target_txt.insert("0.0", new_prompt)

                seg = ctk.CTkSegmentedButton(hdr, values=info["opts"], font=FONT_NORM, 
                                             selected_color=ACCENT_MINT, selected_hover_color=ACCENT_HOVER, 
                                             unselected_color=BTN_DARK, unselected_hover_color=BTN_DARK_HOVER, 
                                             text_color=TEXT_MAIN, corner_radius=8)
                seg.pack(side="right")
                seg.set(selected_opt)
                widgets["seg_btn"] = seg
                
                # Custom Instruction 텍스트 상자
                default_prompt_for_opt = info["prompts"].get(selected_opt, info["prompts"][info["opts"][1]])
                inst_text = conf_media.get("instruction", default_prompt_for_opt)
                
                txt = ctk.CTkTextbox(panel, height=70, wrap="word", font=FONT_NORM, text_color=TEXT_MAIN, fg_color=BTN_DARK, border_width=1, border_color=BORDER_COLOR, corner_radius=8)
                txt.pack(fill="x", padx=20, pady=(0, 20))
                txt.insert("0.0", inst_text)
                widgets["textbox"] = txt
                
                # 콜백 바인딩: 세그먼트 버튼 클릭 시 텍스트 박스 내용 자동 변경
                seg.configure(command=lambda val, k=key, box=txt: on_seg_change(val, k, box))

    def populate_topics(self):
        for widget in self.scroll_topics.winfo_children():
            widget.destroy()
        topics = self.config_data.get("topics", [])
        for t in topics:
            row_frame = ctk.CTkFrame(self.scroll_topics, fg_color="transparent")
            row_frame.pack(fill="x", pady=4)
            
            # 우측 심플한 삭제 버튼 (위아래 여백을 줘서 높이를 줄임)
            btn_del = ctk.CTkButton(row_frame, text="×", width=36, height=36, font=ctk.CTkFont(family=FONT_FAMILY, size=20, weight="bold"), text_color=TEXT_SUB, fg_color="transparent", hover_color=BTN_DARK_HOVER, corner_radius=6, command=lambda top=t: self.delete_topic(top))
            btn_del.pack(side="right", padx=(5, 5))
            
            # 읽기 전용 텍스트박스 대신 버튼으로 만들어 클릭 시 모달창(팝업) 표시
            preview_text = t.replace('\n', ' ').strip()
            if len(preview_text) > 40:
                preview_text = preview_text[:40] + "..."
                
            btn_view = ctk.CTkButton(row_frame, text=preview_text, height=36, font=FONT_NORM, text_color=TEXT_MAIN, fg_color=PANEL_BG, hover_color=BTN_DARK_HOVER, border_width=1, border_color=BORDER_COLOR, corner_radius=6, anchor="w", command=lambda top=t: self.show_topic_modal(top))
            btn_view.pack(side="left", fill="x", expand=True, padx=(5, 5))

    def show_topic_modal(self, topic_text):
        modal = ctk.CTkToplevel(self)
        modal.title("주제 전체 보기")
        modal.geometry("500x400")
        modal.configure(fg_color=APP_BG)
        modal.attributes("-topmost", True)
        modal.grid_columnconfigure(0, weight=1)
        modal.grid_rowconfigure(0, weight=1)
        
        txt = ctk.CTkTextbox(modal, wrap="word", font=FONT_NORM, text_color=TEXT_MAIN, fg_color=PANEL_BG, border_width=1, border_color=BORDER_COLOR, corner_radius=8)
        txt.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        txt.insert("0.0", topic_text)
        txt.configure(state="disabled")
        
        btn_close = ctk.CTkButton(modal, text="닫기", width=120, height=40, font=FONT_BOLD, text_color=TEXT_MAIN, fg_color=BTN_DARK, hover_color=BTN_DARK_HOVER, corner_radius=8, command=modal.destroy)
        btn_close.grid(row=1, column=0, pady=(0, 20))
            
    def add_topic(self):
        new_topic = self.topic_entry.get("0.0", "end").strip()
        if new_topic and new_topic not in self.config_data.get("topics", []):
            if "topics" not in self.config_data:
                self.config_data["topics"] = []
            self.config_data["topics"].append(new_topic)
            self.topic_entry.delete("0.0", "end")
            self.populate_topics()
            
    def delete_topic(self, topic):
        if topic in self.config_data.get("topics", []):
            self.config_data["topics"].remove(topic)
            self.populate_topics()
            
    def create_bat_wrapper(self):
        wrapper_content = f'''@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
cd /d "{Path(__file__).parent}"
if not exist logs mkdir logs
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set logdate=%datetime:~0,4%%datetime:~4,2%%datetime:~6,2%
echo ================================================== >> "logs\\daily_news_%logdate%.log"
echo [ %datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2% %datetime:~8,2%:%datetime:~10,2%:%datetime:~12,2% ] 스케줄 작업 시작 >> "logs\\daily_news_%logdate%.log"
"{UV_EXE}" run "{RUN_SCRIPT}" >> "logs\\daily_news_%logdate%.log" 2>&1
'''
        with open(BAT_WRAPPER, "w", encoding="utf-8") as f:
            f.write(wrapper_content)
            
    def save_and_schedule(self):
        self.save_config()
        self.create_bat_wrapper()
        
        time_str = self.config_data["schedule_time"]
        task_name = "NotebookLMDailyNews"
        bat_path = str(BAT_WRAPPER)
        
        try:
            # 설정 저장 알림을 먼저 보여줌
            active_media = [MEDIA_INFO[k]["title"] for k, v in self.config_data.get("media", {}).items() if v.get("enabled", False)]
            summary_msg = f"✅ 설정 저장 완료!\n\n📌 수집 주제: {', '.join(self.config_data.get('topics', []))}\n⏰ 예약 시간: {time_str}\n🗂 선택된 미디어: {', '.join(active_media)}"
            messagebox.showinfo("저장 완료", summary_msg)
            
            subprocess.run(["schtasks", "/Delete", "/TN", task_name, "/F"], capture_output=True)
            cmd = ["schtasks", "/Create", "/SC", "DAILY", "/TN", task_name, "/TR", bat_path, "/ST", time_str, "/F"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                pass # Already showed success message above
            else:
                messagebox.showerror("오류", f"스케줄러 등록 실패:\n{result.stderr}\n{result.stdout}")
        except Exception as e:
            messagebox.showerror("에러", f"관리자 권한 등의 오류가 발생했습니다.\n{str(e)}")

    def run_now(self):
        self.save_config()
        
        # 1. 라이브 로그를 보여줄 모달 콘솔 창(Toplevel) 생성
        console_win = ctk.CTkToplevel(self)
        console_win.title("진행 상황 로그")
        console_win.geometry("850x550")
        console_win.configure(fg_color=APP_BG)
        console_win.transient(self) # 메인 윈도우 위에 표시
        console_win.grab_set()      # 모달 창 역할 (다른 창 클릭 방지)
        
        # 상단 타이틀
        ctk.CTkLabel(console_win, text="🚀 뉴스 수집 및 미디어 생성 진행 중...", font=FONT_H1, text_color=ACCENT_MINT).pack(pady=(20, 10))
        
        # 로그를 실시간으로 출력할 텍스트박스 (해커 콘솔 감성)
        log_box = ctk.CTkTextbox(console_win, wrap="word", font=("Consolas", 14), fg_color="#0A0A0A", text_color="#1DF0A1", border_width=1, border_color=BORDER_COLOR, corner_radius=10)
        log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # 프로세스 제어를 위한 핸들 저장용 리스트
        process_handle = [None]
        
        # 스레드 접근이 가능하도록 메인 UI루프에 작업 추가 (thread-safe append)
        def safe_append(msg):
            log_box.insert("end", msg + "\n")
            log_box.see("end")

        def _run_thread():
            try:
                # 로그 폴더 생성 및 날짜 포맷
                log_dir = Path(__file__).parent / "logs"
                log_dir.mkdir(exist_ok=True)
                log_date = datetime.now().strftime("%Y%m%d")
                log_file = log_dir / f"daily_news_{log_date}.log"
                
                cmd = [UV_EXE, "run", str(RUN_SCRIPT)]
                startupinfo = None
                if os.name == 'nt':
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"\n==================================================\n")
                    f.write(f"[ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] 즉시 실행 작업 시작\n")
                    
                    console_win.after(0, safe_append, "[System] 스크립트 실행을 시작합니다. (출력에 약간의 지연이 있을 수 있습니다.)")
                    console_win.after(0, safe_append, "==================================================")
                    
                    # 환경 변수를 설정하여 파이썬의 표준 출력 버퍼링을 강제로 해제합니다.
                    env = os.environ.copy()
                    env["PYTHONUNBUFFERED"] = "1"
                    env["PYTHONIOENCODING"] = "utf-8"  # 파이썬 자체 출력도 utf-8로 강제
                    
                    # Popen을 사용해 실시간 stdout 라인 읽기 (에러 무시/대체 옵션 적용)
                    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, startupinfo=startupinfo, encoding='utf-8', errors='replace', bufsize=1, env=env)
                    process_handle[0] = process
                    
                    # 미디어 처리 결과를 저장할 변수들
                    media_success = []
                    media_errors = []
                    
                    # 라인 단위로 뽑아서 출력
                    for line in iter(process.stdout.readline, ''):
                        if not line: break
                        stripped_line = line.rstrip()
                        f.write(stripped_line + "\n")
                        f.flush()
                        
                        # 이슈 파싱 (성공/오류 요약용)
                        if "미디어 생성 완료!" in stripped_line or "미디어 생성 즉시 완료!" in stripped_line:
                            try:
                                # 예: [12:34:56] [Short Topic] [audio] 미디어 생성 완료!
                                media_type = stripped_line.split("] [")[-1].split("]")[0]
                                if media_type not in media_success:
                                    media_success.append(media_type)
                            except: pass
                            
                        elif "에러 발생:" in stripped_line or "미디어 생성 실패!" in stripped_line:
                            try:
                                err_msg = stripped_line.split("] ")[-1]
                                media_errors.append(err_msg)
                            except: pass
                        
                        # UI 쓰레드를 통해 텍스트 박스에 업데이트
                        console_win.after(0, safe_append, stripped_line)
                    
                    process.wait()
                    
                    # 실행 완료 후 요약 모달을 띄우는 함수
                    def show_completion_modal():
                        # 기존 창들 닫기 (메인 윈도우는 숨기고, 로그창은 파괴)
                        self.withdraw()
                        console_win.destroy()
                        
                        summary_win = ctk.CTkToplevel()
                        summary_win.title("작업 완료")
                        summary_win.geometry("500x400")
                        summary_win.configure(fg_color=APP_BG)
                        
                        # 화면 중앙 배치
                        summary_win.update_idletasks()
                        x = (summary_win.winfo_screenwidth() // 2) - (500 // 2)
                        y = (summary_win.winfo_screenheight() // 2) - (400 // 2)
                        summary_win.geometry(f"+{x}+{y}")
                        
                        if process.returncode == 0 and not media_errors:
                            title_text = "✨ 모든 작업이 성공적으로 완료되었습니다!"
                            title_color = ACCENT_MINT
                        else:
                            title_text = f"⚠️ 작업 종료 (오류 {len(media_errors)}건 발생)"
                            title_color = "#FF6B6B"
                            
                        ctk.CTkLabel(summary_win, text=title_text, font=FONT_H1, text_color=title_color).pack(pady=20)
                        
                        # 결과 내용 프레임
                        content_frame = ctk.CTkFrame(summary_win, fg_color=PANEL_BG)
                        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
                        
                        success_str = ", ".join(media_success) if media_success else "없음"
                        ctk.CTkLabel(content_frame, text="[성공한 미디어]", font=FONT_H2, text_color=TEXT_PRIMARY).pack(anchor="w", padx=20, pady=(20, 5))
                        ctk.CTkLabel(content_frame, text=success_str, font=FONT_BODY, text_color=TEXT_SECONDARY).pack(anchor="w", padx=20, pady=0)
                        
                        if media_errors:
                            ctk.CTkLabel(content_frame, text="[발생한 오류]", font=FONT_H2, text_color="#FF6B6B").pack(anchor="w", padx=20, pady=(15, 5))
                            err_textbox = ctk.CTkTextbox(content_frame, height=80, fg_color="#1A1A1A", text_color="#FFBDBD")
                            err_textbox.pack(fill="x", padx=20, pady=(0, 10))
                            for e in media_errors[:5]: # 최대 5개까지만 표시
                                err_textbox.insert("end", f"- {e}\n")
                            err_textbox.configure(state="disabled")
                            
                        # 닫기 버튼 (프로그램 전체 종료)
                        def on_final_close():
                            summary_win.destroy()
                            self.quit()
                            
                        ctk.CTkButton(summary_win, text="확인 및 프로그램 종료", font=FONT_BODY, fg_color=ACCENT_MINT, text_color=APP_BG, command=on_final_close).pack(pady=20)
                        summary_win.protocol("WM_DELETE_WINDOW", on_final_close)

                    console_win.after(1000, show_completion_modal) # 1초 뒤 알림 모달 출력         
                        
            except Exception as e:
                console_win.after(0, safe_append, f"[치명적 오류]: {e}")

        # 콘솔 팝업 x버튼 클릭 시 처리 (강제 종료 경고)
        def on_close():
            if process_handle[0] and process_handle[0].poll() is None:
                if messagebox.askyesno("강제 종료 확인", "아직 작업이 진행 중입니다. 프로세스를 강제로 종료하시겠습니까?", parent=console_win):
                    process_handle[0].terminate()
                    console_win.destroy()
            else:
                console_win.destroy()
                
        console_win.protocol("WM_DELETE_WINDOW", on_close)

        # 백그라운드 워커 스레드 시작
        threading.Thread(target=_run_thread, daemon=True).start()

if __name__ == "__main__":
    app = NewsManagerApp()
    app.mainloop()
