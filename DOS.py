from tkinter import *
from tkinter import messagebox, filedialog, ttk
import threading
import requests
import datetime
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Global Variables 📌
log_data = []
stop_attack = False
global_success_count = [0]
global_fail_count = [0]
graph_updater_running = [False]
x_data, y_data = [0], [0]

# Root Window 🔐
root = Tk()
root.title("DoS Simulator by Dilshan")
root.geometry("960x720")
root.configure(bg="black")
root.resizable(True, True)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# === HEADER EKA ¯\_(ツ)_/¯
header = Label(root, text="DoS Simulator by #Dilshan", font=("Helvetica", 15, "bold"), bg="black", fg="#D3D3D3")
header.grid(row=0, column=0, sticky="W", padx=10, pady=5)

# === TOP SECTION ;)
top_frame = Frame(root, bg="black")
top_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=(5, 0))
top_frame.grid_columnconfigure(0, weight=2)  
top_frame.grid_columnconfigure(1, weight=1)
top_frame.grid_columnconfigure(2, weight=1)
top_frame.grid_rowconfigure(0, weight=1)

# 📈 Graph (LEFT) ☜(ﾟヮﾟ☜)
graph_frame = Frame(top_frame, bg="black")
graph_frame.grid(row=0, column=0, sticky="nsew", padx=(40, 5), pady=5)

fig1 = Figure(figsize=(3.6, 2.5), dpi=100)
fig1.patch.set_facecolor('black')
ax1 = fig1.add_subplot(111)
ax1.set_facecolor('black')
ax1.set_title("📈 Success Requests Over Time", color="white")
ax1.set_xlabel("Seconds", color="white")
ax1.set_ylabel("Success Count", color="white")
ax1.tick_params(axis='x', colors='white')
ax1.tick_params(axis='y', colors='white')
line, = ax1.plot(x_data, y_data, 'lime')
canvas1 = FigureCanvasTkAgg(fig1, master=graph_frame)
canvas1.draw()
canvas1.get_tk_widget().pack(fill=BOTH, expand=True)

# 🎯 Controls (CENTER) ᓚᘏᗢ
form_frame = Frame(top_frame, bg="black")
form_frame.grid(row=0, column=1, sticky="nsew", padx=(15, 20), pady=5)

def add_label(text):
    Label(form_frame, text=text, bg="black", fg="white").pack(pady=2)

add_label("🎯 Target URL:")
entry_url = Entry(form_frame, width=38, bg="#222", fg="white", insertbackground="white")
entry_url.pack()

add_label("🔁 Threads:")
entry_threads = Entry(form_frame, bg="#222", fg="white", insertbackground="white")
entry_threads.insert(0, "5")
entry_threads.pack()

add_label("⏱️ Delay (seconds):")
entry_delay = Entry(form_frame, bg="#222", fg="white", insertbackground="white")
entry_delay.insert(0, "0.5")
entry_delay.pack()

add_label("📦 Total Requests per Thread:")
entry_total = Entry(form_frame, bg="#222", fg="white", insertbackground="white")
entry_total.insert(0, "10")
entry_total.pack()

btn_start = Button(form_frame, text="🚀 Start", command=lambda: start_attack(), bg="#4CAF50", fg="white")
btn_start.pack(pady=3)
btn_stop = Button(form_frame, text="⛔ Stop", command=lambda: stop_attack_func(), state=DISABLED, bg="#f44336", fg="white")
btn_stop.pack(pady=3)
btn_save = Button(form_frame, text="💾 Save Log", command=lambda: save_log(), bg="#555", fg="white")
btn_save.pack(pady=3)
btn_clear = Button(form_frame, text="🧹 Clear Log", command=lambda: clear_log(), bg="#555", fg="white")
btn_clear.pack(pady=3)

# 🥧 Pie Chart (RIGHT) (☞ﾟヮﾟ)☞
pie_frame = Frame(top_frame, bg="black")
pie_frame.grid(row=0, column=2, sticky="nsew", padx=(10, 60), pady=5)

fig2 = Figure(figsize=(3.6, 2.5), dpi=100)
fig2.patch.set_facecolor('black')
ax2 = fig2.add_subplot(111)
pie_labels = ['✅ Success', '❌ Fail']
pie_colors = ['green', 'red']
ax2.set_facecolor("black")
ax2.set_title("🥧 Attack Result Summary", color="white")
ax2.pie([0.0001, 0.0001], labels=pie_labels, colors=pie_colors,
        autopct='%1.1f%%', startangle=90, textprops={'color': 'white'})
canvas2 = FigureCanvasTkAgg(fig2, master=pie_frame)
canvas2.draw()
canvas2.get_tk_widget().pack(fill=BOTH, expand=True)

# === Terminal Log SHOW SETUP (●'◡'●)
log_frame = Frame(root, bg="black")
log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

