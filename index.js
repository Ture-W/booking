function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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
  const url = "https://booking-tp6b.onrender.com/proxy/token"; // se app.py (och README.md)
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
  let bookingTime = new Date((new Date()).setUTCHours(startHour - 2, startMinute, 0, 0)); // -2 timmar för tidzon offset
  const start = bookingTime.toISOString();
  bookingTime.setUTCMinutes(bookingTime.getUTCMinutes()+duration)
  const end = bookingTime.toISOString();

  const url = "https://booking.mazemap.com/api/roombooking/bookroom/";
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };
  const params = {
    "poiid": poiId,
    "token": token,
    "start": start,
    "end": end,
    "provider": "time_edit"
  };

  let now = new Date();
  while (now.getUTCMinutes() < 59 || (now.getUTCMinutes() == 59 && now.getUTCSeconds() < 50)) { await sleep(5000); now = new Date(); }
  while (now.getUTCHours() < 6) { now = new Date(); }
  
  try {
    const response = await $.ajax({
      url: url,
      method: 'POST',
      headers: headers,
      data: JSON.stringify(params)
    });
    
    if (response.success || response.error) { return response; }
    return {"error": response, "success": false};

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
      return "Du har redan andra bokningar just nu.";
    default:
      return "Okänt fel.";
  }
}