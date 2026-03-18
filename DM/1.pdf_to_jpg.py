import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

# --- 專業純淨版 HTML 模板 (黑底、大按鈕、無雜訊) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>門市 DM 電子書</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/blasten/turn.js/turn.min.js"></script>
    <style>
        body { background: #1a1a1a; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; height: 100vh; font-family: sans-serif; overflow: hidden; }
        .header { color: #fff; margin: 10px 0; font-size: 16px; opacity: 0.6; }
        #book-viewport { position: relative; width: 95vw; height: 80vh; display: flex; justify-content: center; align-items: center; margin-top: 10px; }
        #flipbook { width: 1000px; height: 700px; }
        .page { background: white; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        .page img { width: 100%; height: 100%; object-fit: contain; }
        .btn-side { position: absolute; top: 0; width: 15%; height: 100%; border: none; background: rgba(255,255,255,0.02); color: rgba(255,255,255,0.2); font-size: 60px; cursor: pointer; transition: 0.3s; z-index: 10; }
        .btn-side:hover { background: rgba(255,255,255,0.08); color: #fff; }
        .btn-prev-side { left: 0; text-align: left; padding-left: 20px; }
        .btn-next-side { right: 0; text-align: right; padding-right: 20px; }
        .controls { position: fixed; bottom: 30px; display: flex; gap: 30px; align-items: center; z-index: 20; }
        .btn-main { padding: 15px 50px; font-size: 22px; font-weight: bold; cursor: pointer; border: none; border-radius: 50px; background: #ffbe00; color: #000; box-shadow: 0 4px 15px rgba(0,0,0,0.6); }
        .btn-main:hover { background: #ffd04d; transform: scale(1.05); }
        .page-num { color: #fff; font-size: 20px; font-weight: bold; min-width: 100px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">📖 點擊左右邊緣或按鈕翻頁</div>
    <div id="book-viewport">
        <button class="btn-side btn-prev-side" onclick="$('#flipbook').turn('previous')">‹</button>
        <button class="btn-side btn-next-side" onclick="$('#flipbook').turn('next')">›</button>
        <div id="flipbook">REPLACE_PAGES_HERE</div>
    </div>
    <div class="controls">
        <button class="btn-main" onclick="$('#flipbook').turn('previous')">⬅ 上一頁</button>
        <div class="page-num"><span id="cp">1</span> / <span id="tp">TOTAL_COUNT</span></div>
        <button class="btn-main" onclick="$('#flipbook').turn('next')">下一頁 ➡</button>
    </div>
    <script>
        $(window).ready(function() {
            var book = $('#flipbook');
            book.turn({
                width: 1000, height: 700, autoCenter: true, gradients: true, acceleration: true,
                when: { turned: function(e, page) { $('#cp').text(page); } }
            });
        });
    </script>
</body>
</html>
"""

class DM_BookMaker_Final:
    def __init__(self, root):
        self.root = root
        self.root.title("門市 DM 轉檔工具 - 終極穩定版")
        self.root.geometry("500x350")
        
        frame = tk.Frame(root, padx=30, pady=30)
        frame.pack(expand=True, fill="both")
        
        tk.Label(frame, text="專為 32 位元環境優化，支援損壞檔案跳過", font=("Arial", 10), fg="blue").pack()
        
        self.btn_run = tk.Button(frame, text="📂 選擇並轉換 PDF", command=self.process_pdf, 
                                 bg="#28a745", fg="white", font=("Arial", 14, "bold"), 
                                 padx=20, pady=15, relief="raised")
        self.btn_run.pack(pady=20)
        
        self.status = tk.Label(frame, text="狀態：準備就緒", fg="gray")
        self.status.pack(side="bottom")

    def process_pdf(self):
        pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not pdf_path: return
        
        folder_name = os.path.splitext(os.path.basename(pdf_path))[0] + "_WebBook"
        if not os.path.exists(folder_name): os.makedirs(folder_name)
        
        self.status.config(text="正在處理中，請稍候...", fg="blue")
        self.root.update()
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            img_tags = ""
            success_count = 0
            
            for i in range(total_pages):
                try:
                    # 嘗試讀取這一頁
                    page = doc.load_page(i)
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                    img_name = f"p_{i+1:03d}.jpg"
                    img_path = os.path.join(folder_name, img_name)
                    pix.save(img_path)
                    
                    # 圖片瘦身 (Resize & Compress)
                    with Image.open(img_path) as img:
                        if img.width > 1200:
                            ratio = 1200 / float(img.width)
                            new_height = int(float(img.height) * ratio)
                            img = img.resize((1200, new_height), Image.LANCZOS)
                        img.save(img_path, "JPEG", quality=85, optimize=True)
                    
                    img_tags += f'<div class="page"><img src="{img_name}"></div>\\n            '
                    success_count += 1
                    self.status.config(text=f"進度：{i+1} / {total_pages} 頁")
                    self.root.update()
                    
                except:
                    # 如果這一頁報錯 (語法錯誤等)，直接跳過不處理
                    print(f"跳過損壞頁面: 第 {i+1} 頁")
                    continue
            
            doc.close()
            
            # 生成 HTML
            final_html = HTML_TEMPLATE.replace("REPLACE_PAGES_HERE", img_tags)
            final_html = final_html.replace("TOTAL_COUNT", str(success_count))
            
            with open(os.path.join(folder_name, "index.html"), "w", encoding="utf-8") as f:
                f.write(final_html)
            
            self.status.config(text="處理完成！", fg="green")
            messagebox.showinfo("成功", f"轉換完成！\\n總共處理了 {success_count} 頁。")
            os.startfile(folder_name)
            
        except Exception as e:
            messagebox.showerror("嚴重錯誤", f"程式無法開啟此檔案：\\n{str(e)}")
            self.status.config(text="轉換失敗", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = DM_BookMaker_Final(root)
    root.mainloop()
