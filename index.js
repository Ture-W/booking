function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function waitUntil(hour, minute, second = 0) {
  while (true) {
    const now = new Date();
    const currentHour = now.getUTCHours();
    const currentMinute = now.getUTCMinutes();
    const currentSecond = now.getUTCSeconds();
    if (currentHour > hour || (currentHour === hour && currentMinute > minute) || (currentHour === hour && currentMinute === minute && currentSecond >= second)) {
      break;
    }
    await sleep(20000);
  }
}

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
      headers: headers,
      data: params
    });
    return [response.result[0].poiNames[0], response.result[0].poiId];

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
      headers: headers,
      data: JSON.stringify(params)
    });

    if (response.error) {
      console.error('Fel uppstod i getToken:', response.error);
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
      headers: headers,
      data: JSON.stringify(params)
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
      return "Rummet är redan bokat under en tid som krockar med din önskade tid.";
    case "not_allowed_interval":
      return "Den valda tid för bokningen eller tidlängden är inte tillåten för detta rummet.";
    case "time_quota_exceeded":
      return "Du har redan ett eller flera bokade rum för totalt 2 timmar.";
    default:
      return "Okänt fel.";
  }
}