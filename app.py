from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# Common Headers to mimic a real mobile browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded'
}

def clean_text(text):
    return re.sub(r'[:\s\u00a0]+', ' ', text).strip() if text else ""

def parse_generic_html(html_text, roll_no, stream_name):
    if any(x in html_text for x in ["No Records Found", "Invalid", "not found", "<< Back"]):
        return None

    soup = BeautifulSoup(html_text, 'html.parser')
    data = {"ROLL_NO": str(roll_no), "YEAR": "2026", "GROUP": stream_name.upper()}

    try:
        # Flexible Data Extraction
        name_map = {
            "CAN_NAME": ["Candidate Name", "Examinee Name", "Student Name", "Name"],
            "FNAME": ["Father Name", "Father's Name"],
            "MNAME": ["Mother Name", "Mother's Name"],
            "CENT_NAME": ["School/Center", "School Name", "College"]
        }

        for key, tags in name_map.items():
            for tag in tags:
                found = soup.find(string=re.compile(tag, re.I))
                if found:
                    val = clean_text(found.find_next(['td', 'span']).get_text())
                    if val and len(val) > 2 and "New Page" not in val:
                        data[key] = val
                        break
        
        if not data.get("CAN_NAME"): return None

        # Marks Table Extraction
        rows = soup.find_all('tr')
        idx = 1
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                subj = clean_text(cols[0].get_text())
                marks = clean_text(cols[1].get_text())
                if len(subj) > 3 and (marks.isdigit() or marks in ["A", "0", "P"]):
                    data[f"SC{idx}"] = subj
                    data[f"SC{idx}P1"] = marks
                    data[f"TOT{idx}"] = clean_text(cols[-1].get_text())
                    idx += 1
        
        # Result Summary
        full_text = soup.get_text()
        res = re.search(r"(FIRST|SECOND|THIRD|PASS|FAIL|1ST|2ND|3RD|SUPP)", full_text, re.I)
        if res: data["RESULT"] = res.group(1).upper()
        
        return data
    except:
        return None

def fetch_result_logic(roll_no):
    session = requests.Session()
    
    # SOURCE 1: Jagran Josh (Fastest)
    jagran_urls = [
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_ART12.jsp", "ARTS"),
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_SC12.jsp", "SCIENCE"),
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_CO12.jsp", "COMMERCE")
    ]

    for url, s_name in jagran_urls:
        try:
            session.get("https://liveresults.jagranjosh.com/", headers=HEADERS, timeout=5)
            payload = {'roll_no': str(roll_no), 'B1': 'Submit'}
            r = session.post(url, data=payload, headers=HEADERS, timeout=8)
            res = parse_generic_html(r.text, roll_no, s_name)
            if res: return res
        except: continue

    # SOURCE 2: IndiaResults (Fallback)
    ir_url = "https://rj-12-arts-result.indiaresults.com/rj/bser/class-12-arts-result-2026/mrollresult.asp"
    try:
        r_ir = session.post(ir_url, data={'roll': str(roll_no), 'B1': 'Submit'}, headers=HEADERS, timeout=8, verify=False)
        res_ir = parse_generic_html(r_ir.text, roll_no, "ARTS")
        if res_ir: return res_ir
    except: pass

    return None

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    # Demo Result for Testing
    if roll_no == "1234567":
        return jsonify({"ROLL_NO":"1234567","CAN_NAME":"DEMO STUDENT","GROUP":"ARTS","RESULT":"FIRST"})

    result = fetch_result_logic(roll_no)
    if result:
        return jsonify(result)

    return jsonify({"error": "Result Not Found. Server busy ho sakta hai, 1 min baad try karein."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
    
