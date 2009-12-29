.. _features:

*************************
Complete list of features
*************************

.. _implemented:

Implemented
===========

.. _implemented-in-all:

In all tools
------------
- Error and signal handling, graceful dying
- Logging with various log-levels
- Syslog support
- Config file support
- Dry-Run mode (useful in combination with debug logging)


.. _implemented-in-lmtpd:

Response-LMTPd
--------------
- Connection ACLs
- Soft-fail, hard-fail and fail-safe operation modes
- Sender validation using regular expressions
- Recipient validation using regular expressions and/or backend lookups
- Message header name validation using regular expressions
- Message header value validation using regular expressions
- Time-based queue limiting (one response to the same recipient per n seconds)
- Configuration reload on SIGHUP


.. _implemented-in-cleanup:

Response-Cleanup
----------------
- Disable response configs that have expired
- Delete old response records that were not hit for a long time
- Delete response records that belong to disabled configs


.. _implemented-in-notify:

Response-Notify
---------------
- Sending via a remote or local SMTP relay
- SMTP-AUTH support
- STARTTLS support
- Dumping response mails to stdout
- Limiting generation of response mails


.. _implemented-extras:

Extras
------
- Roundcube plugin
- Initscript for Debian-like systems


.. _started:

Started
=======

- ...


.. _pending:

Pending
=======

- Debian / Ubuntu Packaging
- PostgreSQL backend adapter
- PostgreSQL example database schema and queries
- Gentoo Ebuild
- RPM Spec
- Exim examples

Patches welcome! :-)

