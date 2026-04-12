<div align="center">
  
# Ghostbyte

  <img width="400" alt="ghostbyte" src="https://github.com/user-attachments/assets/a3e09134-17f6-464a-a8d3-b37567345423" />

**Personal Data Removal Tool**  

Congratulations you paranoid fuck.  
You’re tired of being Google-able.  
Good. Time to disappear.

Ghostbyte loads the full **184-source** personal data removal list from Michael Bazzell’s *Extreme Privacy* workbook and gives you a clean, retro hacker interface to track every purge like a professional.

No fake “privacy services.” Just you, the terminal, and 184 data brokers about to have a very bad day.

---

<img width="953" height="905" alt="image" src="https://github.com/user-attachments/assets/8b5f613d-bd57-4bfa-904d-ee3942f2b147" />

</div>

## Philosophy & Design

Many commercial privacy tools promise to automate the opt‑out process, but they require you to hand over your full name, address, phone number, and email—often storing this sensitive data on third‑party servers. Ghostbyte takes a fundamentally different approach:

- **No personal data is ever stored in plaintext or transmitted.** The `YOUR_DATA` dictionary in the source code is a placeholder; you are encouraged to keep your actual details in your head or a separate, encrypted location.
- **Progress is tracked locally** in `data/privacy_progress.json`, but only Boolean flags (`submitted`/`verified`) are saved—never your identity.
- **The process remains semi-manual by design.** GhostByte opens a window to your browser for you to the opt‑out page, and mark your progress. This ensures you retain full oversight and never surrender your information to an intermediary.

This hybrid model—guided, systematic, but ultimately human‑controlled—represents a pragmatic balance between convenience and uncompromising privacy.

> **Beta Notice:** Ghostbyte is currently in beta. The interface and feature set are stable, but future updates may include additional categories, improved window scaling, and optional automation for *non‑sensitive* steps (e.g., opening URLs in bulk). Feedback and contributions are welcome.

### Features

- Complete 184-source database from the official workbook
- Beautiful green-on-black CRT interface with real scanlines
- Live progress tracking (submitted / verified / % purged)
- Non-removal URLs automatically dimmed grey so you know when you’re dealing with email-only bullshit
- One-key commands: numbers to toggle, `o <num>` to open link, `v <num>` to verify
- Auto-saves your progress forever
- Loads fresh sources from `data/sources.json` on every run

### Quick Start

```bash
git clone https://github.com/Excalibra/ghostbyte.git
cd ghostbyte
pip install -r requirements.txt
python ghostbyte.py
```

### Folder Structure
```
ghostbyte/
├── ghostbyte.py
├── img/
│   └── ghostbyte.png
├── data/
│   ├── sources.json
│   └── privacy_progress.json   ← auto-generated
├── requirements.txt
├── README.md
└── .gitignore
```

### Commands (inside the GUI)

- `1-9` → select category  
- number → toggle **SUBMITTED**  
- `v <number>` → toggle **VERIFIED**  
- `o <number>` → open the removal URL  
- `m` → menu  
- `a` → show ALL remaining services  
- `b` → back  
- `q` → quit and save

### Pro Tip

Start with **CORE DATA BROKERS (MOST BANG)**.  
Once those are dead, hit the big 184-source list and watch the internet slowly forget you ever existed.

---
