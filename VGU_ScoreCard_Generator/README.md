\# VGU ScoreCard Generator



A Python-based automation tool developed to generate MCA admission scorecards in PDF format from Excel-based student admission data.



The project reads student records from multiple MCA admission sessions, extracts VGUCET candidates, generates continuous application numbers, fills a predefined Word scorecard template, and produces individual PDF scorecards.



\---



\## 📌 Project Purpose



The purpose of this project is to automate the preparation of MCA admission scorecards.



Instead of manually preparing hundreds of scorecards, the system:



1\. Reads student data from Excel.

2\. Detects the VGUCET data section in each worksheet.

3\. Extracts candidate name, score and VGUCET rank.

4\. Combines records from multiple academic sessions.

5\. Sorts records chronologically.

6\. Generates application numbers automatically.

7\. Uses a predefined Word scorecard template.

8\. Replaces placeholders with candidate information.

9\. Generates individual PDF scorecards.

10\. Supports bulk generation of scorecards.



\---



\## ✨ Features



\- Excel-based student data processing

\- Multiple worksheet support

\- Automatic VGUCET section detection

\- Automatic extraction of:

&#x20; - Candidate Name

&#x20; - Score

&#x20; - VGUCET Rank

&#x20; - Academic Year

\- Automatic application number generation

\- Continuous application numbering

\- Word template based scorecard generation

\- PDF generation

\- Individual scorecard generation

\- Bulk scorecard generation

\- Existing PDF detection to avoid unnecessary regeneration

\- Header image support

\- Template-based formatting

\- Student data excluded from Git tracking using `.gitignore`



\---



\## 🏗️ Project Structure



```text

VGU\_ScoreCard\_Generator/

│

├── README.md

├── .gitignore

├── app.py

├── main.py

├── pdf\_generator.py

├── bulk\_pdf\_generator.py

├── requirements.txt

│

└── template/

&#x20;   ├── Header.png

&#x20;   └── Scorecard\_Template.docx

