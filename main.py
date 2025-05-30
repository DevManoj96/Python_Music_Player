import tkinter as tk
from tkinter import messagebox, filedialog
from pygame import mixer
from mutagen.mp3 import MP3
from mutagen.wave import WAVE
import time
import os 

mixer.init()
folder_path = ""
mp3_paths = []
current_time = 0
total_time = 0

is_playing = False
is_paused = False
is_dark = False

def toggle_theme():
    global is_dark
    bg_color = "#222222" if not is_dark else "white"
    fg_color = "white" if not is_dark else "black"
    button_bg = "#333333" if not is_dark else "lightgray"
    listbox_bg = "#1e1e1e" if not is_dark else "white"

    root.configure(bg=bg_color)

    for widget in root.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=bg_color, fg=fg_color)
        elif isinstance(widget, tk.Button):
            widget.configure(bg=button_bg, fg=fg_color, activebackground=bg_color, activeforeground=fg_color)
        elif isinstance(widget, tk.Listbox):
            widget.configure(bg=listbox_bg, fg=fg_color, selectbackground="#444444" if not is_dark else "#cccccc")

    is_dark = not is_dark

def update_time_label():
    if is_playing and not is_paused:
        global current_time
        current_time += 1
        current = time.strftime('%M:%S', time.gmtime(current_time))
        total = time.strftime('%M:%S', time.gmtime(total_time))
        time_label.config(text=f"{current} / {total}")
        
        if mixer.music.get_busy():
            root.after(1000, update_time_label)
        else:
            stop_music()
    elif is_playing and is_paused:
        root.after(1000, update_time_label)

def pause_resume_music():
    global is_paused
    if mixer.music.get_busy() or is_paused:
        if not is_paused:
            mixer.music.pause()
            update_label.config(text="Music paused")
            is_paused = True
        else:
            mixer.music.unpause()
            update_label.config(text="Music resumed")
            is_paused = False
            update_time_label()

def open_folder():
    global folder_path
    box.delete(0, tk.END)
    folder_path = filedialog.askdirectory()
    if folder_path:
        messagebox.showinfo("Folder Selected", f"Selected: {folder_path}")
        load_music(folder_path)
    else:
        messagebox.showinfo("No Selection", "No folder selected")

def load_music(folder_path):
    try:
        files = os.listdir(folder_path)
        mp3_files = [f for f in files if f.lower().endswith('.mp3') or f.lower().endswith('.wav')]

        global mp3_paths
        mp3_paths = []

        for mp3_file in sorted(mp3_files):
            box.insert(tk.END, mp3_file)
            mp3_paths.append(os.path.join(folder_path, mp3_file))

        if not mp3_files:
            box.insert(tk.END, "No Music files found")

    except Exception as e:
        box.insert(tk.END, f"[Error]: {str(e)}")      

def play_music():
    global current_time, is_playing, is_paused, total_time

    selection = box.curselection()
    if not selection:
        messagebox.showwarning("No Selection", "Please select a music file to play")
        return

    index = selection[0]
    music = box.get(index)
    mp3_path = mp3_paths[index]

    if is_playing:
        mixer.music.stop()
        
    mixer.music.load(mp3_path)
    mixer.music.set_volume(1)
    mixer.music.play()

    current_time = 0
    is_paused = False
    is_playing = True
    update_label.config(text=f"▶ Playing: {index + 1}. {music}")

    # Try pygame method first for getting duration
    try:
        import pygame
        sound = pygame.mixer.Sound(mp3_path)
        total_time = int(sound.get_length())
        
        current = time.strftime('%M:%S', time.gmtime(current_time))
        total = time.strftime('%M:%S', time.gmtime(total_time))
        time_label.config(text=f"{current} / {total}")
        
        update_time_label()
        
    except Exception:
        # Fallback to mutagen method
        try:
            if mp3_path.lower().endswith(".mp3"):
                audio = MP3(mp3_path)
            elif mp3_path.lower().endswith(".wav"):
                audio = WAVE(mp3_path)
            else:
                audio = None
                
            if audio:
                total_time = int(audio.info.length)
            else:
                total_time = 0
                
            current = time.strftime('%M:%S', time.gmtime(current_time))
            total = time.strftime('%M:%S', time.gmtime(total_time))
            time_label.config(text=f"{current} / {total}")
            
            update_time_label()
            
        except Exception:
            time_label.config(text="00:00 / 00:00")
            total_time = 0

def stop_music():
    global is_playing, current_time, is_paused
    mixer.music.stop()
    update_label.config(text="Music Stopped")
    box.selection_clear(0, tk.END)  
    is_playing = False
    is_paused = False
    current_time = 0
    time_label.config(text="00:00 / 00:00")

def about():
    info = """Python Music Player v1.0

Developed using Python with tkinter GUI framework

Features:
• Play MP3 and WAV audio files
• Pause and resume playback
• Stop music playback
• Browse and select music folders
• Real-time playback timer
• Dark/Light theme toggle
• Clean and intuitive interface

Libraries Used:
• tkinter - GUI framework
• pygame - Audio playback engine
• mutagen - Audio metadata extraction
• os & time - System utilities

Controls:
• Use Options menu to select music folder
• Click on any track to select it
• Use Play button to start playback
• Pause/Resume for playback control
• Stop to end current track

Enjoy your music! 🎵"""
    
    messagebox.showinfo("About US", info)

root = tk.Tk()
root.title("--- Python Music Player ---")
root.geometry('800x600')
root.resizable(True, True)

menubar = tk.Menu(root)
root.config(menu=menubar)

options_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="Options", menu=options_menu)

options_menu.add_command(label="Open Music Folder", command=open_folder)
options_menu.add_command(label="Toggle Theme", command=toggle_theme)
options_menu.add_separator()
options_menu.add_command(label="About", command=about)

heading1 = tk.Label(root, text="Welcome to Python Music Player", font=("Arial", 13, "bold"))
heading1.pack(pady=5)

label1 = tk.Label(root, text="--- Available Music ---", font=("Arial", 12))
label1.pack(pady=5)

box = tk.Listbox(root, width=65, height=10)
box.pack(pady=5)

update_label = tk.Label(root, text="", font=("Arial", 12))
update_label.pack(pady=5)

time_label = tk.Label(root, text="00:00 / 00:00", font=("Arial", 12))
time_label.pack(pady=5)

play_btn = tk.Button(root, text="Play", command=play_music, font=("Arial", 12), width=20, height=2)
play_btn.pack(pady=5)

pause_resume_btn = tk.Button(root, text="Pause/Resume", command=pause_resume_music, font=("Arial", 12), width=20, height=2)
pause_resume_btn.pack(pady=5)

stop_btn = tk.Button(root, text="Stop", command=stop_music, font=("Arial", 12), width=20, height=2)
stop_btn.pack(pady=5)

exit_btn = tk.Button(root, text="Exit", command=root.quit, font=("Arial", 12), width=20, height=2)
exit_btn.pack(pady=5)

if __name__ == '__main__':
    messagebox.showinfo("Welcome", "Select your music folder from the Options > Open Music Folder")
    root.mainloop()