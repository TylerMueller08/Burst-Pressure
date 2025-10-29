import tkinter as tk
from RecorderController import RecorderController

controller = RecorderController()

def toggleTrial():
    button1.config(state="disabled")
    controller.toggle()
    button1.config(text="Stop Trial" if controller.recording else "Start Trial", state="normal")

root = tk.Tk()
root.title("Burst Pressure Manager")
root.geometry("480x360")
root.config(bg="#232323")

frame = tk.Frame(root, borderwidth=5, relief=tk.RIDGE, bg="#393939", width=480, height=360)

text= tk.Label(
    frame,
    text="Burst Pressure Manager",
    fg="#FFFFFF",
    bg="#393939",
    font=("Verdana", 16)
).pack(anchor="n", pady=10)

button1 = tk.Button(frame, text="Start Trial", command=toggleTrial, bg="gray", fg="#FFFFFF", borderwidth=3, relief=tk.RIDGE, font=("Verdana", 14), width=12)
button1.pack(padx=20, pady=10)

frame.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)

root.mainloop()