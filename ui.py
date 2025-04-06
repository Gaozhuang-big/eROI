import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from Data_processing import process_mzml, create_dataframe, process_excel, process_eroi_data

# 定义语言字典，支持中英文切换
LANGUAGE_DICT = {
    'en': {
        'title': 'eROI Processor',
        'mzml_label': 'mzML File Path:',
        'select_file': 'Select File',
        'sampling_points_label': 'Sampling Points per Minute:',
        'retention_label': 'Retention Time:',
        'to': 'to',
        'min': 'min',
        'mz_label': 'm/z Range:',
        'next': 'Next',
        'output_label': 'Save Path:',
        'run': 'Run',
        'language': 'Language',
        'choose_language': 'Choose Language',
        'confirm': 'Confirm',
        'error': 'Error',
        'success': 'Success',
        'processing': 'Processing...',
        'ready': 'Ready to start...'
    },
    'zh': {
        'title': 'eROI处理器',
        'mzml_label': 'mzML文件路径：',
        'select_file': '选择文件',
        'sampling_points_label': '采样点数/分钟：',
        'retention_label': '保留时间：',
        'to': '至',
        'min': '分钟',
        'mz_label': 'm/z范围：',
        'next': '下一步',
        'output_label': '保存路径：',
        'run': '运行',
        'language': '语言',
        'choose_language': '选择语言',
        'confirm': '确认',
        'error': '错误',
        'success': '成功',
        'processing': '处理中...',
        'ready': '准备开始...'
    }
}

