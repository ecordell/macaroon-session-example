![Gif of session refresh](http://i.giphy.com/xTiTnq4HBjkRgax8Jy.gif)

# Getting Started

- Install docker and compose
- `docker-compose build web && docker-compose up`

It may be necessary to change the `SERVER_NAME` and `AUTH_ORIGIN` env
variables in the `docker-compose.yml` file depending on your local compose/docker setup. 
They should match the url used to access the service.

# What is this?

This is a quick and dirty proof-of-concept for refreshing a macaroon session in browser, without communicating with a third party.

## How it works:

1. A user logs in and is given a session macaroon that will last the length of their browser session.
2. That session macaroon has a third party caveat requiring that they prove they are logged in with the auth service (in this case, the same server).
3. The user is initially given a *discharge macaroon* proving they are logged in (after successful login), but it is short-lived.
4. An invisible sandboxed iframe from the auth service is embedded into the page, and contains the key necessary to mint a new *discharge macaroon*.
5. At any time (user manually clicks a "refresh" link, or automatically in response to user interaction) the user's *discharge macaroon* can be refreshed by using cross-document messaging with the auth iframe, extending the user's session.
6. Because the *discharge key* is available to the client, a limit is placed on the length of time a session may be refreshed.
7. When the user's session expires (they forget to refresh) or the refresh limit is reached, they are automatically logged out.

## Inspiration

This is directly inspired by a suggestion from the [Macaroons Paper]
(http://research.google.com/pubs/pub41892.html):

> *Local Discharging of Third-party Caveats*
>
> Third-party caveats can be used to implement decentralized authorization using holder-of-key proofs from authentication servers, 
as explained in earlier examples. However, third-party caveats may be discharged not just by networked servers, but by any isolated protection domain capable of holding secrets— such as, for example, a Web browser frame or extension, a mobile application, or a hardware token that is available locally to a user at a client.
>
>The delegation of third-party caveat discharging to such local principals 
can improve both performance (by reducing network messages), as well as the precision of authorization policy enforcement. For example, a collection of unrelated Web services may use the same federated login system; if each service maintains separate sessions, logging out of one service may leave the user, unknowingly, still logged in and authorized in other services, and thereby put them at risk. Instead, using macaroons, each request, on all sessions, may derive a fresh, or very short-lived, caveat discharge from the third-party federated login service (e.g., via a hidden iframe that holds the caveat root key to derive discharge macaroons and is accessible from each service’s Web page). Thus, a federated login service may hold the authoritative credentials, and services may be decoupled, yet the user need log out only once to immediately de-authorize all services.



## Notes

 - This is mostly a way to improve the user experience around session 
 staleness, and does little to improve security. The caveat discharge key is 
 available to the browser so a compromised session could be extended 
 indefinitely unless other measures are put in place.
 - This implementation is just one example of an approach, 
and the design could be modified to suit other needs. (It may not be 
desirable to force a logout even if the user is refreshing, 
there may be different ways in which the target service and the auth service 
agree on keys, the auth service may choose not to embed the caveat root key 
locally, etc) 
 - The particular choice of cookies to use and data to expose to different 
 channels is somewhat flexible and should be carefully considered. This 
 example exposes the session macaroon signature to javascript but not the 
 session macaroon itself.
