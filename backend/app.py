from flask import Flask, request, jsonify
from flask_cors import CORS
import requests as rq
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
      headers={
        'Content-type':'application/json,application/x-www-form-urlencoded',
        'Accept':'application/json'
      }

      url = "https://cloud.timeedit.net/hh/web/timeedit/sso/hh_saml2"
      params = {
        "back": "https%3A%2F%2Fcloud.timeedit.net%2Fhh%2Fweb%2Fstudent%2Fauth%3Fredirect_url%3Dhttps%253A%252F%252Fuse.mazemap.com%252Foauthsuccess.html%253Fstate%253D%25257B%252522mazemap_redirect_uri%252522%25253A%252522https%25253A%25252F%25252Fuse.mazemap.com%25252F%252523v%25253D1%252526campusid%25253D278%252526zlevel%25253D1%252526center%25253D12.879905%25252C56.663900%252526zoom%25253D17.6%252526sharepoitype%25253Dpoi%252526sharepoi%25253D1000104175%252526showpoidetails%25253Dtrue%252522%25252C%252522provider%252522%25253A%252522time_edit%252522%25252C%252522providers%252522%25253A%25255B%252522time_edit%252522%25255D%25257D%2526token_handling%253Dtime_edit%26app%3Dtimeedit-mazemap%26id%3D5f5149964087452faeba24ed3c417fed%26timestamp%3D1731095149%26sig%3D7fe640de507bc86bd35a0752e3555d7cab96f1ae"
      }
      response = s.get(url, params=params, headers=headers)

      csrf_start = response.text.find('en" value="')+11
      csrf_token = response.text[csrf_start:response.text.find('"', csrf_start)]

      url = "https://idp.hh.se/idp/profile/SAML2/Redirect/SSO?execution=e1s1"
      params = {
        "csrf_token": csrf_token,
        "shib_idp_ls_success.shib_idp_session_ss": "true",
        "shib_idp_ls_success.shib_idp_persistent_ss": "true",
        "shib_idp_ls_supported": "true",
        "_eventId_proceed": ""
      }
      response = s.post(url, params=params, headers=headers)

      csrf_start = response.text.find('en" value="')+11
      csrf_token = response.text[csrf_start:response.text.find('"', csrf_start)]

      url = "https://idp.hh.se/idp/profile/SAML2/Redirect/SSO?execution=e1s2"
      params = {
        "csrf_token": csrf_token,
        "j_username": hh_username,
        "j_password": hh_password,
        "_eventId_proceed": ""
      }
      response = s.post(url, params=params, headers=headers)

      if not ("__Host-shib_idp_session" in s.cookies.get_dict()):
        return jsonify({"error": "Kunde inte logga in i HH"})

      csrf_start = response.text.find('en" value="')+11
      csrf_token = response.text[csrf_start:response.text.find('"', csrf_start)]

      url = "https://idp.hh.se/idp/profile/SAML2/Redirect/SSO?execution=e1s3"
      params = {
        "csrf_token": csrf_token,
        "shib_idp_ls_success.shib_idp_session_ss": "true",
        "_eventId_proceed": ""
      }
      response = s.post(url, params=params, headers=headers)

      saml_start = response.text.find('lue="')+5
      saml_response = response.text[saml_start:response.text.find('"', saml_start)]

      url = "https://cloud.timeedit.net/hh/web/timeedit/ssoResponse/hh_saml2"
      params = {
        "SAMLResponse": saml_response
      }
      s.get(url, params=params, headers=headers)

      url = s.cookies.get_dict()["sso-parameters"]
      url = url[url.find("https"):url.find("&ssoserv")]
      url = urllib.parse.unquote(urllib.parse.unquote(url))

      response = s.get(url)
      token = response.url[42:]

      if token[:5] != "state":
        return jsonify({"error": "Kunde inte logga in i TimeEdit"})
      
      return jsonify({"token": token})
    
  except Exception as e:
    return jsonify({"error": str(e)})