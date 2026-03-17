import json
import os

# --- 設定 ---
INPUT_FILE = "data.txt"
OUTPUT_FILE = "data.json"

def convert_to_compact_json():
    rows = []
    # 嘗試兩種常見編碼，防止亂碼
    encodings = ['cp950', 'utf-8-sig', 'utf-8']
    
    success = False
    for enc in encodings:
        try:
            with open(INPUT_FILE, "r", encoding=enc) as f:
                for line in f:
                    # 濾掉空白行
                    clean_line = line.strip()
                    if not clean_line: continue
                    
                    p = clean_line.split('\t')
                    if len(p) >= 4:
                        if "部門" in p[0]: continue
                        # 品名合體並縮減多餘空白
                        name = " ".join(p[3:]).strip()
                        # 只存入陣列，不存 Key 名稱 (如 "name":)，這樣可以省下一半的檔案空間
                        rows.append([p[0], p[1], p[2], name])
            success = True
            break
        except UnicodeDecodeError:
            continue

    if success:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            # separators=(',', ':') 會刪除 JSON 裡所有的空格，讓檔案體積最小化
            json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
        
        size_mb = os.path.getsize(OUTPUT_FILE) / (1024*1024)
        print(f"✅ 轉換成功！")
        print(f"📊 總筆數：{len(rows)} 筆")
        print(f"📦 壓縮後體積：{size_mb:.2f} MB")
        print(f"👉 請將 {OUTPUT_FILE} 上傳至 Netlify 即可。")
    else:
        print("❌ 檔案讀取失敗，請確認 data.txt 是否正確。")

if __name__ == "__main__":
    convert_to_compact_json()