class Application(tk.Tk):
    """创建图形用户界面，用于输入参数、选择文件并运行数据处理"""
    def __init__(self):
        super().__init__()
        self.current_language = 'en'  # 默认语言为英文
        self.title(LANGUAGE_DICT[self.current_language]['title'])
        self.geometry("600x250")
        self.create_main_widgets()

    def create_main_widgets(self):
        """创建主窗口的控件"""
        # mzML文件路径输入
        self.label_mzml = tk.Label(self, text=LANGUAGE_DICT[self.current_language]['mzml_label'])
        self.label_mzml.place(x=10, y=10)
        self.mzml_path_entry = tk.Entry(self, width=50)
        self.mzml_path_entry.place(x=140, y=10)
        self.button_select = tk.Button(self, text=LANGUAGE_DICT[self.current_language]['select_file'],
                                       command=self.select_mzml_file)
        self.button_select.place(x=515, y=10)

        # 每分钟采样点数输入
        self.label_extra = tk.Label(self, text=LANGUAGE_DICT[self.current_language]['sampling_points_label'])
        self.label_extra.place(x=2, y=50)
        self.Sampling_points_entry = tk.Entry(self, width=10)
        self.Sampling_points_entry.place(x=140, y=50)
        self.Sampling_points_entry.insert(0, "230")

        # 保留时间范围输入
        self.label_retention = tk.Label(self, text=LANGUAGE_DICT[self.current_language]['retention_label'])
        self.label_retention.place(x=10, y=90)
        self.start_entry = tk.Entry(self, width=10)
        self.start_entry.place(x=140, y=90)
        self.start_entry.insert(0, "2")
        self.label_to = tk.Label(self, text=LANGUAGE_DICT[self.current_language]['to'])
        self.label_to.place(x=229, y=90)
        self.end_entry = tk.Entry(self, width=10)
        self.end_entry.place(x=265, y=90)
        self.end_entry.insert(0, "55")
        self.label_min = tk.Label(self, text=LANGUAGE_DICT[self.current_language]['min'])
        self.label_min.place(x=352, y=90)

        # m/z范围输入
        self.label_mz = tk.Label(self, text=LANGUAGE_DICT[self.current_language]['mz_label'])
        self.label_mz.place(x=10, y=130)
        self.mz_min_entry = tk.Entry(self, width=10)
        self.mz_min_entry.place(x=140, y=130)
        self.label_to_mz = tk.Label(self, text=LANGUAGE_DICT[self.current_language]['to'])
        self.label_to_mz.place(x=229, y=130)
        self.mz_max_entry = tk.Entry(self, width=10)
        self.mz_max_entry.place(x=265, y=130)

        # 按钮
        self.button_next = tk.Button(self, text=LANGUAGE_DICT[self.current_language]['next'],
                                     command=self.open_output_window)
        self.button_next.place(x=446, y=170)
        self.button_language = tk.Button(self, text=LANGUAGE_DICT[self.current_language]['language'],
                                         command=self.open_language_window)
        self.button_language.place(x=10, y=200)

        self.adjust_sampling_points_ui()

    def adjust_sampling_points_ui(self):
        """根据语言调整采样点数标签和输入框位置"""
        if self.current_language == 'en':
            self.label_extra.config(width=25)
            self.Sampling_points_entry.place(x=200, y=50)
        else:
            self.label_extra.config(width=15)
            self.Sampling_points_entry.place(x=140, y=50)

    def update_ui_language(self):
        """更新界面语言"""
        lang = self.current_language
        self.title(LANGUAGE_DICT[lang]['title'])
        self.label_mzml.config(text=LANGUAGE_DICT[lang]['mzml_label'])
        self.button_select.config(text=LANGUAGE_DICT[lang]['select_file'])
        self.label_extra.config(text=LANGUAGE_DICT[lang]['sampling_points_label'])
        self.label_retention.config(text=LANGUAGE_DICT[lang]['retention_label'])
        self.label_to.config(text=LANGUAGE_DICT[lang]['to'])
        self.label_min.config(text=LANGUAGE_DICT[lang]['min'])
        self.label_mz.config(text=LANGUAGE_DICT[lang]['mz_label'])
        self.label_to_mz.config(text=LANGUAGE_DICT[lang]['to'])
        self.button_next.config(text=LANGUAGE_DICT[lang]['next'])
        self.button_language.config(text=LANGUAGE_DICT[lang]['language'])
        if hasattr(self, 'output_window'):
            self.output_window.title(LANGUAGE_DICT[lang]['title'])
            self.label_output.config(text=LANGUAGE_DICT[lang]['output_label'])
            self.button_select_file.config(text=LANGUAGE_DICT[lang]['select_file'])
            self.button_run.config(text=LANGUAGE_DICT[lang]['run'])
        if hasattr(self, 'progress_window'):
            self.progress_window.title(LANGUAGE_DICT[lang]['processing'])
        self.adjust_sampling_points_ui()

    def open_language_window(self):
        """打开语言选择窗口"""
        self.language_window = tk.Toplevel(self)
        self.language_window.title(LANGUAGE_DICT[self.current_language]['choose_language'])
        self.language_window.geometry("200x160")
        self.label_language = tk.Label(self.language_window,
                                       text=LANGUAGE_DICT[self.current_language]['choose_language'])
        self.label_language.pack(pady=10)
        self.language_var = tk.StringVar(value=self.current_language)
        self.radio_en = tk.Radiobutton(self.language_window, text='English',
                                       variable=self.language_var, value='en')
        self.radio_en.pack()
        self.radio_zh = tk.Radiobutton(self.language_window, text='中文',
                                       variable=self.language_var, value='zh')
        self.radio_zh.pack()
        self.button_confirm = tk.Button(self.language_window,
                                        text=LANGUAGE_DICT[self.current_language]['confirm'],
                                        command=self.set_language)
        self.button_confirm.pack(pady=10)

    def set_language(self):
        """设置语言并更新界面"""
        self.current_language = self.language_var.get()
        self.update_ui_language()
        self.language_window.destroy()

    def select_mzml_file(self):
        """选择mzML文件"""
        file_path = filedialog.askopenfilename(filetypes=[("mzML files", "*.mzML")])
        if file_path:
            self.mzml_path_entry.delete(0, tk.END)
            self.mzml_path_entry.insert(0, file_path)

    def open_output_window(self):
        """打开输出文件选择窗口"""
        self.withdraw()
        self.output_window = tk.Toplevel(self)
        self.output_window.title(LANGUAGE_DICT[self.current_language]['title'])
        self.output_window.geometry("530x100")
        self.label_output = tk.Label(self.output_window,
                                     text=LANGUAGE_DICT[self.current_language]['output_label'])
        self.label_output.place(x=10, y=10)
        self.output_file_entry = tk.Entry(self.output_window, width=50)
        self.output_file_entry.place(x=70, y=10)
        self.button_select_file = tk.Button(self.output_window,
                                            text=LANGUAGE_DICT[self.current_language]['select_file'],
                                            command=self.select_output_file)
        self.button_select_file.place(x=450, y=6)
        self.button_run = tk.Button(self.output_window,
                                    text=LANGUAGE_DICT[self.current_language]['run'],
                                    command=self.start_processing)
        self.button_run.place(x=446, y=60)

    def select_output_file(self):
        """选择输出Excel文件路径"""
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            self.output_file_entry.delete(0, tk.END)
            self.output_file_entry.insert(0, file_path)

    def start_processing(self):
        """获取参数"""
        try:
            mzml_file = self.mzml_path_entry.get()
            Sampling_points_needed = int(self.Sampling_points_entry.get())
            integer_range_start = int(self.start_entry.get())
            integer_range_end = int(self.end_entry.get())
            mz_min = float(self.mz_min_entry.get()) if self.mz_min_entry.get() else 0
            mz_max = float(self.mz_max_entry.get()) if self.mz_max_entry.get() else float('inf')
            eroi_data = self.output_file_entry.get()

            if not mzml_file or not eroi_data:
                messagebox.showerror(LANGUAGE_DICT[self.current_language]['error'], "请填写所有文件路径")
                return
            if mz_min > mz_max:
                messagebox.showerror(LANGUAGE_DICT[self.current_language]['error'], "m/z范围无效")
                return

            self.output_window.destroy()
            self.progress_window = tk.Toplevel(self)
            self.progress_window.title(LANGUAGE_DICT[self.current_language]['processing'])
            self.progress_window.geometry("400x100")
            self.progress_label = tk.Label(self.progress_window,
                                           text=LANGUAGE_DICT[self.current_language]['ready'])
            self.progress_label.pack(pady=10)
            self.progress_bar = ttk.Progressbar(self.progress_window, orient="horizontal",
                                                length=300, mode="indeterminate")
            self.progress_bar.pack(pady=10)
            self.progress_bar.start()

            # 定义动态回调函数，根据当前语言更新进度文本
            def progress_callback(message_key):
                message = LANGUAGE_DICT[self.current_language][message_key]
                self.progress_label.config(text=message)

            # 使用多线程运行数据处理，传递回调函数
            threading.Thread(target=self.run_process,
                             args=(mzml_file, eroi_data, Sampling_points_needed,
                                   integer_range_start, integer_range_end, mz_min, mz_max,
                                   progress_callback)).start()
        except ValueError as e:
            messagebox.showerror(LANGUAGE_DICT[self.current_language]['error'], f"输入参数无效：{str(e)}")
            self.output_window.destroy()
        except Exception as e:
            messagebox.showerror(LANGUAGE_DICT[self.current_language]['error'], f"发生错误：{str(e)}")
            self.output_window.destroy()

    def run_process(self, mzml_file, eroi_data, Sampling_points_needed, integer_range_start, integer_range_end, mz_min, mz_max, progress_callback):
        """调用数据处理函数执行流程"""
        try:
            progress_callback('processing')  # 更新为“处理中...”或“Processing...”
            retention_mz_intensity = process_mzml(mzml_file)
            df = create_dataframe(retention_mz_intensity)
            row_df = process_excel(df, Sampling_points_needed, integer_range_start, integer_range_end)
            process_eroi_data(row_df, eroi_data, mz_min, mz_max, integer_range_start, integer_range_end)

            self.progress_bar.stop()
            messagebox.showinfo(LANGUAGE_DICT[self.current_language]['success'], "数据处理成功！")
            self.progress_window.destroy()
            self.deiconify()
        except Exception as e:
            messagebox.showerror(LANGUAGE_DICT[self.current_language]['error'], f"处理过程中发生错误：{str(e)}")
            self.progress_bar.stop()
            self.progress_window.destroy()
            self.deiconify()

if __name__ == "__main__":
    app = Application()
    app.mainloop()
