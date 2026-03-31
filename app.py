from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# Session settings for high-speed scraping
session = requests.Session()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer': 'https://www.jagranjosh.com/'
}

def parse_html_to_frontend_json(html_text, roll_no, stream_name):
    # Agar page par error messages hain
    if any(x in html_text for x in ["No Records Found", "Invalid", "not found", "<< Back"]):
        return {}

    soup = BeautifulSoup(html_text, 'html.parser')
    full_text = soup.get_text(separator=" ", strip=True)
    
    def clean(text):
        return re.sub(r'[:\s\u00a0]+', ' ', text).strip() if text else ""

    data = {"ROLL_NO": str(roll_no), "YEAR": "2026", "GROUP": stream_name.upper()}

    try:
        # Flexible Name Extraction
        name_tags = ["Examinee Name", "Candidate Name", "Student Name", "Name"]
        for tag in name_tags:
            found = soup.find(string=re.compile(tag, re.I))
            if found:
                val = clean(found.find_next(['td', 'span', 'div']).get_text())
                if val and len(val) > 3 and "New Page" not in val:
                    data["CAN_NAME"] = val
                    break
        
        f_found = soup.find(string=re.compile("Father", re.I))
        if f_found: data["FNAME"] = clean(f_found.find_next(['td', 'span', 'div']).get_text())
        
        m_found = soup.find(string=re.compile("Mother", re.I))
        if m_found: data["MNAME"] = clean(m_found.find_next(['td', 'span', 'div']).get_text())

        s_found = soup.find(string=re.compile("School|College|Centre", re.I))
        if s_found: data["CENT_NAME"] = clean(s_found.find_next(['td', 'span', 'div']).get_text())
    except:
        return {}

    if not data.get("CAN_NAME"): return {}

    # Marks Table Extraction
    rows = soup.find_all('tr')
    idx = 1
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 3:
            subj = clean(cols[0].get_text())
            marks = clean(cols[1].get_text())
            if (len(subj) > 2 and not subj.isdigit()) and (marks.isdigit() or marks in ["A", "0", "P"]):
                data[f"SC{idx}"] = subj
                data[f"SC{idx}P1"] = marks
                data[f"SC{idx}P3"] = clean(cols[2].get_text()) if len(cols) > 2 else "0"
                data[f"TOT{idx}"] = clean(cols[-1].get_text())
                idx += 1
                if idx > 12: break

    # Summary logic
    tm = re.search(r"(?:Total|Obtained|Grand Total).*?(\d+)", full_text, re.I)
    pc = re.search(r"(\d+\.\d+)\s*%", full_text)
    rs = re.search(r"(First|Second|Third|Pass|Fail|Supplementary|Distinction)", full_text, re.I)

    if tm: data["TOT_MARKS"] = tm.group(1)
    if pc: data["PER"] = pc.group(1)
    if rs: data["RESULT"] = rs.group(1).upper()

    return data

def scrape_jagran_josh(roll_no, stream_type):
    # Mapping for Jagran Josh URLs
    urls = {
        "ARTS": "https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_ART12.jsp",
        "SCI": "https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_SC12.jsp",
        "COM": "https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_CO12.jsp"
    }
    payload = {'roll_no': str(roll_no), 'B1': 'Submit'}
    try:
        r = session.post(urls[stream_type], data=payload, headers=HEADERS, timeout=10)
        return parse_html_to_frontend_json(r.text, roll_no, stream_type)
    except: return {}

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    # 1. Demo Result
    if roll_no == "1234567":
        return jsonify({"ROLL_NO":"1234567","CAN_NAME":"DEMO STUDENT","GROUP":"SCIENCE","RESULT":"FIRST DIVISION","TOT_MARKS":"480","PER":"96.00"})

    # 2. Main Logic: Check Jagran Josh first (All 3 Streams)
    for stream in ["ARTS", "SCI", "COM"]:
        data = scrape_jagran_josh(roll_no, stream)
        if data and data.get("CAN_NAME"):
            return jsonify(data)

    return jsonify({"error": "Result Not Found. Server busy ho sakta hai, thodi der baad try karein."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
