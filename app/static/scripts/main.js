var cookie = require('cookie');
var MacaroonsBuilder = require('macaroons.js').MacaroonsBuilder;
var moment = require('moment');
var countdown = require('countdown');

var sessionIntervalId = null;
var maxRefreshIntervalId = null;

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

function getMaxRefreshTime() {
  var cookies = cookie.parse(document.cookie);
  if (cookies['max_refresh_time']) {
    return moment(cookies['max_refresh_time']).toDate();
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
      "session_signature": cookies['session_signature'],
      "max_refresh_time": getMaxRefreshTime()
    }
  }
  var o = document.getElementsByTagName('iframe')[0];
  o.contentWindow.postMessage(JSON.stringify(payload), 'http://192.168.59.103:8000/refresh-token/');
}

function updateSessionTimer(deadline) {
  var timer = document.getElementById("logout-timer");
  if (sessionIntervalId !== null) {
    clearInterval(sessionIntervalId);
  }
  timer.innerHTML = countdown(deadline).toString();
  sessionIntervalId = setInterval(function(){
    if (countdown(deadline).value <= 0) {
      timer.innerHTML = countdown(deadline).toString();
    } else {
      clearInterval(sessionIntervalId);
      window.location.replace("/logout");
    }
  }, 1000);
}

function updateMaxRefreshTimer(deadline) {
  var timer = document.getElementById("max-refresh-timer");
  if (maxRefreshIntervalId !== null) {
    clearInterval(maxRefreshIntervalId);
  }
  timer.innerHTML = countdown(deadline).toString();
  maxRefreshIntervalId = setInterval(function(){
    if (countdown(deadline).value <= 0) {
      timer.innerHTML = countdown(deadline).toString();
    } else {
      clearInterval(maxRefreshIntervalId);
      window.location.replace("/logout");
    }
  }, 1000);
}

function updateRefreshNotice() {
  var refreshWarning = document.getElementById('refresh-warning');
  if (getSessionExpireTime() !== null) {
    refreshWarning.style.display = 'block';
    updateSessionTimer(getSessionExpireTime());
    updateMaxRefreshTimer(getMaxRefreshTime());
  } else {
    refreshWarning.style.display = 'none';
  }
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
    updateRefreshNotice();
    return;
  }
  return reciever
}

function onload() {
   var refreshButton = document.getElementById("refresh-auth-session-button");
   refreshButton.onclick = sendAuthRefreshRequest;
   updateRefreshNotice();
}

window.onload = onload;
window.recieveNewAuthMacaroon = recieveNewAuthMacaroon;


