import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import time

# --- 設定 ---
# コマンドプロンプトで "netsh interface show interface" を打って確認した名前にしてください
WIFI_INTERFACE_NAME = "Wi-Fi 2"
WORK_TIME = 1 * 10  # 25分
BREAK_TIME = 1 * 10   # 5分

class PomodoroWifiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Wi-Fi Control")
        self.root.geometry("350x250")

        # UI要素の配置
        self.label_status = tk.Label(root, text="待機中", font=("MS Gothic", 16, "bold"))
        self.label_status.pack(pady=10)

        self.label_timer = tk.Label(root, text="25:00", font=("Helvetica", 48))
        self.label_timer.pack(pady=10)

        self.btn_start = tk.Button(root, text="集中開始", font=("MS Gothic", 12), 
                                   command=self.start_timer, width=15, height=2)
        self.btn_start.pack(pady=20)

        self.is_running = False

    def set_wifi(self, enable):
        """Wi-Fiの有効/無効を切り替える"""
        state = "enabled" if enable else "disabled"
        try:
            # shell=True を使うことでWindowsコマンドを適切に実行
            subprocess.run(f'netsh interface set interface "{WIFI_INTERFACE_NAME}" admin={state}', 
                           shell=True, check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("エラー", "管理者権限で実行するか、Wi-Fi名を確認してください。")

    def start_timer(self):
        if not self.is_running:
            self.is_running = True
            self.btn_start.config(state="disabled")
            # メイン画面が固まらないように別スレッドで実行
            threading.Thread(target=self.pomodoro_cycle, daemon=True).start()

    def pomodoro_cycle(self):
        # 1. 集中フェーズ (Wi-Fi ON)
        self.run_countdown(WORK_TIME, "🔥 集中時間中", "#e74c3c") # 赤系
        
        # 2. Wi-Fi切断
        self.set_wifi(False)
        
        # 3. 休憩フェーズ (Wi-Fi OFF)
        self.run_countdown(BREAK_TIME, "☕ 休憩中 (通信OFF)", "#3498db") # 青系
        
        # 4. Wi-Fi復帰
        self.set_wifi(True)
        
        # 5. 終了処理
        self.label_status.config(text="1セット完了！", fg="black")
        self.btn_start.config(state="normal")
        self.is_running = False
        messagebox.showinfo("お疲れ様でした", "Wi-Fiが再接続されました。次のセットに進みますか？")

    def run_countdown(self, seconds, status_text, color):
        self.label_status.config(text=status_text, fg=color)
        while seconds >= 0:
            mins, secs = divmod(seconds, 60)
            self.label_timer.config(text=f"{mins:02d}:{secs:02d}")
            self.root.update()
            time.sleep(1)
            seconds -= 1

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroWifiApp(root)
    root.mainloop()