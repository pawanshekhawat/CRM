# Personal CRM - Portable Institute Edition (PySide6 + SQLite)

A 100% portable, offline desktop CRM engineered to run directly from a USB flash drive or portable SSD without storing application data or databases on the host PC.

---

## 🚀 Quick Start / How to Run

1. **Plug in your USB drive** on any Windows computer.
2. Double-click **`launcher.bat`** (or **`start_crm.bat`**) in the `CRM` folder.
3. The native desktop application opens immediately.

> [!NOTE]
> All paths (database `crm.db`, student photos, fee receipts, PDF slips, Excel exports, and temporary caches) are calculated dynamically relative to the USB drive (`%~dp0`). It works seamlessly regardless of whether the drive is assigned `D:`, `E:`, `F:`, or any other drive letter.

---

## 📋 Features Implemented

### 1. Complete CADDESK Admission Form Mapping
- **Header & Identity**: ID No. (with Auto-Generator), Online Admission flag, Online Portal Reference No., Passport Photo upload/preview.
- **Personal & Academic**: Student Name, Father's Name, Mother's Name, Date of Birth, Father's Occupation, College/School, Primary Course Name, Year/Semester, Aadhar UIDAI No.
- **Contact & Address**: Primary Mobile No., Email ID, Father's Contact, 2. Alternate Contact, Permanent Address, District, State, PIN Code.
- **Course Sessions & Book Record**: Multi-session breakdown (e.g. *1st & 2nd-Session*, *Full Stack Development*, etc.) with Book Issued status, Book title/issue details, and Student Signature confirmation.
- **10-Installment Fee Ledger**:
  - Total Course Fee, Scholarship / Discount, and Net Payable calculations.
  - 10 distinct installment rows (1st through 10th) tracking Due Amount, Paid Amount, Payment Date, Payment Mode (Cash, UPI, Bank Transfer, Cheque), Receipt / UTR No., and Remarks.
  - Live auto-calculated **Total Paid** and **Balance Due** metrics.
- **Declaration & Status**: Integrated terms declaration and student lifecycle statuses (*Active*, *Completed*, *Dropped*, *Inquiry*).

### 2. Extensible Hybrid Schema (Dynamic Custom Fields)
- Add new custom inputs (e.g., *Blood Group*, *Batch Timing*, *Previous Qualification*) dynamically via the **"⚙️ Custom Fields"** button without changing any code or running database migrations.
- Supports Text, Number, Date, Dropdown Select, Checkbox, and Textarea types.

### 3. Printable PDF Admission Slip & Receipts
- Generates official **Admission Slips & Fee Receipts in PDF format** mirroring the physical CADDESK registration form.
- Saved automatically to `./data/receipts/` and viewable with one click.

### 4. Excel & CSV Export
- Instant one-click export of student directories and financial metrics into `./data/exports/`.

### 5. Pluggable Module Architecture
- Built on an extensible `BaseModule` and `ModuleRegistry` interface.
- New modules (e.g., Staff, Inquiries, Inventory, Batches, Exams) can be added as separate plugins under `app/modules/<module_name>/` without altering existing student records.

---

## 📂 USB Directory Layout

```
CRM/
├── launcher.bat               # 1-Click silent Windows launcher
├── start_crm.bat              # Console launcher with debug fallback
├── requirements.txt           # Python dependency specifications
├── README.md                  # System manual
│
├── app/                       # PySide6 Application Source
│   ├── main.py                # Desktop GUI Bootstrap & Navigation
│   ├── core/                  # Path config, SQLite engine, Base ORM
│   ├── models/                # Relational Student & Custom Field models
│   ├── modules/               # Pluggable modules (Students)
│   └── ui/                    # Dark theme design system & widgets
│
├── data/                      # 100% Isolated Data Directory
│   ├── crm.db                 # SQLite database
│   ├── attachments/photos/    # Student photo storage
│   ├── receipts/              # Generated PDF admission slips
│   ├── exports/               # Exported Excel/CSV sheets
│   └── temp/                  # Isolated temporary file cache
│
└── logs/                      # Isolated application logs (crm.log)
```
