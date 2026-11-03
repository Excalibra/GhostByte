#!/usr/bin/env python3
"""
Ghostbyte
Personal Data Removal Tool
"""

import json
import os
import re
import webbrowser
import tkinter as tk
from PIL import Image, ImageTk
from tkinter import font as tkfont

DATA_FILE = "data/privacy_progress.json"
SOURCES_FILE = "data/sources.json"

# Column widths for the service table (shared by rendering and window sizing)
NAME_W = 22
LINK_W = 26
NOTES_W = 40
SUB_W = 5
VER_W = 5

YOUR_DATA = {
    "full_name": "YOUR FULL NAME HERE",
    "address": "YOUR FULL ADDRESS HERE",
    "phone": "YOUR PHONE HERE",
    "email": "your_anon_email@protonmail.com"
}

def load_sources():
    """Load default categories and services from the JSON file."""
    if os.path.exists(SOURCES_FILE):
        with open(SOURCES_FILE, "r") as f:
            return json.load(f)
    return {}

class MatrixCRTApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ghostbyte")
        self.root.configure(bg="#0c0c0c")

        try:
            icon_img = Image.open("img/ghostbyte.png")
            icon_img = icon_img.resize((64, 64), Image.Resampling.LANCZOS)
            self.icon_image = ImageTk.PhotoImage(icon_img)
            self.root.iconphoto(True, self.icon_image)
        except Exception:
            pass

        self.data = self.load_progress()
        self.current_category = None
        self.current_services = []
        self.current_view = "categories"
        self.intro_shown = False

        self.custom_font = tkfont.Font(family="Courier", size=10)
        self.bold_font = tkfont.Font(family="Courier", size=10, weight="bold")

        self.create_header()
        self.create_main_frame()
        self.create_status_bar()
        self.create_input_area()

        self.apply_scanlines()
        self.root.update_idletasks()
        self.scanline_canvas.tk.call('lower', self.scanline_canvas._w)

        self.adjust_window_size()

        self.clear_output()
        self.show_intro()

    def adjust_window_size(self):
        """Set window width to fit the table, capped to a compact size."""
        dummy_row = (f"│ {'#':>2} │ {'Service Name':<{NAME_W}} │ {'Link':<{LINK_W}} │ "
                     f"{'Notes':<{NOTES_W}} │ {'Sub':^{SUB_W}} │ {'Ver':^{VER_W}} │")
        inner_chars = len(dummy_row) - 2

        char_width_px = self.custom_font.measure("A")
        table_width_px = int(inner_chars * char_width_px) + 100

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        target_width = min(table_width_px, int(screen_width * 0.8))
        target_height = min(int(screen_height * 0.7), 760)

        self.root.geometry(f"{target_width}x{target_height}")
        self.root.minsize(700, 450)

    # ---------- DATA HANDLING ----------
    def load_progress(self):
        sources = load_sources()
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                saved_data = json.load(f)
            for cat_name, services in sources.items():
                if cat_name not in saved_data:
                    saved_data[cat_name] = services
                else:
                    saved_names = {s["name"] for s in saved_data[cat_name]}
                    for svc in services:
                        if svc["name"] not in saved_names:
                            saved_data[cat_name].append(svc)
            return saved_data
        return sources

    def save_progress(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=2)
        self.update_status()

    # ---------- UI ----------
    def create_header(self):
        header_frame = tk.Frame(self.root, bg="#0c0c0c", height=120)
        header_frame.pack(fill="x", pady=(10, 0))
        header_frame.pack_propagate(False)

        try:
            img = Image.open("img/ghostbyte.png")
            target_height = 100
            orig_width, orig_height = img.size
            ratio = target_height / orig_height
            new_width = int(orig_width * ratio)
            img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(img)
            logo_label = tk.Label(header_frame, image=self.logo_image, bg="#0c0c0c")
            logo_label.pack()
        except Exception:
            logo_label = tk.Label(header_frame, text="Ghostbyte",
                                  font=self.bold_font, fg="#7fff7f", bg="#0c0c0c")
            logo_label.pack()

        subtitle = tk.Label(header_frame,
                            text="Ghostbyte — github.com/Excalibra",
                            font=self.bold_font, fg="#ff5555", bg="#0c0c0c")
        subtitle.pack()

        tk.Frame(header_frame, height=2, bg="#4a9a4a").pack(fill="x", pady=5)

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg="#0c0c0c")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.output_text = tk.Text(self.main_frame, wrap="none", bg="#0c0c0c", fg="#7fff7f",
                                   insertbackground="#7fff7f", font=self.custom_font,
                                   relief="flat", borderwidth=0, highlightthickness=0,
                                   takefocus=0, cursor="arrow")
        self.output_text.pack(side="left", fill="both", expand=True)
        self.output_text.bind("<Button-1>", self.on_output_click)

        self.output_text.tag_configure("bright", foreground="#7fff7f")
        self.output_text.tag_configure("dim", foreground="#555555")

        v_scrollbar = tk.Scrollbar(self.main_frame, command=self.output_text.yview, bg="#0c0c0c",
                                   troughcolor="#0c0c0c", activebackground="#7fff7f")
        v_scrollbar.pack(side="right", fill="y")

        h_scrollbar = tk.Scrollbar(self.root, orient="horizontal", command=self.output_text.xview,
                                   bg="#0c0c0c", troughcolor="#0c0c0c", activebackground="#7fff7f")
        h_scrollbar.pack(side="bottom", fill="x")
        self.output_text.config(xscrollcommand=h_scrollbar.set)
        self.output_text.config(yscrollcommand=v_scrollbar.set)
        self.output_text.config(state="disabled")

    def create_status_bar(self):
        status_frame = tk.Frame(self.root, bg="#0c0c0c", height=25)
        status_frame.pack(fill="x", side="bottom", padx=10, pady=5)
        status_frame.pack_propagate(False)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(status_frame, textvariable=self.status_var,
                                     font=self.custom_font, fg="#7fff7f", bg="#0c0c0c",
                                     anchor="w")
        self.status_label.pack(fill="x")
        self.update_status()

        tk.Frame(status_frame, height=1, bg="#4a9a4a").pack(fill="x", pady=2)

    def update_status(self):
        total = sum(len(services) for services in self.data.values())
        completed = sum(1 for services in self.data.values() for svc in services if svc["submitted"])
        pct = int(completed / total * 100) if total else 0
        self.status_var.set(f" TRACE PROGRAM: ACTIVE | SIGNAL: {pct}% | PURGED: {completed}/{total}")

    def create_input_area(self):
        input_frame = tk.Frame(self.root, bg="#0c0c0c", height=30)
        input_frame.pack(fill="x", side="bottom", padx=20, pady=(0,10))
        input_frame.pack_propagate(False)

        self.prompt_label = tk.Label(input_frame, text=">", font=self.bold_font,
                                     fg="#7fff7f", bg="#0c0c0c")
        self.prompt_label.pack(side="left")

        self.input_entry = tk.Entry(input_frame, font=self.custom_font,
                                    bg="#0c0c0c", fg="#7fff7f", insertbackground="#7fff7f",
                                    relief="flat", borderwidth=1, highlightcolor="#7fff7f",
                                    highlightbackground="#4a9a4a", highlightthickness=1)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(5,0))
        self.input_entry.bind("<Return>", self.process_command)
        self.input_entry.focus_set()
        self.root.bind("<FocusIn>", lambda e: self.input_entry.focus_set())

        self.blink_cursor()

    def blink_cursor(self):
        current = self.input_entry.cget("insertbackground")
        new_color = "#0c0c0c" if current == "#7fff7f" else "#7fff7f"
        self.input_entry.config(insertbackground=new_color)
        self.root.after(500, self.blink_cursor)

    def apply_scanlines(self):
        self.scanline_canvas = tk.Canvas(self.root, highlightthickness=0, bg="#0c0c0c")
        self.scanline_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.root.bind("<Configure>", self.redraw_scanlines)
        self.redraw_scanlines()
        self.scanline_canvas.bind("<Button-1>", lambda e: None)
        self.scanline_canvas.bind("<Button-2>", lambda e: None)
        self.scanline_canvas.bind("<Button-3>", lambda e: None)

    def redraw_scanlines(self, event=None):
        self.scanline_canvas.delete("all")
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        for y in range(0, height, 4):
            self.scanline_canvas.create_line(0, y, width, y,
                                             fill="#1a3a1a", width=1, stipple="gray50")

    # ---------- OUTPUT & COMMANDS ----------
    def append_output(self, text, tag=None):
        self.output_text.config(state="normal")
        if tag:
            self.output_text.insert("end", text, tag)
        else:
            self.output_text.insert("end", text)
        self.output_text.see("end")
        self.output_text.config(state="disabled")

    def clear_output(self):
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, "end")
        self.output_text.config(state="disabled")

    def on_output_click(self, event):
        self.input_entry.focus_set()
        index = self.output_text.index(f"@{event.x},{event.y}")
        line = self.output_text.get(f"{index} linestart", f"{index} lineend")
        match = re.match(r"\s*│\s*(\d+)\s*│", line)
        if match:
            num = int(match.group(1))
            if self.current_view == "categories":
                self.append_output(f"> {num}\n")
                self.select_category(num - 1)
            elif self.current_view == "services":
                self.append_output(f"> {num}\n")
                self.toggle_submitted(num - 1)
        return "break"

    def process_command(self, event=None):
        cmd = self.input_entry.get().strip()
        self.input_entry.delete(0, "end")
        self.append_output(f"> {cmd}\n")
        self.handle_command(cmd)

    def handle_command(self, cmd):
        parts = cmd.split()
        if not parts:
            return

        if cmd.lower() in ("q", "quit", "exit"):
            self.save_progress()
            self.root.quit()
        elif cmd.lower() in ("m", "menu"):
            self.show_categories()
        elif cmd.lower() in ("a", "all"):
            self.show_all_services()
        elif cmd == "b":
            if self.current_view == "services":
                self.show_categories()
            else:
                self.append_output("[!] 'b' only goes back from service view. Use 'm' for main menu.\n")
        elif parts[0] == "o" and len(parts) > 1:
            try:
                num = int(parts[1])
                self.open_url(num - 1)
            except ValueError:
                self.append_output("[!] Usage: o <number>\n")
        elif parts[0] == "v" and len(parts) > 1:
            try:
                num = int(parts[1])
                self.toggle_verified(num - 1)
            except ValueError:
                self.append_output("[!] Usage: v <number>\n")
        elif cmd.isdigit():
            num = int(cmd)
            if self.current_view == "categories":
                self.select_category(num - 1)
            elif self.current_view == "services":
                self.toggle_submitted(num - 1)
            else:
                self.append_output("[!] Numbers work only in category or service lists.\n")
        else:
            self.append_output("[!] Commands: m=Menu, a=All, q=Quit, b=Back (services), o <number>, v <number>, or enter a number.\n")

    # ---------- VIEWS ----------
    def show_intro(self):
        self.append_output("\n\nWake up, Neo...\n")
        self.root.after(800, lambda: self.append_output("The data brokers have you...\n"))
        self.root.after(1600, lambda: self.append_output("Follow the green ghost.\n"))
        self.root.after(2400, lambda: self.append_output("Knock, knock, Neo.\n\n"))
        self.root.after(3200, lambda: self.append_output("[ Ghostbyte - System Boot Complete ]\n\n"))
        self.root.after(4000, self.finish_intro)

    def finish_intro(self):
        self.intro_shown = True
        self.show_categories_content()

    def show_categories_content(self):
        NUM_W = 4
        CAT_W = 52
        REM_W = 24
        dummy_header = f"│ {'#':>2} │ {'Category Name':<{CAT_W}} │ {'Rem.':>{REM_W}} │"
        INNER_WIDTH = len(dummy_header) - 2

        self.append_output("┌" + "─" * INNER_WIDTH + "┐\n")
        self.append_output("│" + " SELECT CATEGORY TO PURGE".center(INNER_WIDTH) + "│\n")
        self.append_output("├" + "─" * INNER_WIDTH + "┤\n")
        self.append_output(dummy_header + "\n")
        self.append_output("├" + "─" * INNER_WIDTH + "┤\n")

        for i, (cat_name, services) in enumerate(self.data.items(), 1):
            remaining = sum(1 for s in services if not s["submitted"])
            display_name = (cat_name[:CAT_W-2] + "..") if len(cat_name) > CAT_W else cat_name.ljust(CAT_W)
            row = f"│ {i:2} │ {display_name} │ {remaining:>{REM_W}} │"
            row = row.ljust(INNER_WIDTH + 2)
            self.append_output(row + "\n")

        self.append_output("└" + "─" * INNER_WIDTH + "┘\n")
        self.append_output("\nEnter a number (or click a row) to select a category.\n")
        self.append_output("Commands: m=Menu, a=All, q=Quit\n")
        self.current_view = "categories"

    def show_categories(self):
        self.clear_output()
        self.show_categories_content()

    def select_category(self, idx):
        if 0 <= idx < len(self.data):
            self.current_category = list(self.data.keys())[idx]
            self.current_services = self.data[self.current_category]
            self.current_view = "services"
            self.show_services(self.current_category, self.current_services)
        else:
            self.append_output("[!] Invalid category index.\n")

    def show_services(self, cat_name, services):
        self.clear_output()

        dummy_row = (f"│ {'#':>2} │ {'Service Name':<{NAME_W}} │ {'Link':<{LINK_W}} │ "
                     f"{'Notes':<{NOTES_W}} │ {'Sub':^{SUB_W}} │ {'Ver':^{VER_W}} │")
        INNER_WIDTH = len(dummy_row) - 2

        self.append_output(f"\n┌{'─' * INNER_WIDTH}┐\n")
        self.append_output(f"│ {cat_name.center(INNER_WIDTH - 2)} │\n")
        self.append_output(f"├{'─' * INNER_WIDTH}┤\n")
        self.append_output(dummy_row + "\n")
        self.append_output(f"├{'─' * INNER_WIDTH}┤\n")

        self.output_text.config(state="normal")
        for i, svc in enumerate(services, 1):
            name_raw = svc['name']
            name = (name_raw[:NAME_W-2] + "..") if len(name_raw) > NAME_W else name_raw.ljust(NAME_W)

            dedicated = svc.get("dedicated_removal", True)
            link_tag = "bright" if dedicated else "dim"
            if svc.get("url"):
                raw = svc["url"].replace("https://", "").replace("http://", "").replace("www.", "")
                link_display = f"[{raw}]"
                link_text = (link_display[:LINK_W-2] + "..") if len(link_display) > LINK_W else link_display.ljust(LINK_W)
            else:
                link_text = "-".ljust(LINK_W)

            notes_raw = svc.get("notes", "")
            notes = (notes_raw[:NOTES_W-2] + "..") if len(notes_raw) > NOTES_W else notes_raw.ljust(NOTES_W)

            sub = "✔" if svc["submitted"] else "✘"
            ver = "✔" if svc["verified"] else "✘"

            self.output_text.insert("end", f"│ {i:2} │ {name} │ ")
            self.output_text.insert("end", link_text, link_tag)
            self.output_text.insert("end", f" │ {notes} │ {sub:^{SUB_W}} │ {ver:^{VER_W}} │")
            current_line_length = len(f"│ {i:2} │ {name} │ {link_text} │ {notes} │ {sub:^{SUB_W}} │ {ver:^{VER_W}} │")
            if current_line_length < INNER_WIDTH + 2:
                self.output_text.insert("end", " " * (INNER_WIDTH + 2 - current_line_length))
            self.output_text.insert("end", "\n")

        self.output_text.config(state="disabled")
        self.append_output(f"└{'─' * INNER_WIDTH}┘\n")
        self.append_output("\nEnter a number (or click a row) to toggle SUBMITTED.\n")
        self.append_output("Type 'v <number>' to toggle VERIFIED.\n")
        self.append_output("Type 'o <number>' to open the URL.\n")
        self.append_output("Commands: b=Back, q=Quit\n")
        self.current_view = "services"

    def toggle_submitted(self, idx):
        if self.current_view == "services" and 0 <= idx < len(self.current_services):
            svc = self.current_services[idx]
            svc["submitted"] = not svc["submitted"]
            self.save_progress()
            status = "✔ SUBMITTED" if svc["submitted"] else "✘ Not submitted"
            self.append_output(f"[{svc['name']}] {status}\n")
            self.show_services(self.current_category, self.current_services)
        else:
            self.append_output("[!] Invalid service number or not in service view.\n")

    def toggle_verified(self, idx):
        if self.current_view == "services" and 0 <= idx < len(self.current_services):
            svc = self.current_services[idx]
            svc["verified"] = not svc["verified"]
            self.save_progress()
            status = "✔ VERIFIED" if svc["verified"] else "✘ Not verified"
            self.append_output(f"[{svc['name']}] {status}\n")
            self.show_services(self.current_category, self.current_services)
        else:
            self.append_output("[!] Invalid service number or not in service view.\n")

    def open_url(self, idx):
        if self.current_view == "services" and 0 <= idx < len(self.current_services):
            svc = self.current_services[idx]
            if svc.get("url"):
                webbrowser.open(svc["url"])
                self.append_output(f"[ Opened {svc['url']} ]\n")
            else:
                self.append_output("[!] No URL for this service.\n")
        else:
            self.append_output("[!] Invalid service number or not in service view.\n")

    def show_all_services(self):
        self.clear_output()
        self.append_output("\n" + "="*80 + "\n")
        self.append_output(" ALL REMAINING SERVICES\n")
        self.append_output("="*80 + "\n\n")
        for cat_name, services in self.data.items():
            for svc in services:
                if not svc["submitted"]:
                    self.append_output(f"* {svc['name']} ({cat_name})\n")
        self.append_output("\nCommands: m=Menu, q=Quit\n")
        self.current_view = "all"

def main():
    root = tk.Tk()
    app = MatrixCRTApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
