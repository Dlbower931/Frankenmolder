import tkinter as tk

# Create the main window
window = tk.Tk()
window.title("My First Tkinter App")

# Create a label
label = tk.Label(window, text="Hello, World!")
label.pack()

# Start the event loop
window.mainloop()