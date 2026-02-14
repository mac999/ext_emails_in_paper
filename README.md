# Journal Email OCR Extractor

OCR-based tool for extracting author contact information from academic journal papers.

## Features

- Screen capture OCR: Captures left half of screen on F9 keypress
- Email extraction: Identifies and filters author emails
- Corresponding author detection: Marks authors with asterisk (*) indicators
- Metadata extraction: Paper title, author names, institutional affiliations
- Clipboard integration: Automatic URL/DOI capture from clipboard
- CSV export: Appends data to journal_emails.csv with timestamp
- Audio feedback: Beep on success/failure

## Requirements

**System:**
- Python 3.7 or higher
- Tesseract OCR 4.0+

**Python packages:**
```bash
pip install pytesseract pillow keyboard pandas pyperclip
```

## Installation

**Step 1: Install Tesseract OCR**

Download from: https://github.com/UB-Mannheim/tesseract/wiki

Default installation path: `C:\Program Files\Tesseract-OCR\tesseract.exe`

**Step 2: Install Python dependencies**

```bash
pip install -r requirements.txt
```

**Step 3: Configure Tesseract path**

Edit line 12 in `ext_email_in_paper.py` if Tesseract is installed elsewhere:
```python
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'
```

## Usage

**Preparation:**
1. Open academic paper in PDF viewer or browser
2. Position window on LEFT half of screen
3. Scroll to ensure visibility of: title, author names, emails, affiliations, "*Correspondence:" section
4. (Optional) Copy paper URL or DOI to clipboard

**Execution:**
```bash
python ext_email_in_paper.py
```

**Controls:**
- F9: Trigger screen capture and extraction
- ESC: Exit program

**Output:**

Data appends to `journal_emails.csv` with columns:
- Email: Author email address
- Type: "Corresponding" or "Co-author"
- All_Authors: Comma-separated author list
- Paper_Title: Extracted paper title
- Affiliation: Primary institutional affiliation
- URL_or_DOI: Documentation link from clipboard
- Captured_Time: Timestamp (YYYY-MM-DD HH:MM:SS)

## Extraction Logic

**Screen capture:**
- Captures left screen region: (0, 0, width/2, height)
- Processes via Tesseract OCR engine

**Email detection:**
- Regex pattern: `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- Filters system emails: mdpi.com, w3.org, example.com, noreply, etc.

**Corresponding author identification:**
- Method 1: "*Correspondence:" keyword followed by name and/or email
- Method 2: Author name with asterisk notation (e.g., "John Doe 1*")
- Fallback: First email in list if pattern matching fails

**Author name extraction:**
- Locates "Article" keyword boundary
- Extracts capitalized names followed by numbers/asterisks
- Filters common title keywords (design, system, model, etc.)
- Stops at "Abstract" or institutional affiliation sections

**Title extraction:**
- Searches lines between "Article" and author section
- Excludes metadata lines: Abstract, Keywords, Citation, Received, Published
- Combines up to 6 consecutive non-metadata lines

**Affiliation extraction:**
- Keywords: university, institute, college, department, laboratory, etc.
- Captures primary line plus following 1-2 address lines
- Stops at non-address content

## Troubleshooting

**No emails found:**
- Verify author section is visible on LEFT screen half
- Check OCR quality: High DPI displays may need scaling adjustments
- Ensure PDF text layer exists (not scanned image)

**Incorrect author extraction:**
- Edit `title_keywords` list (lines 99-107) to filter false positives
- Verify "Article" keyword appears above author section
- Check for unusual journal formatting

**Tesseract error:**
- Confirm installation path matches line 12 configuration
- Verify Tesseract is in system PATH
- Reinstall if necessary

**Missing corresponding author:**
- Ensure "*Correspondence:" section is visible on screen
- Verify asterisk notation on author name
- Check console output for pattern matching failures

**CSV encoding issues:**
- UTF-8-sig encoding used for compatibility
- Open with Excel or text editor supporting UTF-8

## Technical Details

**Dependencies:**
- pytesseract: Python wrapper for Tesseract OCR
- PIL/Pillow: Screen capture and image processing
- keyboard: Global hotkey registration
- pandas: Data manipulation and CSV operations
- pyperclip: Clipboard access

## License

MIT License

## Notes

- Designed for academic research purposes
- Works best with standard journal article formats (MDPI, Elsevier, etc.)
- Manual verification recommended for critical data collection
- Screen capture size is fixed to left half; adjust display accordingly

