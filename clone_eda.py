import os
import shutil
from pathlib import Path

REPO_URL = "https://github.com/wotttoo/vintelligence-datathon.git"
TEMP_DIR = Path("D:/DataThon/temp_repo")
DEST_DIR = Path("D:/DataThon/EDA_Dashboard")

# Xóa folder cũ nếu có để tránh lỗi ghi đè
if DEST_DIR.exists():
    shutil.rmtree(DEST_DIR)

print("⏳ Đang tải Repository từ GitHub...")
# Gọi lệnh git clone
exit_code = os.system(f"git clone {REPO_URL} {TEMP_DIR}")

if exit_code == 0:
    print("\n✅ Tải thành công! Đang trích xuất toàn bộ phần Dashboard...")
    
    found_dashboard = False
    # Tìm kiếm thư mục hoặc file có chữ 'dashboard' hoặc 'eda'
    for root, dirs, files in os.walk(TEMP_DIR):
        # Bỏ qua thư mục .git
        if '.git' in root:
            continue
            
        # Tìm thư mục tên Dashboard
        for d in dirs:
            if 'dashboard' in d.lower() or 'eda' in d.lower():
                src_dir = os.path.join(root, d)
                shutil.copytree(src_dir, DEST_DIR)
                print(f"  -> Đã copy toàn bộ thư mục '{d}' vào {DEST_DIR.name}/")
                found_dashboard = True
                break
        
        if found_dashboard:
            break
            
    # Nếu không thấy thư mục Dashboard, thử tìm các file lẻ có tên dashboard (.pbix, .twbx, .py, .html...)
    if not found_dashboard:
        DEST_DIR.mkdir(exist_ok=True)
        for root, dirs, files in os.walk(TEMP_DIR):
            if '.git' in root: continue
            for f in files:
                if 'dashboard' in f.lower() or f.endswith(('.pbix', '.twbx')):
                    src = os.path.join(root, f)
                    shutil.copy(src, DEST_DIR / f)
                    print(f"  -> Đã copy file Dashboard '{f}' vào {DEST_DIR.name}/")
                    found_dashboard = True
                    
    if not found_dashboard:
        print("⚠️ Không tìm thấy file/thư mục Dashboard nào! Hãy kiểm tra lại tên thư mục trên repo.")
else:
    print("❌ Lỗi: Không thể clone repository.")

# Dọn dẹp thư mục tạm
print("\n🧹 Đang dọn dẹp thư mục rác...")
try:
    os.system(f'rmdir /S /Q "{TEMP_DIR}"')
except Exception as e:
    pass
    
print("🎉 Hoàn tất trích xuất phần Dashboard!")
