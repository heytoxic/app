from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

session = requests.Session()
retry = Retry(total=2, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def parse_html_to_frontend_json(html_text, roll_no, stream_name, year):
    soup = BeautifulSoup(html_text, 'html.parser')
    full_text = soup.get_text(separator=" ", strip=True)
    
    def clean(text):
        return re.sub(r'[:\s\u00a0]+', ' ', text).strip() if text else ""

    data = {"ROLL_NO": str(roll_no), "YEAR": str(year), "GROUP": stream_name.upper()}

    try:
        # Flexible Name Search
        name_tags = ["Examinee Name", "Candidate Name", "Student Name", "Name"]
        for tag in name_tags:
            found = soup.find(string=re.compile(tag, re.I))
            if found:
                val = clean(found.find_next('td').get_text())
                if val and "<< Back" not in val and len(val) > 2:
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

    if not data.get("CAN_NAME") or "<< Back" in data["CAN_NAME"]:
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
    tm = re.search(r"(?:Total|Grand Total|Obtained).*?(\d+)", full_text, re.I)
    pc = re.search(r"(\d+\.\d+)\s*%", full_text)
    rs = re.search(r"(First|Second|Third|Pass|Fail|Supplementary|Distinction)", full_text, re.I)

    if tm: data["TOT_MARKS"] = tm.group(1)
    if pc: data["PER"] = pc.group(1)
    if rs: data["RESULT"] = rs.group(1)

    return data

def scrape_official_rbse(roll_no, prefix, stream_name, year):
    url = f"https://rajeduboard.rajasthan.gov.in/RESULT2026/{prefix}/Roll_Output.asp"
    payload = {'roll_no': roll_no, 'B1': 'Submit'}
    try:
        r = session.post(url, data=payload, timeout=12)
        r.encoding = r.apparent_encoding
        return parse_html_to_frontend_json(r.text, roll_no, stream_name, year)
    except: return {}

def scrape_india_results(roll_no, year):
    # Arts Fallback URL (Aapne jo diya)
    url = "https://rj-12-arts-result.indiaresults.com/rj/bser/class-12-arts-result-2026/mrollresult.asp"
    payload = {'roll': roll_no, 'btnSubmit': 'Submit'}
    try:
        r = session.post(url, data=payload, timeout=12)
        return parse_html_to_frontend_json(r.text, roll_no, "ARTS", year)
    except: return {}

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    year = str(req_data.get('year', '2026'))
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    # Demo
    if roll_no == "1234567":
        return jsonify({"ROLL_NO":"1234567","CAN_NAME":"DEMO STUDENT","FNAME":"DEMO FATHER","GROUP":"ARTS","RESULT":"FIRST DIVISION","SC1":"HINDI","SC1P1":"80","TOT1":"100","TOT_MARKS":"450","PER":"90.00"})

    # Check Official
    for pref, name in [("ARTS", "ARTS"), ("SCI", "SCIENCE"), ("COM", "COMMERCE")]:
        data = scrape_official_rbse(roll_no, pref, name, year)
        if data and data.get("CAN_NAME"): return jsonify(data)

    # Fallback to IndiaResults
    data_ir = scrape_india_results(roll_no, year)
    if data_ir and data_ir.get("CAN_NAME"): return jsonify(data_ir)

    return jsonify({"error": "Result not found or RBSE server is down."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
    
