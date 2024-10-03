from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime, time, timedelta
import requests as rq
import time as t
import urllib


app = Flask(__name__)
CORS(app, origins=['https://ture-w.github.io'])


@app.route('/proxy/token', methods=['POST'])
def get_token():
  try:
    data = request.get_json()
    hh_username = data.get('hhUsername')
    hh_password = data.get('hhPassword')

    with rq.Session() as s:
      url = "https://cloud.timeedit.net/hh/web/timeedit/sso/hh_saml2?back=https%3A%2F%2Fcloud.timeedit.net%2Fhh%2Fweb%2Fstudent%2Fauth%3Fredirect_url%3Dhttps%253A%252F%252Fuse.mazemap.com%252Foauthsuccess.html%253Fstate%253D%25257B%252522mazemap_redirect_uri%252522%25253A%252522https%25253A%25252F%25252Fuse.mazemap.com%25252F%252523v%25253D1%252526campusid%25253D278%252526zlevel%25253D1%252526center%25253D12.879858%25252C56.663184%252526zoom%25253D17.7%252526sharepoitype%25253Dpoi%252526sharepoi%25253D1000043720%252526showpoidetails%25253Dtrue%252522%25252C%252522provider%252522%25253A%252522time_edit%252522%25252C%252522providers%252522%25253A%25255B%252522time_edit%252522%25255D%25257D%2526token_handling%253Dtime_edit%26app%3Dtimeedit-mazemap%26id%3D4ceaffb327ef45e7b900415b14934d2d%26timestamp%3D1727875724%26sig%3D55ecf82fda9e958a909f2d34ab45e69ee0e35359"
      s.get(url)

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

      cookies = s.cookies.get_dict()
      if not ("shib_idp_session" in cookies and "shib_idp_session_ss" in cookies):
        return jsonify({"error": "HH login failed"})

      url = "https://cloud.timeedit.net/hh/web/timeedit/ssoResponse/hh_saml2"
      start = response.text.find('lue="')+5
      end = response.text.find('"', start)
      saml_resp = response.text[start:end]
      params = { "SAMLResponse": saml_resp }
      s.post(url, data=params, headers=headers)

      url = s.cookies.get_dict()["sso-parameters"]
      url = url[url.find("https"):url.find("&ssoserv")]
      url = urllib.parse.unquote(url)

      response = s.get(url)
      return jsonify({"token": response.url[42:]})
    
  except Exception as e:
    return jsonify({"error": str(e)})

def book_room(poi_id: int, booking_start: time, duration: timedelta, token: str) -> dict:
  url = "https://booking.mazemap.com/api/roombooking/bookroom/"
  headers={
    'Content-type':'application/json',
    'Accept':'application/json'
  }
  booking_time = datetime.combine(datetime.now().date(), booking_start)
  start = booking_time.isoformat()[:-3]+"Z"
  end = (booking_time+duration).isoformat()[:-3]+"Z"
  payload = {
    "poiid": poi_id,
    "token": token,
    "start": start,
    "end": end,
    "provider": "time_edit"
  }
  response = rq.post(url, json=payload, headers=headers)

  try:
    return response.json()
  except:
    return {"error": response.text, "success": False}

@app.route('/proxy/book', methods=['POST'])
def time_booking():
  try:
    data = request.get_json()
    poi_id = data.get('poiId')
    start_hour = data.get('startHour')
    start_minute = data.get('startMinute')
    duration = data.get('duration')
    token = data.get('token')

    while datetime.now().time().hour < 6: t.sleep(0.01)

    return jsonify(book_room(poi_id, time(start_hour, start_minute), timedelta(minutes=duration), token))
  
  except Exception as e:
    return jsonify({"error": str(e), "success": False})

@app.route('/proxy/test', methods=['POST'])
def test():
  json = {
    "time": datetime.now().isoformat()[:-3]+"Z"
  }
  return jsonify(json)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)