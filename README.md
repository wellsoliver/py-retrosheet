PY-RETROSHEET
=============

Python scripts for Retrosheet data downloading and parsing.

YE REQUIREMENTS
---------------

- Chadwick 0.7.2 http://chadwick.sourceforge.net/ (0.7.2 tested, should work with all versions)

- python 3.8+ (For python 2.5+ compatibility: [Here is a zip of the python code](https://github.com/MatthewMaginniss/py-retrosheet/releases/tag/python-v2.5%2B))

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

#### Environment Variables (optional)

Instead of editing the `config.ini` file, you may, optionally, use environment variables to set configuration options. Name the environment variables in the format `<SECTION>_<OPTION>`. Thus, an environment variable that sets the database username would be called `DATABASE_USER`. The environment variables overwrite any settings in the `config.ini` file.

Example,

    $ DATABASE_DATABASE=rtrsht_testing CHADWICK_DIRECTORY=/usr/bin/ python parse.py -y 1956


YE GRATITUDE
------------

Github user jeffcrow made many fixes and additions and added sqlite support

JUST THE DATA
-------------

If you're using PostgreSQL (and you should be), you can get a dump of all data up through 2016 (warning: 521MB) [here](https://www.dropbox.com/s/kg01np4ev3u2jsx/retrosheet.2016.psql?dl=0)

### Importing into PostgreSQL
After creating a PostgreSQL user named `wells`, you can create a database from the dump by running `pg_restore -U <USERNAME> -d <DATABASE> -1 retrosheet.2016.psql`.

### License

I don't care. Have at it.
