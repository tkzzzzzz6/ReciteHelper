import speech_recognition as sr
import tkinter as tk
from tkinter import scrolledtext, ttk, font, filedialog
import time
import jieba
import threading
from difflib import SequenceMatcher
import queue
import numpy as np
from aip import AipSpeech  # 百度语音识别API
from aip import AipNlp  # 添加百度NLP支持
import config
import re
from ttkthemes import ThemedTk  # 添加主题支持
import os

class RecitationChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("文言文背诵助手")
        self.root.geometry("1200x800")
        
        # 设置主题和样式
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Microsoft YaHei", 16, "bold"))
        style.configure("Text.TLabel", font=("Microsoft YaHei", 12))
        style.configure("Stats.TLabel", font=("Microsoft YaHei", 11))
        
        # 配置百度语音识别
        self.APP_ID = config.APP_ID
        self.API_KEY = config.API_KEY
        self.SECRET_KEY = config.SECRET_KEY
        self.client = AipSpeech(self.APP_ID, self.API_KEY, self.SECRET_KEY)
        
        # 配置百度NLP客户端
        self.nlp_client = AipNlp(config.NLP_APP_ID, config.NLP_API_KEY, config.NLP_SECRET_KEY)
        
        self.setup_ui()
        self.setup_variables()
        
    def setup_ui(self):
        # 主容器
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(title_frame, text="文言文背诵助手", style="Title.TLabel").pack()
        
        # 添加文本标题显示
        self.text_title_label = ttk.Label(
            title_frame,
            text="当前文本：未选择",
            style="Text.TLabel"
        )
        self.text_title_label.pack(pady=5)
        
        # 创建左右分栏
        self.paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)
        
        # 左侧面板 - 背诵文本
        left_frame = ttk.LabelFrame(self.paned, text="背诵内容", padding="5")
        self.paned.add(left_frame, weight=1)
        
        # 原文输入（隐藏）
        self.original_text = scrolledtext.ScrolledText(
            left_frame, 
            height=15, 
            font=("Microsoft YaHei", 12),
            wrap=tk.WORD
        )
        self.original_text.pack(fill=tk.BOTH, expand=True)
        
        # 模糊文本显示
        self.blur_text = scrolledtext.ScrolledText(
            left_frame,
            height=15,
            font=("Microsoft YaHei", 12),
            wrap=tk.WORD,
            background="#F5F5F5"
        )
        self.blur_text.pack(fill=tk.BOTH, expand=True)
        self.original_text.pack_forget()
        
        # 右侧面板 - 识别结果
        right_frame = ttk.LabelFrame(self.paned, text="识别结果", padding="5")
        self.paned.add(right_frame, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(
            right_frame,
            height=15,
            font=("Microsoft YaHei", 12),
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制面板
        control_frame = ttk.Frame(main_container, padding="5")
        control_frame.pack(fill=tk.X, pady=10)
        
        # 进度条和计时器
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.progress = ttk.Progressbar(
            progress_frame, 
            length=300, 
            mode='determinate',
            style="Accent.Horizontal.TProgressbar"
        )
        self.progress.pack(side=tk.LEFT, padx=(0, 10))
        
        self.timer_label = ttk.Label(
            progress_frame,
            text="10:00",
            style="Text.TLabel"
        )
        self.timer_label.pack(side=tk.LEFT)
        
        # 控制按钮
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        self.start_button = ttk.Button(
            button_frame,
            text="开始背诵",
            command=self.start_recognition,
            style="Accent.TButton",
            width=15
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="停止背诵",
            command=self.stop_recognition,
            state=tk.DISABLED,
            width=15
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 添加文本选择按钮
        self.select_text_button = ttk.Button(
            button_frame,
            text="选择文本",
            command=self.select_text,
            width=15
        )
        self.select_text_button.pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        status_frame = ttk.Frame(main_container, padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.stats_label = ttk.Label(
            status_frame,
            text="准备就绪",
            style="Stats.TLabel"
        )
        self.stats_label.pack(side=tk.LEFT)
        
    def setup_variables(self):
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.recognized_text = ""
        self.remaining_time = 600
        self.recognizer = sr.Recognizer()
        # 调整语音识别参数，提高灵敏度
        self.recognizer.energy_threshold = 1500  # 降低能量阈值，提高灵敏度
        self.recognizer.dynamic_energy_threshold = True  # 开启动态阈值
        self.recognizer.pause_threshold = 0.5  # 缩短停顿判断时间
        self.recognizer.phrase_threshold = 0.3  # 降低短语阈值
        self.recognizer.non_speaking_duration = 0.3  # 缩短非说话判断时间
        self.correct_chars = set()
        self.current_sentence_index = 0
        self.sentences = []
        self.accumulated_text = ""  # 用于累积识别文本
        self.last_recognition_time = 0  # 用于控制识别频率
        
        # 初始化文本相关变量
        self.current_text_path = None
        self.texts_dir = os.path.join(os.path.dirname(__file__), 'texts')
        
        # 确保texts目录存在
        if not os.path.exists(self.texts_dir):
            os.makedirs(self.texts_dir)
    
    def select_text(self):
        """选择要背诵的文本文件"""
        file_path = filedialog.askopenfilename(
            initialdir=self.texts_dir,
            title="选择要背诵的文本",
            filetypes=(("文本文件", "*.txt"), ("所有文件", "*.*"))
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_content = f.read().strip()
                
                # 更新文本显示
                self.original_text.delete(1.0, tk.END)
                self.original_text.insert(tk.END, text_content)
                
                # 更新标题显示
                text_name = os.path.splitext(os.path.basename(file_path))[0]
                self.text_title_label.config(text=f"当前文本：{text_name}")
                
                # 保存当前文本路径
                self.current_text_path = file_path
                
                # 重置识别状态
                self.current_sentence_index = 0
                self.accumulated_text = ""
                self.update_blur_text()
                
                # 启用开始按钮
                self.start_button.config(state=tk.NORMAL)
                
            except Exception as e:
                tk.messagebox.showerror("错误", f"无法加载文本文件：{str(e)}")
    
    def start_recognition(self):
        # 检查是否已选择文本
        if not self.current_text_path:
            tk.messagebox.showwarning("警告", "请先选择要背诵的文本！")
            return
            
        original = self.original_text.get(1.0, tk.END).strip()
        # 只按句号分割文本，保留句号
        self.sentences = []
        temp_sentences = original.split('。')
        for s in temp_sentences:
            if s.strip():  # 确保不是空字符串
                self.sentences.append(s.strip() + '。')
        
        # 移除最后一个句子的句号（如果原文没有以句号结尾）
        if not original.endswith('。'):
            self.sentences[-1] = self.sentences[-1][:-1]
        
        self.current_sentence_index = 0
        self.accumulated_text = ""
        self.last_recognition_time = 0
        
        self.is_recording = True
        self.remaining_time = 600
        self.progress['value'] = 0
        
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        self.correct_chars.clear()  # 重置正确字符记录
        self.update_blur_text()  # 更新模糊显示
        
        # 启动多线程
        threading.Thread(target=self.audio_capture_thread, daemon=True).start()
        threading.Thread(target=self.recognition_thread, daemon=True).start()
        threading.Thread(target=self.update_ui_thread, daemon=True).start()
        threading.Thread(target=self.timer_thread, daemon=True).start()
    
    def audio_capture_thread(self):
        with sr.Microphone(sample_rate=16000) as source:
            # 缩短环境噪音自适应时间
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while self.is_recording:
                try:
                    # 调整监听参数
                    audio = self.recognizer.listen(
                        source,
                        timeout=1,  # 缩短超时时间
                        phrase_time_limit=2,  # 缩短短语时间限制
                    )
                    self.audio_queue.put(audio)
                except sr.WaitTimeoutError:
                    continue
    
    def get_semantic_similarity(self, text1, text2):
        """使用百度NLP判断语义相似度"""
        try:
            result = self.nlp_client.simnet(text1, text2)
            if result.get('score'):
                return result['score']
            return 0
        except Exception as e:
            print(f"NLP错误: {str(e)}")
            return 0

    def recognition_thread(self):
        while self.is_recording:
            try:
                audio = self.audio_queue.get(timeout=1)
                current_time = time.time()
                
                if current_time - self.last_recognition_time < 0.3:
                    continue
                
                audio_data = audio.get_wav_data()
                result = self.client.asr(audio_data, 'wav', 16000, {
                    'dev_pid': 1537,
                    'enable_voice_detection': True,
                })
                
                if result['err_no'] == 0:
                    recognized_text = result['result'][0]
                    if len(recognized_text.strip()) > 2:
                        current_sentence = self.sentences[self.current_sentence_index]
                        
                        # 使用百度NLP进行语义相似度判断
                        similarity = self.get_semantic_similarity(recognized_text, current_sentence)
                        
                        if similarity > 0.7:  # 语义相似度阈值
                            # 相似度高，使用原句
                            self.accumulated_text = current_sentence
                        elif similarity > 0.5:
                            # 部分相似，使用识别文本但标记为部分匹配
                            self.accumulated_text = recognized_text
                            self.partial_match = True
                        else:
                            # 相似度低，使用识别文本
                            self.accumulated_text = recognized_text
                            self.partial_match = False
                        
                        self.text_queue.put(self.accumulated_text)
                        self.last_recognition_time = current_time
                        
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
    
    def update_blur_text(self):
        self.blur_text.delete(1.0, tk.END)
        
        for i, sentence in enumerate(self.sentences):
            if i < self.current_sentence_index:
                # 已完成的句子显示为绿色
                self.blur_text.insert(tk.END, sentence, 'completed')
            elif i == self.current_sentence_index:
                # 当前句子显示为半透明
                for char in sentence:
                    if char in ['，', '：', '"', '"', '。']:
                        self.blur_text.insert(tk.END, char, 'punctuation')
                    else:
                        self.blur_text.insert(tk.END, '∎', 'current')
            else:
                # 未开始的句子显示为浅灰色方块
                for char in sentence:
                    if char in ['，', '：', '"', '"', '。']:
                        self.blur_text.insert(tk.END, char, 'punctuation')
                    else:
                        self.blur_text.insert(tk.END, '□', 'future')
            
            # 添加段落间距
            if i < len(self.sentences) - 1:
                self.blur_text.insert(tk.END, "\n")
        
        # 配置标签样式
        self.blur_text.tag_config('completed', foreground='#2ECC71', font=("Microsoft YaHei", 12, "bold"))
        self.blur_text.tag_config('current', foreground='#3498DB', font=("Microsoft YaHei", 12))
        self.blur_text.tag_config('future', foreground='#BDC3C7', font=("Microsoft YaHei", 12))
        self.blur_text.tag_config('punctuation', foreground='#34495E', font=("Microsoft YaHei", 12))
    
    def real_time_compare(self):
        if self.current_sentence_index >= len(self.sentences):
            return
        
        current_sentence = self.sentences[self.current_sentence_index]
        recognized = self.accumulated_text.strip()
        
        if len(recognized) < 5:
            return
        
        # 计算相似度
        similarity = SequenceMatcher(None, current_sentence, recognized).ratio()
        
        # 使用更宽松的判断标准，考虑发音相似性
        char_match_ratio = sum(1 for c in current_sentence if c in recognized) / len(current_sentence)
        
        # 如果accumulated_text就是current_sentence，说明NLP已经确认发音相近
        is_nlp_matched = (recognized == current_sentence)
        
        if is_nlp_matched or similarity > 0.4 or char_match_ratio > 0.6:
            self.current_sentence_index += 1
            self.accumulated_text = ""
            self.update_blur_text()
            
            if self.current_sentence_index < len(self.sentences):
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "✓ 当前句背诵正确！\n\n", 'success')
                self.result_text.insert(tk.END, "下一句：\n", 'prompt')
                self.result_text.insert(tk.END, f"{self.sentences[self.current_sentence_index]}\n\n", 'current')
                self.result_text.insert(tk.END, "您的朗读：\n", 'prompt')
            else:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, "🎉 恭喜！全文背诵完成！", 'success')
                self.stop_recognition()
            
            # 更新统计信息
            total_sentences = len(self.sentences)
            completed_sentences = self.current_sentence_index
            
            stats = f"总句数: {total_sentences} | 已完成: {completed_sentences} | "
            stats += f"进度: {(completed_sentences/total_sentences*100):.1f}%"
            if similarity > 0.6:
                stats += f" | 准确率: {(similarity*100):.1f}%"
            self.stats_label.config(text=stats)
        
        # 更新识别结果显示
        self.result_text.delete(1.0, tk.END)
        if self.current_sentence_index < len(self.sentences):
            self.result_text.insert(tk.END, "当前句：\n", 'prompt')
            self.result_text.insert(tk.END, f"{self.sentences[self.current_sentence_index]}\n\n", 'current')
        self.result_text.insert(tk.END, "您的朗读：\n", 'prompt')
        self.result_text.insert(tk.END, recognized, 'recognized')
    
    def stop_recognition(self):
        self.is_recording = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.real_time_compare()

if __name__ == "__main__":
    root = ThemedTk(theme="arc")  # 使用现代主题
    app = RecitationChecker(root)
    
    root.mainloop()
