import pytesseract
from PIL import ImageGrab
import keyboard
import re
import pandas as pd
import os
import time
import winsound
import pyperclip

# Tesseract installation path
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'

# Output file name
SAVE_FILE = "journal_emails.csv"

def extract_emails_from_screen():
    try:
        # Capture left half of screen
        from PIL import ImageGrab
        full_screen = ImageGrab.grab()
        width, height = full_screen.size
        left_half = full_screen.crop((0, 0, width // 2, height))
        extracted_text = pytesseract.image_to_string(left_half, lang='eng')
        lines = extracted_text.split('\n')
        
        # Extract emails
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        found_emails = re.findall(email_pattern, extracted_text)
        
        # Filter out system/example emails
        real_emails = []
        exclude_patterns = ['mdpi.com', 'w3.org', '.png', '.jpg', '.gif', 
                           'noreply', 'example.com', 'test.com', 'sample.com',
                           'your-email', 'email.com']
        
        for email in found_emails:
            email_lower = email.lower()
            if not any(pattern in email_lower for pattern in exclude_patterns):
                if '@' in email and '.' in email.split('@')[1]:
                    real_emails.append(email)
        
        real_emails = list(set(real_emails))
        
        # Identify corresponding author
        corresponding_email = ""
        corresponding_author = ""
        
        corr_patterns = [
            r'[\*\s]*Correspondence[:\s]+([A-Za-z\s\-\.]+)[;,]\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'[\*\s]*Correspondence[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
            r'[\*\s]*(?:Author)?[:\s]+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        for pattern in corr_patterns:
            matches = re.search(pattern, extracted_text, re.IGNORECASE)
            if matches:
                groups = matches.groups()
                if len(groups) == 2:
                    corresponding_author = groups[0].strip()
                    corresponding_email = groups[1].strip()
                elif len(groups) == 1:
                    corresponding_email = groups[0].strip()
                break
        
        # If not found, look for starred author names
        if not corresponding_email and real_emails:
            starred_author_pattern = r'([A-Z][a-z]+(?:\-[A-Z][a-z]+)?\s+[A-Z][a-z]+)\s*\d*\*'
            starred_match = re.search(starred_author_pattern, extracted_text)
            if starred_match:
                corresponding_author = starred_match.group(1).strip()
                corresponding_email = real_emails[0]
        
        # Extract author names
        authors_list = ""
        article_idx = -1
        author_end_idx = -1
        for i, line in enumerate(lines):
            if article_idx == -1 and 'article' in line.lower() and len(line.strip()) < 20:
                article_idx = i
            if article_idx >= 0 and i > article_idx + 1:
                if ('abstract' in line.lower() or 
                    re.match(r'^\s*\d+\s+[A-Z]', line) or
                    'division' in line.lower() or
                    'department' in line.lower() or
                    'university' in line.lower()):
                    author_end_idx = i
                    break
        
        if article_idx >= 0:
            author_section_lines = lines[article_idx + 1:author_end_idx if author_end_idx > 0 else article_idx + 10]
            author_section_text = " ".join([l.strip() for l in author_section_lines if len(l.strip()) > 5])
            
            author_pattern = r'\b([A-Z][a-z]+(?:\-[A-Z][a-z]+)?\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*[\d\*,]'
            author_matches = re.findall(author_pattern, author_section_text)
            
            if author_matches:
                unique_authors = []
                title_keywords = [
                    'article', 'study', 'analysis', 'review', 'research', 'development', 'evaluation',
                    'system', 'method', 'approach', 'model', 'framework', 'application', 'design',
                    'implementation', 'investigation', 'assessment', 'characterization', 'optimization',
                    'novel', 'improved', 'enhanced', 'comprehensive', 'systematic', 'comparative',
                    'effect', 'impact', 'influence', 'role', 'mechanism', 'process', 'technique',
                    'based', 'using', 'toward', 'towards', 'new', 'advanced', 'intelligent',
                    'data', 'information', 'knowledge', 'learning', 'neural', 'network', 'deep',
                    'machine', 'artificial', 'intelligence', 'digital', 'smart', 'autonomous',
                    'sustainable', 'green', 'eco', 'climate', 'environmental', 'energy', 'renewable',
                    'health', 'medical', 'clinical', 'disease', 'cancer', 'treatment', 'therapy',
                    'molecular', 'genetic', 'protein', 'cell', 'tissue', 'biological', 'chemical'
                ]
                
                for author in author_matches[:15]:
                    if (author not in unique_authors and 
                        len(author) > 5 and 
                        author.lower() not in title_keywords and
                        not any(kw in author.lower() for kw in title_keywords)):
                        unique_authors.append(author)
                
                authors_list = ", ".join(unique_authors)
        
        # Extract paper title
        current_title = ""
        article_idx = -1
        for i, line in enumerate(lines):
            if 'article' in line.lower() and len(line.strip()) < 20:
                article_idx = i
                break
        
        if article_idx >= 0:
            title_parts = []
            for i in range(article_idx + 1, min(article_idx + 15, len(lines))):
                line = lines[i].strip()
                
                is_meta = any(skip in line for skip in ['Abstract', 'Keywords', 'Citation', 
                                                        'Downloaded', 'Received', 'Accepted',
                                                        'Published', 'Correspondence'])
                is_author_line = re.search(r'[A-Z][a-z]+\s+[A-Z][a-z]+\s*[\d\*,]', line)
                starts_with_number = re.match(r'^\s*\d+\s+', line)
                
                if len(line) > 10 and not is_meta and not is_author_line and not starts_with_number:
                    title_parts.append(line)
                elif len(title_parts) > 0 and (is_author_line or starts_with_number):
                    break
            
            if title_parts:
                current_title = " ".join(title_parts[:6])
        
        if not current_title:
            for line in lines[:15]:
                if len(line.strip()) > 40 and 'article' not in line.lower():
                    current_title = line.strip()
                    break
        
        # Extract affiliation
        affiliation = ""
        affiliation_keywords = ['university', 'institute', 'college', 'laboratory', 
                                'department', 'school', 'academy', 'center', 'research',
                                'hospital', 'corporation', 'company', 'division']
        
        affiliation_lines = []
        found_affiliation = False
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            clean_line = line.strip()
            
            if not found_affiliation and any(keyword in line_lower for keyword in affiliation_keywords):
                if len(clean_line) > 15 and len(clean_line) < 200:
                    affiliation_lines.append(clean_line)
                    found_affiliation = True
                    
                    for j in range(i + 1, min(i + 3, len(lines))):
                        next_line = lines[j].strip()
                        if (len(next_line) > 10 and 
                            (re.search(r'\d+', next_line) or 
                             'korea' in next_line.lower() or
                             'republic' in next_line.lower() or
                             any(kw in next_line.lower() for kw in ['ro,', 'st,', 'street', 'road']))):
                            affiliation_lines.append(next_line)
                        else:
                            break
                    break
        
        if affiliation_lines:
            affiliation = " ".join(affiliation_lines)
        
        # Get URL/DOI from clipboard
        current_url = ""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                if clipboard_text.startswith("http") or "doi.org" in clipboard_text or "doi:" in clipboard_text:
                    current_url = clipboard_text.strip()
        except:
            pass
        
        if real_emails:
            save_to_excel(real_emails, current_title, affiliation, current_url, 
                         authors_list, corresponding_author, corresponding_email)
            winsound.Beep(1000, 200)
            print(f"Saved {len(real_emails)} email(s)")
        else:
            winsound.Beep(500, 100)
            winsound.Beep(500, 100)
            print("No emails found")

    except Exception as e:
        print(f"Error: {e}")

def save_to_excel(emails, title, affiliation, url, authors, corr_author, corr_email):
    """Save extracted data to Excel file"""
    new_data = []
    for email in emails:
        is_corresponding = (email.lower() == corr_email.lower()) if corr_email else False
        
        new_data.append({
            'Email': email,
            'Type': 'Corresponding' if is_corresponding else 'Co-author',
            'All_Authors': authors if authors else '(Unknown)',
            'Paper_Title': title if title else '(Unknown)',
            'Affiliation': affiliation if affiliation else '(Unknown)',
            'URL_or_DOI': url if url else '(None)',
            'Captured_Time': time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    df_new = pd.DataFrame(new_data)
    
    if os.path.exists(SAVE_FILE):
        df_old = pd.read_csv(SAVE_FILE)
        df_final = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_final = df_new
    
    column_order = ['Email', 'Type', 'All_Authors',
                    'Paper_Title', 'Affiliation', 'URL_or_DOI', 'Captured_Time']
    df_final = df_final[column_order]
    
    df_final.to_csv(SAVE_FILE, index=False, encoding='utf-8-sig')



def main():
    print(f"Journal Email OCR Extractor | Output: {SAVE_FILE}")
    print("Press F9 to capture, ESC to exit\n")
    
    keyboard.add_hotkey('F9', extract_emails_from_screen)
    keyboard.wait('esc')

if __name__ == "__main__":
    main()