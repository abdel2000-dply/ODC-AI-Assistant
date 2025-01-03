import tkinter as tk
from tkinter import font
from itertools import cycle
import subprocess
import os  # Add this import

# Check if DISPLAY environment variable is set
if not os.environ.get('DISPLAY'):
    os.environ['DISPLAY'] = ':0'

root = tk.Tk()
root.title("AI Assistant Interface")
root.attributes('-fullscreen', True)
root.geometry("640x480")
root.configure(bg="black")

button_font = font.Font(family="Monospace", size=16, weight="bold")
typing_font = ("Monospace", 45)

# Define functions for each interface
def show_first_interface():
    for widget in root.winfo_children():
        widget.destroy()

    # Create a label to display the text with typing effect
    def typing_effect(label, lines, line_index=0, char_index=0, show_cursor=True):
        if line_index < len(lines):
            text = lines[line_index]
            if char_index < len(text):
                label.config(text="\n".join(lines[:line_index]) + "\n" + text[:char_index+1] + ("|" if show_cursor else ""))
                label.after(150, typing_effect, label, lines, line_index, char_index+1, not show_cursor)
            else:
                label.after(100, typing_effect, label, lines, line_index+1, 0, True)
        else:
            label.after(2000, typing_effect, label, lines, 0, 0, True)

    typing_label = tk.Label(root, text="", font=typing_font, fg="orange", bg="black", anchor="center")
    typing_label.pack(expand=True)

    # The text split into three lines
    lines = ["Hello", "I'm ODC", "AI Assistant"]

    # Start the typing effect
    typing_effect(typing_label, lines)

    # Add the "Let's Chat" button
    chat_button = tk.Button(root, text="Let's Chat", font=button_font, command=open_terminal, bg="orange", fg="black", bd=0, highlightthickness=0, activebackground="orange", activeforeground="black")
    chat_button.pack(pady=20, ipadx=20, ipady=10)

def open_terminal():
    venv_activate = os.path.join(os.getcwd(), 'venv', 'bin', 'activate')
    command = f"source {venv_activate} && python main.py"
    subprocess.Popen(command, shell=True, executable='/bin/bash')

def show_language_interface():
    for widget in root.winfo_children():
        widget.destroy()

    button_frame = tk.Frame(root, bg="black")
    button_frame.pack(expand=True, pady=50)

    button_width = 10

    button_ar = tk.Button(button_frame, text="Arabic", font=button_font, width=button_width, command=lambda: show_talking_interface("AR"), bg="orange", fg="black", bd=0, highlightthickness=0, activebackground="orange", activeforeground="black")
    button_ar.pack(pady=10, ipady=10)

    button_fr = tk.Button(button_frame, text="French", font=button_font, width=button_width, command=lambda: show_talking_interface("FR"), bg="orange", fg="black", bd=0, highlightthickness=0, activebackground="orange", activeforeground="black")
    button_fr.pack(pady=10, ipady=10)

    button_eng = tk.Button(button_frame, text="English", font=button_font, width=button_width, command=lambda: show_talking_interface("ENG"), bg="orange", fg="black", bd=0, highlightthickness=0, activebackground="orange", activeforeground="black")
    button_eng.pack(pady=10, ipady=10)

def show_talking_interface(language):
    for widget in root.winfo_children():
        widget.destroy()

    # Simulate moving AI talking animation
    ellipses = [
        [" ●     ", "   ●   ", "    ●  "],
        ["   ●   ", "    ●  ", " ●     "]
    ]
    animation_frames = cycle(ellipses[0] + ellipses[1])

    def animate_face():
        text = next(animation_frames)
        talk_label.config(text=text)
        root.after(300, animate_face)

    talk_label = tk.Label(root, text="", font=("Monospace", 100), bg="black", fg="orange")
    talk_label.pack(expand=True)
    animate_face()

    # Add typing effect for the "Talking..." text
    def typing_effect(label, text, char_index=0, show_cursor=True):
        if char_index < len(text):
            label.config(text=text[:char_index+1] + ("|" if show_cursor else ""))
            label.after(150, typing_effect, label, text, char_index+1, not show_cursor)

    typing_label = tk.Label(root, text="", font=("Monospace", 20), fg="orange", bg="black")
    typing_label.place(relx=0.5, rely=0.9, anchor="center")
    typing_effect(typing_label, "Talking...")

    # Add the "Talk" button
    talk_button = tk.Button(root, text="Talk", font=button_font, command=show_listening_interface, bg="orange", fg="black", bd=0, highlightthickness=0, activebackground="orange", activeforeground="black", relief="flat")
    talk_button.place(relx=0.98, rely=0.02, anchor="ne")

def show_listening_interface():
    for widget in root.winfo_children():
        widget.destroy()

    # Create the "eye" animation with two dots that appear/disappear together
    blink_states = ["   ●   ", "       "]  # Two dots appearing and disappearing together
    animation_frames = cycle(blink_states)

    def animate_face():
        text = next(animation_frames)
        listen_label.config(text=text)
        root.after(500, animate_face)  # Adjust this to control the blink speed

    listen_label = tk.Label(root, text="", font=("Monospace", 120), bg="black", fg="white")
    listen_label.pack(expand=True)
    animate_face()

    # Add typing effect for the "Listening..." text
    def typing_effect(label, text, char_index=0, show_cursor=True):
        if char_index < len(text):
            label.config(text=text[:char_index+1] + ("|" if show_cursor else ""))
            label.after(150, typing_effect, label, text, char_index+1, not show_cursor)

    typing_label = tk.Label(root, text="", font=("Monospace", 20), fg="white", bg="black")
    typing_label.place(relx=0.5, rely=0.9, anchor="center")
    typing_effect(typing_label, "Listening...")

    # Add the "Exit" button
    exit_button = tk.Button(root, text="Exit", font=button_font, command=show_first_interface, bg="white", fg="black", bd=0, highlightthickness=0, activebackground="black", activeforeground="white", relief="flat")
    exit_button.place(relx=0.98, rely=0.02, anchor="ne")

# Start with the first interface
show_first_interface()

# Run the application
root.mainloop()
