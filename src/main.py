import tkinter as tk
from tkinter import filedialog, messagebox
import os
import json
import subprocess
import sys

SETTINGS_FILENAME = ".focus_settings.json"
DEFAULT_WINDOW_SIZE = 5

def load_settings(project_dir):
    path = os.path.join(project_dir, SETTINGS_FILENAME)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"window_size": DEFAULT_WINDOW_SIZE}

def save_settings(project_dir, settings):
    path = os.path.join(project_dir, SETTINGS_FILENAME)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f)

def get_txt_file(project_dir):
    files = [f for f in os.listdir(project_dir) if f.endswith(".txt")]
    if len(files) == 1:
        return os.path.join(project_dir, files[0])
    return None

def read_text(txt_path):
    if not os.path.exists(txt_path):
        return ""
    with open(txt_path, "r", encoding="utf-8") as f:
        return f.read()

def write_text(txt_path, text):
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)

def get_last_n_words(text, n):
    words = text.split()
    return words[-n:] if len(words) >= n else words


class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ForwardOnly")
        self.root.resizable(False, False)
        self.root.geometry("360x260")
        self.project_dir = None
        self.settings = {}
        self.txt_path = None
        self._build_ui()

    def _build_ui(self):
        pad = dict(padx=20, pady=8)

        tk.Label(self.root, text="ForwardOnly", font=("Courier New", 16, "bold")).pack(pady=(24, 2))
        tk.Label(self.root, text="a forward-only writing tool", font=("Courier New", 9), fg="#888").pack(pady=(0, 16))

        self.project_label = tk.Label(self.root, text="No project open", font=("Courier New", 9), fg="#555")
        self.project_label.pack()

        tk.Button(self.root, text="Open Project Folder", font=("Courier New", 10),
                  command=self.open_project, width=22).pack(**pad)

        frame = tk.Frame(self.root)
        frame.pack(pady=4)
        tk.Label(frame, text="Window size:", font=("Courier New", 9)).pack(side=tk.LEFT)
        self.window_size_var = tk.IntVar(value=DEFAULT_WINDOW_SIZE)
        spin = tk.Spinbox(frame, from_=1, to=20, textvariable=self.window_size_var,
                          width=4, font=("Courier New", 10))
        spin.pack(side=tk.LEFT, padx=6)
        tk.Label(frame, text="words", font=("Courier New", 9)).pack(side=tk.LEFT)

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=12)
        self.write_btn = tk.Button(btn_frame, text="Write", font=("Courier New", 10),
                                   command=self.open_write_mode, width=10, state=tk.DISABLED)
        self.write_btn.pack(side=tk.LEFT, padx=6)
        self.review_btn = tk.Button(btn_frame, text="Review", font=("Courier New", 10),
                                    command=self.open_review_mode, width=10, state=tk.DISABLED)
        self.review_btn.pack(side=tk.LEFT, padx=6)

    def open_project(self):
        folder = filedialog.askdirectory(title="Select project folder")
        if not folder:
            return
        txt = get_txt_file(folder)
        if txt is None:
            txts = [f for f in os.listdir(folder) if f.endswith(".txt")]
            if len(txts) == 0:
                create = messagebox.askyesno("No .txt file found",
                    "No .txt file found in this folder.\nCreate one now?")
                if create:
                    name = os.path.basename(folder) + ".txt"
                    txt = os.path.join(folder, name)
                    write_text(txt, "")
                else:
                    return
            else:
                messagebox.showerror("Multiple .txt files",
                    "More than one .txt file found.\nPlease keep only one per project folder.")
                return

        self.project_dir = folder
        self.txt_path = txt
        self.settings = load_settings(folder)
        self.window_size_var.set(self.settings.get("window_size", DEFAULT_WINDOW_SIZE))
        self.project_label.config(
            text=f"Project: {os.path.basename(folder)}  |  {os.path.basename(txt)}")
        self.write_btn.config(state=tk.NORMAL)
        self.review_btn.config(state=tk.NORMAL)

    def open_write_mode(self):
        wsize = self.window_size_var.get()
        self.settings["window_size"] = wsize
        save_settings(self.project_dir, self.settings)
        text = read_text(self.txt_path)
        self.root.withdraw()
        WriteWindow(self.root, self.txt_path, text, wsize, self._on_write_close)

    def _on_write_close(self):
        self.root.deiconify()

    def open_review_mode(self):
        try:
            os.startfile(self.txt_path)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file:\n{e}")


