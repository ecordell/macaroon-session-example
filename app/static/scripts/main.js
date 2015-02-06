var cookie = require('cookie');
var MacaroonsBuilder = require('macaroons.js').MacaroonsBuilder;
var moment = require('moment');
var countdown = require('countdown');

var counterIntervalId = null;

function getSessionExpireTime() {
  var cookies = cookie.parse(document.cookie);
  if (cookies['auth_discharge']) {
    var auth_macaroon = MacaroonsBuilder.deserialize(cookies['auth_discharge']);
    var date_string = auth_macaroon.caveatPackets[0].getValueAsText().slice(7);
    return moment(date_string).toDate();
  } else {
    return null;
  }
}

function sendAuthRefreshRequest() {
  console.log('Requesting session refresh.');
  var cookies = cookie.parse(document.cookie);
  if (cookies['auth_discharge']) {
    var payload = {
      "auth_macaroon_serialized": cookies['auth_discharge'],
      "session_signature": cookies['session_signature']
    }
  }
  var o = document.getElementsByTagName('iframe')[0];
  o.contentWindow.postMessage(JSON.stringify(payload), 'http://192.168.59.103:8000/refresh-token/');
}

function recieveNewAuthMacaroon(origin)
{
  function reciever(event) {
    if (event.origin !== origin)
      return;

    console.log('Received updated session.');
    request = JSON.parse(event.data)

    document.cookie = cookie.serialize(
      'auth_discharge',
      request['protected_discharge'],
      {
        path: '/',
        expires: moment(request['expires']).toDate()
      }
    );
    setupTimer("logout-timer", getSessionExpireTime());
    return;
  }
  return reciever
}

function setupTimer(id, deadline) {
  var timer = document.getElementById(id)
  var refreshWarning = document.getElementById('refresh-warning');
  if (deadline !== null) {
    refreshWarning.style.display = 'block';
    count = countdown(deadline);
    if (counterIntervalId !== null) {
      clearInterval(counterIntervalId);
    }
    timer.innerHTML = countdown(deadline).toString();
    counterIntervalId = setInterval(function(){
      if (countdown(deadline).value <= 0) {
        timer.innerHTML = countdown(deadline).toString();
      } else {
        clearInterval(counterIntervalId);
        window.location.replace("/logout");
      }
    }, 1000);
  } else {
    refreshWarning.style.display = 'none';
  }
}


function onload() {
   var refreshButton = document.getElementById("refresh-auth-session-button");
   refreshButton.onclick = sendAuthRefreshRequest;
   setupTimer("logout-timer", getSessionExpireTime());
}

window.onload = onload;
window.recieveNewAuthMacaroon = recieveNewAuthMacaroon;


