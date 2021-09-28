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