class WriteWindow:
    def __init__(self, parent, txt_path, existing_text, window_size, on_close):
        self.parent = parent
        self.txt_path = txt_path
        self.window_size = window_size
        self.on_close = on_close

        # Internal state: full text written this session appended to existing
        self.base_text = existing_text
        self.session_text = ""  # only new text typed this session

        self.win = tk.Toplevel(parent)
        self.win.title("ForwardOnly — Write Mode")
        self.win.geometry("700x420")
        self.win.protocol("WM_DELETE_WINDOW", self._finish)
        self.win.focus_force()

        self._build_ui()
        self._refresh_display()
        self.win.bind("<Key>", self._on_key)
        self.win.bind("<Button-1>", lambda e: self.win.focus_force())

    def _build_ui(self):
        top = tk.Frame(self.win)
        top.pack(fill=tk.X, padx=16, pady=(12, 0))

        tk.Label(top, text="write mode", font=("Courier New", 9), fg="#888").pack(side=tk.LEFT)

        self.word_count_label = tk.Label(top, text="", font=("Courier New", 9), fg="#888")
        self.word_count_label.pack(side=tk.RIGHT)

        self.display = tk.Text(self.win, font=("Courier New", 18),
                               wrap=tk.WORD, state=tk.DISABLED,
                               relief=tk.FLAT, bd=0,
                               padx=32, pady=32,
                               cursor="arrow")
        self.display.pack(fill=tk.BOTH, expand=True, padx=4, pady=8)

        # Tags for hidden vs visible text
        self.display.tag_config("hidden", foreground="#e8e8e8")
        self.display.tag_config("visible", foreground="#111111")
        self.display.tag_config("cursor_block", background="#111111", foreground="#111111")

        bottom = tk.Frame(self.win)
        bottom.pack(fill=tk.X, padx=16, pady=(0, 12))
        tk.Label(bottom, text="esc or close window to finish and save",
                 font=("Courier New", 8), fg="#aaa").pack(side=tk.LEFT)

        self.win.bind("<Escape>", lambda e: self._finish())

    def _full_text(self):
        return self.base_text + self.session_text

    def _refresh_display(self):
        full = self._full_text()
        tokens = full.split()
        total_words = len(tokens)

        # Determine visible window: last N words
        n = self.window_size
        if total_words <= n:
            hidden_words = []
            visible_words = tokens
        else:
            hidden_words = tokens[:-n]
            visible_words = tokens[-n:]

        hidden_text = " ".join(hidden_words)
        visible_text = " ".join(visible_words)

        # Preserve leading/trailing whitespace feel
        # Reconstruct so spacing after hidden block matches original
        if hidden_words and visible_words:
            display_text = hidden_text + " " + visible_text
            hidden_end = len(hidden_text) + 1
        elif hidden_words:
            display_text = hidden_text
            hidden_end = len(hidden_text)
        else:
            display_text = visible_text
            hidden_end = 0

        self.display.config(state=tk.NORMAL)
        self.display.delete("1.0", tk.END)
        self.display.insert(tk.END, display_text)

        # Apply tags
        self.display.tag_remove("hidden", "1.0", tk.END)
        self.display.tag_remove("visible", "1.0", tk.END)

        if hidden_end > 0:
            self.display.tag_add("hidden", "1.0", f"1.0 + {hidden_end} chars")
            self.display.tag_add("visible", f"1.0 + {hidden_end} chars", tk.END)
        else:
            self.display.tag_add("visible", "1.0", tk.END)

        # Scroll to end
        self.display.see(tk.END)
        self.display.config(state=tk.DISABLED)

        # Update word count
        self.word_count_label.config(text=f"{total_words} words")

    def _on_key(self, event):
        blocked = {"BackSpace", "Delete", "Left", "Right", "Up", "Down",
                   "Home", "End", "Prior", "Next"}
        if event.keysym in blocked:
            return "break"

        # Let modifier combos through (Ctrl+C etc) but not Ctrl+Z (undo)
        if event.state & 0x4:  # Ctrl held
            if event.keysym.lower() == 'z':
                return "break"
            return  # allow other ctrl combos

        if event.keysym == "Escape":
            return  # handled by bind

        if event.char and event.char.isprintable():
            self.session_text += event.char
            self._refresh_display()
            return "break"

        if event.keysym == "Return":
            self.session_text += "\n"
            self._refresh_display()
            return "break"

        if event.keysym == "Tab":
            self.session_text += "\t"
            self._refresh_display()
            return "break"

        if event.keysym == "space":
            self.session_text += " "
            self._refresh_display()
            return "break"

        return "break"

    def _finish(self):
        full = self._full_text()
        write_text(self.txt_path, full)
        self.win.destroy()
        self.on_close()


def main():
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
