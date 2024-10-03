
async function getPoi(name) {
  const url = "https://search.mazemap.com/search/equery/";
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  const params = {
    "q": name,
    "rows": 1,
    "withpois": true
  };
  
  try {
    const response = await $.ajax({
      url: url,
      method: 'GET',
      headers: JSON.stringify(headers),
      body: JSON.stringify(params)
    });
    return response.result[0].poiId;

  } catch (error) {
    console.error('Fel uppstod i getPoi:', error);
    return null;
  }
}

async function getToken(hhUsername, hhPassword) {
  const url = "https://booking-tp6b.onrender.com/proxy/token";
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  const params = {
    "hhUsername": hhUsername,
    "hhPassword": hhPassword
  };

  try {
    const response = await $.ajax({
      url: url,
      method: 'POST',
      headers: JSON.stringify(headers),
      body: JSON.stringify(params)
    });

    if (response.error) {
      console.error('Fel uppstod i getToken:', error);
      return null;
    }
    return response.token

  } catch (error) {
    console.error('Fel uppstod i getToken:', error);
    return null;
  }
}

async function bookRoom(poiId, startHour, startMinute, duration, token) {
  const url = "https://booking-tp6b.onrender.com/proxy/book";
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  const params = {
    "action": "book",
    "poiId": poiId,
    "startHour": startHour,
    "startMinute": startMinute,
    "duration": duration,
    "token": token
  };

  try {
    const response = await $.ajax({
      url: url,
      method: 'POST',
      headers: JSON.stringify(headers),
      body: JSON.stringify(params)
    });

    return response

  } catch (error) {
    console.error('Fel uppstod i bookRoom:', error);
    return null;
  }
}

function parseBookingError(errorText) {
  switch (errorText) {
    case "busy":
      return "Rummet är redan bokat under en tid som krockar med din önskade tid";
    case "not_allowed_interval":
      return "Den valda perioden är inte tillåten för detta rummet eller din önskade tid är inte en intervall av tillåtna perioder för bokning." +
      " Detta felet kan också hända om din valda tid redan passerat eller om bokningen försöktes under en otillåten tid (t.ex. innan kl 08:00).";
    case "time_quota_exceeded":
      return "Du har redan ett eller flera bokade rum för totalt 2 timmar.";
    default:
      return "Okänt fel.";
  }
}