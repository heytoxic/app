from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)
CORS(app)

# User-Agent ko bilkul real browser jaisa rakha hai
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Origin': 'https://rj-12-arts-result.indiaresults.com',
    'Referer': 'https://rj-12-arts-result.indiaresults.com/rj/bser/class-12-arts-result-2026/mrollresult.asp'
}

def parse_india_results_amp(html_text, roll_no, year):
    soup = BeautifulSoup(html_text, 'html.parser')
    data = {"ROLL_NO": str(roll_no), "YEAR": str(year), "GROUP": "ARTS"}
    
    # 1. Name, Father, Mother Search (Flexible for AMP)
    def get_val(label):
        tag = soup.find(string=re.compile(label, re.I))
        if tag:
            # AMP tables mein data aksar next td ya div mein hota hai
            parent = tag.find_parent(['td', 'tr', 'div'])
            return parent.find_next_sibling().get_text(strip=True) if parent.find_next_sibling() else ""
        return ""

    data["CAN_NAME"] = get_val("Name")
    data["FNAME"] = get_val("Father")
    data["MNAME"] = get_val("Mother")

    # Agar naam abhi bhi nahi mila, matlab page sahi load nahi hua
    if not data["CAN_NAME"] or "<< Back" in data["CAN_NAME"]:
        return {}

    # 2. Marks Extraction (AMP version uses specific table classes)
    rows = soup.find_all('tr')
    idx = 1
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:
            subj = cols[0].get_text(strip=True)
            marks = cols[1].get_text(strip=True)
            # Subject filtering
            if marks.isdigit() or marks in ["A", "0", "P"]:
                data[f"SC{idx}"] = subj
                data[f"SC{idx}P1"] = marks
                data[f"TOT{idx}"] = cols[-1].get_text(strip=True)
                idx += 1

    # 3. Summary
    full_text = soup.get_text()
    tm = re.search(r"Total Marks Obtained.*?(\d+)", full_text, re.I)
    rs = re.search(r"Result\s*:\s*([\w\s]+)", full_text, re.I)
    
    if tm: data["TOT_MARKS"] = tm.group(1)
    if rs: data["RESULT"] = rs.group(1).strip()
    
    return data

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    # Demo Result for Testing
    if roll_no == "1234567":
        return jsonify({"ROLL_NO":"1234567","CAN_NAME":"DEMO TEST OK","GROUP":"ARTS","RESULT":"PASS"})

    # IndiaResults AMP Post
    url = "https://rj-12-arts-result.indiaresults.com/rj/bser/class-12-arts-result-2026/mrollresult.asp"
    payload = {'roll': roll_no, 'btnSubmit': 'Submit'}
    
    try:
        r = requests.post(url, data=payload, headers=HEADERS, timeout=10)
        data = parse_india_results_amp(r.text, roll_no, "2026")
        
        if data and data.get("CAN_NAME"):
            return jsonify(data)
        else:
            return jsonify({"error": "Invalid Roll Number or No Data Found"}), 404
            
    except Exception as e:
        return jsonify({"error": f"Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
