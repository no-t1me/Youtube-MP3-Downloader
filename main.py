import tkinter
from calendar import error
from ctypes import windll, byref, sizeof, c_int
import ctypes
import threading
import tkinter as tk
import webbrowser
from ftplib import all_errors
from pathlib import Path
import yt_dlp
import subprocess
import platform
from tkinter.ttk import *
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import font

#Increase quality of text
ctypes.windll.shcore.SetProcessDpiAwareness(1)

#Opening download folder
def OpenFolder():
    open_path = "explorer" + " " + save_path + "\\Youtube Downloader"
    subprocess.Popen(open_path)

#Selfpromo
def OpenLink():
    webbrowser.open("https://github.com/no-t1me")

#Rightclick paste menu
class Rightclick:
    def __init__(self, e):
        command = "Paste"
        menu = tk.Menu(None, tearoff=0, takefocus=0)

        menu.add_command(label=command, command=lambda e=e, command=command:self.ClickCommand(e, command))

        menu.tk_popup(e.x_root + 40, e.y_root + 10, entry="0")

    @staticmethod
    def ClickCommand(e, cmd):
        e.widget.event_generate(f'<<{cmd}>>')

#Hiding and showing buttons to stop the impostor
def HideButtons():
    button.config(state="disabled")
    download_from_file.config(state="disabled")

def ShowButtons():
    button.config(state="normal")
    download_from_file.config(state="normal")

def ResetLabels():
    status_label.configure(text="")
    status_label2.configure(text="")

def OpenErrors():
    error_popup = Toplevel(root)
    error_popup.configure(bg="#292929")
    error_popup.geometry("1400x600")
    error_popup.title("List of errors")
    scrollbar = Scrollbar(error_popup)
    error_text = Listbox(error_popup,
                      yscrollcommand = scrollbar.set,
                      justify="left",
                      bg="#292929",
                      fg="red",
                      height=200,
                      width=600,
                      selectmode=tk.EXTENDED,
                     )
    for i in all_errors:
        error_text.insert(END, i)
    scrollbar.pack(side=RIGHT,
                   fill=Y
                   )
    scrollbar.config(command=error_text.yview)
    error_text.pack()
    WindowCenter(error_popup)

def SetEndLabel(is_single_link):
    global correct_download_count
    global number_of_links
    status_label.config(text="Cleaning! Almost done.", fg="#0027cf")
    if is_single_link:
            link_entry.delete(0, END)
            status_label.config(text="Download and convertion successful!", fg="#00c200")
            progress.stop()
            ShowButtons()
    else:
        link_entry.delete(0, END)
        status_label.config(text=f"Download and convertion successful for {correct_download_count} out of {number_of_links} links!", fg="#00c200")
        progress.stop()
        if correct_download_count != number_of_links:

            f = font.Font(status_label2, status_label2.cget("font"))
            f.configure(underline=True)
            status_label2.configure(text="Some links were skipped due to errors", fg="red", font=f, cursor= "hand2")
            status_label2.bind("<Button-1>", lambda e:OpenErrors())
        ShowButtons()

class Logger(object):
    def debug(self, msg):
        global number_of_links
        global correct_download_count
        end_message = "[ExtractAudio]"
        if end_message in msg:
            correct_download_count = correct_download_count + 1
            status_label2.configure(text=f"Done downloading {correct_download_count}/{number_of_links}", fg="#0027c2")

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        global correct_download_count
        msg = msg + " | Index number of bad url: #" + str(correct_download_count + 1)
        all_errors.append(msg)


def Download(single_link, file_name, ydl_opts):
    progress.start()
    status_label.config(text="", fg="black")
    if file_name != "":
        # global single_downloads
        # single_downloads = 0
        is_single_link = False
        with open(file_name, 'r') as file:
            links = [line.strip() for line in file]
            while '' in links:
                links.remove('')
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(links)
            return SetEndLabel(is_single_link)
    else:
        is_single_link = True
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([single_link])
            return SetEndLabel(is_single_link)
        except:
            progress.stop()
            ShowButtons()
            status_label.configure(fg="red", text="Invalid link! Try again or use different url.")
            return

# Function starting thread to stop program from freezing
def StartThread(single_link, file_name, ydl_opts):
    thread = threading.Thread(target=Download, args=[single_link, file_name, ydl_opts])
    thread.start()

def SetOptions(is_single_link):
    if is_single_link:
        ydl_opts = {
            'outtmpl': save_path + '/Youtube Downloader/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # 'ffmpeg_location': './ffmpeg/bin/ffmpeg.exe',
            'socket_timeout': 1,
            'logger': Logger(),
        }
        return ydl_opts
    else:
        ydl_opts = {
            'outtmpl': save_path + '/Youtube Downloader/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # 'ffmpeg_location': './ffmpeg/bin/ffmpeg.exe',
            'socket_timeout': 1,
            'ignoreerrors': True,
            'ignore_no_formats_error': True,
            'logger': Logger(),
        }
        return ydl_opts

