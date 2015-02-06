# Getting Started

- Install docker and fig
- `fig build web && fig up`

The redis instance can be reached with `redis-cli -h redis`


# What is this?

This is a quick and dirty proof-of-concept for refreshing a macaroon session in browser, without communicating with a third party.

## Here's how it works:

1. A user logs in and is given a session macaroon that will last the length of their browser session.
2. That session macaroon has a third party caveat requiring that they prove they are logged in with the auth service (in this case, the same server).
3. The user is initially given a discharge macaroon proving they are logged in (after successful login), but it is short-lived.
4. An invisible sandboxed iframe from the auth service is embedded into the page, and contains the key necessary to mint a new discharge macaroon.
5. At any time (user manually clicks a "refresh" link, or automatically in response to user interaction) the user's discharge macaroon can be refreshed by using cross-document messaging with the auth iframe, extending the user's session.
6. Because the discharge key is available to the client, a limit is placed on the length of time a session may be refreshed.
7. When the user's session expires (they forget to refresh) or the refresh limit is reached, they are automatically logged out.

## TODO

- Enforce max refresh on client side (currently only enforced server side - so user can refresh past the max, but their credentials will be invalid).
- Refactor, rewrite in ES6, wrap up into an npm module. (And a python package?)
- Write a component (react?) that will overlay a session expiration warning.
- Add another login option by wrapping an oauth service - Google?
