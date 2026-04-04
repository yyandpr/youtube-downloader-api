#!/usr/bin/env python3
"""Test if YouTube cookies work correctly."""
import os
import sys

# Set the cookie before importing config
COOKIES_JSON = '''[
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192686,
    "hostOnly": false,
    "httpOnly": false,
    "name": "__Secure-1PAPISID",
    "path": "/",
    "sameSite": "unspecified",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "dhFW5aD8z65x-LFQ/AwvTS5BWM8Qu6EvPF",
    "id": 1
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192352,
    "hostOnly": false,
    "httpOnly": true,
    "name": "__Secure-1PSID",
    "path": "/",
    "sameSite": "unspecified",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "g.a0008gjUeBJwwJW3-VbfMA_LRENDALnvtHbA1hYoNpiotboEXYo9-V6l2c8VM-9NWhtzcoAdhwACgYKAasSARUSFQHGX2Mink9kYdWGJbUTxOieb6a1FhoVAUF8yKqOEaI3r_KrF0K-SO4br9Lo0076",
    "id": 2
},
{
    "domain": ".youtube.com",
    "expirationDate": 1806835436.850527,
    "hostOnly": false,
    "httpOnly": true,
    "name": "__Secure-1PSIDCC",
    "path": "/",
    "sameSite": "unspecified",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "AKEyXzUrRvNPDEH_7RQT3KhtTWwxfn_IdKGvemB4SwGpT4rDXdmEUtocmshPiwWuPKmdK020Lg",
    "id": 3
},
{
    "domain": ".youtube.com",
    "expirationDate": 1806683166.145688,
    "hostOnly": false,
    "httpOnly": true,
    "name": "__Secure-1PSIDTS",
    "path": "/",
    "sameSite": "unspecified",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "sidts-CjUBWhotCSCxeRWtM6oGCctM9bCA2Sa5_XfvgxidjzNd64GWMO7MocJY2QXxsZy10cm29PU0bxAA",
    "id": 4
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192789,
    "hostOnly": false,
    "httpOnly": false,
    "name": "__Secure-3PAPISID",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "dhFW5aD8z65x-LFQ/AwvTS5BWM8Qu6EvPF",
    "id": 5
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192408,
    "hostOnly": false,
    "httpOnly": true,
    "name": "__Secure-3PSID",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "g.a0008gjUeBJwwJW3-VbfMA_LRENDALnvtHbA1hYoNpiotboEXYo9-ZdqPYM_9t62HpGDXJ9c1QACgYKAbsSARUSFQHGX2MiFLbhyhCsUDtk1IkvNlgoYhoVAUF8yKoUNfxqzZv0hmYclfxbElHK0076",
    "id": 6
},
{
    "domain": ".youtube.com",
    "expirationDate": 1806835436.850577,
    "hostOnly": false,
    "httpOnly": true,
    "name": "__Secure-3PSIDCC",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "AKEyXzW47-f_aDRensNfQaRTPO3Qx1hIO6fnWNIP8f45dExZR9ck5wEjC9uUJIlqpH8hTk9t8g",
    "id": 7
},
{
    "domain": ".youtube.com",
    "expirationDate": 1806683166.145737,
    "hostOnly": false,
    "httpOnly": true,
    "name": "__Secure-3PSIDTS",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "sidts-CjUBWhotCSCxeRWtM6oGCctM9bCA2Sa5_XfvgxidjzNd64GWMO7MocJY2QXxsZy10cm29PU0bxAA",
    "id": 8
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809180764.564444,
    "hostOnly": false,
    "httpOnly": true,
    "name": "__Secure-YENID",
    "path": "/",
    "sameSite": "lax",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "14.YTE=bQ2Keiw6SeRh-G58yKeAQUNykb2nBpPe46UTSOPNABCkHoerD9ic1tS2j9wcOZEElbzlnj580ilAaeMmC8Egj_731C-ZfjY3Gem1aI0eoDLggZC-BMJYFzABLpU5D00zdFtyc-A0uE_C3Qhd59-QmnKJjJ46RXpbKdLmH9tzIX8q7iol7RHbzOfNWVzJyfrHGm5f4Yk8WUqOt_bmnZ5gEweSMw1LDPDpcV-fTqEJnDZXRfiEHGbLrJkWY3WIEvqwpZuqW7CWyvHqquJlP6LNvLH1zWSix29A1fEvZ8sRgONuLWmDu46lA71A5VqUmQ2ebCQIc5QsX8aOb6lMBjbfQg",
    "id": 9
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192575,
    "hostOnly": false,
    "httpOnly": false,
    "name": "APISID",
    "path": "/",
    "sameSite": "unspecified",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "TZI0RvFmcosHmaMm/A61kUxKgAR64JQQky",
    "id": 10
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192464,
    "hostOnly": false,
    "httpOnly": true,
    "name": "HSID",
    "path": "/",
    "sameSite": "unspecified",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "AML-VWUv-6jbtF8EM",
    "id": 11
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809803012.965126,
    "hostOnly": false,
    "httpOnly": true,
    "name": "LOGIN_INFO",
    "path": "/",
    "sameSite": "no_restriction",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "AFmmF2swRQIhALTLwIfD0N4_fuWcKGHP5ypkFOXteA7JwIuRr7zCSVZmAiB0PQDHdjPfEc891sCRO8FVXClvC3eEV5M7cjCc398CXA:QUQ3MjNmeXdCdmwyRzNsUU94UGJLVWpFZWg1eWdlZGtSaVBMRENpWmcwZW5LVmF4SlZ4dFJNeFFBTjF1YmVOc3I4YkJCRU5mdE04UWREM3c2TF9DRmdMY0FnSUx4cDlQRDZuYmN3TEEwQUJaRWZSUHNsdlF2STZ6SHJOcVk3Zmh5bzVfaUFpVG5lQXJrN1hWOXBwdXE1aDluN1VHMEw0aVhR",
    "id": 12
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809859296.953359,
    "hostOnly": false,
    "httpOnly": false,
    "name": "PREF",
    "path": "/",
    "sameSite": "unspecified",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "tz=Asia.Shanghai&f6=40000000&f7=100&f4=10000",
    "id": 13
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192631,
    "hostOnly": false,
    "httpOnly": false,
    "name": "SAPISID",
    "path": "/",
    "sameSite": "unspecified",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "dhFW5aD8z65x-LFQ/AwvTS5BWM8Qu6EvPF",
    "id": 14
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192295,
    "hostOnly": false,
    "httpOnly": false,
    "name": "SID",
    "path": "/",
    "sameSite": "unspecified",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "g.a0008gjUeBJwwJW3-VbfMA_LRENDALnvtHbA1hYoNpiotboEXYo9b9lYtCEL_C4qisT96V16XQACgYKAZQSARUSFQHGX2MiefmIZrM-z49p5uoX8OIvSBoVAUF8yKrNhkVE4mvrembnD877y2dq0076",
    "id": 15
},
{
    "domain": ".youtube.com",
    "expirationDate": 1806835436.850415,
    "hostOnly": false,
    "httpOnly": false,
    "name": "SIDCC",
    "path": "/",
    "sameSite": "unspecified",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "AKEyXzXbCnczxxGhKYWBbC3c2upClX6OiaVyTE4uOTbCjzwM_2FQuLorNQl1L9163zz3cTZ18w",
    "id": 16
},
{
    "domain": ".youtube.com",
    "expirationDate": 1809796256.192519,
    "hostOnly": false,
    "httpOnly": true,
    "name": "SSID",
    "path": "/",
    "sameSite": "unspecified",
    "secure": true,
    "session": false,
    "storeId": "0",
    "value": "A3DuIfAOSIbMIfIEQ",
    "id": 17
},
{
    "domain": ".youtube.com",
    "expirationDate": 1775299443,
    "hostOnly": false,
    "httpOnly": false,
    "name": "ST-3opvp5",
    "path": "/",
    "sameSite": "unspecified",
    "secure": false,
    "session": false,
    "storeId": "0",
    "value": "session_logininfo=AFmmF2swRQIhALTLwIfD0N4_fuWcKGHP5ypkFOXteA7JwIuRr7zCSVZmAiB0PQDHdjPfEc891sCRO8FVXClvC3eEV5M7cjCc398CXA%3AQUQ3MjNmeXdCdmwyRzNsUU94UGJLVWpFZWg1eWdlZGtSaVBMRENpWmcwZW5LVmF4SlZ4dFJNeFFBTjF1YmVOc3I4YkJCRU5mdE04UWREM3c2TF9DRmdMY0FnSUx4cDlQRDZuYmN3TEEwQUJaRWZSUHNsdlF2STZ6SHJOcVk3Zmh5bzVfaUFpVG5lQXJrN1hWOXBwdXE1aDluN1VHMEw0aVhR",
    "id": 18
}
]'''

os.environ['YOUTUBE_COOKIES'] = COOKIES_JSON

# Now test
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import COOKIES_FILE, setup_youtube_cookies
import json

print(f"COOKIES_FILE exists: {COOKIES_FILE.exists()}")
if COOKIES_FILE.exists():
    with open(COOKIES_FILE, 'r') as f:
        content = f.read()
    print(f"Cookies file has {len(content)} chars, {len(content.splitlines())} lines")
    print("First 3 lines:")
    for line in content.splitlines()[:3]:
        print(f"  {line}")
else:
    print("Cookies file was NOT created!")
    print("Trying to parse cookies manually...")
    try:
        data = json.loads(COOKIES_JSON)
        print(f"JSON parse OK: {len(data)} cookies")
    except Exception as e:
        print(f"JSON parse ERROR: {e}")