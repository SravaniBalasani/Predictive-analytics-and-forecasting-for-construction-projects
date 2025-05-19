import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
root = tk.Tk()
root.title("Construction Progress Monitoring Dashboard")
root.geometry("1000x700")
comparison_log = []
planned_progress = 70  
actual_progress = 0
different_label = None  
image_label = tk.Label(root)
status_label = tk.Label(root, text="", padx=10, pady=10)
chart_frame = tk.Frame(root)
report_text = tk.Text(root, height=10, width=80)
def mse(img1, img2):
    h, w = img1.shape
    diff = cv2.subtract(img1, img2)
    err = np.sum(diff ** 2)
    mse_val = err / float(h * w)
    return mse_val, diff
def update_report(error):
    global actual_progress
    actual_progress = max(0, 100 - error / 100) 
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log = f"[{timestamp}] MSE Error: {error:.2f}, Estimated Actual Progress: {actual_progress:.2f}%\n"
    comparison_log.append(log)
    report_text.delete(1.0, tk.END)
    report_text.insert(tk.END, "".join(comparison_log))
    update_chart()
def update_chart():
    for widget in chart_frame.winfo_children():
        widget.destroy()
    fig, ax = plt.subplots(figsize=(4, 3))
    categories = ['Planned', 'Actual']
    values = [planned_progress, actual_progress]
    ax.bar(categories, values, color=['blue', 'green'])
    ax.set_ylim(0, 100)
    ax.set_title('Progress Comparison')
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
def display_image(file_path):
    image = Image.open(file_path)
    image.thumbnail((400, 400))
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.photo = photo
def open_image():
    global different_label
    file_path1 = filedialog.askopenfilename(title="Open Image File 1")
    file_path2 = filedialog.askopenfilename(title="Open Image File 2")
    if not file_path1 or not file_path2:
        return
    try:
        img1 = cv2.imread(file_path1)
        img2 = cv2.imread(file_path2)
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        # Resize img2 to match img1
        img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))
    except Exception as e:
        status_label.config(text=f"Error loading images: {e}")
        return
    error, diff = mse(img1_gray, img2_gray)
    update_report(error)
    display_image(file_path1)
    diiferent_normalized = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    different_colored = cv2.applyColorMap(diiferent_normalized.astype(np.uint8), cv2.COLORMAP_JET)
    different_pil = Image.fromarray(cv2.cvtColor(different_colored, cv2.COLOR_BGR2RGB))
    different_pil.thumbnail((400, 400))
    different_photo = ImageTk.PhotoImage(different_pil)
    if different_label is None:
        different_label = tk.Label(root)
        different_label.pack()
    different_label.config(image=different_photo)
    different_label.image = different_photo
    status_label.config(text=f"Image Comparison Done. MSE: {error:.2f}")
header = tk.Label(root, text="Construction Site Monitoring Dashboard", font=("Arial", 20, "bold"), fg="darkblue")
header.pack(pady=10)
open_button = tk.Button(root, text="Compare Images", command=open_image, bg="lightblue", font=("Arial", 12))
open_button.pack(pady=5)
image_label.pack()
status_label.pack()
chart_frame.pack(pady=10)
report_label = tk.Label(root, text="Progress Report", font=("Arial", 14, "bold"))
report_label.pack()
report_text.pack(pady=5)
root.mainloop()