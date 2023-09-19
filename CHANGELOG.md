# v0.6.0

* Removed ability to pickle the `LinkedInMessaging` cookies. Use `from_cookies`
  and pass `JSESSIONID` and `li_at` individually.

# v0.5.7

* Added objects to support message edits.

# v0.5.6

* Added objects to support voice messages.
* Updated versions of many dependencies and all of the pre-commit hooks.

# v0.5.5

* Add back support for the `TIMEOUT` special event. All other errors still need
  to be handled by API consumers.

# v0.5.4

* Fix the `__license__` property in the package.
* Added some objects to support posts media. Contributed by @mehdiirh in #5
* Dropped support for the `STREAM_ERROR` and `TIMEOUT` special events. Consumers
  of that API should just handle errors thrown by the `start_listener` call
  and perform the appropriate error mitigations.

* Examples

  * Add `ALL_EVENTS` listener example.

* Internal:

  * Convert to flit for managing the package and dependencies.

* Developer experience:

  * Add dependabot for GitHub Actions and Python requirements.
  * Use [pre-commit/action](https://github.com/pre-commit/action) for linting in
    CI.
  * Update all of the pre-commit hooks.

# v0.5.3

* Add manual login option where you can specify the `li_at` and `JSESSIONID`
  cookies manually. For example, you could open a private browser window, log
  in, and extract the cookies from the developer tools.

* Internal:

  * Update GitHub Actions workflow to not use a matrix for Python versions.

# v0.5.2

* Parse timestamp from LinkedIn as UTC timestamps in case the server's timezone
  is different than UTC.
* Internal:

  * Add isort and pre-commit.
  * Changed maximum line length from 88 to 99.
  * Reordered imports to be more in line with other mautrix bridges.

# v0.5.1

* Add objects for typing notifications and read receipts.
* Add `set_typing` function for sending typing notifications.

# v0.5.0

* Add objects for shared feed updates.

# v0.4.3

* Add conversation name field to `Conversation` and name update custom content
  to `MessageCustomContent`.

# v0.4.2

* Explicitly specify the timeout of each event stream connection to help avoid
  weird states where the event stream is open but not receiving events.
* Add more logging and error handling when event listener handlers fail.

# v0.4.1

* Added special events for monitoring listener connection status.
* Added the ability to mark a conversation as read.

# v0.4.0

* Dropped support for everything except for Python 3.9+.
* Made all API fields optional.

# v0.3.0

* Add support for deleting messages.
* Added support for the `recalled_at` property on `MessageEvent`s.
* Add support for adding and removing reactions.
* Add support for getting the reactors of a message and emoji.
* Improved error handling when there is a JSON decode error.

# v0.2.1

* Removed `liap` cookie as required for being authenticated.

# v0.2.0

* Implemented logout endpoint.

# v0.1.7

* Fix typo in InMail parsing.

# v0.1.6

* Add support for parsing alternate names and images for InMail profiles

# v0.1.5

* Add support for parsing InMail messages

# v0.1.4

* Add `py.typed` file to indicate that the library has type hints.

# v0.1.3

* Made the `URN` object hashable. This is useful for using `URN`s as keys for
  dictionaries
* Added more function type annotations and enforced using annotations via
  flake8-annotations.

# v0.1.2

* Add a few convenience methods for URNs.
* Add `get_all_conversations` async generator for iterating through all of the
  user's conversations.
* Add better error handling to download functions.
* Add examples

# v0.1.1

This is the initial release. Features include:

* Login helper and session manager. Works with 2FA.
* Get a list of the user's conversations.
* Retrieve the messages and media in a particular conversation.
* Send messages to a particular conversation or set of recipients. Multimedia is
  supported.
* An event listener structure for listening for new events.
