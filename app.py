from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings()

app = Flask(__name__)
CORS(app)

HEADERS_MOBILE = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 16; RMX5120 Build/UKQ1.231108.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/146.0.7680.120 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'hi-IN,hi;q=0.9,en-IN;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded',
}

HEADERS_DESKTOP = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded',
}

def clean(text):
    return re.sub(r'[\s\u00a0\t]+', ' ', text or '').strip()

def is_valid_html(html):
    if not html or len(html) < 300:
        return False
    bad = ["no records found", "invalid roll", "not found", "no record",
           "record not found", "wrong roll", "please enter", "enter roll"]
    lower = html.lower()
    return not any(b in lower for b in bad)

def parse_result(html, roll_no, stream):
    if not is_valid_html(html):
        return None
    soup = BeautifulSoup(html, 'html.parser')
    full_text = clean(soup.get_text(' '))
    if not re.search(r'(candidate|examinee|student|name)', full_text, re.I):
        return None

    data = {"ROLL_NO": str(roll_no), "YEAR": "2026", "GROUP": stream.upper()}

    tds = soup.find_all('td')
    key_map = {
        "CAN_NAME":  ["candidate name", "examinee name", "student name", "name of candidate"],
        "FNAME":     ["father name", "father's name", "fathers name"],
        "MNAME":     ["mother name", "mother's name"],
        "CENT_NAME": ["school", "center name", "centre name", "college"],
    }
    for i, td in enumerate(tds):
        label = clean(td.get_text()).lower()
        for key, patterns in key_map.items():
            if key in data:
                continue
            if any(p == label or label.startswith(p) for p in patterns):
                nxt = tds[i+1] if i+1 < len(tds) else None
                if nxt:
                    val = clean(nxt.get_text())
                    if val and len(val) > 1:
                        data[key] = val

    if not data.get("CAN_NAME"):
        m = re.search(r'(?:Candidate|Student|Examinee)\s*Name\s*[:\-]?\s*([A-Z][A-Z\s\.]{2,40})', full_text, re.I)
        if m:
            data["CAN_NAME"] = m.group(1).strip()

    if not data.get("CAN_NAME"):
        return None

    skip_labels = {"sub", "subject", "sr", "s.no", "sno", "theory", "practical",
                   "internal", "total", "grand total", "marks", "obtained"}
    idx = 1
    for row in soup.find_all('tr'):
        cols = row.find_all(['td', 'th'])
        if len(cols) < 2:
            continue
        subj = clean(cols[0].get_text())
        marks = clean(cols[1].get_text())
        if (subj.lower() not in skip_labels and len(subj) > 3 and
                re.match(r'^\d{1,3}$|^AB$|^[AE]$', marks)):
            data[f"SC{idx}"] = subj
            data[f"SC{idx}P1"] = marks
            data[f"TOT{idx}"] = clean(cols[-1].get_text())
            idx += 1
            if idx > 10:
                break

    m = re.search(
        r'\b(FIRST|SECOND|THIRD|PASS|FAIL|COMPARTMENT|SUPPLEMENTARY|SUPP|1ST|2ND|3RD|DISTINCTION|ATKT)\b',
        full_text, re.I)
    if m:
        data["RESULT"] = m.group(1).upper()

    m = re.search(r'(?:grand\s*total|total\s*marks?|aggregate)\s*[:\-]?\s*(\d{3,4})', full_text, re.I)
    if m:
        data["TOTAL"] = m.group(1)

    m = re.search(r'(\d{1,3}\.\d{1,2})\s*%', full_text)
    if m:
        data["PERCENT"] = m.group(1)

    return data


def try_post(url, stream, roll_no, hdrs, extra_headers=None, verify=True, get_first=False):
    """
    rollNo is CONFIRMED field name from Jagran Josh HTML source:
      <input type="text" name="rollNo" ...>
    get_first=True does a GET before POST to acquire JSESSIONID (Tomcat requirement).
    """
    payload_keys = ["rollNo", "rollno", "RollNo", "roll_no", "txtrollno", "roll", "txtRollNo"]
    h = {**hdrs}
    if extra_headers:
        h.update(extra_headers)

    for key in payload_keys:
        try:
            s = requests.Session()
            if get_first:
                s.get(url, headers=h, timeout=8, verify=verify)
            r = s.post(url, data={key: str(roll_no)},
                       headers=h, timeout=12, verify=verify)
            if r.status_code == 200 and len(r.text) > 800:
                result = parse_result(r.text, roll_no, stream)
                if result:
                    return result
        except:
            continue
    return None


