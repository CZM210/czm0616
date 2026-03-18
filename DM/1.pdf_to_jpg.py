import fitz  # PyMuPDF
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# --- HTML 模板 (保持不變) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>門市電子 DM - 翻頁書模式</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/blasten/turn.js/turn.min.js"></script>
    <style>
        body { background: #444; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; overflow: hidden; font-family: "Microsoft JhengHei", sans-serif; }
        .header { color: white; margin-bottom: 15px; text-align: center; }
        #book-viewport { width: 90vw; height: 80vh; display: flex; justify-content: center; align-items: center; }
        #flipbook { width: 1000px; height: 700px; }
        .page { background-color: white; width: 500px; height: 700px; }
        .page img { width: 100%; height: 100%; object-fit: contain; }
        .btn-container { margin-top: 20px; display: flex; gap: 20px; }
        button { padding: 12px 25px; font-size: 16px; cursor: pointer; border-radius: 8px; border: none; background: #ffbe00; color: #333; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.2); }
        button:hover { background: #e6ac00; }
    </style>
</head>
<body>
    <div class="header">
        <h2 id="title">📖 門市最新活動 DM</h2>
        <p style="color: #ccc; font-size: 14px;">(點擊邊角或按鈕翻頁)</p>
    </div>
    <div id="book-viewport">
        <div id="flipbook">REPLACE_PAGES_HERE</div>
    </div>
    <div class="btn-container">
        <button onclick="$('#flipbook').turn('previous')">⬅️ 上一頁</button>
        <button onclick="$('#flipbook').turn('next')">下一頁 ➡️</button>
    </div>
    <script>
        $(window).ready(function() {
            $('#flipbook').turn({ width: 1000, height: 700, autoCenter: true, duration: 800, gradients: true });
        });
        $(window).bind('keydown', function(e) {
            if (e.keyCode == 37) $('#flipbook').turn('previous');
            else if (e.keyCode == 39) $('#flipbook').turn('next');
        });
    </script>
</body>
</html>
"""

class PDFtoBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("門市 DM 翻頁書轉換工具 (修正版)")
        self.root.geometry("400x250")
        
        tk.Label(root, text="PDF 轉網頁電子書", font=("Arial", 14, "bold"), pady=10).pack()

        frame_conf = tk.Frame(root)
        frame_conf.pack(pady=10)
        tk.Label(frame_conf, text="壓縮品質 (10-100):").grid(row=0, column=0)
        self.quality_var = tk.IntVar(value=75)
        self.quality_spin = tk.Spinbox(frame_conf, from_=10, to=100, textvariable=self.quality_var, width=5)
        self.quality_spin.grid(row=0, column=1, padx=5)

        self.btn_start = tk.Button(root, text="選擇 PDF 並開始轉換", bg="#28a745", fg="white", 
                                  font=("Arial", 12, "bold"), padx=20, pady=10, command=self.process)
        self.btn_start.pack(pady=20)
        self.status_label = tk.Label(root, text="準備就緒", fg="gray")
        self.status_label.pack()

    def process(self):
        pdf_path = filedialog.askopenfilename(title="請選擇 PDF DM", filetypes=[("PDF Files", "*.pdf")])
        if not pdf_path: return

        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_dir = f"{base_name}_Flipbook"
        if not os.path.exists(output_dir): os.makedirs(output_dir)

        self.status_label.config(text="正在轉檔中...", fg="blue")
        self.root.update()

        try:
            doc = fitz.open(pdf_path)
            img_tags = ""
            q = self.quality_var.get()
            mat = fitz.Matrix(1.5, 1.5)

            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=mat)
                img_name = f"page_{i+1:03d}.jpg"
                img_path = os.path.join(output_dir, img_name)
                
                # --- 關鍵修正處 ---
                # 改用 jpg_quality 參數
                pix.save(img_path, jpg_quality=q)
                
                img_tags += f'<div class="page"><img src="{img_name}"></div>\\n            '
            
            doc.close()

            final_html = HTML_TEMPLATE.replace("REPLACE_PAGES_HERE", img_tags)
            with open(os.path.join(output_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(final_html)

            self.status_label.config(text="轉換成功！", fg="green")
            messagebox.showinfo("完成", "已成功產出翻頁網頁！")
            os.startfile(output_dir)

        except Exception as e:
            self.status_label.config(text="轉換出錯", fg="red")
            messagebox.showerror("錯誤", f"轉換過程中發生問題：\\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFtoBookApp(root)
    root.mainloop()
