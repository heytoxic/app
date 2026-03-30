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
        data["CAN_NAME"] = clean(soup.find(string=re.compile("Examinee Name")).find_next('td').get_text())
        data["FNAME"] = clean(soup.find(string=re.compile("Father's Name")).find_next('td').get_text())
        data["MNAME"] = clean(soup.find(string=re.compile("Mother's Name")).find_next('td').get_text())
        
        school_elem = soup.find(string=re.compile("School"))
        data["CENT_NAME"] = clean(school_elem.find_next('td').get_text()) if school_elem else "Rajasthan Board Result"
    except:
        return {}

    rows = soup.find_all('tr')
    idx = 1
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 4:
            th_val = clean(cols[1].get_text())
            if th_val.isdigit() or th_val == "A":
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

    tm_match = re.search(r"Total\s*marks\s*obtain\s*(\d+)", full_text, re.IGNORECASE)
    pc_match = re.search(r"(\d+\.\d+\s*%)", full_text)
    rs_match = re.search(r"Result\s*([\w\s]+Division|Pass|Fail|Supplementary)", full_text, re.IGNORECASE)

    if tm_match: data["TOT_MARKS"] = tm_match.group(1)
    if pc_match: data["PER"] = pc_match.group(1).replace("%", "").strip()
    if rs_match: data["RESULT"] = clean(rs_match.group(1).replace("Result", ""))

    return data

def scrape_official_rbse(roll_no, prefix, stream_name, year):
    url = f"https://rajeduboard.rajasthan.gov.in/RESULT2026/{prefix}/Roll_Output.asp"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
    }
    payload = {'roll_no': roll_no, 'B1': 'Submit'}
    
    try:
        response = session.post(url, data=payload, headers=headers, timeout=10)
        response.encoding = response.apparent_encoding
        return parse_html_to_frontend_json(response.text, roll_no, stream_name, year)
    except Exception:
        return {}

@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.json or {}
    roll_no = str(req_data.get('roll_no', '')).strip()
    year = str(req_data.get('year', '2026'))
    
    if not roll_no:
        return jsonify({"error": "Roll Number required"}), 400

    if roll_no == "1234567":
        return jsonify({
            "ROLL_NO": "1234567", "YEAR": year, "GROUP": "SCIENCE",
            "CAN_NAME": "DEMO STUDENT", "FNAME": "DEMO FATHER", "MNAME": "DEMO MOTHER",
            "CENT_NAME": "GOVT SR SEC SCHOOL, JAIPUR",
            "SC1": "HINDI", "SC1P1": "080", "SC1P3": "020", "TOT1": "100",
            "SC2": "ENGLISH", "SC2P1": "075", "SC2P3": "020", "TOT2": "095",
            "SC3": "PHYSICS", "SC3P1": "050", "SC3P3": "014", "SC3PT": "030", "TOT3": "094",
            "SC4": "CHEMISTRY", "SC4P1": "052", "SC4P3": "014", "SC4PT": "030", "TOT4": "096",
            "SC5": "MATHEMATICS", "SC5P1": "078", "SC5P3": "020", "TOT5": "098",
            "TOT_MARKS": "483", "PER": "96.60", "RESULT": "FIRST DIVISION"
        })

    streams_to_check = [
        ("SCI", "SCIENCE"),
        ("ARTS", "ARTS"),
        ("COM", "COMMERCE")
    ]
    
    for prefix, stream_name in streams_to_check:
        data = scrape_official_rbse(roll_no, prefix, stream_name, year)
        if data and data.get("CAN_NAME"): 
            return jsonify(data)

    return jsonify({"error": "Result not found or server is experiencing heavy traffic."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
    
