from datetime import datetime, time, timedelta
import requests as rq
import time as t
import urllib

booking_start = time(10, 15) # timme, minut
duration = timedelta(hours=2)
room_name = "s1016" # namnet som scriptet använder för att söka på mazemap. Den tar det översta resultatet så det behöver inte vara exakt

hh_username = ""  # DITT HH ANVÄNDARNAMN SÄTTER DU IN HÄR
hh_password = ""  # DITT HH LÖSENORD SÄTTER DU IN HÄR



def get_poi(name: str) -> int:
  url = "https://search.mazemap.com/search/equery/"
  headers={
    'Content-type':'application/json',
    'Accept':'application/json'
  }
  params = {
    "q": name,
    "rows": 1,
    "withpois": True
  }
  response = rq.get(url, params=params, headers=headers)
  return response.json()["result"][0]["poiId"]


def get_token(hh_username: str, hh_password: str) -> str:
  with rq.Session() as s:
    url = "https://cloud.timeedit.net/hh/web/timeedit/sso/hh_saml2?back=https%3A%2F%2Fcloud.timeedit.net%2Fhh%2Fweb%2Fstudent%2Fauth%3Fredirect_url%3Dhttps%253A%252F%252Fuse.mazemap.com%252Foauthsuccess.html%253Fstate%253D%25257B%252522mazemap_redirect_uri%252522%25253A%252522https%25253A%25252F%25252Fuse.mazemap.com%25252F%252523v%25253D1%252526campusid%25253D278%252526zlevel%25253D1%252526center%25253D12.879858%25252C56.663184%252526zoom%25253D17.7%252526sharepoitype%25253Dpoi%252526sharepoi%25253D1000043720%252526showpoidetails%25253Dtrue%252522%25252C%252522provider%252522%25253A%252522time_edit%252522%25252C%252522providers%252522%25253A%25255B%252522time_edit%252522%25255D%25257D%2526token_handling%253Dtime_edit%26app%3Dtimeedit-mazemap%26id%3D4ceaffb327ef45e7b900415b14934d2d%26timestamp%3D1727875724%26sig%3D55ecf82fda9e958a909f2d34ab45e69ee0e35359"
    response = s.get(url)

    url = "https://idp.hh.se/idp/profile/SAML2/Redirect/SSO?execution=e1s1"
    headers={
      'Content-type':'application/json,application/x-www-form-urlencoded',
      'Accept':'application/json'
    }
    params = {
      "j_username": hh_username,
      "j_password": hh_password,
      "_eventId_proceed": True
    }
    response = s.post(url, params=params, headers=headers)

    cookies = response.cookies.get_dict()
    if not ("shib_idp_session" in cookies and "shib_idp_session_ss" in cookies):
      return None

    url = "https://cloud.timeedit.net/hh/web/timeedit/ssoResponse/hh_saml2"
    start = response.text.find('lue="')+5
    end = response.text.find('"', start)
    saml_resp = response.text[start:end]
    params = { "SAMLResponse": saml_resp }
    response = s.post(url, data=params, headers=headers)

    url = s.cookies.get_dict()["sso-parameters"]
    url = url[url.find("https"):url.find("&ssoserv")]
    url = urllib.parse.unquote(url)

    response = s.get(url)
    return response.url[42:]



poi_id = get_poi(room_name)

while True:
  now = datetime.now().time()
  if now.hour > 5 or (now.hour == 5 and now.minute >= 58):
    break
  t.sleep(30)

token = get_token(hh_username, hh_password)
if token == None:
  print("Kunde inte validera HH inloggningsuppgifter")
  exit()

url = "https://booking.mazemap.com/api/roombooking/bookroom/"
headers={
  'Content-type':'application/json',
  'Accept':'application/json'
}
booking_time = datetime.combine(datetime.now().date(), booking_start) - timedelta(hours=2)
start = booking_time.isoformat()+".000Z"
end = (booking_time+duration).isoformat()+".000Z"
payload = {
  "poiid": poi_id,
  "token": token,
  "start": start,
  "end": end,
  "provider": "time_edit"
}

booking = None
while datetime.now().time().hour < 6:
  continue

response = rq.post(url, json=payload, headers=headers)
try:
  booking = response.json()
except:
  booking = {"error": response.text, "success": False}

if booking["success"]:
  print("Lyckades boka rummet")
else:
  print(f"Error: \"{booking['error']}\"")