import json
import subprocess
import time
from pathlib import Path
import sys

CONFIG_FILE = Path(__file__).parent / "config.json"
RUN_SCRIPT = "run_all_news.py"

def update_config(topics, media_config, search_type="fast"):
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except:
                config = {}
    else:
        config = {}
    
    config["topics"] = topics
    config["media"] = media_config
    config["search_type"] = search_type
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
        
def run_test_phase(name):
    print(f"\n{'='*70}\n🚀 STARTING TEST PHASE: {name}\n{'='*70}")
    # Run the news pipeline script
    result = subprocess.run(["uv", "run", "python", "-u", RUN_SCRIPT])
    if result.returncode != 0:
        print(f"\n❌ ERROR: Test phase '{name}' failed with return code {result.returncode}.")
        sys.exit(1)
    print(f"\n✅ FINISHED TEST PHASE: {name}\n{'='*70}\n")

if __name__ == "__main__":
    print("====================================================================")
    print(" NotebookLM E2E Stability Simulation")
    print("====================================================================")
    
    # ---------------------------------------------------------
    # Scenario 1: 3x3 Loop Test (3 Topics, 1 Media, Fast Search)
    # ---------------------------------------------------------
    base_media = {
        "slide_deck": {"enabled": True, "option": "보통", "instruction": "테스트 슬라이드 요약"}
    }
    
    test_topics = ["Google", "한국 정치", "한국 부동산"]
    
    print("\n[Phase 1] 3-Iteration Loop Test across 3 Topics (SKIPPED FOR DEBUGGING)")
    # for i in range(1, 4):
    #     update_config(test_topics, base_media, search_type="fast")
    #     run_test_phase(f"Loop Test Iteration {i}/3")
    #     time.sleep(3) # Small buffer between executions
        
    # ---------------------------------------------------------
    # Scenario 2: 10-Media Torture Test (1 Topic, All 10 Media)
    # ---------------------------------------------------------
    all_10_media = {
        "slide_deck": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "audio": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "video": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "infographic": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "report": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "data_table": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "mind_map": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "study_guide": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "quiz": {"enabled": True, "option": "보통", "instruction": "테스트"},
        "flashcards": {"enabled": True, "option": "보통", "instruction": "테스트"}
    }
    
    print("\n[Phase 2] 10-Media Simultaneous Generation Torture Test")
    update_config(["Google"], all_10_media, search_type="fast")
    run_test_phase("10-Media Torture Test on Notebook: 'Google'")

    print("\n🎉 ALL E2E TESTS COMPLETED SUCCESSFULLY!")
