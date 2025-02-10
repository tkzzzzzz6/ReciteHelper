import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext, ttk
import time
import jieba
import threading
from difflib import SequenceMatcher
import queue
import numpy as np
from aip import AipSpeech  # 百度语音识别API
import config

class RecitationChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("文言文背诵检查器")
        self.root.geometry("1000x800")
        
        # 配置百度语音识别
        self.APP_ID = config.APP_ID
        self.API_KEY = config.API_KEY
        self.SECRET_KEY = config.SECRET_KEY
        self.client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        
        self.setup_ui()
        self.setup_variables()
        
    def setup_ui(self):
        # 创建左右分栏
        self.paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 左侧面板 - 原文
        left_frame = ttk.Frame(self.paned)
        self.paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="原文:", font=('TkDefaultFont', 12, 'bold')).pack(pady=5)
        self.original_text = scrolledtext.ScrolledText(left_frame, height=15, font=('TkDefaultFont', 11))
        self.original_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 右侧面板 - 识别结果
        right_frame = ttk.Frame(self.paned)
        self.paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="实时识别结果:", font=('TkDefaultFont', 12, 'bold')).pack(pady=5)
        self.result_text = scrolledtext.ScrolledText(right_frame, height=15, font=('TkDefaultFont', 11))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 控制面板
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress = ttk.Progressbar(control_frame, length=300, mode='determinate')
        self.progress.pack(side=tk.LEFT, padx=5)
        
        self.timer_label = ttk.Label(control_frame, text="10:00", font=('TkDefaultFont', 12))
        self.timer_label.pack(side=tk.LEFT, padx=5)
        
        self.start_button = ttk.Button(control_frame, text="开始识别", command=self.start_recognition)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="停止识别", command=self.stop_recognition, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 统计信息面板
        self.stats_label = ttk.Label(self.root, text="", font=('TkDefaultFont', 11))
        self.stats_label.pack(pady=5)
        
    def setup_variables(self):
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.recognized_text = ""
        self.remaining_time = 600
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 1000  # 调整语音识别灵敏度
        self.recognizer.dynamic_energy_threshold = True
        
    def start_recognition(self):
        self.is_recording = True
        self.recognized_text = ""
        self.remaining_time = 600
        self.progress['value'] = 0
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # 启动多线程
        threading.Thread(target=self.audio_capture_thread, daemon=True).start()
        threading.Thread(target=self.recognition_thread, daemon=True).start()
        threading.Thread(target=self.update_ui_thread, daemon=True).start()
        threading.Thread(target=self.timer_thread, daemon=True).start()
    
    def audio_capture_thread(self):
        with sr.Microphone(sample_rate=16000) as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_recording:
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=5)
                    self.audio_queue.put(audio)
                except sr.WaitTimeoutError:
                    continue
    
    def recognition_thread(self):
        while self.is_recording:
            try:
                audio = self.audio_queue.get(timeout=2)
                # 使用百度API进行识别
                audio_data = audio.get_wav_data()
                result = self.client.asr(audio_data, 'wav', 16000, {
                    'dev_pid': 1537,  # 普通话识别
                })
                
                if result['err_no'] == 0:
                    text = result['result'][0]
                    self.recognized_text += text
                    self.text_queue.put(text)
            except queue.Empty:
                continue
            except Exception as e:
                print(f"识别错误: {str(e)}")
    
    def update_ui_thread(self):
        while self.is_recording:
            try:
                text = self.text_queue.get(timeout=0.1)
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, self.recognized_text)
                self.real_time_compare()
            except queue.Empty:
                continue
    
    def timer_thread(self):
        while self.is_recording and self.remaining_time > 0:
            minutes = self.remaining_time // 60
            seconds = self.remaining_time % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.progress['value'] = ((600 - self.remaining_time) / 600) * 100
            time.sleep(1)
            self.remaining_time -= 1
            
        if self.remaining_time <= 0:
            self.stop_recognition()
    
    def real_time_compare(self):
        original = self.original_text.get(1.0, tk.END).strip()
        recognized = self.recognized_text.strip()
        
        # 使用结巴分词
        original_words = list(jieba.cut(original))
        recognized_words = list(jieba.cut(recognized))
        
        # 计算相似度
        similarity = SequenceMatcher(None, original, recognized).ratio()
        correct_words = sum(1 for word in recognized_words if word in original_words)
        total_words = len(recognized_words)
        
        # 更新统计信息
        stats = f"总字数: {total_words} | 正确字数: {correct_words} | "
        stats += f"正确率: {(correct_words/total_words*100):.1f}% | "
        stats += f"整体相似度: {similarity*100:.1f}%"
        self.stats_label.config(text=stats)
        
        # 标记文本
        self.result_text.delete(1.0, tk.END)
        for word in recognized_words:
            if word in original_words:
                self.result_text.insert(tk.END, word, 'correct')
            else:
                self.result_text.insert(tk.END, word, 'wrong')
        
        self.result_text.tag_config('correct', foreground='green')
        self.result_text.tag_config('wrong', foreground='red')
    
    def stop_recognition(self):
        self.is_recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.real_time_compare()

if __name__ == "__main__":
    root = tk.Tk()
    app = RecitationChecker(root)
    
    # 添加示例文言文
    sample_text = "初，权谓吕蒙曰：“卿今当涂掌事，不可不学！”蒙辞以军中多务。权曰：“孤岂欲卿治经为博士邪！但当涉猎，见往事耳。卿言多务，孰若孤？孤常读书，自以为大有所益。”蒙乃始就学。及鲁肃过寻阳，与蒙论议，大惊曰：“卿今者才略，非复吴下阿蒙！”蒙曰：“士别三日，即更刮目相待，大兄何见事之晚乎！”肃遂拜蒙母，结友而别。"
    app.original_text.insert(tk.END, sample_text)
    
    root.mainloop()
