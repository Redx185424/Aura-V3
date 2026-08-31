# ===============================================
# Aura Gen 3 - Redx Edition (LIVING VISUALS)
# Features: Matrix Rain + Reactor Loader + Scanner HUD
# ===============================================

import tkinter as tk
from tkinter import scrolledtext, messagebox
import pyttsx3
import speech_recognition as sr
import webbrowser
import time
import os
import threading
import requests
import queue
import random
import smtplib
import ssl
import json
import math
from email.message import EmailMessage

# ================== 🔴 CONFIG 🔴 ==================
MIC_DEVICE_ID = 1  
SENDER_EMAIL = "isro48481@gmail.com"        
SENDER_PASSWORD = "ynwd mhzu hlly vzjx"      

# ================== THEMES ==================
THEMES = {
    "redx": {
        "primary": "#00f2ea", "secondary": "#a855f7", "bg": "#050505", "text": "white",
        "welcome": "Systems Online. Welcome back, Redx."
    },
    "captain demon": {
        "primary": "#00ff00", "secondary": "#006400", "bg": "#000900", "text": "#ccffcc",
        "welcome": "WAR MODE ACTIVATED. READY FOR BATTLE, CAPTAIN."
    },
    "gemini": {
        "primary": "#1a73e8", "secondary": "#d93025", "bg": "#f0f2f5", "text": "#202124",
        "welcome": "Gemini Protocol Initialized."
    }
}

# ================== USER DB ==================
DB_FILE = "aura_users.json"
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f: return json.load(f)
    return {}
def save_new_user(u, p):
    users = load_users(); users[u] = p
    with open(DB_FILE, "w") as f: json.dump(users, f)

# ================== ENGINES ==================
class TTSEngine:
    def __init__(self):
        self.queue = queue.Queue()
        threading.Thread(target=self._worker, daemon=True).start()
    def speak(self, text): self.queue.put(text)
    def _worker(self):
        eng = pyttsx3.init()
        eng.setProperty("rate", 165)
        try: eng.setProperty("voice", eng.getProperty("voices")[1].id)
        except: pass
        while True:
            t = self.queue.get()
            if t is None: break
            try: eng.say(t); eng.runAndWait()
            except: pass
            self.queue.task_done()

aura_voice = TTSEngine()

def download_image(query, console=None):
    try:
        folder = "Aura_Images"
        if not os.path.exists(folder): os.makedirs(folder)
        url = f"https://source.unsplash.com/600x400/?{query}"
        response = requests.get(url, timeout=5)
        filename = f"{folder}/{query.replace(' ','_')}_{int(time.time())}.jpg"
        with open(filename, "wb") as f: f.write(response.content)
        if console: console.insert(tk.END, f"📸 Saved: {filename}\n")
        aura_voice.speak("Image downloaded.")
        os.startfile(folder)
    except: pass

# ================== PRO MAIL UI ==================
def send_email_core(to, sub, body, log):
    try:
        msg = EmailMessage(); msg.set_content(body); msg['Subject']=sub; msg['From']=SENDER_EMAIL; msg['To']=to
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
            s.login(SENDER_EMAIL, SENDER_PASSWORD); s.send_message(msg)
        log("✅ Email Sent."); aura_voice.speak("Sent.")
    except Exception as e: log(f"❌ Error: {e}"); aura_voice.speak("Failed.")

class EmailPopup:
    def __init__(self, parent, theme, log):
        self.top = tk.Toplevel(parent); self.top.geometry("600x500"); self.top.configure(bg=theme["bg"])
        self.log = log; p = theme["primary"]
        tk.Label(self.top, text="COMPOSE MESSAGE", bg="#111", fg=p, font=("Consolas", 10, "bold"), height=2).pack(fill="x")
        f = tk.Frame(self.top, bg=theme["bg"], padx=20, pady=20); f.pack(fill="both", expand=True)

        def row(txt):
            tk.Label(f, text=txt, bg=theme["bg"], fg="gray", font=("Consolas", 9)).pack(anchor="w")
            e = tk.Entry(f, bg="#1a1a1a", fg="white", font=("Consolas", 11), bd=0, insertbackground=p)
            e.pack(fill="x", pady=(0, 10), ipady=3); tk.Frame(f, bg=p, height=1).pack(fill="x", pady=(0, 15))
            return e
        
        self.to = row("RECIPIENT"); self.sub = row("SUBJECT")
        tk.Label(f, text="MESSAGE BODY", bg=theme["bg"], fg="gray", font=("Consolas", 9)).pack(anchor="w")
        self.txt = tk.Text(f, height=8, bg="#1a1a1a", fg="white", font=("Consolas", 11), bd=0, insertbackground=p)
        self.txt.pack(fill="both", expand=True, pady=5)
        
        btn = tk.Button(self.top, text="SEND", bg=p, fg="black", font=("Consolas", 11, "bold"), command=self.send, relief="flat", padx=20)
        btn.pack(pady=10)

    def send(self):
        to, sub, body = self.to.get(), self.sub.get(), self.txt.get("1.0", tk.END)
        if not to: return
        self.top.destroy(); self.log(f"📧 Sending to {to}...")
        threading.Thread(target=send_email_core, args=(to, sub, body, self.log)).start()

