# Put a database dump here to load it in postgresql

Us the format `01_*.sql.gz` or `01_*.sql`. Files are loaded alphabetically, it needs to
be loaded after the creation of the odoo user and before we disable cron.

A postgres user has to be created because otherwise there will be errors importing the
dump.
