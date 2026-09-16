# Isolated CRM (Desktop Edition)

A portable, offline desktop CRM application engineered to run locally with complete data privacy and zero cloud storage.

---

## 🚀 Quick Start / How to Run

1. Run **`start_crm.bat`** (or launch **`PersonalCRM.exe`**).
2. The desktop application will launch immediately.

> [!NOTE]
> All application data (database, attachments, and logs) are stored locally inside the application directory. No data is sent to or stored in the cloud.

---

## 🔒 Local Data Privacy & In-App Updates

- **100% Offline Storage**: All records and attachments stay strictly in the local `data/` directory.
- **Built-in Auto-Updater**: Check for new software releases and update directly from within the application with automatic pre-update database backups.

---

## 📂 Directory Layout

```
CRM/
├── start_crm.bat              # Windows batch launcher
├── requirements.txt           # Python dependencies
├── README.md                  # System manual
│
├── app/                       # Application Source
│   ├── main.py                # Desktop GUI Bootstrap & Navigation
│   ├── core/                  # Path config, SQLite engine, updater
│   ├── models/                # Database models
│   ├── modules/               # Feature modules
│   └── ui/                    # Dark theme design system & widgets
│
├── data/                      # Local Data Directory
│   ├── crm.db                 # SQLite database
│   ├── attachments/           # Local file attachments
│   └── backups/               # Local database backups
│
└── logs/                      # Application logs
```
