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
        self.selected_idx = None
        self.table_first_line = None
        self.intro_shown = False

        self.custom_font = tkfont.Font(family="Courier", size=10)
        self.bold_font = tkfont.Font(family="Courier", size=10, weight="bold")

        self.create_header()
        self.create_main_frame()
        self.create_status_bar()
        self.create_button_bar()
        # Pack the expanding main area last so bottom bars keep their space
        # when the window is resized smaller.
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.root.bind("<Up>", self.on_arrow_up)
        self.root.bind("<Down>", self.on_arrow_down)
        self.root.bind("<Return>", self.on_enter)

        self.apply_scanlines()
        self.root.update_idletasks()
        self.scanline_canvas.tk.call('lower', self.scanline_canvas._w)

        self.adjust_window_size()

        self.clear_output()
        self.show_intro()
        self.update_buttons()

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

        self.output_text = tk.Text(self.main_frame, wrap="none", bg="#0c0c0c", fg="#7fff7f",
                                   insertbackground="#7fff7f", font=self.custom_font,
                                   relief="flat", borderwidth=0, highlightthickness=0,
                                   takefocus=0, cursor="arrow")
        self.output_text.pack(side="left", fill="both", expand=True)
        self.output_text.bind("<Button-1>", self.on_output_click)

        self.output_text.tag_configure("bright", foreground="#7fff7f")
        self.output_text.tag_configure("dim", foreground="#555555")
        self.output_text.tag_configure("sel", background="#7fff7f", foreground="#0c0c0c")
        self.output_text.tag_configure("guide", foreground="#b8ffb8")

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

    def create_button_bar(self):
        self.button_frame = tk.Frame(self.root, bg="#0c0c0c", height=34)
        self.button_frame.pack(fill="x", side="bottom", padx=20, pady=(0, 10))
        self.button_frame.pack_propagate(False)

    def make_button(self, text, command):
        btn = tk.Button(self.button_frame, text=f"[ {text} ]", font=self.bold_font,
                        bg="#0c0c0c", fg="#7fff7f", activebackground="#7fff7f",
                        activeforeground="#0c0c0c", relief="flat", bd=0,
                        highlightthickness=1, highlightbackground="#4a9a4a",
                        highlightcolor="#7fff7f", padx=10, pady=2,
                        cursor="hand2", takefocus=0, command=command)
        btn.bind("<Enter>", lambda e: btn.config(bg="#7fff7f", fg="#0c0c0c"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#0c0c0c", fg="#7fff7f"))
        return btn

    def update_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        if self.current_view == "categories":
            buttons = [("ALL REMAINING", self.show_all_services),
                       ("QUIT", self.quit_app)]
        elif self.current_view == "services":
            buttons = [("BACK", self.show_categories),
                       ("OPEN LINK", self.open_selected_url),
                       ("SUBMIT", self.submit_selected),
                       ("VERIFY", self.verify_selected),
                       ("QUIT", self.quit_app)]
        else:
            buttons = [("MENU", self.show_categories),
                       ("QUIT", self.quit_app)]

        for text, command in buttons:
            self.make_button(text, command).pack(side="left", padx=6)

    def quit_app(self):
        self.save_progress()
        self.root.quit()

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
        index = self.output_text.index(f"@{event.x},{event.y}")
        line = self.output_text.get(f"{index} linestart", f"{index} lineend")
        match = re.match(r"\s*│\s*(\d+)\s*│", line)
        if match:
            num = int(match.group(1))
            if self.current_view == "categories":
                self.selected_idx = num - 1
                self.highlight_selection()
                self.select_category(num - 1)
            elif self.current_view == "services":
                self.selected_idx = num - 1
                self.highlight_selection()
        return "break"

    # ---------- SELECTION ----------
    def current_row_count(self):
        if self.current_view == "categories":
            return len(self.data)
        if self.current_view == "services":
            return len(self.current_services)
        return 0

    def highlight_selection(self):
        self.output_text.tag_remove("sel", "1.0", "end")
        if self.selected_idx is None or self.table_first_line is None:
            return
        line = self.table_first_line + self.selected_idx
        self.output_text.tag_add("sel", f"{line}.0", f"{line}.end")
        self.output_text.tag_raise("sel")
        self.output_text.see(f"{line}.0")

    def move_selection(self, delta):
        count = self.current_row_count()
        if count == 0:
            return
        if self.selected_idx is None:
            self.selected_idx = 0
        else:
            self.selected_idx = max(0, min(count - 1, self.selected_idx + delta))
        self.highlight_selection()

    def on_arrow_up(self, event=None):
        self.move_selection(-1)
        return "break"

    def on_arrow_down(self, event=None):
        self.move_selection(1)
        return "break"

    def on_enter(self, event=None):
        if self.selected_idx is None:
            return "break"
        if self.current_view == "categories":
            self.select_category(self.selected_idx)
        elif self.current_view == "services":
            self.open_url(self.selected_idx)
        return "break"

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

        self.table_first_line = int(self.output_text.index("end-1c").split(".")[0])
        for i, (cat_name, services) in enumerate(self.data.items(), 1):
            remaining = sum(1 for s in services if not s["submitted"])
            display_name = (cat_name[:CAT_W-2] + "..") if len(cat_name) > CAT_W else cat_name.ljust(CAT_W)
            row = f"│ {i:2} │ {display_name} │ {remaining:>{REM_W}} │"
            row = row.ljust(INNER_WIDTH + 2)
            self.append_output(row + "\n")

        self.append_output("└" + "─" * INNER_WIDTH + "┘\n")
        self.append_output("\nUse UP/DOWN + ENTER, or click a row, to select a category.\n")
        self.current_view = "categories"
        self.selected_idx = 0 if self.data else None
        self.highlight_selection()
        self.update_buttons()

    def show_categories(self):
        self.clear_output()
        self.show_categories_content()

    def select_category(self, idx):
        if 0 <= idx < len(self.data):
            self.current_category = list(self.data.keys())[idx]
            self.current_services = self.data[self.current_category]
            self.current_view = "services"
            self.selected_idx = 0
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
        self.table_first_line = int(self.output_text.index("end-1c").split(".")[0])
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
        self.append_output("\nUse UP/DOWN to select a row, ENTER to open its link.\n")
        self.append_output("Use the buttons below to OPEN LINK, SUBMIT, or VERIFY the selected row.\n")
        self.current_view = "services"
        if services:
            if self.selected_idx is None:
                self.selected_idx = 0
            self.selected_idx = min(self.selected_idx, len(services) - 1)
        else:
            self.selected_idx = None
        self.highlight_selection()
        self.update_buttons()

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

    def open_selected_url(self):
        if self.current_view == "services" and self.selected_idx is not None:
            self.open_url(self.selected_idx)
        else:
            self.append_output("[!] Select a service row first.\n")

    def submit_selected(self):
        if self.current_view == "services" and self.selected_idx is not None:
            self.toggle_submitted(self.selected_idx)
        else:
            self.append_output("[!] Select a service row first.\n")

    def verify_selected(self):
        if self.current_view == "services" and self.selected_idx is not None:
            self.toggle_verified(self.selected_idx)
        else:
            self.append_output("[!] Select a service row first.\n")

    def removal_guide(self, svc):
        """Build short, service-specific opt-out instructions from its metadata."""
        notes = svc.get("notes", "")
        notes_l = notes.lower()
        email = YOUR_DATA["email"]
        steps = []

        if not svc.get("dedicated_removal", True):
            email_match = re.search(r"[\w.+-]+@[\w-]+\.[a-z]{2,}", notes)
            if email_match:
                steps.append(f"Send a removal request from {email} to {email_match.group(0)}")
            else:
                steps.append("Use the site's contact/feedback channel to request removal")
            steps.append("Include your full name, current + past addresses, phone, and record URL")
            steps.append("Ask for written confirmation once the record is deleted")
        else:
            steps.append("Search the site for your full name + city/state and open YOUR listing")
            steps.append("Copy the exact listing URL, then paste it into the opt-out form")
            steps.append(f"Fill in: full name, address, phone, and email {email}")
            if "email" in notes_l:
                steps.append("Watch your inbox (and spam) and click the confirmation link")
            if "select profile" in notes_l:
                steps.append("Double-check you selected YOUR exact profile before submitting")

        lines = ["  GUIDE — how to disappear from this site:"]
        lines += [f"   {i}. {s}" for i, s in enumerate(steps, 1)]
        return lines

    def open_url(self, idx):
        if self.current_view == "services" and 0 <= idx < len(self.current_services):
            svc = self.current_services[idx]
            if svc.get("url"):
                webbrowser.open(svc["url"])
                self.append_output(f"[ Opened {svc['url']} ]\n")
                self.append_output("\n".join(self.removal_guide(svc)) + "\n", "guide")
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
        self.current_view = "all"
        self.selected_idx = None
        self.table_first_line = None
        self.update_buttons()

def main():
    root = tk.Tk()
    app = MatrixCRTApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
