import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import speech_recognition as sr
import pyttsx3
import re

class VoiceCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ماشین حساب صوتی")
        self.root.geometry("500x400")
        
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()

        self.create_widgets()
        
    def create_widgets(self):

        title_label = tk.Label(self.root, text="ماشین حساب صوتی", font=("B Nazanin", 20, "bold"))
        title_label.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(self.root, width=50, height=10, font=("B Nazanin", 12))
        self.text_area.pack(pady=10, padx=10)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        listen_btn = tk.Button(button_frame, text="🎤 گوش دادن", font=("B Nazanin", 14),
                              command=self.start_listening, bg="lightblue", width=15)
        listen_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(button_frame, text="پاک کردن", font=("B Nazanin", 14),
                             command=self.clear_text, bg="lightcoral", width=15)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = tk.Button(button_frame, text="خروج", font=("B Nazanin", 14),
                            command=self.root.quit, bg="lightgray", width=15)
        exit_btn.pack(side=tk.LEFT, padx=5)

        help_label = tk.Label(self.root, text="راهنمای استفاده:", font=("B Nazanin", 12, "bold"))
        help_label.pack(pady=5)
        
        help_text = tk.Label(self.root, text="""پس از کلیک روی دکمه 'گوش دادن'، یکی از دستورات زیر را بگویید:
- پنج به علاوه سه
- ده منهای دو
- چهار ضربدر شش
- نه تقسیم بر سه
- یا خروج برای پایان""", font=("B Nazanin", 10), justify=tk.LEFT)
        help_text.pack()
        
    def log(self, message):
        """نمایش پیام در محیط متنی"""
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.see(tk.END)
    
    def speak(self, text):
        """تبدیل متن به گفتار"""
        self.log(f"ماشین حساب: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    
    def start_listening(self):
        """شروع گوش دادن در یک ترد جداگانه"""
        thread = threading.Thread(target=self.listen_and_process)
        thread.start()
    
    def listen_and_process(self):
        """گوش دادن و پردازش دستور"""
        try:
            with sr.Microphone() as source:
                self.log("در حال گوش دادن... لطفا صحبت کنید.")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                command = self.recognizer.recognize_google(audio, language='fa-IR')
                
                self.log(f"شما گفتید: {command}")
                self.process_command(command.lower())
                
        except sr.WaitTimeoutError:
            self.log("زمان گوش دادن به پایان رسید")
        except sr.UnknownValueError:
            self.log("متوجه نشدم، لطفا دوباره بگویید")
        except sr.RequestError:
            self.log("مشکل در اتصال به سرویس تشخیص گفتار")
        except Exception as e:
            self.log(f"خطا: {str(e)}")
    
    def process_command(self, command):
        """پردازش دستور دریافتی"""
        if 'خروج' in command or 'تمام' in command:
            self.speak("خداحافظ")
            self.root.after(1000, self.root.quit)
            return

        persian_to_english = {
            'صفر': '0', 'یک': '1', 'دو': '2', 'سه': '3', 'چهار': '4',
            'پنج': '5', 'شش': '6', 'هفت': '7', 'هشت': '8', 'نه': '9',
            'ده': '10', 'یازده': '11', 'دوازده': '12', 'سیزده': '13',
            'چهارده': '14', 'پانزده': '15', 'شانزده': '16', 'هفده': '17',
            'هجده': '18', 'نوزده': '19', 'بیست': '20'
        }

        operations = {
            'به علاوه': '+', 'منهای': '-', 'ضربدر': '*', 'تقسیم بر': '/',
            'به اضافه': '+', 'منفی': '-', 'زمان': '*', 'بر': '/'
        }

        for persian, english in persian_to_english.items():
            command = command.replace(persian, english)
        
        for persian_op, symbol in operations.items():
            command = command.replace(persian_op, symbol)
        
        try:

            expr = command.replace(' ', '')

            operators = ['+', '-', '*', '/']
            op = None
            for operator in operators:
                if operator in expr:
                    op = operator
                    break
            
            if op:
                num1_str, num2_str = expr.split(op)
                num1 = float(num1_str)
                num2 = float(num2_str)
                
                if op == '+':
                    result = num1 + num2
                    op_text = "جمع"
                elif op == '-':
                    result = num1 - num2
                    op_text = "تفریق"
                elif op == '*':
                    result = num1 * num2
                    op_text = "ضرب"
                elif op == '/':
                    if num2 == 0:
                        result = "خطا: تقسیم بر صفر"
                    else:
                        result = num1 / num2
                    op_text = "تقسیم"
                
                message = f"نتیجه {op_text} {num1} و {num2} برابر است با {result}"
                self.speak(message)
            else:
                self.speak("عملیات ریاضی تشخیص داده نشد")
                
        except Exception as e:
            self.speak(f"خطا در پردازش دستور: {str(e)}")
    
    def clear_text(self):
        """پاک کردن متن نمایش داده شده"""
        self.text_area.delete(1.0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceCalculatorGUI(root)
    root.mainloop()