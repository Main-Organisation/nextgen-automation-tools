# VGU Drive Inventory System

A lightweight Google Apps Script automation for recursively scanning Google Drive repositories and generating a centralized academic-content compliance dashboard.

## Features

- Recursive Google Drive scanning
- Scans root files and files inside nested folders
- Complete file/folder inventory
- Total file count
- Module/Unit 1–5 detection
- Handout detection
- TLP detection
- Lab Manual detection
- Assignment file counting
- Latest file update tracking
- Program, Subject Code, Subject and Faculty mapping
- Centralized Dashboard
- Missing-resource reporting
- Complete/Pending status
- Works with messy and inconsistent folder hierarchies

## Project Structure

```text
Drive-Inventory-System/
├── Code.gs
├── Analyzer.gs
├── README.md
├── CHANGELOG.md
└── screenshots/
    ├── dashboard.png
    └── inventory.png
```

## How It Works

```text
Drive_List
    |
    v
scanAllDrives()
    |
    v
Google Drive Repository
    |
    +-- Root files
    +-- Folders
         +-- Files
         +-- Subfolders
              +-- Files
    |
    v
Inventory Sheets
    |
    v
generateDashboard()
    |
    v
Centralized Dashboard
```

## Drive_List Format

Create a sheet named `Drive_List` with:

| S No | Program | Subject Code | Subject | Faculty Name | Drive Link |
|---:|---|---|---|---|---|
| 1 | BCA-I | UGCSA102 | Introduction to Computers and Programming in C | FACULTY NAME | Google Drive Folder URL |
| 2 | BCA-I | UGCSA103 | Computer Systems and Organization | FACULTY NAME | Google Drive Folder URL |

The Drive Link should point to the Google Drive folder to be scanned.

## Setup

1. Create a Google Spreadsheet.
2. Create a `Drive_List` sheet.
3. Add the columns shown above.
4. Create a `Dashboard` sheet.
5. Add `Code.gs` and `Analyzer.gs` to Apps Script.
6. Authorize Google Drive and Google Sheets access when prompted.
7. Add repository links to `Drive_List`.
8. Run:

```text
scanAllDrives()
```

9. Then run:

```text
generateDashboard()
```

## Dashboard

The Dashboard reports:

| Field | Description |
|---|---|
| Program | Academic program |
| Subject Code | Course/subject code |
| Subject | Subject name |
| Faculty | Assigned faculty |
| Total Files | Total files found recursively |
| Modules | Modules/Units detected out of 5 |
| Handout | Availability |
| TLP | Availability |
| Lab Manual | Availability |
| Assignments | Number of assignment files detected |
| Last Updated | Latest file update timestamp |
| Missing | Missing required items |
| Status | Overall repository status |

## Inventory Sheets

Each scanned repository gets an inventory sheet named:

```text
Subject | Faculty
```

Example:

```text
Machine Learning | ARIJIT PATRA
```

The inventory records:

- Serial number
- Folder level
- Folder path
- Item name
- Item type
- File extension
- File size
- Last updated time
- Google Drive URL

## Detection

### Handout

Recognizes names containing:

```text
handout
course handout
course handbook
```

### TLP

Recognizes:

```text
tlp
teaching learning plan
teaching lecture plan
```

### Lab Manual

Recognizes:

```text
lab manual
laboratory manual
lab mannual
```

### Modules / Units

Detects Module/Unit 1–5 using common patterns such as:

```text
Module 1
Module-1
Module_1
Unit 1
Unit-1
Unit_1
Unit I
Unit-II
```

### Assignments

Assignment files are detected when the filename contains:

```text
assignment
```

## Use Cases

### Faculty Content Audit

Check whether repositories contain required Notes/Modules, Handout, TLP, Lab Manual and Assignments.

### Messy Drive Audit

The scanner does not require a fixed folder hierarchy. Files may exist in the root or any nested folder.

Example:

```text
Root/
├── Notes.pdf
├── TLP.docx
├── Module 1.pdf
├── Notes/
│   ├── Module 2.pdf
│   └── Module 3.pdf
└── TLP/
    └── Teaching Learning Plan.docx
```

The scanner recursively searches the complete repository.

### Student Submission Audit

The same scanning approach can be adapted to audit student assignment repositories and identify uploaded or missing submissions.

## Technology

- Google Apps Script
- Google Drive
- Google Sheets
- JavaScript

## Privacy

Do not publish real institutional Drive links, private faculty/student data, credentials, API keys, or confidential information in a public GitHub repository.

For a public release, use sample or anonymized `Drive_List` data.

## Version

**v1.0.0 — Initial Stable Release**

## Screenshots

Add screenshots to the `screenshots/` folder and reference them with:

```markdown
![Dashboard](screenshots/dashboard.png)
![Inventory](screenshots/inventory.png)
```

## Future Enhancements

- Lab Required Yes/No rules
- Completion percentage
- Summary cards
- Repository health indicators
- Assignment 1–5 detection
- Duplicate file detection
- Empty-folder detection
- Naming-standard validation
- Faculty-wise reporting
- Student assignment submission tracking
- PDF report generation

## License

MIT License
