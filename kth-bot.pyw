import time
import threading
import tkinter as tk
from tkinter import scrolledtext
import sys
import ctypes
from PIL import Image, ImageDraw
import pystray
from playwright.sync_api import sync_playwright

URL = "https://cloud.timeedit.net/kth/web/stud02/s.html?sid=22&object=949f8f95-8bf8-492b-8dff-563335b2b335&type=room&p=0.m%2C2.w&rr=1"
USERNAME = ""
PASSWORD = ""
STOP_EVENT = threading.Event()

BG_MAIN = "#1e1e1e"
BG_TEXT = "#2d2d2d"
FG_TEXT = "#d4d4d4"

def set_dark_titlebar(window):
    try:
        window.update()
        set_window_attribute = ctypes.windll.dwmapi.DwmSetWindowAttribute
        get_parent = ctypes.windll.user32.GetParent
        hwnd = get_parent(window.winfo_id())
        value = ctypes.c_int(2)
        set_window_attribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
    except:
        pass

def dark_message(parent, title, message):
    dlg = tk.Toplevel(parent)
    dlg.title(title)
    dlg.geometry("300x150")
    dlg.configure(bg=BG_MAIN)
    set_dark_titlebar(dlg)
    
    dlg.grab_set()
    dlg.focus_force()
    
    tk.Label(dlg, text=message, bg=BG_MAIN, fg=FG_TEXT, wraplength=280).pack(expand=True, fill="both", pady=20)
    tk.Button(dlg, text="OK", bg=BG_TEXT, fg=FG_TEXT, relief="flat", command=dlg.destroy, width=10).pack(pady=(0,20))
    parent.wait_window(dlg)

def ask_login(parent):
    dialog = tk.Toplevel(parent)
    dialog.title("KTH Login")
    dialog.geometry("250x200")
    dialog.configure(bg=BG_MAIN)
    set_dark_titlebar(dialog)
    
    dialog.grab_set()
    dialog.focus_force()

    result = []

    tk.Label(dialog, text="KTH Email:", bg=BG_MAIN, fg=FG_TEXT).pack(pady=(20, 5))
    user_entry = tk.Entry(dialog, bg=BG_TEXT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat")
    user_entry.pack(pady=5, padx=20, fill="x")
    user_entry.focus()

    tk.Label(dialog, text="Password:", bg=BG_MAIN, fg=FG_TEXT).pack(pady=(10, 5))
    pwd_entry = tk.Entry(dialog, show="*", bg=BG_TEXT, fg=FG_TEXT, insertbackground=FG_TEXT, relief="flat")
    pwd_entry.pack(pady=5, padx=20, fill="x")
    
    def submit(event=None):
        result.append((user_entry.get(), pwd_entry.get()))
        dialog.destroy()
    
    def cancel():
        dialog.destroy()

    dialog.bind('<Return>', submit)

    btn_frame = tk.Frame(dialog, bg=BG_MAIN)
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text="Login", bg=BG_TEXT, fg=FG_TEXT, relief="flat", command=submit, width=10).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Cancel", bg=BG_TEXT, fg=FG_TEXT, relief="flat", command=cancel, width=10).pack(side="right", padx=10)

    dialog.protocol("WM_DELETE_WINDOW", cancel)
    parent.wait_window(dialog)
    
    return result[0] if result else (None, None)

def log_to_ui(message):
    def update_text():
        timestamp = time.strftime("[%H:%M:%S] ")
        log_box.config(state='normal')
        log_box.insert(tk.END, timestamp + message + "\n")
        log_box.see(tk.END)
        log_box.config(state='disabled')
    root.after(0, update_text)

def validate_and_confirm(user, pwd, is_test=False):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(URL, timeout=10000)
            page.click("button:has-text('KTH – SSO')", timeout=5000)
            page.fill("input#userNameInput", user, timeout=5000)
            page.click("span#nextButton", timeout=5000)
            page.fill("input#passwordInput", pwd, timeout=5000)
            page.click("span#submitButton", timeout=5000)

            try:
                page.click("button[name='_eventId_proceed']", timeout=1500)
            except:
                pass

            page.wait_for_url("**/cloud.timeedit.net/**", timeout=3000)
            
            if is_test:
                browser.close()
                return True 

            page.wait_for_load_state("networkidle", timeout=5000)
            try:
                confirm_button = page.locator("label[data-name='Bekräfta']").first
                confirm_button.wait_for(state="visible", timeout=3000)
                confirm_button.click()
                log_to_ui("Booking confirmed!")
            except:
                log_to_ui("Checked: No booking found.")
                log_to_ui("Next check in 10 Minutes.")
            
            browser.close()
            return True
    except Exception:
        return False

def background_loop():
    while not STOP_EVENT.is_set():
        validate_and_confirm(USERNAME, PASSWORD)
        STOP_EVENT.wait(600)

def quit_app(icon):
    STOP_EVENT.set()
    icon.stop()
    root.after(0, root.destroy)

def show_window():
    root.after(0, root.deiconify)

def minimize_to_tray():
    root.withdraw()

def setup_tray():
    width, height = 64, 64
    image = Image.new('RGB', (width, height), (0, 0, 139))
    dc = ImageDraw.Draw(image)
    dc.text((10, 20), "KTH", fill=(255, 255, 255))
    
    menu = pystray.Menu(
        pystray.MenuItem("Show", show_window),
        pystray.MenuItem("Quit", quit_app)
    )
    icon = pystray.Icon("KTH Bot", image, "KTH Auto Confirm", menu)
    icon.run()

root = tk.Tk()
root.title("KTH Bot Dashboard")
root.geometry("400x300")
root.configure(bg=BG_MAIN)
set_dark_titlebar(root)
root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

log_box = scrolledtext.ScrolledText(
    root, 
    state='disabled', 
    wrap=tk.WORD, 
    bg=BG_TEXT, 
    fg=FG_TEXT, 
    insertbackground=FG_TEXT,
    highlightthickness=0,
    borderwidth=0
)
log_box.pack(expand=True, fill='both', padx=10, pady=10)

root.withdraw()

while True:
    USERNAME, PASSWORD = ask_login(root)
    
    if USERNAME is None or PASSWORD is None:
        root.destroy()
        sys.exit()

    if not USERNAME or not PASSWORD:
        dark_message(root, "Warning", "Username and Password cannot be empty.")
        continue

    loading_dlg = tk.Toplevel(root)
    loading_dlg.title("Status")
    loading_dlg.geometry("250x100")
    loading_dlg.configure(bg=BG_MAIN)
    set_dark_titlebar(loading_dlg)
    loading_dlg.grab_set()
    loading_dlg.focus_force()
    tk.Label(loading_dlg, text="Validating credentials...\nPlease wait.", bg=BG_MAIN, fg=FG_TEXT).pack(expand=True)
    loading_dlg.update()

    is_valid = validate_and_confirm(USERNAME, PASSWORD, is_test=True)

    loading_dlg.destroy()

    if is_valid:
        print("Login valid! Bot is starting.")
        break
    else:
        dark_message(root, "Error", "Invalid login or connection error. Please try again.")

root.deiconify()
log_to_ui(f"Bot started for {USERNAME}")
threading.Thread(target=background_loop, daemon=True).start()
threading.Thread(target=setup_tray, daemon=True).start()

root.mainloop()
