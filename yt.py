import os
import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import yt_dlp
import threading
import sys

def update_progress_bar(percent):
    progress_bar['value'] = percent
    progress_label.config(text=f"{percent:.2f}%")
    root.update_idletasks()

def download_hook(d):
    if d['status'] == 'downloading':
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded_bytes = d.get('downloaded_bytes', 0)
        if total_bytes:
            percent = downloaded_bytes / total_bytes * 100
            update_progress_bar(percent)
    elif d['status'] == 'finished':
        update_progress_bar(100)
        title_label.config(text="Download concluído!")

def download_from_youtube(url, download_directory, download_type, ffmpeg_location=None):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', 'Vídeo/Áudio')
            title_label.config(text=f"Baixando: {title}")

        if download_type == 'video':
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'merge_output_format': 'mp4',
                'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s'),
                'progress_hooks': [download_hook],
                'postprocessors': [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': 'mp4'},  # Converte para mp4
                ],
            }
        else:  # Áudio
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s'),
                'progress_hooks': [download_hook],
            }

        if ffmpeg_location:
            ydl_opts['ffmpeg_location'] = ffmpeg_location

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        messagebox.showinfo("Sucesso", f"{'Vídeo' if download_type == 'video' else 'Áudio'} baixado com sucesso!")
        progress_bar['value'] = 0  # Resetar a barra de progresso ao terminar
        progress_label.config(text="")
        title_label.config(text="")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao baixar {'o vídeo' if download_type == 'video' else 'o áudio'}: {str(e)}")
        progress_bar['value'] = 0  # Resetar a barra de progresso em caso de erro
        progress_label.config(text="")
        title_label.config(text="")

def start_download():
    url = url_entry.get()
    download_directory = directory_entry.get()
    ffmpeg_location = os.path.join(sys._MEIPASS, 'ffmpeg.exe') if hasattr(sys, '_MEIPASS') else 'ffmpeg.exe'
    download_type = download_type_var.get()
    if not url or not download_directory:
        messagebox.showwarning("Aviso", "Por favor, insira a URL e o diretório de download.")
        return
    threading.Thread(target=download_from_youtube, args=(url, download_directory, download_type, ffmpeg_location)).start()

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, directory)

# Criação da interface
root = tk.Tk()
root.title("Downloader de Vídeo ou Áudio do YouTube")

# Widgets
tk.Label(root, text="URL do YouTube:").grid(row=0, column=0, padx=10, pady=10)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Diretório de Download:").grid(row=1, column=0, padx=10, pady=10)
directory_entry = tk.Entry(root, width=50)
directory_entry.grid(row=1, column=1, padx=10, pady=10)
browse_button = tk.Button(root, text="Procurar", command=browse_directory)
browse_button.grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text="Tipo de Download:").grid(row=2, column=0, padx=10, pady=10)
download_type_var = tk.StringVar(value="video")
radio_video = tk.Radiobutton(root, text="Vídeo", variable=download_type_var, value="video")
radio_audio = tk.Radiobutton(root, text="Áudio", variable=download_type_var, value="audio")
radio_video.grid(row=2, column=1, padx=10, pady=5, sticky='w')
radio_audio.grid(row=2, column=1, padx=10, pady=5, sticky='e')

download_button = tk.Button(root, text="Baixar", command=start_download)
download_button.grid(row=3, column=0, columnspan=3, pady=10)

# Label para mostrar o título do arquivo em download
title_label = tk.Label(root, text="")
title_label.grid(row=4, column=0, columnspan=3)

# Barra de progresso
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

# Label de progresso
progress_label = tk.Label(root, text="")
progress_label.grid(row=6, column=0, columnspan=3)

# Execução da interface
root.mainloop()
