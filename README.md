<div align="center">
  
# Ghostbyte

  <img width="400" alt="ghostbyte" src="https://github.com/user-attachments/assets/a3e09134-17f6-464a-a8d3-b37567345423" />

**Personal Data Removal Tool**  

Congratulations you paranoid fuck.  
You’re tired of being Google-able.  
Good. Time to disappear.

Ghostbyte loads the full **184-source** personal data removal list from Michael Bazzell’s *Extreme Privacy* workbook and gives you a clean, retro hacker interface to track every purge like a professional.

No fake “privacy services.”
Just you, the terminal, and 184 data brokers about to have a very bad day.

---
</div>

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
