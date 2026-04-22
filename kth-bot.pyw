import time
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import sys
from PIL import Image, ImageDraw
import pystray
from playwright.sync_api import sync_playwright

# --- Pre-Config ---
URL = "https://cloud.timeedit.net/kth/web/stud02/s.html?sid=22&object=949f8f95-8bf8-492b-8dff-563335b2b335&type=room&p=0.m%2C2.w&rr=1"
USERNAME = ""
PASSWORD = ""
RUNNING = True

def log_to_ui(message):
    timestamp = time.strftime("[%H:%M:%S] ")
    log_box.config(state='normal')
    log_box.insert(tk.END, timestamp + message + "\n")
    log_box.see(tk.END)
    log_box.config(state='disabled')

def validate_and_confirm(user, pwd, is_test=False):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(URL)
            page.click("button:has-text('KTH – SSO')")
            page.fill("input#userNameInput", user)
            page.click("span#nextButton")
            page.fill("input#passwordInput", pwd)
            page.click("span#submitButton")

            try:
                page.click("button[name='_eventId_proceed']", timeout=4000)
            except:
                pass

            page.wait_for_url("**/cloud.timeedit.net/**", timeout=4000)
            
            if is_test:
                browser.close()
                return True 

            page.wait_for_load_state("networkidle")
            try:
                confirm_button = page.locator("label[data-name='Bekräfta']").first
                confirm_button.wait_for(state="visible", timeout=5000)
                confirm_button.click()
                log_to_ui("Booking confirmed!")
            except:
                log_to_ui("Checked: No booking found.")
            
            browser.close()
            return True
    except Exception:
        return False

def background_loop():
    while RUNNING:
        validate_and_confirm(USERNAME, PASSWORD)
        for _ in range(600): # 10-minute wait
            if not RUNNING: break
            time.sleep(1)

def quit_app(icon):
    global RUNNING
    RUNNING = False
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
root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

log_box = scrolledtext.ScrolledText(root, state='disabled', wrap=tk.WORD)
log_box.pack(expand=True, fill='both', padx=10, pady=10)

root.withdraw()

while True:
    USERNAME = simpledialog.askstring("KTH Login", "Enter KTH Email:", parent=root)
    if USERNAME is None:
        root.destroy()
        sys.exit()

    PASSWORD = simpledialog.askstring("KTH Login", "Enter Password:", show='*', parent=root)
    if PASSWORD is None:
        root.destroy()
        sys.exit()

    if not USERNAME or not PASSWORD:
        messagebox.showwarning("Warning", "Username and Password cannot be empty.")
        continue

    if validate_and_confirm(USERNAME, PASSWORD, is_test=True):
        messagebox.showinfo("Success", "Login valid! Bot is starting.")
        break
    else:
        messagebox.showerror("Error", "Invalid login or connection error. Please try again.")

root.deiconify()
log_to_ui(f"Bot started for {USERNAME}")
threading.Thread(target=background_loop, daemon=True).start()
threading.Thread(target=setup_tray, daemon=True).start()

root.mainloop()