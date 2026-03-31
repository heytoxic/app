from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

session = requests.Session()

def parse_jagran_html(html_text, roll_no, stream_name):
    # Agar data nahi hai
    if "No Records Found" in html_text or "Invalid" in html_text:
        return {}

    soup = BeautifulSoup(html_text, 'html.parser')
    
    # Check if student name exists
    name_elem = soup.find(string=re.compile("Candidate Name", re.I))
    if not name_elem:
        return {}

    def clean(text):
        return re.sub(r'[:\s\u00a0]+', ' ', text).strip() if text else ""

    data = {
        "ROLL_NO": str(roll_no),
        "YEAR": "2026",
        "GROUP": stream_name.upper(),
        "CAN_NAME": clean(name_elem.find_next('td').get_text()),
        "FNAME": clean(soup.find(string=re.compile("Father Name", re.I)).find_next('td').get_text()),
        "MNAME": clean(soup.find(string=re.compile("Mother Name", re.I)).find_next('td').get_text()),
        "CENT_NAME": clean(soup.find(string=re.compile("School/Center", re.I)).find_next('td').get_text())
    }

    # Marks Extraction
    rows = soup.find_all('tr')
    idx = 1
    for row in rows:
        cols = row.find_all('td')
        # Jagran Josh usually has subject in one row and marks in next or same.
        # This logic targets rows with numeric marks
        if len(cols) >= 2:
            subj = clean(cols[0].get_text())
            marks = clean(cols[1].get_text())
            if marks.isdigit() and len(subj) > 2:
                data[f"SC{idx}"] = subj
                data[f"SC{idx}P1"] = marks
                data[f"TOT{idx}"] = marks # Jagran simplified table
                idx += 1
    
    # Result Summary
    full_text = soup.get_text()
    res_match = re.search(r"(FIRST|SECOND|THIRD|PASS|FAIL)", full_text, re.I)
    if res_match:
        data["RESULT"] = res_match.group(1).upper()

    return data

def fetch_from_jagran(roll_no):
    # Streams check
    streams = [
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_ART12.jsp", "ARTS"),
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_SC12.jsp", "SCIENCE"),
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_CO12.jsp", "COMMERCE")
    ]
    
    # IMPORTANT: Jagran mangta hai application/x-www-form-urlencoded
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; RMX5120)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Referer': 'https://liveresults.jagranjosh.com/'
    }

    for url, s_name in streams:
        try:
            # Payload must be a DICT for form-encoded
            payload = {'roll_no': str(roll_no), 'B1': 'Submit'}
            r = session.post(url, data=payload, headers=headers, timeout=10)
            result = parse_jagran_html(r.text, roll_no, s_name)
            if result and result.get("CAN_NAME"):
                return result
        except:
            continue
    return None

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    # Demo
    if roll_no == "1234567":
        return jsonify({"ROLL_NO":"1234567","CAN_NAME":"DEMO","GROUP":"ARTS","RESULT":"PASS"})

    data = fetch_from_jagran(roll_no)
    if data:
        return jsonify(data)

    return jsonify({"error": "Result Not Found. Server busy ho sakta hai."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
    
