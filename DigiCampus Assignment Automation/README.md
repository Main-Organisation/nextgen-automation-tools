
# DigiCampus Assignment Automation 🚀

A Python-based automation system for creating and uploading assignments to the DigiCampus LMS.

This project automates the repetitive process of creating multiple assignments by reading assignment details from an Excel file, uploading the corresponding DOCX files to the DigiCampus attachment storage, and creating assignment drafts through the DigiCampus API.

---

## 🎯 Problem Statement

Creating multiple assignments manually in an LMS is repetitive and time-consuming.

The traditional workflow involves:

1. Login to DigiCampus
2. Open the classroom
3. Navigate to Assignments
4. Click Create Assignment
5. Enter assignment title
6. Enter start and due dates
7. Enter description
8. Upload the assignment document
9. Save the assignment
10. Repeat the entire process for every assignment

For 5–10 assignments, this becomes unnecessary repetitive work.

This project automates the complete workflow.

---

## 💡 Solution

The automation takes assignment information from an Excel spreadsheet and performs the following workflow:

```text
Excel File
    │
    ├── Assignment Title
    ├── Description
    ├── Start Date
    ├── Due Date
    └── DOCX Path
          │
          ▼
     Python Automation
          │
          ▼
   DigiCampus Authentication
          │
          ▼
    Auth Token Capture
          │
          ▼
 Generate Attachment Signed URL
          │
          ▼
       Amazon S3
     DOCX Upload
          │
          ▼
 DigiCampus Assignment API
          │
          ▼
    Assignment Draft
````

---

## ✨ Features

* Automated DigiCampus login workflow
* Manual Google/Cloudflare verification support
* Browser-based authentication using Selenium
* Automatic authentication-token capture
* Excel-based assignment configuration
* DOCX assignment upload
* Automatic signed URL generation
* Direct upload to Amazon S3 using the signed URL
* Automatic assignment creation through DigiCampus REST API
* Multiple assignments processed sequentially
* Assignment creation as **Draft**
* Publish operation intentionally excluded for safety
* Detailed console logging
* Success/failure tracking

---

## 🛠️ Technology Stack

* **Python**
* **Selenium**
* **Requests**
* **OpenPyXL**
* **Microsoft Excel**
* **DigiCampus REST API**
* **Amazon S3**
* **DOCX**

---

## 📁 Project Structure

```text
DigiCampus-Assignment-Automation/
│
├── automation.py
├── assignments.xlsx
├── requirements.txt
├── README.md
│
└── assignments/
    ├── Assignment_1_Introduction_to_Computers_Programming_Algorithms.docx
    ├── Assignment_2_C_Basics_Operators_Loops.docx
    ├── Assignment_3_Arrays_and_Functions.docx
    ├── Assignment_4_Structure_and_Union.docx
    └── Assignment_5_Pointers_and_File_Handling.docx
```

---

# 📊 Excel Configuration

Assignments are controlled through an Excel file.

The spreadsheet contains:

| Column        | Description            |
| ------------- | ---------------------- |
| `Title`       | Assignment title       |
| `Description` | Assignment description |
| `StartDate`   | Assignment start date  |
| `DueDate`     | Assignment due date    |
| `DocxPath`    | Path to the DOCX file  |

Example:

```text
Title:
Assignment 1 - Introduction to Computer, Programming & Algorithms

Description:
Unit 1 assignment covering computer system components,
hardware and software, algorithms, complexity and flowcharts.

StartDate:
30 Aug 2026 10:00

DueDate:
31 Aug 2026 23:00

DocxPath:
assignments/Assignment_1_Introduction_to_Computers_Programming_Algorithms.docx
```

---

# 🔄 Automation Workflow

## 1. Authentication

Selenium opens the DigiCampus login page.

The user completes Google login and any Cloudflare verification manually if required.

The automation then detects the authenticated browser session.

```text
Chrome
   ↓
Google Login
   ↓
DigiCampus
   ↓
Authenticated Session
```

---

## 2. Authentication Token

After authentication, the automation captures the required DigiCampus authentication token from the browser session.

The token is never printed to the console.

---

## 3. Generate Signed Upload URL

For every DOCX file, the automation calls:

```text
/rest/attachment/generatePutSignedUrl
```

The request contains information such as:

```text
fileName
contentLength
contentType
feature = ASSIGNMENT_RESOURCE
```

DigiCampus returns:

* Media ID
* Document ID
* Signed S3 URL

---

## 4. Upload DOCX to Amazon S3

The DOCX file is uploaded directly to the signed Amazon S3 URL.

The automation verifies the HTTP response.

```text
Signed URL
     ↓
Amazon S3
     ↓
HTTP 200
     ↓