def SingleLink():
    global correct_download_count
    correct_download_count = 0
    global number_of_links
    number_of_links = 1
    global all_errors
    all_errors = []
    is_single_link = True
    HideButtons()
    ResetLabels()
    ydl_opts = SetOptions(is_single_link)
    single_link = link.get()
    StartThread(single_link, "", ydl_opts)

def NumberOfLinks(file_name):
    file = open(file_name)
    with file as file:
        links = [line.strip() for line in file]
        while '' in links:
            links.remove('')
    links_count = len(links)
    file.close()
    return links_count

def BatchLink():
    global correct_download_count
    correct_download_count = 0
    global number_of_links
    is_single_link = False
    global all_errors
    all_errors = []
    filetypes = (
        ('text files', '*.txt'),
    )
    file_name = fd.askopenfilename(
        title='Open a file',
        filetypes=filetypes)
    try:
        #disable the buttons to stop impostors
        HideButtons()
        #calculate number of links in the file
        number_of_links = NumberOfLinks(file_name)
        #change status text
        status_text = "Links to download: " + str(number_of_links) + " Starting..."
        status_label.config(text=status_text, fg="#0027c2")
        status_label2.configure(text=f"Done downloading 0/{number_of_links}", fg="#0027c2")
        root.update()
        ydl_opts = SetOptions(is_single_link)
        #Starting batch download
        StartThread("", file_name, ydl_opts)

    #exception for no file chosen
    except:
        status_label.configure(fg="red", text="No file selected!")
        ShowButtons()

#Configuration of root window
root = Tk()
root.title('Youtube MP3 Downloader')
window_width = 600
window_height = 400
root.tk.call('tk', 'scaling', 2.0)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.resizable(False, False)
root.iconbitmap('./assets/icon.ico')
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

#Variables
link = tk.StringVar()
save_path = str(Path.home() / "Downloads")

#Top filler :D
l1 = tk.Label(root, background="#292929", foreground="white")
l1.pack(pady="1")

#Main label setup
link_label = ttk.Label(root, text='↓Paste link here↓',background="#292929", foreground="white")
link_label.pack(pady=10)

#Textbox for link setup
link_entry = ttk.Entry(root, textvariable=link, background="#292929")
link_entry.pack(padx=15, fill="x" )
link_entry.focus()

#Progressbar setup
progress = Progressbar(root, orient = HORIZONTAL, mode = 'determinate')
progress.pack(padx=15,pady="10", fill="x")

#Biding rightclick to paste url into textbox
link_entry.bind("<Button-3>", Rightclick)

#Button to start downloading setup
button = tk.Button(root, text="Download", command=SingleLink, background="#0027c2", relief=FLAT, foreground="white")
button.pack(pady=10)
#Download from a file button
download_from_file = tk.Button(root, text="Download all links from txt file", command=BatchLink, relief="ridge", borderwidth="1", background="#292929", foreground="white")
download_from_file.pack(pady=10)

#Label displaying result setup
status_label = tk.Label(root, background="#292929")
status_label.pack()
status_label2 = tk.Label(root, background="#292929")
status_label2.pack()

#Button opening download folder
icon_dark_folder = PhotoImage(file='./assets/folder_dark_mode.png')
open_download = tk.Button(root, image=icon_dark_folder, command=OpenFolder, relief=FLAT, background="#292929")
open_download.place(relx = 0.92, rely = 0.55, anchor = CENTER)

#Selfpromo setup XD
icon_github = PhotoImage(file="./assets/github_dark_mode.png")
github_button = tk.Button(root, image=icon_github, relief=FLAT, command=OpenLink, background="#292929", foreground="white")
github_button.place(relx = 0.95, rely = 0.93, anchor = CENTER)
github_label = tk.Label(root, text="made by: no-t1me", background="#292929", foreground="white")
github_label.place(relx = 0.75, rely = 0.93, anchor = CENTER)

root.configure(background="#292929")

#Centering window
def WindowCenter(window):
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width_center = window.winfo_screenwidth()
    screen_height_center = window.winfo_screenheight()
    x = (screen_width_center - width) // 2
    y = (screen_height_center - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

def ChangeTitleBarColor():
    #Checking if user is using Windows 11 to change color of title bar
    if platform.release() == "11":
        hwnd = windll.user32.GetParent(root.winfo_id())
        dmwa_caption_color = 35
        color = 0x00292929
        windll.dwmapi.DwmSetWindowAttribute(hwnd, dmwa_caption_color, byref(c_int(color)), sizeof(c_int))
    else:
        pass

WindowCenter(root)
ChangeTitleBarColor()
root.mainloop()


