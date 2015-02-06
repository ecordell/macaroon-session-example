var cookie = require('cookie');
var MacaroonsBuilder = require('macaroons.js').MacaroonsBuilder;
var moment = require('moment');

function getSessionExpireTime() {
  var cookies = cookie.parse(document.cookie);
  var auth_macaroon = MacaroonsBuilder.deserialize(cookies['auth_discharge']);
  var date_string = auth_macaroon.caveatPackets[0].getValueAsText().slice(7);
  return 'Session will expire ' + moment(date_string).fromNow();
}

function sendAuthRefreshRequest() {
  console.log('Requesting session refresh.');
  var cookies = cookie.parse(document.cookie);
  var payload = {
    "auth_macaroon_serialized": cookies['auth_discharge'],
    "session_signature": cookies['session_signature']
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
    console.log(getSessionExpireTime());
    return;
  }
  return reciever
}

function onload() {
   var refreshButton = document.getElementById("refresh-auth-session-button");
   refreshButton.onclick = sendAuthRefreshRequest;
   console.log(getSessionExpireTime());
}

window.onload = onload;
window.recieveNewAuthMacaroon = recieveNewAuthMacaroon;
