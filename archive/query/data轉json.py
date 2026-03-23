import json

def fast_shrink():
    src, out = "data.txt", "data.json"
    rows = []
    # 預設編碼清單
    for enc in ['cp950', 'utf-8-sig', 'utf-8']:
        try:
            with open(src, "r", encoding=enc) as f:
                for line in f:
                    p = line.strip().split('\t')
                    if len(p) < 4 or "部門" in p[0]: continue
                    
                    # 瘦身關鍵 1：移除品名中佔空間的固定字眼
                    name = " ".join(p[3:]).strip().replace("( 統倉 ) ", "").replace("(統倉)", "")
                    
                    # 瘦身關鍵 2：只存入最核心數據
                    rows.append([p[0], p[1], p[2], name])
            break
        except: continue

    # 瘦身關鍵 3：移除 JSON 內所有不必要的空白字元
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, separators=(',', ':'))
    
    print("✅ 數據脫水完成")

if __name__ == "__main__":
    fast_shrink()