# ================== 🟢 MATRIX RAIN LOGIN 🟢 ==================
class GlitchLogin:
    def __init__(self, on_success):
        self.root = tk.Tk(); self.root.overrideredirect(True)
        w, h = 450, 580; x, y = (self.root.winfo_screenwidth()//2 - w//2), (self.root.winfo_screenheight()//2 - h//2)
        self.root.geometry(f"{w}x{h}+{x}+{y}"); self.root.configure(bg="#000")
        self.cb = on_success; self.is_reg = False
        self.c = "#00f2ea"

        # Background Canvas for Rain
        self.bg = tk.Canvas(self.root, bg="#000", highlightthickness=0)
        self.bg.pack(fill="both", expand=True)
        
        # Matrix Drops
        self.drops = [{"x": i*15, "y": random.randint(-500, 0), "s": random.randint(2, 5)} for i in range(30)]
        self.running = True; self.animate_rain()

        # Login Card (Floating on top)
        self.card_x, self.card_y = w//2, h//2
        self.draw_ui()

        self.root.bind('<Return>', self.act); self.root.mainloop()

    def draw_ui(self):
        # Card Background (Semi-transparent look simulation)
        self.bg.create_rectangle(35, 35, 415, 545, fill="#050505", outline=self.c, width=2, tags="ui")
        
        self.head = self.bg.create_text(225, 70, text="AURA OS v10.2", fill=self.c, font=("Consolas", 16, "bold"), tags="ui")
        self.sub = self.bg.create_text(225, 95, text="SECURE ACCESS", fill="gray", font=("Consolas", 9), tags="ui")

        self.u_var, self.p_var = tk.StringVar(), tk.StringVar()
        self.mk_inp(150, "IDENTITY", self.u_var)
        self.mk_inp(230, "KEY", self.p_var, True)

        self.btn = self.bg.create_rectangle(75, 350, 375, 400, outline=self.c, width=2, fill="#0d0d0d", tags="ui")
        self.txt = self.bg.create_text(225, 375, text="INITIATE LINK", fill=self.c, font=("Consolas", 12, "bold"), tags="ui")
        
        self.bg.tag_bind(self.btn, "<Button-1>", self.act); self.bg.tag_bind(self.txt, "<Button-1>", self.act)
        
        self.tog = self.bg.create_text(225, 440, text="[ NEW USER REGISTRATION ]", fill="gray", font=("Consolas", 10), tags="ui")
        self.bg.tag_bind(self.tog, "<Button-1>", self.tog_mode)

    def mk_inp(self, y, txt, var, pw=False):
        self.bg.create_text(75, y, text=txt, fill=self.c, anchor="w", font=("Consolas", 8), tags="ui")
        e = tk.Entry(self.root, textvariable=var, bg="#111", fg="white", bd=0, insertbackground=self.c, show="*" if pw else "", font=("Consolas", 12))
        e.place(x=75, y=y+15, width=300, height=30)
        self.bg.create_line(75, y+50, 375, y+50, fill="#333", width=2, tags="ui")

    def animate_rain(self):
        if not self.running: return
        self.bg.delete("rain")
        for d in self.drops:
            self.bg.create_text(d["x"], d["y"], text=random.choice("01"), fill="#003300", font=("Consolas", 10), tags="rain")
            self.bg.create_text(d["x"], d["y"]+15, text=random.choice("01"), fill="#00ff00", font=("Consolas", 10), tags="rain")
            d["y"] += d["s"]
            if d["y"] > 580: d["y"] = random.randint(-100, 0)
        self.bg.tag_raise("ui") # Keep UI on top of rain
        self.root.after(50, self.animate_rain)

    def tog_mode(self, e=None):
        self.is_reg = not self.is_reg
        if self.is_reg:
            self.bg.itemconfig(self.head, text="NEW IDENTITY"); self.bg.itemconfig(self.sub, text="DATABASE WRITE MODE")
            self.bg.itemconfig(self.txt, text="CREATE RECORD"); self.bg.itemconfig(self.tog, text="[ CANCEL ]", fill=self.c)
        else:
            self.bg.itemconfig(self.head, text="AURA OS v10.2"); self.bg.itemconfig(self.sub, text="SECURE ACCESS")
            self.bg.itemconfig(self.txt, text="INITIATE LINK"); self.bg.itemconfig(self.tog, text="[ NEW USER REGISTRATION ]", fill="gray")

    def act(self, e=None):
        u = self.u_var.get().strip().lower(); p = self.p_var.get().strip()
        if not u or not p: return

        if self.is_reg:
            if u in load_users() or u in ["redx", "captain demon"]: self.bg.itemconfig(self.txt, text="EXISTS")
            else:
                save_new_user(u, p); self.bg.itemconfig(self.txt, text="CREATED")
                self.bg.update(); time.sleep(1); self.ok(u)
        else:
            if (u == "redx" and p == "prime@007") or (u == "captain demon" and p == "captain"): self.ok(u)
            elif u in load_users() and load_users()[u] == p: self.ok(u)
            else: 
                self.bg.itemconfig(self.txt, text="DENIED"); self.bg.itemconfig(self.btn, outline="red")
                self.root.after(1000, lambda: [self.bg.itemconfig(self.txt, text="INITIATE LINK"), self.bg.itemconfig(self.btn, outline=self.c)])

    def ok(self, u):
        self.running = False
        self.bg.itemconfig(self.txt, text="GRANTED"); self.bg.itemconfig(self.btn, outline="#00ff00")
        self.bg.update(); time.sleep(0.5); self.root.destroy(); self.cb(u)

# ================== 🔴 REACTOR LOADER 🔴 ==================
class ReactorLoader:
    def __init__(self, user, cb):
        self.root = tk.Tk(); self.root.overrideredirect(True)
        w, h = 400, 400; x, y = (self.root.winfo_screenwidth()//2 - w//2), (self.root.winfo_screenheight()//2 - h//2)
        self.root.geometry(f"{w}x{h}+{x}+{y}"); self.root.configure(bg="#000")
        
        self.c = tk.Canvas(self.root, bg="black", highlightthickness=0); self.c.pack(fill="both", expand=True)
        self.color = THEMES.get(user, THEMES["gemini"])["primary"]
        self.angle = 0
        
        self.loading = True; self.animate(); 
        self.root.after(3500, lambda: [self.destroy_me(), cb()])
        self.root.mainloop()

    def destroy_me(self): self.loading = False; self.root.destroy()

    def animate(self):
        if not self.loading: return
        self.c.delete("all")
        cx, cy = 200, 200
        
        # Draw 3 Rotating Arcs
        for i, r in enumerate([60, 80, 100]):
            a = self.angle * (i+1)
            x0, y0 = cx - r, cy - r; x1, y1 = cx + r, cy + r
            self.c.create_arc(x0, y0, x1, y1, start=a, extent=60, outline=self.color, width=4, style="arc")
            self.c.create_arc(x0, y0, x1, y1, start=a+180, extent=60, outline=self.color, width=4, style="arc")

        self.c.create_text(cx, cy, text="LOADING", fill="white", font=("Courier", 12, "bold"))
        self.angle += 10
        self.root.after(50, self.animate)

# ================== MAIN APP (SCANNER HUD) ==================
def start_main_aura(username):
    t = THEMES.get(username, THEMES["gemini"])
    root = tk.Tk(); root.title(f"Aura Gen 3 - {username}"); root.geometry("900x650"); root.configure(bg=t["bg"])

    # === SCANNER GRID BACKGROUND ===
    bg = tk.Canvas(root, bg=t["bg"], highlightthickness=0); bg.place(x=0, y=0, relwidth=1, relheight=1)
    
    # Draw Static Grid
    gc = "#ccc" if username not in ["redx", "captain demon"] else "#111"
    for i in range(0, 900, 40): bg.create_line(i, 0, i, 650, fill=gc)
    for i in range(0, 650, 40): bg.create_line(0, i, 900, i, fill=gc)

    # Scanner Line Animation
    scan_line = bg.create_line(0, 0, 900, 0, fill=t["primary"], width=2)
    def scan_anim(y=0, d=2):
        bg.coords(scan_line, 0, y, 900, y)
        if y > 650 or y < 0: d = -d
        root.after(20, lambda: scan_anim(y+d, d))
    scan_anim()

    # UI Components
    tk.Label(root, text=f"⚡ AURA OS: {username.upper()} ⚡", fg=t["primary"], bg=t["bg"], font=("Consolas", 18, "bold")).place(x=20, y=20)
    
    # Console
    cf = tk.Frame(root, bg=t["bg"], highlightbackground=t["primary"], highlightthickness=1); cf.place(x=20, y=100, width=600, height=400)
    c_bg = "#f0f2f5" if username == "gemini" else "#080808"
    console = scrolledtext.ScrolledText(cf, bg=c_bg, fg=t["text"], font=("Consolas", 10), bd=0); console.pack(fill="both", expand=True)

    # Sidebar
    sf = tk.Frame(root, bg=t["bg"]); sf.place(x=640, y=100, width=240, height=400)
    def mk_wid(txt, y):
        f = tk.Frame(sf, bg=c_bg, highlightbackground=t["primary"], highlightthickness=1); f.place(x=0, y=y, width=240, height=80)
        tk.Label(f, text=txt, fg="gray", bg=c_bg, font=("Consolas", 8)).pack(anchor="w", padx=5)
        v = tk.Label(f, text="ACTIVE", fg=t["primary"], bg=c_bg, font=("Consolas", 14, "bold")); v.pack()
        return v
    wid_mic = mk_wid("AUDIO SENSOR", 90); mk_wid("SYSTEM STATUS", 0)

    # Input
    inf = tk.Frame(root, bg=t["bg"], highlightbackground=t["primary"], highlightthickness=1); inf.place(x=20, y=520, width=860, height=60)
    entry = tk.Entry(inf, bg=c_bg, fg=t["text"], font=("Consolas", 14), bd=0, insertbackground=t["primary"]); entry.place(x=20, y=15, width=700, height=30)
    lbl_st = tk.Label(inf, text="[ READY ]", fg="gray", bg=t["bg"], font=("Consolas", 10)); lbl_st.place(x=750, y=20)

    def log(txt): console.insert(tk.END, f"{txt}\n"); console.see(tk.END)

    def process_command(cmd):
        log(f"> {cmd}")
        fixed = cmd.lower().replace("check review", "chakravyuh").replace("have a menu", "abhimanyu")

        if any(x in fixed for x in ["search", "find", "look up"]):
            topic = fixed.replace("search for", "").replace("search", "").replace("find", "").replace("look up", "").strip()
            if topic:
                log(f"🌐 Opening Google: {topic}")
                webbrowser.open(f"https://www.google.com/search?q={topic}")
                aura_voice.speak(f"Searching for {topic}")
            else: aura_voice.speak("What should I search for?")

        elif "email" in fixed: aura_voice.speak("Opening mail."); EmailPopup(root, t, log)
        elif "shutdown" in fixed: aura_voice.speak("Terminating."); root.destroy()
        elif "download image" in fixed: q = fixed.replace("download image", "").strip(); download_image(q, console)
        else: aura_voice.speak("Command accepted.")

    entry.bind('<Return>', lambda e: [process_command(entry.get()), entry.delete(0, tk.END)])

    def voice():
        r = sr.Recognizer()
        with sr.Microphone(device_index=MIC_DEVICE_ID) as s:
            r.adjust_for_ambient_noise(s); wid_mic.config(text="LISTENING...")
            while True:
                try: 
                    txt = r.recognize_google(r.listen(s)).lower()
                    entry.delete(0, tk.END); entry.insert(0, txt); lbl_st.config(text="[ HEARD ]", fg=t["primary"])
                    root.after(500, lambda: process_command(txt))
                except: lbl_st.config(text="[ IDLE ]", fg="gray")
    
    threading.Thread(target=voice, daemon=True).start()
    aura_voice.speak(t["welcome"])
    root.mainloop()

if __name__ == "__main__":
    if os.name == "nt": os.system("cls")
    print("🔮 AURA GEN 3: LIVING INTERFACE 🔮")
    GlitchLogin(lambda user: ReactorLoader(user, lambda: start_main_aura(user)))