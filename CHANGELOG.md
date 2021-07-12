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
