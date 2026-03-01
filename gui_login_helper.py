import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

def get_storage_path() -> Path:
    """Return path to global storage state."""
    # Matches notebooklm-py paths
    return Path.home() / ".notebooklm" / "storage_state.json"

def get_browser_profile_dir() -> Path:
    """Return path to persistent browser profile."""
    # Matches notebooklm-py paths
    return Path.home() / ".notebooklm" / "browser_profile"

def run_login_flow():
    storage_path = get_storage_path()
    browser_profile = get_browser_profile_dir()
    
    storage_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    browser_profile.mkdir(parents=True, exist_ok=True, mode=0o700)

    print("Opening browser for Google login...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(browser_profile),
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--password-store=basic",
            ],
            ignore_default_args=["--enable-automation"],
        )

        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://notebooklm.google.com/")

        print("Waiting for login to complete... (Will close automatically when successful)")

        # 사용자가 수동으로 로그인할 때까지 대기
        # 로그인 성공 후 notebooklm.google.com 도메인으로 리다이렉션 되며 
        # Notebooks 대시보드가 로딩됨을 감지합니다. (최대 5분 대기)
        try:
            # wait_for_url은 계정 로그인(accounts.google.com)이 끝난 후 본래 사이트로 올 때까지 기다립니다.
            # 정확한 홈 URL (질의 문자열 포함 가능성)
            page.wait_for_url("https://notebooklm.google.com/**", timeout=300000)
            
            # 페이지가 안정적으로 로딩될 때까지 잠시 대기
            page.wait_for_load_state("networkidle", timeout=30000)
            print("Login successful! Saving authentication data...")
            
            context.storage_state(path=str(storage_path))
            
            try:
                storage_path.chmod(0o600)
            except OSError:
                pass # 윈도우 환경 권한 무시
                
            print(f"Authentication saved to: {storage_path}")
            sys.exit(0)
        except Exception as e:
            print(f"Login timeout or error: {e}")
            sys.exit(1)
        finally:
            context.close()

if __name__ == "__main__":
    run_login_flow()
