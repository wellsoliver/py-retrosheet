PY-RETROSHEET
=============

Python scripts for Retrosheet data downloading and parsing.

YE REQUIREMENTS
---------------

- Chadwick 0.6.2 http://chadwick.sourceforge.net/

- python 2.5+ , python 3.4+

- sqlalchemy: http://www.sqlalchemy.org/

- [if using postgres] psycopg2 python package (dependency for sqlalchemy)

USAGE
-----

### Setup

    cp scripts/config.ini.dist scripts/config.ini

Edit `scripts/config.ini` as needed.  See the steps below for what might need to be changed.

### Download

    python download.py [-y <4-digit-year> | --year <4-digit-year>]

The `scripts/download.py` script downloads Retrosheet data. Edit the config.ini file to configure what types of files should be downloaded. Optionally set the year to download via the command line argument.

- `download` > `dl_eventfiles` determines if Retrosheet Event Files should be downloaded or not. These are the only files that can be processed by `parse.py` at this time.

- `download` > `dl_gamelogs` determines if Retrosheet Game Logs should be downloaded or not. These are not able to be processed by `parse.py` at this time.

### Parse into SQL

    python parse.py [-y <4-digit-year>]
    
After the files have been downloaded, parse them into SQL with `parse.py`.

1. Create database called `retrosheet` (or whatever).

2. Add schema to the database w/ the included SQL script (the .postgres.sql one works nicely w/ PG, the other w/ MySQL)

3. Configure the file `config.ini` with your appropriate `ENGINE`, `USER`, `HOST`, `PASSWORD`, and `DATABASE` values - if you're using postgres, you can optionally define `SCHEMA` and download directory

    - Valid values for `ENGINE` are valid sqlalchemy engines e.g. 'mysql', 'postgresql', or 'sqlite',
    
    - If you have your server configured to allow passwordless connections, you don't need to define `USER` and `PASSWORD`.
    
    - If you are using sqlite3, `database` in the config should be the path to your database file.
    
    - Specify directory for retrosheet files to be downloaded to, needs to exist before script runs
    
5. Run `parse.py` to parse the files and insert the data into the database. (optionally use `-y YYYY` to import just one year)

YE GRATITUDE
------------

Github user jeffcrow made many fixes and additions and added sqlite support

JUST THE DATA
-------------

If you're using PostgreSQL (and you should be), you can get a dump of all data up through 2014 (warning: 502MB) [here](https://www.dropbox.com/s/nv9712l1ylvh64n/retrosheet.psql?dl=0)