def src_jagranjosh(roll_no):
    """
    GET first -> JSESSIONID cookie -> POST rollNo=<roll>
    Confirmed from curl: <input name="rollNo"> in form HTML
    """
    endpoints = [
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_ART12.jsp", "ARTS"),
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_SC12.jsp",  "SCIENCE"),
        ("https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_CO12.jsp",  "COMMERCE"),
    ]
    for url, stream in endpoints:
        extra = {'Referer': url, 'Origin': 'https://liveresults.jagranjosh.com'}
        r = try_post(url, stream, roll_no, HEADERS_MOBILE, extra, get_first=True)
        if r:
            r["SOURCE"] = f"jagranjosh_{stream.lower()}"
            return r
    return None


def src_rajresults(roll_no):
    endpoints = [
        ("https://rajresults.nic.in/strictmrollno12art.htm", "ARTS"),
        ("https://rajresults.nic.in/strictmrollno12sci.htm", "SCIENCE"),
        ("https://rajresults.nic.in/strictmrollno12com.htm", "COMMERCE"),
        ("https://rajresults.nic.in/RJ12ART26.htm",  "ARTS"),
        ("https://rajresults.nic.in/RJ12SCI26.htm",  "SCIENCE"),
        ("https://rajresults.nic.in/RJ12COM26.htm",  "COMMERCE"),
    ]
    for url, stream in endpoints:
        extra = {'Referer': url, 'Origin': 'https://rajresults.nic.in'}
        r = try_post(url, stream, roll_no, HEADERS_DESKTOP, extra, verify=False)
        if r:
            r["SOURCE"] = f"rajresults_{stream.lower()}"
            return r
    return None


def src_indiaresults(roll_no):
    endpoints = [
        ("https://rj-12-arts-result.indiaresults.com/rj/bser/class-12-arts-result-2026/mrollresult.asp",       "ARTS"),
        ("https://rj-12-science-result.indiaresults.com/rj/bser/class-12-science-result-2026/mrollresult.asp", "SCIENCE"),
        ("https://rj-12-commerce-result.indiaresults.com/rj/bser/class-12-commerce-result-2026/mrollresult.asp","COMMERCE"),
    ]
    for url, stream in endpoints:
        base   = url.rsplit('/', 1)[0]
        origin = "https://" + url.split('/')[2]
        extra  = {'Referer': base + '/query.htm', 'Origin': origin}
        r = try_post(url, stream, roll_no, HEADERS_MOBILE, extra, verify=False)
        if r:
            r["SOURCE"] = f"indiaresults_{stream.lower()}"
            return r
    return None


def src_rajeduboard(roll_no):
    endpoints = [
        ("https://rajeduboard.rajasthan.gov.in/RESULT2026/ARTS/mrollresult.asp",     "ARTS"),
        ("https://rajeduboard.rajasthan.gov.in/RESULT2026/SCIENCE/mrollresult.asp",  "SCIENCE"),
        ("https://rajeduboard.rajasthan.gov.in/RESULT2026/COMMERCE/mrollresult.asp", "COMMERCE"),
        ("https://rajeduboard.rajasthan.gov.in/result12art26.aspx",  "ARTS"),
        ("https://rajeduboard.rajasthan.gov.in/result12sci26.aspx",  "SCIENCE"),
        ("https://rajeduboard.rajasthan.gov.in/result12com26.aspx",  "COMMERCE"),
    ]
    extra = {'Referer': 'https://rajeduboard.rajasthan.gov.in/',
             'Origin':  'https://rajeduboard.rajasthan.gov.in'}
    for url, stream in endpoints:
        r = try_post(url, stream, roll_no, HEADERS_DESKTOP, extra, verify=False)
        if r:
            r["SOURCE"] = f"rajeduboard_{stream.lower()}"
            return r
    return None


def fetch_result_parallel(roll_no):
    sources = [src_jagranjosh, src_rajresults, src_indiaresults, src_rajeduboard]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(fn, roll_no): fn.__name__ for fn in sources}
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    return result
            except:
                continue
    return None


@app.route('/api/result', methods=['POST'])
def fetch_result():
    body = request.get_json(force=True, silent=True) or {}
    roll_no = str(body.get('roll_no', '')).strip()

    if not roll_no or not roll_no.isdigit():
        return jsonify({"error": "Valid Roll Number required"}), 400

    if roll_no == "1234567":
        return jsonify({
            "ROLL_NO": "1234567", "CAN_NAME": "DEMO STUDENT",
            "FNAME": "DEMO FATHER", "GROUP": "ARTS", "RESULT": "FIRST",
            "SC1": "HINDI", "SC1P1": "85", "TOT1": "85", "SOURCE": "demo"
        })

    result = fetch_result_parallel(roll_no)
    if result:
        return jsonify(result)

    return jsonify({
        "error": "Result nahi mila. Official servers busy hain — 2-3 min baad try karein."
    }), 404


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
