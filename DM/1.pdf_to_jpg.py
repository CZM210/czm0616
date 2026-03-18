import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

# --- 高階自適應 HTML 模板 (已優化) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>門市 DM 電子書</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/blasten/turn.js/turn.min.js"></script>
    <style>
        body { background: #1a1a1a; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; overflow: hidden; font-family: sans-serif; }
        #viewport { width: 95vw; height: 85vh; display: flex; justify-content: center; align-items: center; position: relative; }
        #flipbook { box-shadow: 0 0 25px rgba(0,0,0,0.9); }
        .page { background: #000; overflow: hidden; }
        .page img { width: 100%; height: 100%; object-fit: contain; }
        .controls { position: fixed; bottom: 40px; display: flex; align-items: center; gap: 20px; z-index: 999; }
        .btn-main { padding: 15px 40px; font-size: 20px; font-weight: bold; border: none; border-radius: 50px; background: #ffbe00; color: #000; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        .page-num { color: #fff; font-size: 18px; font-weight: bold; min-width: 80px; text-align: center; }
        .click-area { position: absolute; top: 0; width: 20%; height: 100%; z-index: 10; cursor: pointer; }
        .next-area { right: 0; }
        .prev-area { left: 0; }
    </style>
</head>
<body>
    <div id="viewport">
        <div class="click-area prev-area" onclick="$('#flipbook').turn('previous')"></div>
        <div class="click-area next-area" onclick="$('#flipbook').turn('next')"></div>
        <div id="flipbook">REPLACE_PAGES_HERE</div>
    </div>
    <div class="controls">
        <button class="btn-main" onclick="$('#flipbook').turn('previous')">⬅ 上一頁</button>
        <div class="page-num"><span id="cp">1</span> / TOTAL_COUNT</div>
        <button class="btn-main" onclick="$('#flipbook').turn('next')">下一頁 ➡</button>
    </div>
    <script>
        $(window).ready(function() {
            var ratio = IMG_RATIO;
            function resizeBook() {
                var winW = $(window).width() * 0.95;
                var winH = $(window).height() * 0.8;
                var width, height;
                if (winW / winH > ratio * 2) {
                    height = winH;
                    width = height / ratio * 2;
                } else {
                    width = winW;
                    height = (width / 2) * ratio;
                }
                $('#flipbook').turn('size', width, height);
            }
            $('#flipbook').turn({
                acceleration: true, gradients: true, autoCenter: true, elevation: 50,
                when: { turned: function(e, page) { $('#cp').text(page); } }
            });
            resizeBook();
            $(window).resize(resizeBook);
        });
    </script>
</body>
</html>
"""

class DM_Fixer:
    def __init__(self, root):
        self.root = root
        self.root.title("DM 自適應轉檔工具 v3.1")
        self.root.geometry("400x250")
        
        tk.Label(root, text="修正「Document Closed」錯誤版", fg="red").pack(pady=10)
        self.btn = tk.Button(root, text="📂 選擇 PDF 開始轉檔", command=self.run, 
                             bg="#28a745", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
        self.btn.pack(pady=20)
        self.status = tk.Label(root, text="等待操作...", fg="gray")
        self.status.pack(side="bottom", pady=10)

    def run(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if not file_path: return

        folder = os.path.splitext(os.path.basename(file_path))[0] + "_DM_Web"
        if not os.path.exists(folder): os.makedirs(folder)
        
        self.status.config(text="處理中，請稍候...", fg="blue")
        self.root.update()

        try:
            doc = fitz.open(file_path)
            total_pages = len(doc) # 先把總頁數記下來
            
            # 取得第一頁比例
            first_page = doc.load_page(0)
            img_ratio = first_page.rect.height / first_page.rect.width
            
            img_tags = ""
            for i in range(total_pages):
                img_name = f"p_{i+1:03d}.jpg"
                img_path = os.path.join(folder, img_name)
                
                # 高清轉圖
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                pix.save(img_path)
                
                # 瘦身壓縮
                with Image.open(img_path) as img:
                    img = img.convert("RGB")
                    if img.width > 1100: # 稍微調小一點點，手機跑更順
                        img.thumbnail((1100, 1100), Image.LANCZOS)
                    img.save(img_path, "JPEG", quality=80, optimize=True)
                
                img_tags += f'<div class="page"><img src="{img_name}"></div>\\n            '
            
            doc.close() # 圖片跑完才關閉檔案

            # --- 填入參數 (這時候用變數，不直接讀 doc) ---
            content = HTML_TEMPLATE.replace("REPLACE_PAGES_HERE", img_tags)
            content = content.replace("TOTAL_COUNT", str(total_pages))
            content = content.replace("IMG_RATIO", str(img_ratio))

            with open(os.path.join(folder, "index.html"), "w", encoding="utf-8") as f:
                f.write(content)

            self.status.config(text="轉換成功！", fg="green")
            messagebox.showinfo("完成", f"已成功產出！\\n請開啟資料夾內的 index.html")
            os.startfile(folder)

        except Exception as e:
            messagebox.showerror("錯誤", f"程式發生問題：\\n{str(e)}")
            self.status.config(text="執行失敗", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    DM_Fixer(root)
    root.mainloop()