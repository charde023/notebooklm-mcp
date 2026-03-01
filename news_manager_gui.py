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
    "slide_deck": {"title": "슬라이드 브리핑", "opts": ["자세히", "보통", "요약"], "default_inst": "비즈니스 전문가를 위한 심층 보고서 형식으로 구체적인 데이터와 주요 인용구를 포함해 상세하게 작성해주세요."},
    "audio": {"title": "오디오 개요(팟캐스트)", "opts": ["길게", "보통", "짧게"], "default_inst": "전문적이고 분석적인 뉴스 브리핑 톤으로 남녀가 교차 진행하며, 단순히 뉴스의 사실만 읽지 말고 산업에 미치는 파급력과 전망까지 깊게 토론(Deep Dive)해 주세요."},
    "video": {"title": "비디오 개요", "opts": ["길게", "보통", "짧게"], "default_inst": "시각적으로 매력적이고 핵심 정보를 잘 전달할 수 있는 비디오 스크립트 형태의 개요를 작성해주세요."},
    "infographic": {"title": "핵심 인포그래픽", "opts": ["상세히", "보통", "요약"], "default_inst": "오늘 뉴스의 가장 핵심이 되는 트렌드 변화, 통계 지표, 그리고 관련 기업들의 동향을 한눈에 들어오는 구조로 꼼꼼하게 요약해주세요."},
    "report": {"title": "브리핑 분석 보고서", "opts": ["상세히", "보통", "요약"], "default_inst": "주요 핵심 사항과 함께 뉴스의 배경, 시사점을 포함한 종합적인 브리핑 문서를 작성해주세요."},
    "data_table": {"title": "데이터 분석 표", "opts": ["상세히", "보통", "요약"], "default_inst": "뉴스 기사에 등장하는 주요 통계치, 기업 실적, 지표 등을 추출하여 한눈에 비교할 수 있는 데이터 표(테이블) 형태로 정리해주세요."},
    "mind_map": {"title": "논리 마인드맵", "opts": ["상세히", "보통", "핵심만"], "default_inst": "주요 뉴스 테마를 중심으로 서브 토픽, 파생 효과들을 가지치기하듯 연결한 마인드맵 텍스트 구조로 핵심 개념들을 시각적으로 맵핑해주세요."},
    "study_guide": {"title": "스터디 가이드", "opts": ["심층", "보통", "핵심만"], "default_inst": "이 내용을 처음 배우는 학생이나 실무자를 위한 친절한 설명, 용어 해설, 그리고 이해도를 확인하는 스터디 가이드를 만들어주세요."},
    "quiz": {"title": "지식 확인 퀴즈", "opts": ["어렵게 (10개)", "보통 (5개)", "쉽게 (3개)"], "default_inst": "이 뉴스 주제에 대해 독자들이 내용을 제대로 이해했는지 확인할 수 있는 핵심 퀴즈와 정답 해설을 구성해주세요."},
    "flashcards": {"title": "핵심 암기 플래시카드", "opts": ["많이 (15개)", "보통 (10개)", "적게 (5개)"], "default_inst": "뉴스에서 꼭 기억해야 할 주요 키워드와 개념들의 핵심만 모아서 빠르게 복습할 수 있는 암기용 플래시카드 세트를 작성해주세요."}
}

DEFAULT_CONFIG = {
    "topics": ["AI Technology"],
    "schedule_time": "05:00",
    "media": {
        "slide_deck": {"enabled": True, "option": "자세히", "instruction": MEDIA_INFO["slide_deck"]["default_inst"]},
        "audio": {"enabled": True, "option": "보통", "instruction": MEDIA_INFO["audio"]["default_inst"]},
        "infographic": {"enabled": True, "option": "상세히", "instruction": MEDIA_INFO["infographic"]["default_inst"]}
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
                selected_opt = widgets["seg_btn"].get() if widgets["seg_btn"].get() else MEDIA_INFO[key]["opts"][0]
                instruction = widgets["textbox"].get("0.0", "end").strip()
            else:
                conf_media = self.config_data.get("media", {}).get(key, {})
                selected_opt = conf_media.get("option", MEDIA_INFO[key]["opts"][0])
                instruction = conf_media.get("instruction", MEDIA_INFO[key]["default_inst"])
            
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
        self.topic_entry = ctk.CTkEntry(input_frame, placeholder_text="예: 애플 M4, 오픈AI 동향", height=36, font=FONT_NORM, fg_color=BTN_DARK, border_color=BORDER_COLOR, text_color=TEXT_MAIN, corner_radius=8)
        self.topic_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(input_frame, text="✚ 추가", width=70, height=36, font=FONT_BOLD, text_color=APP_BG, fg_color=ACCENT_MINT, hover_color=ACCENT_HOVER, corner_radius=8, command=self.add_topic).pack(side="left")
        
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
                
                seg = ctk.CTkSegmentedButton(hdr, values=info["opts"], font=FONT_NORM, 
                                             selected_color=ACCENT_MINT, selected_hover_color=ACCENT_HOVER, 
                                             unselected_color=BTN_DARK, unselected_hover_color=BTN_DARK_HOVER, 
                                             text_color=TEXT_MAIN, corner_radius=8)
                seg.pack(side="right")
                seg.set(selected_opt)
                widgets["seg_btn"] = seg
                
                # Custom Instruction 텍스트 상자
                inst_text = conf_media.get("instruction", info["default_inst"])
                txt = ctk.CTkTextbox(panel, height=70, wrap="word", font=FONT_NORM, text_color=TEXT_MAIN, fg_color=BTN_DARK, border_width=1, border_color=BORDER_COLOR, corner_radius=8)
                txt.pack(fill="x", padx=20, pady=(0, 20))
                txt.insert("0.0", inst_text)
                widgets["textbox"] = txt

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
            
            # 읽기 전용 텍스트박스를 이용해 가로 스크롤 지원
            txt = ctk.CTkTextbox(row_frame, height=36, wrap="none", font=FONT_NORM, text_color=TEXT_MAIN, fg_color=PANEL_BG, border_width=1, border_color=BORDER_COLOR, corner_radius=6)
            txt.pack(side="left", fill="x", expand=True, padx=(5, 5))
            txt.insert("0.0", t)
            txt.configure(state="disabled")
            
    def add_topic(self):
        new_topic = self.topic_entry.get().strip()
        if new_topic and new_topic not in self.config_data.get("topics", []):
            if "topics" not in self.config_data:
                self.config_data["topics"] = []
            self.config_data["topics"].append(new_topic)
            self.topic_entry.delete(0, "end")
            self.populate_topics()
            
    def delete_topic(self, topic):
        if topic in self.config_data.get("topics", []):
            self.config_data["topics"].remove(topic)
            self.populate_topics()
            
    def create_bat_wrapper(self):
        wrapper_content = f'''@echo off
chcp 65001 > nul
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
                    
                    # 라인 단위로 뽑아서 출력
                    for line in iter(process.stdout.readline, ''):
                        if not line: break
                        stripped_line = line.rstrip()
                        f.write(stripped_line + "\n")
                        f.flush()
                        
                        # UI 쓰레드를 통해 텍스트 박스에 업데이트
                        console_win.after(0, safe_append, stripped_line)
                    
                    process.wait()
                    
                    if process.returncode == 0:
                        console_win.after(0, safe_append, "\n✅ [완료] 모든 뉴스 수집 및 미디어 생성이 성공적으로 완료되었습니다!")
                    else:
                        console_win.after(0, safe_append, f"\n❌ [오류] 작업 중 일부 단계에서 오류가 발생했습니다. (종료 코드: {process.returncode})")
                        
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
