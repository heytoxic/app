from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import urllib3
urllib3.disable_warnings()

app = Flask(__name__)
CORS(app)

# Real mobile browser headers (matching what works in screenshots)
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 16; RMX5120 Build/UKQ1.231108.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/146.0.7680.120 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'hi-IN,hi;q=0.9,en-IN;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Upgrade-Insecure-Requests': '1',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}

def clean_text(text):
    return re.sub(r'[\s\u00a0]+', ' ', text).strip() if text else ""

def is_invalid_response(html):
    """Check if response indicates no result found"""
    checks = ["No Records Found", "Invalid Roll", "not found", "no record",
              "record not found", "wrong roll", "result not found"]
    lower = html.lower()
    return any(x.lower() in lower for x in checks)

def parse_result_html(html_text, roll_no, stream_name):
    if is_invalid_response(html_text):
        return None

    soup = BeautifulSoup(html_text, 'html.parser')
    full_text = soup.get_text(" ", strip=True)
    
    # Must have candidate name somewhere
    if not re.search(r'(candidate|examinee|student|name)', full_text, re.I):
        return None

    data = {"ROLL_NO": str(roll_no), "YEAR": "2026", "GROUP": stream_name.upper()}

    try:
        # --- Extract personal info from table rows ---
        all_tds = soup.find_all('td')
        
        field_map = {
            "CAN_NAME":  ["candidate name", "examinee name", "student name"],
            "FNAME":     ["father name", "father's name"],
            "MNAME":     ["mother name", "mother's name"],
            "CENT_NAME": ["school", "center", "college", "institution"],
        }

        for i, td in enumerate(all_tds):
            td_text = clean_text(td.get_text()).lower()
            for key, patterns in field_map.items():
                if key in data:
                    continue
                if any(p in td_text for p in patterns):
                    # Value is in next TD
                    if i + 1 < len(all_tds):
                        val = clean_text(all_tds[i + 1].get_text())
                        if val and len(val) > 1:
                            data[key] = val

        # Fallback: try regex on full text
        if not data.get("CAN_NAME"):
            m = re.search(r'(?:Candidate|Student|Examinee)\s+Name\s*[:\-]?\s*([A-Z][A-Z\s]+)', full_text, re.I)
            if m:
                data["CAN_NAME"] = m.group(1).strip()

        if not data.get("CAN_NAME"):
            return None

        # --- Extract marks table ---
        rows = soup.find_all('tr')
        idx = 1
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) >= 2:
                subj = clean_text(cols[0].get_text())
                marks = clean_text(cols[1].get_text())
                # Valid subject: len > 3, marks is number or special value
                if (len(subj) > 3 and subj.upper() not in ["SUB", "SUBJECT", "SR", "S.NO"] and
                        re.match(r'^\d+$|^[AEP]$|^AB$', marks)):
                    data[f"SC{idx}"] = subj
                    data[f"SC{idx}P1"] = marks
                    data[f"TOT{idx}"] = clean_text(cols[-1].get_text())
                    idx += 1

        # --- Result/Division ---
        res_match = re.search(
            r'\b(FIRST|SECOND|THIRD|PASS|FAIL|COMPARTMENT|SUPP(?:LEMENT(?:ARY)?)?|1ST|2ND|3RD|DISTINCTION)\b',
            full_text, re.I
        )
        if res_match:
            data["RESULT"] = res_match.group(1).upper()

        # --- Total marks ---
        total_match = re.search(r'(?:total|grand total|aggregate)\s*[:\-]?\s*(\d{3,4})', full_text, re.I)
        if total_match:
            data["TOTAL"] = total_match.group(1)

        return data
    except Exception as e:
        print(f"Parse error: {e}")
        return None


