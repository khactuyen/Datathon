import json
from pathlib import Path

# Danh sách các notebook cần sửa đường dẫn
notebooks = [
    Path('D:/DataThon/notebooks/Part3_Model.ipynb'),
    Path('D:/DataThon/notebooks/train_forecasting_DA_Master.ipynb'), # phòng trường hợp tên cũ
    Path('D:/DataThon/notebooks/part1_MCQ_answers.ipynb')
]

for nb_path in notebooks:
    if nb_path.exists():
        with open(nb_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Biến đường dẫn tuyệt đối thành tương đối để chạy được trên mọi máy
        content = content.replace("Path('D:/DataThon/dataset')", "Path('../dataset')")
        
        # 2. Sửa đường dẫn xuất file submit (và dùng đường dẫn tương đối luôn)
        content = content.replace("Path('D:/DataThon/submition')", "Path('../submissions')")
        content = content.replace("Path('D:/DataThon/submissions')", "Path('../submissions')")
        
        with open(nb_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✅ Đã biến đổi thành công sang đường dẫn ĐỘNG (relative path) trong: {nb_path.name}")
