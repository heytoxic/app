from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# Browser jaisa Session create karein
session = requests.Session()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Origin': 'https://rajeduboard.rajasthan.gov.in',
    'Referer': 'https://rajeduboard.rajasthan.gov.in/'
}

def parse_html_to_frontend_json(html_text, roll_no, stream_name, year):
    if "No Records Found" in html_text or "Invalid" in html_text or "<< Back" in html_text:
        return {}

    soup = BeautifulSoup(html_text, 'html.parser')
    full_text = soup.get_text(separator=" ", strip=True)
    
    def clean(text):
        return re.sub(r'[:\s\u00a0]+', ' ', text).strip() if text else ""

    data = {"ROLL_NO": str(roll_no), "YEAR": str(year), "GROUP": stream_name.upper()}

    try:
        # Flexible Search for Name
        name_found = soup.find(string=re.compile("Examinee Name|Candidate Name|Name", re.I))
        if name_found:
            data["CAN_NAME"] = clean(name_found.find_next('td').get_text())
        
        f_found = soup.find(string=re.compile("Father", re.I))
        if f_found: data["FNAME"] = clean(f_found.find_next('td').get_text())
        
        m_found = soup.find(string=re.compile("Mother", re.I))
        if m_found: data["MNAME"] = clean(m_found.find_next('td').get_text())

        s_found = soup.find(string=re.compile("School|College|Centre", re.I))
        if s_found: data["CENT_NAME"] = clean(s_found.find_next('td').get_text())
    except:
        return {}

    if not data.get("CAN_NAME") or "New Page" in data["CAN_NAME"]:
        return {}

    # Marks Extraction
    rows = soup.find_all('tr')
    idx = 1
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 3:
            subj = clean(cols[0].get_text())
            marks = clean(cols[1].get_text())
            if marks.isdigit() or marks in ["A", "0", "P"]:
                data[f"SC{idx}"] = subj
                data[f"SC{idx}P1"] = marks
                data[f"SC{idx}P3"] = clean(cols[2].get_text()) if len(cols) > 2 else "0"
                data[f"TOT{idx}"] = clean(cols[-1].get_text())
                idx += 1
                if idx > 12: break

    # Summary
    tm = re.search(r"(?:Total|Obtained).*?(\d+)", full_text, re.I)
    pc = re.search(r"(\d+\.\d+)\s*%", full_text)
    rs = re.search(r"(First|Second|Third|Pass|Fail|Supplementary|Distinction)", full_text, re.I)

    if tm: data["TOT_MARKS"] = tm.group(1)
    if pc: data["PER"] = pc.group(1)
    if rs: data["RESULT"] = rs.group(1)

    return data

def scrape_official_rbse(roll_no, prefix, stream_name, year):
    # Pehle main page par jana padega session cookies lene ke liye
    main_url = "https://rajeduboard.rajasthan.gov.in/"
    url = f"https://rajeduboard.rajasthan.gov.in/RESULT2026/{prefix}/Roll_Output.asp"
    payload = {'roll_no': roll_no, 'B1': 'Submit'}
    
    try:
        session.get(main_url, headers=HEADERS, timeout=10) # Cookies refresh
        r = session.post(url, data=payload, headers=HEADERS, timeout=15)
        r.encoding = r.apparent_encoding
        return parse_html_to_frontend_json(r.text, roll_no, stream_name, year)
    except:
        return {}

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    # Demo Result
    if roll_no == "1234567":
        return jsonify({"ROLL_NO":"1234567","CAN_NAME":"DEMO STUDENT","GROUP":"ARTS","RESULT":"FIRST DIVISION","TOT_MARKS":"450","PER":"90.00"})

    # Auto-Detect Check (Arts First)
    streams = [("ARTS", "ARTS"), ("SCI", "SCIENCE"), ("COM", "COMMERCE")]
    for pref, name in streams:
        data = scrape_official_rbse(roll_no, pref, name, "2026")
        if data and data.get("CAN_NAME"):
            return jsonify(data)

    return jsonify({"error": "Result Not Found. Please check Roll Number or try after some time."}), 404

if __name__ == '__main__':
    # VPS par port 5000 par run karein
    app.run(host='0.0.0.0', port=5000, threaded=True)
    