style = ttk.Style()
style.theme_use("default")
style.configure("Purple.Vertical.TScrollbar", background="#800080", troughcolor="#1e1e1e", arrowcolor="white")

scrollbar = ttk.Scrollbar(log_frame, orient=VERTICAL, style="Purple.Vertical.TScrollbar")
log = Text(log_frame, height=16, yscrollcommand=scrollbar.set, bg="#1e1e1e", fg="white", insertbackground='white')
scrollbar.config(command=log.yview)
scrollbar.pack(side=RIGHT, fill=Y)
log.pack(side=LEFT, fill=BOTH, expand=True)

log.tag_config("success", foreground="lime")
log.tag_config("error", foreground="#FF4444")

# === Functions 🎆
def reset_graph_labels():
    ax1.set_facecolor('black')
    ax1.set_title("📈 Success Requests Over Time", color="white")
    ax1.set_xlabel("Seconds", color="white")
    ax1.set_ylabel("Success Count", color="white")
    ax1.tick_params(axis='x', colors='white')
    ax1.tick_params(axis='y', colors='white')

def safe_pie():
    success = global_success_count[0]
    fail = global_fail_count[0]
    pie_data = [success, fail] if (success + fail) > 0 else [0.0001, 0.0001]
    ax2.clear()
    ax2.set_facecolor("black")
    ax2.set_title("🥧 Attack Result Summary", color="white")
    ax2.pie(pie_data, labels=pie_labels, colors=pie_colors,
            autopct='%1.1f%%', startangle=90, textprops={'color': 'white'})
    canvas2.draw()

def update_graphs():
    start_time = time.time()
    while graph_updater_running[0]:
        elapsed = int(time.time() - start_time)
        x_data.append(elapsed)
        y_data.append(global_success_count[0])
        if len(x_data) > 20:
            x_data.pop(0)
            y_data.pop(0)
        line.set_data(x_data, y_data)
        ax1.relim()
        ax1.autoscale_view()
        canvas1.draw()
        safe_pie()
        time.sleep(1)

def start_graph_thread():
    if not graph_updater_running[0]:
        graph_updater_running[0] = True
        threading.Thread(target=update_graphs, daemon=True).start()

def stop_graph_thread():
    graph_updater_running[0] = False

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

        btn_start.config(state=DISABLED)
        btn_stop.config(state=NORMAL)
        global_success_count[0] = 0
        global_fail_count[0] = 0
        x_data.clear()
        y_data.clear()
        x_data.append(0)
        y_data.append(0)
        start_graph_thread()

        completed_threads = [0]

        def attack():
            for _ in range(total):
                if stop_attack:
                    break
                try:
                    r = requests.get(url, timeout=5)
                    msg = f"[{r.status_code}] -> {url}"
                    log.insert(END, msg + "\n", "success")
                    log_data.append(msg)
                    log.yview_moveto(1.0)
                    global_success_count[0] += 1
                except Exception as e:
                    err = f"[ERROR] -> {str(e)}"
                    log.insert(END, err + "\n", "error")
                    log_data.append(err)
                    log.yview_moveto(1.0)
                    global_fail_count[0] += 1
                time.sleep(delay)

            completed_threads[0] += 1
            if completed_threads[0] == threads:
                btn_start.config(state=NORMAL)
                btn_stop.config(state=DISABLED)
                stop_graph_thread()
                messagebox.showinfo("Done", f"✅ Done!\nSuccess: {global_success_count[0]}\nFail: {global_fail_count[0]}")

        for _ in range(threads):
            threading.Thread(target=attack).start()

    except Exception as e:
        messagebox.showerror("Error", str(e))
        btn_start.config(state=NORMAL)
        btn_stop.config(state=DISABLED)
#STOP ATTACK FUNCTION
def stop_attack_func():
    global stop_attack
    stop_attack = True
    btn_start.config(state=NORMAL)
    btn_stop.config(state=DISABLED)
    stop_graph_thread()
#SAVE LOG FUNCTION
def save_log():
    if not log_data:
        messagebox.showwarning("Warning", "No logs to save.")
        return
    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=f"log_{now}.txt")
    if file_path:
        with open(file_path, "w") as f:
            for line in log_data:
                f.write(line + "\n")
        messagebox.showinfo("Saved", f"Saved to " + file_path)
#LOG CLEAR PLACE
def clear_log():
    log.delete(1.0, END)
    log_data.clear()
    global_success_count[0] = 0
    global_fail_count[0] = 0
    x_data.clear()
    y_data.clear()
    x_data.append(0)
    y_data.append(0)
    ax1.clear()
    reset_graph_labels()
    global line
    line, = ax1.plot(x_data, y_data, 'lime')
    ax1.relim()
    ax1.autoscale_view()
    canvas1.draw()
    safe_pie()

# === Mainloop
root.mainloop()

# === END (IWARAI) 🎃
