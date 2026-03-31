from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# Session settings to mimic a real mobile browser
session = requests.Session()
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://rj-12-arts-result.indiaresults.com',
    'Referer': 'https://rj-12-arts-result.indiaresults.com/rj/bser/class-12-arts-result-2026/rollquery.htm'
}

def parse_html_to_frontend_json(html_text, roll_no, stream_name, year):
    # Agar page par "No Records" ya "Invalid" likha hai toh turant return {}
    if any(x in html_text for x in ["No Records Found", "Invalid", "New Page", "<< Back"]):
        return {}

    soup = BeautifulSoup(html_text, 'html.parser')
    full_text = soup.get_text(separator=" ", strip=True)
    
    def clean(text):
        return re.sub(r'[:\s\u00a0]+', ' ', text).strip() if text else ""

    data = {"ROLL_NO": str(roll_no), "YEAR": str(year), "GROUP": stream_name.upper()}

    try:
        # Flexible Name Extraction
        name_tags = ["Examinee Name", "Candidate Name", "Student Name", "Name"]
        for tag in name_tags:
            found = soup.find(string=re.compile(tag, re.I))
            if found:
                val = clean(found.find_next('td').get_text())
                if val and len(val) > 3 and "New Page" not in val:
                    data["CAN_NAME"] = val
                    break
        
        f_found = soup.find(string=re.compile("Father", re.I))
        if f_found: data["FNAME"] = clean(f_found.find_next('td').get_text())
        
        m_found = soup.find(string=re.compile("Mother", re.I))
        if m_found: data["MNAME"] = clean(m_found.find_next('td').get_text())

        s_found = soup.find(string=re.compile("School|College|Centre", re.I))
        if s_found: data["CENT_NAME"] = clean(s_found.find_next('td').get_text())
    except:
        return {}

    if not data.get("CAN_NAME"): return {}

    # Marks Table Extraction (Robust Logic)
    rows = soup.find_all('tr')
    idx = 1
    for row in rows:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 3:
            subj = clean(cols[0].get_text())
            marks = clean(cols[1].get_text())
            # Subject names check (English, Hindi, etc.) aur marks check
            if (len(subj) > 3 and not subj.isdigit()) and (marks.isdigit() or marks in ["A", "0", "P"]):
                data[f"SC{idx}"] = subj
                data[f"SC{idx}P1"] = marks
                data[f"SC{idx}P3"] = clean(cols[2].get_text()) if len(cols) > 2 else "0"
                data[f"TOT{idx}"] = clean(cols[-1].get_text())
                idx += 1
                if idx > 12: break

    # Result Summary
    tm = re.search(r"(?:Total|Obtained|Grand Total).*?(\d+)", full_text, re.I)
    pc = re.search(r"(\d+\.\d+)\s*%", full_text)
    rs = re.search(r"(First|Second|Third|Pass|Fail|Supplementary|Distinction|1st|2nd|3rd)", full_text, re.I)

    if tm: data["TOT_MARKS"] = tm.group(1)
    if pc: data["PER"] = pc.group(1)
    if rs: data["RESULT"] = rs.group(1).upper()

    return data

def scrape_india_results(roll_no):
    # Aapne jo Arts ka URL diya tha wahi hai
    url = "https://rj-12-arts-result.indiaresults.com/rj/bser/class-12-arts-result-2026/mrollresult.asp"
    payload = {'roll': str(roll_no), 'B1': 'Submit'}
    try:
        # IndiaResults verify=False mangta hai kabhi kabhi
        r = session.post(url, data=payload, headers=HEADERS, timeout=15, verify=False)
        r.encoding = 'utf-8'
        return parse_html_to_frontend_json(r.text, roll_no, "ARTS", "2026")
    except: return {}

def scrape_official_rbse(roll_no, prefix, stream_name):
    url = f"https://rajeduboard.rajasthan.gov.in/RESULT2026/{prefix}/Roll_Output.asp"
    payload = {'roll_no': roll_no, 'B1': 'Submit'}
    try:
        r = session.post(url, data=payload, headers=HEADERS, timeout=12)
        r.encoding = r.apparent_encoding
        return parse_html_to_frontend_json(r.text, roll_no, stream_name, "2026")
    except: return {}

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    # 1. Demo
    if roll_no == "1234567":
        return jsonify({"ROLL_NO":"1234567","CAN_NAME":"DEMO STUDENT","GROUP":"ARTS","RESULT":"FIRST DIVISION","TOT_MARKS":"450","PER":"90.00"})

    # 2. Pehle IndiaResults Try Karein (Sabse Fast)
    data = scrape_india_results(roll_no)
    if data and data.get("CAN_NAME"):
        return jsonify(data)

    # 3. Fir Official RBSE Check Karein (Fallback)
    for pref, name in [("ARTS", "ARTS"), ("SCI", "SCIENCE"), ("COM", "COMMERCE")]:
        data = scrape_official_rbse(roll_no, pref, name)
        if data and data.get("CAN_NAME"): return jsonify(data)

    return jsonify({"error": "Result Not Found. Server busy ho sakta hai, thodi der baad try karein."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
    
