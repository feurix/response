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


.. _implemented-in-lmtpd:

Response-LMTPd
--------------
- Connection ACLs
- Soft-fail, hard-fail and fail-safe operation modes
- Sender validation using regular expressions
- Recipient validation using regular expressions and/or backend lookups
- Message header name validation using regular expressions
- Message header value validation using regular expressions
- Time-based rate limiting (one response to the same recipient per n seconds)


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


.. _started:

Started
=======

- PostgreSQL backend adapter
- Roundcube plugin


.. _pending:

Pending
=======

- Initscripts
- Config file
- Debian / Ubuntu Packaging
- Gentoo Ebuild
- RPM Spec
- Exim examples

Patches welcome! :-)
