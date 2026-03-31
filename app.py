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
retry = Retry(total=1, backoff_factor=0.2, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def parse_html_to_frontend_json(html_text, roll_no, stream_name, year):
    soup = BeautifulSoup(html_text, 'html.parser')
    full_text = soup.get_text(separator=" ", strip=True)

    def clean(text):
        return re.sub(r'[:\s\u00a0]+', ' ', text).strip() if text else ""

    data = {
        "ROLL_NO": str(roll_no), "YEAR": str(year), "GROUP": stream_name.upper()
    }

    try:
        # Dono sites ke liye generic patterns
        name_elem = soup.find(string=re.compile("Examinee Name|Name|CANDIDATE NAME", re.I))
        data["CAN_NAME"] = clean(name_elem.find_next('td').get_text()) if name_elem else ""
        
        fname_elem = soup.find(string=re.compile("Father's Name|Father Name", re.I))
        data["FNAME"] = clean(fname_elem.find_next('td').get_text()) if fname_elem else ""
        
        mname_elem = soup.find(string=re.compile("Mother's Name|Mother Name", re.I))
        data["MNAME"] = clean(mname_elem.find_next('td').get_text()) if mname_elem else ""
        
        school_elem = soup.find(string=re.compile("School|College|CENTRE", re.I))
        data["CENT_NAME"] = clean(school_elem.find_next('td').get_text()) if school_elem else "RBSE Result 2026"
    except:
        return {}

    if not data.get("CAN_NAME"): return {}

    rows = soup.find_all('tr')
    idx = 1
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 4:
            th_val = clean(cols[1].get_text())
            if th_val.isdigit() or th_val == "A" or th_val == "0":
                data[f"SC{idx}"] = clean(cols[0].get_text())
                data[f"SC{idx}P1"] = th_val
                sessional = clean(cols[2].get_text())
                total = clean(cols[-1].get_text())
                if len(cols) == 5:
                    data[f"SC{idx}P3"] = sessional
                    data[f"SC{idx}PT"] = clean(cols[3].get_text())
                else:
                    data[f"SC{idx}P3"] = sessional
                data[f"TOT{idx}"] = total
                idx += 1
                if idx > 13: break

    tm_match = re.search(r"Total\s*marks\s*obtain\s*(\d+)", full_text, re.I)
    pc_match = re.search(r"(\d+\.\d+\s*%)", full_text)
    rs_match = re.search(r"Result\s*([\w\s]+Division|Pass|Fail|Supplementary)", full_text, re.I)

    if tm_match: data["TOT_MARKS"] = tm_match.group(1)
    if pc_match: data["PER"] = pc_match.group(1).replace("%", "").strip()
    if rs_match: data["RESULT"] = clean(rs_match.group(1).replace("Result", ""))

    return data

def scrape_official_rbse(roll_no, prefix, stream_name, year):
    url = f"https://rajeduboard.rajasthan.gov.in/RESULT2026/{prefix}/Roll_Output.asp"
    payload = {'roll_no': roll_no, 'B1': 'Submit'}
    try:
        r = session.post(url, data=payload, timeout=8)
        return parse_html_to_frontend_json(r.text, roll_no, stream_name, year)
    except: return {}

def scrape_india_results_arts(roll_no, year):
    # Aapne jo URL diya wahi use kiya hai
    url = "https://rj-12-arts-result.indiaresults.com/rj/bser/class-12-arts-result-2026/mrollresult.asp"
    payload = {'roll': roll_no, 'btnSubmit': 'Submit'}
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10)'}
    try:
        r = session.post(url, data=payload, headers=headers, timeout=8)
        return parse_html_to_frontend_json(r.text, roll_no, "ARTS", year)
    except: return {}

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    year = str(req_data.get('year', '2026'))
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    # Demo Testing
    if roll_no == "1234567":
        return jsonify({"ROLL_NO": "1234567", "YEAR": year, "GROUP": "ARTS", "CAN_NAME": "DEMO STUDENT", "FNAME": "DEMO FATHER", "RESULT": "FIRST DIVISION"})

    # Step 1: Official RBSE Scan
    for prefix, name in [("ARTS", "ARTS"), ("SCI", "SCIENCE"), ("COM", "COMMERCE")]:
        data = scrape_official_rbse(roll_no, prefix, name, year)
        if data and data.get("CAN_NAME"): return jsonify(data)

    # Step 2: IndiaResults Fallback (Sirf Arts ke liye jo aapne link diya)
    data_ir = scrape_india_results_arts(roll_no, year)
    if data_ir and data_ir.get("CAN_NAME"): return jsonify(data_ir)

    return jsonify({"error": "Result not found or server busy."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
    
