Welcome to Ubuntu 22.04.5 LTS (GNU/Linux 5.15.0-173-generic x86_64)
 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro
 System information as of Tue Mar 31 05:25:25 UTC 2026
  System load:  0.0                Processes:               292
  Usage of /:   6.0% of 484.40GB   Users logged in:         2
  Memory usage: 3%                 IPv4 address for enp1s0: 103.25.175.203  Swap usage:   0%
  => There are 4 zombie processes.
 * Strictly confined Kubernetes makes edge and IoT secure. Learn how MicroK8s
   just raised the bar for easy, resilient and secure K8s cluster deployment.
   https://ubuntu.com/engage/secure-kubernetes-at-the-edge
Expanded Security Maintenance for Applications is not enabled.
0 updates can be applied immediately.
24 additional security updates can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm
New release '24.04.4 LTS' available.
Run 'do-release-upgrade' to upgrade to it.
Last login: Tue Mar 31 05:15:25 2026 from 157.48.234.244
ubuntu@dev:~$ curl -X POST https://toxic-api-back.vercel.app/api/result \
     -H "Content-Type: application/json" \
     -d '{"roll_no": "3295691"}'
{"error":"Result nahi mila. Thodi der baad try karein ya roll number check karein."}
ubuntu@dev:~$ curl -v -X POST "https://liveresults.jagranjosh.com/Result2026/jsp/rj/RJ_ART12.jsp" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "roll_no=3295691&B1=Submit"
Note: Unnecessary use of -X or --request, POST is already inferred.
*   Trying 35.244.152.223:443...
* Connected to liveresults.jagranjosh.com (35.244.152.223) port 443 (#0)
* ALPN, offering h2
* ALPN, offering http/1.1
*  CAfile: /etc/ssl/certs/ca-certificates.crt
*  CApath: /etc/ssl/certs
* TLSv1.0 (OUT), TLS header, Certificate Status (22):
* TLSv1.3 (OUT), TLS handshake, Client hello (1):
* TLSv1.2 (IN), TLS header, Certificate Status (22):
* TLSv1.3 (IN), TLS handshake, Server hello (2):
* TLSv1.2 (IN), TLS header, Finished (20):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.3 (IN), TLS handshake, Encrypted Extensions (8):
* TLSv1.3 (IN), TLS handshake, Certificate (11):
* TLSv1.3 (IN), TLS handshake, CERT verify (15):
* TLSv1.3 (IN), TLS handshake, Finished (20):
* TLSv1.2 (OUT), TLS header, Finished (20):
* TLSv1.3 (OUT), TLS change cipher, Change cipher spec (1):
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
* TLSv1.3 (OUT), TLS handshake, Finished (20):
* SSL connection using TLSv1.3 / TLS_AES_256_GCM_SHA384
* ALPN, server accepted to use h2
* Server certificate:
*  subject: CN=liveresults.jagranjosh.com
*  start date: Mar  3 17:53:53 2026 GMT
*  expire date: Jun  1 18:48:07 2026 GMT
*  subjectAltName: host "liveresults.jagranjosh.com" matched cert's "liveresults.jagranjosh.com"
*  issuer: C=US; O=Google Trust Services; CN=WR3
*  SSL certificate verify ok.
* Using HTTP2, server supports multiplexing
* Connection state changed (HTTP/2 confirmed)
* Copying HTTP/2 data in stream buffer to connection buffer after upgrade: len=0
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
* Using Stream ID: 1 (easy handle 0x55e0f2bcb9f0)
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
> POST /Result2026/jsp/rj/RJ_ART12.jsp HTTP/2
> Host: liveresults.jagranjosh.com
> user-agent: curl/7.81.0
> accept: */*
> content-type: application/x-www-form-urlencoded
> content-length: 25
>
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
* We are completely uploaded and fine
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* TLSv1.3 (IN), TLS handshake, Newsession Ticket (4):
* old SSL session ID is stale, removing
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.2 (OUT), TLS header, Supplemental data (23):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
* TLSv1.2 (IN), TLS header, Supplemental data (23):
< HTTP/2 200
< set-cookie: JSESSIONID=JSESSIONID_Tomcat4~9C733D243420F3CF426F5AD17021D197; Path=/Result2026; HttpOnly
< content-type: text/html;charset=UTF-8
< date: Tue, 31 Mar 2026 05:32:25 GMT
< cache-control: no-cache, max-age=600000
< via: 1.1 google
< alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000
<
* TLSv1.2 (IN), TLS header, Supplemental data (23):
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Jagran Josh Results</title>
<link rel="stylesheet"
        href="/Result2026/style/style.css?v=30032026" />
<script src="/Result2026/js/jquery.min.js"></script>
<script type="text/javascript"
        src="/Result2026/js/Validation.js"></script>
<script type="text/javascript"
        src="/Result2026/js/popupAds.js?v1"></script>
<!-- Result Header for class 12th - Narendra - 01-Mar-2024   -->
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-N62LNQ');</script>
<!-- End Google Tag Manager -->
<!-- *************************** Google Ads Code *************************** -->
<script>
        var googletag = googletag || {};
        googletag.cmd = googletag.cmd || [];
</script>
<script>
        googletag.cmd.push(function() {
                googletag.defineSlot(
                                '/13276288/josh/lite/JSP-results-12th/detail/ATF_300x250',
                                [ 300, 250 ], 'div-gpt-ad-1525091425361-0').addService(
                                googletag.pubads());
                googletag.defineSlot(
* TLSv1.2 (IN), TLS header, Supplemental data (23):
                                '/13276288/josh/lite/JSP-results-12th/detail/BTF_300x250',
                                [ 300, 250 ], 'div-gpt-ad-1525091425361-1').addService(
                                googletag.pubads());
                googletag.pubads().collapseEmptyDivs();
                googletag.enableServices();
        });
</script>
<script>
        var gtmCd = {};
        gtmCd.event = 'pageview';
        gtmCd.category = "results",
        gtmCd.page_type= "JSP Detail",
        gtmCd.series= "Results",
        gtmCd.sections= "Result 12"
        dataLayer.push(gtmCd);
</script>
<meta name="viewport"
        content="width=device-width,minimum-scale=1,initial-scale=1">
<body>
        <div class="ads">
                <!-- /1025214/Josh_ROS_Results_Detail_ATF_300x250_M -->
                <div id='div-gpt-ad-1525091425361-0'>
                        <script>
                                googletag.cmd.push(function() {
                                        googletag.display('div-gpt-ad-1525091425361-0');
                                });
                        </script>
                </div>
        </div>
</body>
<!-- taboola integration -->
<script type=""text/javascript"">
  window._taboola = window._taboola || [];
  _taboola.push({category:'auto'});
  !function (e, f, u, i) {
    if (!document.getElementById(i)){
      e.async = 1;
      e.src = u;
      e.id = i;
      f.parentNode.insertBefore(e, f);
    }
  }(document.createElement('script'),
  document.getElementsByTagName('script')[0],
  '//cdn.taboola.com/libtrc/jagrannewmedia-jagranjosh/loader.js',
  'tb_loader_script');
  if(window.performance && typeof window.performance.mark == 'function')
* TLSv1.2 (IN), TLS header, Supplemental data (23):
    {window.performance.mark('tbl_ic');}
</script>
</head>
<!-- Global Variable is Declared Start Narendra 01-Mar-2024 -->
<!--  Global Variable End -->
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N62LNQ"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
        <!-- Script Area Start Added By Narendra - 31-May-14 -->
        <script type="text/javascript">
                function downloadPdf() {
                        dataLayer.push({
                                'event': 'result_events',
                                'eventCategory': '12th Result',
                                'eventAction': 'Download PDF',
                                'eventLabel': 'Rajasthan Board'
                                });
                                        openLeadForm();
                }
                function leadFormEvent(actionText) {
                        dataLayer.push({
                                'event' : 'result_events',
                                'eventCategory' : '12th Result',
                                'eventAction' : actionText,
                                'eventLabel' : 'Rajasthan Board'
                        });
                        if(actionText=='Submit PDF')
                                window.open('https://mocktest.jagranjosh.com/ecatalog/2514/cuet-ug', '_blank');
                }
        </script>
* TLSv1.2 (IN), TLS header, Supplemental data (23):
        <!--    Script Aera End -->
        <form action="RJPdf.jsp" id="downloadPdfForm">
                <input type="hidden" name="rollNo" value="null"> <input
                        type="hidden" name="fileName" value="RajasthanClass12ArtsResult.pdf">
                <input type="hidden" name="tableName" value="RJ_ART_RESULT_2026_12">
                <input type="hidden" name="poolName" value="jdbc/Mysql3">
        </form>
        <div>
                        <!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Jagran Josh Results</title>
<link rel="stylesheet" href="/Result2026/style/style.css?v=30032026" />
<script src="/Result2026/js/jquery.min.js"></script>
<script type="text/javascript" src="/Result2026/js/Validation.js?v=052025"></script>
<script type="text/javascript" src="/Result2026/js/popupAds.js?v=1"></script>
<!-- *************************** Page View Tracker *************************** -->
<meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
        <!-- Google Tag Manager -->
        <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer','GTM-N62LNQ');</script>
        <!-- End Google Tag Manager -->
* TLSv1.2 (IN), TLS header, Supplemental data (23):
<script type='text/javascript'>
        var googletag = googletag || {};
        googletag.cmd = googletag.cmd || [];
        (function() {
                var gads = document.createElement('script');
                gads.async = true;
                gads.type = 'text/javascript';
                var useSSL = 'https:' == document.location.protocol;
                gads.src = (useSSL ? 'https:' : 'http:')
                                + '//www.googletagservices.com/tag/js/gpt.js';
                var node = document.getElementsByTagName('script')[0];
                node.parentNode.insertBefore(gads, node);
        })();
</script>
<script type="text/javascript">
        var _comscore = _comscore || [];
        _comscore.push({
                c1 : "2",
                c2 : "13184768"
        });
        (function() {
                var s = document.createElement("script"), el = document
                                .getElementsByTagName("script")[0];
                s.async = true
                true;
                s.src = (document.location.protocol == "https:" ? "https://sb"
                                : "http://b")
                                + ".scorecardresearch.com/beacon.js";
                el.parentNode.insertBefore(s, el);
        })();
        $(document).ready(function() {
                //For com Score
                $.ajax({
                        type : "POST",
                        url : "/Result2026/resource/pv.xml",
                        data : {
                                c1 : 2,
                                c2 : 1318476
                        }
                }).done(function(res) {
                        console.log(res);
                });
        });
        self.COMSCORE && COMSCORE.beacon({
                c1 : "2",
                c2 : "13184768"
        });
</script>
<noscript>
        <img
                src="http://b.scorecardresearch.com/p?c1=2&c2=13184768&cv=2.0&cj=1" />
</noscript>
<script>
* TLSv1.2 (IN), TLS header, Supplemental data (23):
                $("document").ready(
                                function() {
                                        $(".result-sumbit").click(
                                                        function() {
                                                                if (rollNoValidation()) {
                                                                        dataLayer.push({
                                                                         'event': 'result_events',
                                                                         'eventCategory': '12th Result',
                                                                         'eventAction': 'Show Result',
                                                                         'eventLabel': 'Rajasthan Board'
                                                                         });
                                                                        return true;
                                                                } else {
                                                                        return false;
                                                                }
                                                        });
                                });
        </script>
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N62LNQ"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
        <div class="result-roll-form">
                <p class="title">Result Declared</p>
                <div class="g_head">
                        Rajasthan Board Class 12th (Arts) Exam-2026
                        Result
                </div>
                <div class="inpt_sect">
                        <form method="post" action="RJ_ART12.jsp" target="_blank">
                                <div class="rollnobox">
                                        <input type="text" class="input_inner" name="rollNo" id="rollNo"
                                                value="Roll No" onBlur="if(value=='') value = 'Roll No'"
                                                onFocus="if(value=='Roll No') value = ''" />
                                        <div class="err" id="rollNoError"></div>
                                </div>
                                <p align="center" class="rolsubmit">
                                        <input type="submit" value="Submit" id="submit"
                                                class="result-sumbit" />
                                </p>
                                <p class="clear"></p>
* TLSv1.2 (IN), TLS header, Supplemental data (23):
                        </form>
                </div>
        </div>
</body>
</html>
                <!--    Result Area End -->
                <div
                        class="note">
                        <b>Note : </b> JagranJosh.com is not responsible for any
                        inadvertent error that may have crept in the results being published
                        on this website. The results published on net are
for immediate
                        information to the examinees. These cannot be treated as original
                        mark sheets. Original mark sheets have been issued by the Board
                        separately. Copy of the Marks Sheet can be obtained from Vidhyarthi
                        Seva Kendra of your District
                </div>
                <!-- Result Footer Narendra - 01-Mar-2024   -->
                <!-- Result Footer for class 12th -  Narendra - 01-Mar-2024    -->
<!-- *************************** Page View Tracker *************************** -->
<script type='text/javascript'>
        var googletag = googletag || {};
        googletag.cmd = googletag.cmd || [];
        (function() {
                var gads = document.createElement('script');
                gads.async = true;
                gads.type = 'text/javascript';
                var useSSL = 'https:' == document.location.protocol;
                gads.src = (useSSL ? 'https:' : 'http:')
                                + '//www.googletagservices.com/tag/js/gpt.js';
                var node = document.getElementsByTagName('script')[0];
                node.parentNode.insertBefore(gads, node);
        })();
</script>
<script type="text/javascript">
        var _comscore = _comscore || [];
        _comscore.push({
                c1 : "2",
* TLSv1.2 (IN), TLS header, Supplemental data (23):
                c2 : "13184768"
        });
        (function() {
                var s = document.createElement("script"), el = document
                                .getElementsByTagName("script")[0];
                s.async = true
                true;
                s.src = (document.location.protocol == "https:" ? "https://sb"
                                : "http://b")
                                + ".scorecardresearch.com/beacon.js";
                el.parentNode.insertBefore(s, el);
        })();
        $(document).ready(function() {
                //For com Score
                $.ajax({
                        type : "POST",
                        url : "/Result2026/resource/pv.xml",
                        data : {
                                c1 : 2,
                                c2 : 1318476
                        }
                }).done(function(res) {
                        console.log(res);
                });
        });
        self.COMSCORE && COMSCORE.beacon({
                c1 : "2",
                c2 : "13184768"
        });
</script>
<noscript>
        <img src="http://b.scorecardresearch.com/p?c1=2&c2=13184768&cv=2.0&cj=1" />
</noscript>
<!-- *************************** Google Ads Code *************************** -->
<script src="https://www.googletagservices.com/tag/js/gpt.js" async="async"></script>
<script>
        var googletag = googletag || {};
        googletag.cmd = googletag.cmd || [];
</script>
<script>
        googletag.cmd.push(function() {
                googletag.defineSlot('/1025214/Josh_ROS_Results_Submission_1x1_M',
                                [ 1, 1 ], 'div-gpt-ad-1484313354312-6').addService(
                                googletag.pubads());
                googletag.pubads().set("page_url", "http://www.jagranjosh.com/");
                googletag.pubads().collapseEmptyDivs();
* TLSv1.2 (IN), TLS header, Supplemental data (23):
                //googletag.pubads().setTargeting('category', []);
                googletag.enableServices();
        });
</script>
<!-- *************************** Footer Content *************************** -->
<div style="width: 100%; float: left;">
        <div class="disclaimerN">
                <b>Disclaimer : </b>We are not responsible for any inadvertent error
                that may have crept in the results being published on NET. The results
                published on net are for immediate information to the examinees. These
                cannot be treated as original mark sheets. Original mark sheets have
                been issued by the Board separately.
        </div>
</div>
<br>
<div class="ads">
        <!-- /1025214/Josh_ROS_Results_Detail_BTF_300x250_M -->
        <div id='div-gpt-ad-1525091425361-1'>
                <script>
                        googletag.cmd.push(function() {
                                googletag.display('div-gpt-ad-1525091425361-1');
                        });
                </script>
        </div>
</div>
<div class="ads-ctn">
<!-- OutBrain -->
<div class="OUTBRAIN" data-src="DROP_PERMALINK_HERE" data-widget-id="MB_1"></div> <script type="text/javascript" async="async" src="//widgets.outbrain.com/outbrain.js"></script>
<script>$(function() {if($('.OUTBRAIN').length) {$('.OUTBRAIN').attr('data-src', window.location.href);}});</script>
</div>
<!-- <div class="sticky-ad">
<script src='https://www.googletagservices.com/tag/js/gpt.js'>
* TLSv1.2 (IN), TLS header, Supplemental data (23):
  googletag.pubads().definePassback('/21751243814/JagranJosh_12th_Mobile_320x50_STMA', [[320, 50], [728, 90], 'fluid']).set("page_url","jagranjosh.com").display();
</script>
</div> -->
<!-- taboola integration -->
<script type="text/javascript">
  window._taboola = window._taboola || [];
  _taboola.push({flush: true});
</script>
<div style="max-width:800px; margin:20px auto; padding:20px">
                <div id="taboola-below-article-thumbnails"></div>
                <script type="text/javascript">
                  window._taboola = window._taboola || [];
                  _taboola.push({
                    mode: 'thumbnails-a',
                    container: 'taboola-below-article-thumbnails',
                    placement: 'Below Article Thumbnails Results',
                    target_type: 'mix'
                  });
                </script>
                <div id="taboola-nextup-thumbnails"></div>
                <script type="text/javascript">
                window._taboola = window._taboola || [];
                _taboola.push({
                mode: 'blend-next-up-a',
                container: 'taboola-nextup-thumbnails',
                placement: 'Nextup Thumbnails',
                target_type: 'mix'
                });
                </script>
</div>
        <style>
* TLSv1.2 (IN), TLS header, Supplemental data (23):
                .sticky-ad{ position: fixed; bottom: 0; z-index: 5; text-align: center;width:100%;}
        </style>
        </div>
</body>
</html>
* Connection #0 to host liveresults.jagranjosh.com left intact
ubuntu@dev:~$