def try_jagran_josh(session, roll_no):
    """Try Jagran Josh - all 3 streams"""
    endpoints = [
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_ART12.jsp", "ARTS"),
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_SC12.jsp", "SCIENCE"),
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_CO12.jsp", "COMMERCE"),
    ]
    
    # Multiple payload key formats to try (different sites use different keys)
    payload_formats = [
        lambda r: {'roll_no': str(r), 'B1': 'Submit'},
        lambda r: {'rollno': str(r), 'B1': 'Submit'},
        lambda r: {'RollNo': str(r), 'B1': 'Submit'},
        lambda r: {'txtrollno': str(r), 'B1': 'Submit'},
        lambda r: {'roll': str(r), 'B1': 'Submit'},
    ]

    for url, stream in endpoints:
        for payload_fn in payload_formats:
            try:
                hdrs = {**HEADERS, 'Referer': url, 'Origin': 'https://liveresults.jagranjosh.com'}
                session.get("https://liveresults.jagranjosh.com/", headers=hdrs, timeout=6)
                payload = payload_fn(roll_no)
                r = session.post(url, data=payload, headers=hdrs, timeout=10)
                if r.status_code == 200 and len(r.text) > 500:
                    result = parse_result_html(r.text, roll_no, stream)
                    if result:
                        result["SOURCE"] = "jagranjosh"
                        return result
            except:
                continue
    return None


def try_indiaresults(session, roll_no):
    """Try IndiaResults - arts stream"""
    base = "https://rj-12-arts-result.indiaresults.com"
    referer = f"{base}/rj/bser/class-12-arts-result-2026/mquery.htm"
    post_url = f"{base}/rj/bser/class-12-arts-result-2026/mrollresult.asp"
    
    payload_formats = [
        {'roll': str(roll_no), 'B1': 'Submit'},
        {'rollno': str(roll_no), 'B1': 'Submit'},
        {'roll_no': str(roll_no), 'B1': 'Submit'},
        {'RollNo': str(roll_no), 'B1': 'Submit'},
    ]
    
    for payload in payload_formats:
        try:
            hdrs = {**HEADERS, 'Referer': referer, 'Origin': base}
            session.get(referer, headers=hdrs, timeout=6)
            r = session.post(post_url, data=payload, headers=hdrs, timeout=10, verify=False)
            if r.status_code == 200 and len(r.text) > 500:
                result = parse_result_html(r.text, roll_no, "ARTS")
                if result:
                    result["SOURCE"] = "indiaresults"
                    return result
        except:
            continue
    return None


def try_rajresults(session, roll_no):
    """Try rajresults.nic.in - official source"""
    urls = [
        ("https://rajresults.nic.in/strictmrollno12art.htm", "ARTS"),
        ("https://rajresults.nic.in/strictmrollno12sci.htm", "SCIENCE"),
        ("https://rajresults.nic.in/strictmrollno12com.htm", "COMMERCE"),
    ]
    for url, stream in urls:
        try:
            hdrs = {**HEADERS, 'Referer': url, 'Origin': 'https://rajresults.nic.in'}
            r = session.post(url, data={'rollno': str(roll_no), 'B1': 'Submit'},
                           headers=hdrs, timeout=10, verify=False)
            if r.status_code == 200 and len(r.text) > 500:
                result = parse_result_html(r.text, roll_no, stream)
                if result:
                    result["SOURCE"] = "rajresults"
                    return result
        except:
            continue
    return None


def fetch_result_logic(roll_no):
    session = requests.Session()
    session.max_redirects = 5

    # Try all sources in order
    for fn in [try_jagran_josh, try_indiaresults, try_rajresults]:
        result = fn(session, roll_no)
        if result:
            return result
    return None


@app.route('/api/result', methods=['POST'])
def fetch_result():
    req_data = request.get_json(force=True, silent=True) or {}
    roll_no = str(req_data.get('roll_no', '')).strip()

    if not roll_no or not roll_no.isdigit():
        return jsonify({"error": "Valid Roll Number required"}), 400

    # Demo result for testing
    if roll_no == "1234567":
        return jsonify({
            "ROLL_NO": "1234567", "CAN_NAME": "DEMO STUDENT",
            "FNAME": "DEMO FATHER", "GROUP": "ARTS", "RESULT": "FIRST",
            "SC1": "HINDI(COMP.)", "SC1P1": "085", "TOT1": "085"
        })

    result = fetch_result_logic(roll_no)
    if result:
        return jsonify(result)

    return jsonify({"error": "Result nahi mila. Thodi der baad try karein ya roll number check karein."}), 404


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True, debug=False)