Upload Successful
```

---

## 5. Create Assignment Draft

After the file has been uploaded, the automation sends the assignment information to:

```text
/rest/assignments/v1/?classId=<CLASS_ID>
```

The payload includes:

```text
name
description
assignmentType
startDate
dueDate
draft
submissionType
resources
```

The resource contains the Media ID and Document ID generated during the upload process.

---

# 📝 Assignment Draft Mode

This project intentionally creates assignments as **Drafts**.

The automation does **NOT** call the Publish API.

This is an intentional safety mechanism.

The workflow is:

```text
Create Assignment
       ↓
     Draft
       ↓
Manual Review
       ↓
Manual Publish
```

This prevents accidental publishing of incorrect assignments.

---

# 🧪 Tested Workflow

The system was tested with five assignments.

| Assignment                        | API Status | Result    |
| --------------------------------- | ---------: | --------- |
| Unit 1 – Computer & Algorithms    |        201 | ✅ Created |
| Unit 2 – C Basics & Loops         |        201 | ✅ Created |
| Unit 3 – Arrays & Functions       |        201 | ✅ Created |
| Unit 4 – Structure & Union        |        201 | ✅ Created |
| Unit 5 – Pointers & File Handling |        201 | ✅ Created |

Final test result:

```text
Successful: 5 / 5
```

All five assignments were successfully created as drafts.

---

# ⚙️ Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd DigiCampus-Assignment-Automation
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 📦 Requirements

Create a `requirements.txt` file containing:

```text
selenium
requests
openpyxl
python-docx
```

---

# ▶️ Running the Automation

Place the assignment DOCX files inside:

```text
assignments/
```

Update:

```text
assignments.xlsx
```

with the required assignment information.

Then run:

```bash
python automation.py
```

Chrome will open automatically.

Complete the DigiCampus Google login manually.

After authentication, the automation will process the assignments sequentially.

Example:

```text
Assignments found: 5

ASSIGNMENT 1/5
...
Assignment API: 201
Assignment created successfully.

ASSIGNMENT 2/5
...
Assignment API: 201
Assignment created successfully.

...

Successful: 5 / 5
```

---

# 🔐 Security

Never commit the following information to GitHub:

* Passwords
* Authentication tokens
* Browser cookies
* Session credentials
* Signed S3 URLs
* API secrets
* Personal credentials

The automation is designed so that authentication credentials remain outside the source code.

Add sensitive files to `.gitignore`.

Example:

```text
.venv/
__pycache__/
*.pyc

.env
credentials.json
cookies.json

*.log
```

---

# ⚠️ Important Notes

This project is designed for authorized use with an institution's DigiCampus account.

The automation should only be used by users who have permission to automate assignment creation in the LMS.

The project does not attempt to bypass Google authentication or Cloudflare verification.

Google/Cloudflare verification is completed manually.

---

# 🚀 Future Improvements

Possible future versions could include:

* Automatic assignment generation from a syllabus
* AI-assisted question generation
* Automatic DOCX generation
* Automatic Excel generation
* Assignment validation before upload
* Duplicate assignment detection
* Retry mechanism for failed API requests
* Detailed execution logs
* GUI interface
* Dry-run mode
* Automatic draft verification
* Batch processing for multiple courses
* Course selection from Excel
* Optional manual publish workflow

---

# 📚 Example Use Case

Suppose a course has five units.

Instead of manually creating five assignments:

```text
Unit 1 → Assignment
Unit 2 → Assignment
Unit 3 → Assignment
Unit 4 → Assignment
Unit 5 → Assignment
```

The instructor prepares:

```text
5 DOCX files
+
1 Excel file
```

Then runs:

```bash
python automation.py
```

The system processes all five assignments automatically.

---

# 🎓 Educational Automation

This project demonstrates how traditional academic administrative workflows can be converted into reusable automation pipelines using:

* Browser automation
* REST APIs
* Cloud storage
* Structured data
* Document processing
* Batch processing

The core idea is simple:

> **Prepare once, automate the repetitive work, and keep the final academic decision under human control.**

---

## 👨‍💻 Author

**Vivek Saxena**

Assistant Professor
Faculty of Computer Science & Applications
Vivekanand Global University, Jaipur

---

## ⭐ Project Status

**Status: Working Prototype / Production-Oriented Automation**

Current verified workflow:

```text
Login
  ↓
Authentication
  ↓
Excel
  ↓
DOCX
  ↓
Signed URL
  ↓
Amazon S3
  ↓
DigiCampus Assignment API
  ↓
Draft Creation
  ↓
5 / 5 Successful
```

---

## 📄 License

This project is intended for educational and authorized institutional automation purposes.

````

