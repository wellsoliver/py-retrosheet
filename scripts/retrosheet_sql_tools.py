#!/usr/bin/env python

'''
This file provides a class for interacting with a retrosheet database. 
It has two main purposes: 

 i. add some additional quantities to the events and games tables

  games
   - playoff_flag
   - year_id

  events
   - playoff_flag
   - year_id
   - time_since_1900 : an integer giving the number of seconds 
                       since Jan 1, 1900, UTC
   - tto : times through the order
   - sun_alt, sun_az : altitude and azimuth of the sun
   - woba_pts : woba_pts for the event
   - woba_pts_expected : placeholder for woba_pts expected 
                         from the matchup of batter vs pitcher. 

   the location of the sun computations require PyEphem
   http://rhodesmill.org/pyephem/

   the time computations require timezone information, 
   to translate everything to a common timezone (UTC)
   pytz: http://pytz.sourceforge.net
   tzwhere: https://github.com/pegler/pytzwhere/tree/master/tzwhere

   This file can be imported to get access to the methods, or run via:
   python retrosheet_sql_tools.py 
   with optional arguments 
   -minyr minyr 
   -maxyr maxyr 
   -vbose vbose
   -n2print n2print

   NOTE: This script will write out an sql file VARD_(TIMESTAMP).sql, 
   which can then be sourced by your SQL implementation (VARD stand for 
   Value Added Retrosheet Database; the Value Added terminology is a 
   nod to my astronomy days, as in "Value Added Galaxy Catalog", 
   http://sdss.physics.nyu.edu/vagc/). It DOES NOT store any variables 
   to the database. It does update the schema, however, by adding columns 
   for the computed variables.

 ii. provides a method to read sql data into a numpy array, with automatic 
     determination of variable type. The relevant method is 
     sqlQueryToArray(query_string), 
     which returns a numpy array of result of the query

  an example of use is 
   import retrosheet_sql_tools
   configFileLocation = 'config.ini'
   minyr = 2004
   maxyr = 2004
   rs = retrosheet_sql_tools.retrosheet_sql(cfgFile=configFileLocation)
   rs.updateSchema()
   rs.computeValueAdded(minyr=minyr, maxyr=maxyr)
  
   q = 'select tto, avg(woba_pts) as wo, avg(woba_pts_expected) as wx from retrosheet.events where year_id=2004 and woba_pts>=0 and pit_start_fl=\'T\' group by tto'
   data = rs.sqlQueryToArray(q)
   print data

'''

import json
import sqlalchemy
from configparser import ConfigParser
from configparser import NoOptionError
import sys
import datetime
import decimal
import numpy as np
import ephem
import pytz
from tzwhere import tzwhere

bump = 1


class retrosheet_sql:

##########################
    def __init__(self, vbose=0, cfgFile=None):
        ''' Some methods to conveniently read data from retrosheet 
        database and store as numpy arrays,
        and also some methods to add some useful quantities.
        '''
        self.vbose = vbose

        # placeholder for the fangraphs guts data 
        self.guts = None
        self.seamheads = None

        # go ahead and read it in on initialization?
#        self.guts = self.readFgGutsJson()

        # read the database configuration, and make a connection
        config = ConfigParser()
        if cfgFile is None:
            config.read('config.ini')
        else:
            config.read(cfgFile)

        try:
            self.conn = self.dbConnect(config)
        except Exception as e:
            print(('Cannot connect to database: %s' % e))
            raise SystemExit

        self.config = config
        self.mysql_db = config.get('database', 'database')

        self.cursor = self.conn.connection.cursor()
#        self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        self.TABLE_NAMES = {}

        self.TABLE_NAMES['TBL_RETRO_PARKCODE'] = '%s.parkcode' % self.mysql_db
        self.TABLE_NAMES['TBL_RETRO_EVENTS'] = '%s.events' % self.mysql_db
        self.TABLE_NAMES['TBL_RETRO_GAMES'] = '%s.games' % self.mysql_db
        self.TABLE_NAMES['TBL_RETRO_LAST_DAY'] = '%s.last_day' % self.mysql_db
        self.TABLE_NAMES['TBL_FGGUTS'] = 'mlb.fgGuts'

        self.eventUpdateData = {}

        self.rad2deg = 180.0/np.pi
        self.deg2rad = 1.0/self.rad2deg


##########################
    def __str__(self):
        print(self.config)
        return ''

###############
    def dbConnect(self, config):
        ''' Connect to the retrosheet database, using the config.ini file
        '''
        try:
            ENGINE = config.get('database', 'engine')
            DATABASE = config.get('database', 'database')
            
            HOST = None if not config.has_option('database', 'host') else config.get('database', 'host')
            USER = None if not config.has_option('database', 'user') else config.get('database', 'user')
            PASSWORD = None if not config.has_option('database', 'password') else config.get('database', 'password')
        except NoOptionError:
            print('Need to define engine, user, password, host, and database parameters')
            raise SystemExit

        if ENGINE == 'sqlite':
            dbString = ENGINE + ':///%s' % (DATABASE)
        else:
            if USER and PASSWORD:
                dbString = ENGINE + '://%s:%s@%s/%s' % (USER, PASSWORD, HOST, DATABASE)
            elif USER:
                dbString = ENGINE + '://%s@%s/%s' % (USER, HOST, DATABASE)
            else:
                dbString = ENGINE + '://%s/%s' % (HOST, DATABASE)
        
        db = sqlalchemy.create_engine(dbString)
        conn = db.connect()
    
        return conn

###############
    def updateSchema(self, vbose=0):
        ''' Updates the retrosheet database tables with new 
        "Value Added" variables'''
        qs = {}
        qs['TBL_RETRO_GAMES'] = {}
        qs['TBL_RETRO_GAMES']['YEAR_ID'] = 'int(4)'
        qs['TBL_RETRO_GAMES']['PLAYOFF_FLAG'] = 'tinyint(1)'

        qs['TBL_RETRO_EVENTS'] = {}

        qs['TBL_RETRO_EVENTS']['YEAR_ID'] = 'int(4)'
        qs['TBL_RETRO_EVENTS']['PLAYOFF_FLAG'] = 'tinyint(1)'
        qs['TBL_RETRO_EVENTS']['wOBA_pts'] = 'float'
        qs['TBL_RETRO_EVENTS']['wOBA_pts_expected'] = 'float'
        qs['TBL_RETRO_EVENTS']['tto'] = 'tinyint(2)'
        qs['TBL_RETRO_EVENTS']['sun_alt'] = 'float(8, 4)'
        qs['TBL_RETRO_EVENTS']['sun_az'] = 'float(8, 4)'
        qs['TBL_RETRO_EVENTS']['time_since_1900'] = 'bigint(20)'

        for t in qs:
            for c in qs[t]:
                q = 'alter table %s add column %s %s ' % (self.TABLE_NAMES[t], c, qs[t][c])
                if vbose>=1:
                    print(q)
                try:
                    self.cursor.execute(q)
#                    self.conn.commit()
                except Exception as e:
                    if vbose>=1:
                        print('Warning: ' , e)
                    pass


###############
    def getSeamheadsParksData(self, 
                              ifile='external_data/seamheads_parks.json'):
        ''' Read in the parks data, provided by seamheads. 
        ''' 
        return json.load(open(ifile,'r'))



###############
    def resultToNpDtype(self, keys, row, vbose=0):
        ''' Given a result row from a sql query, determine data type, 
        and generate a corresponding numpy.dtype object 
        '''
        arr = []
        for i, k in enumerate(keys):
            x = row[i]
            if vbose>=1:
                print(k, x, type(x))
            if type(x)==type(1):
                s = (k, 'i4')
            elif type(x)==type(1):
                s = (k, 'i8')
            elif type(x)==type(decimal.Decimal(1)):
                s = (k, 'f8')
            elif type(x)==type(1.0):
                s = (k, 'f8')
            else:
                s = (k, 'S256')
            arr.append(s)

        dt = np.dtype(arr)
        if vbose>=1:
            print('dtype', arr, dt)
        return dt

###############
    def descriptToKeys(self):
        return [d[0] for d in self.cursor.description]

###############
    def sqlQueryToArray(self, q, vbose=0):
        ''' Given a sql query, execute the query, and return the results 
        in a numpy array. The data type of each column automatically 
        determined, and an appropriate numpy.dtype object is created 
        and filled.
        '''
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        if len(rows)==0:
            return []

        row = rows[0]

        keys = self.descriptToKeys()

        dt = self.resultToNpDtype(keys, row, vbose=vbose)

        data = []
        for row in rows:
            tmp = []
            if vbose>=1:
                print('********************')
            for i, k in enumerate(keys):
                x = row[i]
                if vbose>=1:
                    print(k, row[i])
                tmp.append(x)
            data.append(tuple(tmp))
        if vbose>=1:
            print(data)
        return np.array(data, dtype=dt)

###############
    def readFgGutsJson(self, gutsFile='external_data/fgGuts.json'):
        return json.load(open(gutsFile,'r'))

###############
    def csvToArray(self, csvfile, skeys=[], ikeys=[], fkeys=[], delimiter=',', vbose=0):
        ''' Read a csv file into a numpy array. The default is to treat 
        all variables as double-precision. There is no automatic data-type 
        detection. Columns can be cast to specific data types with the 
        skeys (cast these columns as character arrays), ikeys (cast these 
        columns as 4-byte integers), and fkeys (cast these columns as 
        4-byte floats) parameters. These should be arrays of column names. 
        A 1-line header on the csv file is assumed.
        '''
        ifp = open(csvfile,'r')
        hd = next(ifp)
        ifp.close()
        keys = hd.split('%s' % delimiter)
        arr = []
        for sk in keys:
            k = sk.strip()
            if k in ikeys:
                s = (k, 'i4')
            elif k in fkeys:
                s = (k, 'f4')
            elif k in skeys:
                s = (k, 'S256')
            else:
                s = (k, 'f8')

            if vbose>=1:
                print('k', k, 's', s)

            arr.append(s)
#        print arr
        try:
            dt = np.dtype(arr)
        except ValueError:
            tmp = []
            for a in arr:
                tmp.append(a[0])
            tmp.sort()
            
            
            print('dt arr',arr)
            print('dt arr', tmp)
            print(len(tmp), len(np.unique(tmp)))
            print('dt arr u', np.unique(tmp))
            sys.exit()

        if vbose>=1:
            print(dt)
        return np.genfromtxt(csvfile, skip_header=1, delimiter=delimiter, dtype=dt)


##########################
    def computeWobaPlayer(self, plid=None, yrid=None, 
                          lbat=None, 
                          ibb=False, 
                          lpost=False, 
                          lOBP=False, 
                          lGrouped = False,
                          vbose=False):
        ''' Use the retrosheet events table to compute seasonal wOBA for 
        a player, batter (lbat=True) or pitcher (lbat=False, in which case 
        it's wOBA-against). This aggregates data for the named player and 
        passes it on the lower-level method computeWoba. If the lOBP parameter 
        is True, then it computes OBP rather than wOBA. 
        '''

        if lbat:
            ptype = 'bat_id'
        else:
            ptype = 'pit_id'

        if lGrouped:
            q = ' select event_cd, event_tx, count(*) n from %s where year_id=%d and %s=\'%s\' ' % (self.TABLE_NAMES['TBL_RETRO_EVENTS'], yrid, ptype, plid)
        else:
            q = ' select event_cd, event_tx from %s where year_id=%d and %s=\'%s\' ' % (self.TABLE_NAMES['TBL_RETRO_EVENTS'], yrid, ptype, plid)

        if not lpost:
            q += ' and playoff_flag=0 '

        if lGrouped:
            q += ' group by %s ' % 'event_cd'

        if vbose:
            print(q)

        self.cursor.execute(q)
        rows = self.sqlQueryToArray()

        if lGrouped:
            data = {}
        else:
            data = []

        for row in rows:
            if vbose:
                print(row)
            if lGrouped:
                data[int(row['event_cd'])] = int(row['n'])
            else:
                data.append(int(row['event_cd']))


        ans = self.computeWoba(data, yrid=yrid, ibb=ibb, lOBP=lOBP, lGrouped=lGrouped, vbose=vbose)
        return ans


##########################
    def makePlayoffFlag(self, yrid, vbose=0):
#        datetime.datetime.
        ''' Use some heuristics to automatically determine which games 
        are playoffs and which are regular season. Returns a dictionary. 
        The key 'gids' has a value which is a dictionary of 
        game_id-playoff_flag pairs. playoff_flag is an integer, 
        0=regular season, 1=playoffs
        '''
        data = {}

        q = 'select a.* from (select game_id, home_team_id, away_team_id, cast(substr(game_id,4,4) as unsigned) as year_id, cast(substr(game_id,8,2) as unsigned) as mn_id, cast(substr(game_id,10,2) as unsigned) as day_id, game_ct from %s group by game_id ) a where year_id=%d order by year_id, mn_id, day_id, game_ct ' % (self.TABLE_NAMES['TBL_RETRO_GAMES'], yrid)

        tmp = []
        rows = self.sqlQueryToArray(q)
        for row in rows:
            aa = row['away_team_id']
            hh = row['home_team_id']
            for t in [aa, hh]:
                if not t in data:
                    data[t] = {}
                    data[t]['gid'] = []
                    data[t]['ngame'] = 0
                data[t]['ngame'] += 1
                data[t]['gid'].append(row['game_id'])

        if vbose>=1:
            print('data', data)

        for k in data:
            tmp.append(data[k]['ngame'])
        tmp = np.array(tmp)
        mm = int(np.median(tmp))

        if vbose>=1:
            print('*************')
            print(yrid, mm)

        max_time = -1
        for k in data:
            ng = data[k]['ngame']
            if not ng==mm:
                continue
            gid = data[k]['gid'][-1]
            yr = int(gid[3:3+4])
            mn = int(gid[7:7+2])
            day = int(gid[9:9+2])
            tt = datetime.datetime(yr, mn, day)
            ttI = tt.toordinal()
#            print gid, yr, mn, day, tt, ttI
            if ttI>max_time:
                max_time=ttI
            newtt = datetime.datetime.fromordinal(ttI)
            if vbose>=1:
                print(k, data[k]['gid'][-1], ttI, \
                    datetime.datetime.fromordinal(ttI), \
                    newtt.year, newtt.month, newtt.day)

        hack = {}
        hack[1950] = [10, 4]
        hack[1951] = [10, 4]
        hack[1952] = [10, 1]
        hack[1953] = [9, 30]
        hack[1981] = [10, 6]
        hack[1994] = [12, 31]
        hack[1995] = [10, 3]

        if yrid in hack:
            mn, day = hack[yrid]
            tt = datetime.datetime(yrid, mn, day)
            ttI = tt.toordinal()
            max_time = ttI-1

        ndata = {}
        ndata['gids'] = {}
        for k in data:
            for gid in data[k]['gid']:
                yr = int(gid[3:3+4])
                mn = int(gid[7:7+2])
                day = int(gid[9:9+2])
                tt = datetime.datetime(yr, mn, day)
                ttI = tt.toordinal()
                if ttI > max_time:
                    pflag = 1
                else:
                    pflag = 0
                ndata['gids'][gid] = pflag

        if vbose>=1:
            print(ndata)
        ndata['mm'] = mm

        if vbose>=1:
            print(yr, max_time)
        newtt = datetime.datetime.fromordinal(max_time)
        ndata['newtt'] = newtt
        ndata['max_time'] = max_time
        ndata['tmp'] = tmp

        return ndata

##########################
    def computeWoba(self
                    ,indata
                    ,yrid=None 
                    ,ibb=False 
                    ,lOBP=False
                    ,lGrouped=False
                    ,vbose=False):

        ''' Given some data in the form of retrosheet event_cd, compute wOBA. 
        The ibb parameter determines if IBB are included or ignored. lOBP 
        determines whether to compute wOBA (lOBP=False) or OBP (lOBP=True). 
        If lGrouped=True, it expects a dictionary of event_cd-number pairs. 
        Otherwise it just cycles through the values of indata (which are 
        the event_cd values) and adds up the wOBA points one at a time. 
        Returns a tuple of wOBA_pts, PA, and wOBA=wOBA_pts/PA.
        '''

        wpts = 0.0
        pa = 0

        ww = {}
        row = self.guts[str('yrid')]
        for k in list(row.keys()):
            if lOBP:
                ww[k] = 1.0
            else:
                ww[k] = row[k]
        if vbose:
            print('wOBA (OBP) weights: ' , ww)

        for ev in indata:
            if lGrouped:
                val = indata[ev]
            else:
                val = 1.0

            if vbose:
                print(ev, val)
            if ev in [2,3]:
                pa += val
            elif ev in [14]:
                pa += val
                wpts += ww['wBB']*val
            elif ev in [15] and ibb:
                pa += val
                wpts += ww['wBB']*val
            elif ev in [16]:
                pa += val
                wpts += ww['wHBP']*val
            elif ev in [20]:
                pa += val
                wpts += ww['w1B']*val
            elif ev in [21]:
                pa += val
                wpts += ww['w2B']*val
            elif ev in [22]:
                pa += val
                wpts += ww['w3B']*val
            elif ev in [23]:
                pa += val
                wpts += ww['wHR']*val

        if pa>0:
            ans = (1.0*wpts)/pa
        else:
            ans = None
        return wpts, pa, ans

###############
    def getEventCount(self, minyr=1950, maxyr=2014, vbose=0):
        ''' Simple query to find the max event_id for each game_id. 
        This is useful for estimating time stamps.
        '''
        q = 'select game_id, max(event_id) as total_events from events group by game_id'
        dd = self.sqlQueryToArray(q)
        aa = {}
        for d in dd:
            aa[d['game_id']] = d['total_events']
        del dd
        return aa

###############
    def getEventWoba(self, ev, yrid, vbose=0):
        ''' Given an event_cd, and a year, return the wOBA value 
        '''
        outs_cds = [2,3,19]
        ev2w = {}
        ev2w[14] = 'wBB'
        ev2w[15] = 'wBB'
        ev2w[16] = 'wHBP'
        ev2w[20] = 'w1B'
        ev2w[21] = 'w2B'
        ev2w[22] = 'w3B'
        ev2w[23] = 'wHR'

    # hack, set a RBOE same as 1B
        ev2w[18] = 'w1B'

        g = self.guts[str(yrid)]

        if ev in outs_cds:
            return 0.0
        elif ev in ev2w:
            return g[ev2w[ev]]
        else:
            return None


###############
    def computeValueAdded(self, minyr=1950, maxyr=2014, vbose=0):
        ''' Compute the "Value Added" variables. 

        for games table:
        - playoff_flag
        - year_id
        for events table:
        - playoff_flag
        - year_id
        - time_since_1900 : an integer giving the number of seconds since Jan 1, 1900, UTC
        - tto : times through the order
        - sun_alt, sun_az : altitude and azimuth of the sun
        - woba_pts : woba_pts for the event
        - woba_pts_expected : placeholder for woba_pts expected from the matchup of batter vs pitcher. 

'''

        if self.guts is None:
            self.guts = self.readFgGutsJson()
            
        if self.seamheads is None:
            self.seamheads = self.getSeamheadsParksData()

        aptz = {}
        tzw = tzwhere.tzwhere()
        sun = ephem.Sun()

        aa_total_events = self.getEventCount()
        pflags = {}


        q = 'select a.*, b.event_id, b.event_cd, b.bat_id, b.pit_id, b.bat_lineup_id from (select game_id, start_game_tm, minutes_game_ct, park_id, daynight_park_cd, cast(substr(game_id, 4, 4) as unsigned) as year_id, cast(substr(game_id, 8, 2) as unsigned) as mn_id, cast(substr(game_id, 10, 2) as unsigned) as day_id from %s) a inner join %s b on a.game_id=b.game_id where a.year_id>=%d and a.year_id<=%d ' % (self.TABLE_NAMES['TBL_RETRO_GAMES'], self.TABLE_NAMES['TBL_RETRO_EVENTS'], minyr, maxyr)

        if vbose>=1:
            print(q)
        data = self.sqlQueryToArray(q)

        rdata = {}
        rdata['TBL_RETRO_GAMES'] = []
        rdata['TBL_RETRO_EVENTS'] = []
        aTTO = {}
        for d in data:
            mval = {}        
            if vbose>=1:
                print(d)
            gid = d['game_id']
            pid = d['pit_id']
            bl = d['bat_lineup_id']
            ev_id = d['event_id']
            ev_cd = d['event_cd']

            yr = int(gid[3:3+4])
            mn = int(gid[7:7+2])
            dy = int(gid[9:9+2])

            if not yr in pflags:
                pflags[yr] = self.makePlayoffFlag(yr)['gids']

            mval['year_id'] = yr
            mval['playoff_flag'] = pflags[yr][gid]
            
            park = d['park_id']


            lat = float(self.seamheads[park]['Latitude'])
            lon = float(self.seamheads[park]['Longitude'])
            elev = float(self.seamheads[park]['Altitude'])
            if not park in aptz:
                aptz[park] = tzw.tzNameAt(lat, lon)
            tz = aptz[park]
            tzi = pytz.timezone(tz)

            dt = d['minutes_game_ct']
            st = d['start_game_tm']

            shrs = st/100
            smins = st-100*(st/100)
            if shrs<9:
                shrs += 12

            tstart = datetime.datetime(yr, mn, dy, shrs, smins, 0, 0)
            x = datetime.timedelta(0,int(dt*60))
            tend = tstart + x
            dn = (1.0*dt)/aa_total_events[gid]

            t0 = datetime.datetime(1900, 1, 1, 0, 0, 0)
            t0 = tzi.localize(t0).astimezone(pytz.utc)
            
            if dt>0:
                obs = ephem.Observer()
                if vbose>=1:
                    print('dn', dn, 'ev_id', ev_id)
                x = datetime.timedelta(0,np.floor(dn*(ev_id-1)*60)) 
                blah = tzi.localize(tstart + x).astimezone(pytz.utc)
                obs.date = blah
                sun.compute(obs)
                x_1900 = (blah-t0).days*86400 + (blah-t0).seconds

                obs.lat  = lat*self.deg2rad
                obs.long = lon*self.deg2rad
                obs.elev = elev
                                
                mval['sun_alt'] = float(sun.alt)*self.rad2deg
                mval['sun_az'] = float(sun.az)*self.rad2deg
                mval['time_since_1900'] = x_1900

            k = '%s_%s' % (gid, pid)
            if not k in aTTO:
                aTTO[k] = {}
            if not bl in aTTO[k]:
                aTTO[k][bl] = 0
            aTTO[k][bl] += 1
            mval['tto'] = aTTO[k][bl]

            if not gid in self.eventUpdateData:
                self.eventUpdateData[gid] = {}
            self.eventUpdateData[gid][ev_id] = {}
            self.eventUpdateData[gid][ev_id]['tto'] = aTTO[k][bl]

            woba_pts = self.getEventWoba(ev_cd, yr, vbose=vbose)
            if not woba_pts is None:
                self.eventUpdateData[gid][ev_id]['woba_pts'] = woba_pts
                mval['woba_pts'] = woba_pts
            if vbose>=1:
                print(gid, ev_id, ev_cd, yr, aTTO[k][bl],  aa_total_events[gid])
            
            tmp = {}

            mval['game_id'] = gid
            mval['event_id'] = ev_id
            rdata['TBL_RETRO_GAMES'].append({'game_id' : mval['game_id'], 'playoff_flag' : mval['playoff_flag'], 'year_id' : mval['year_id']})
            rdata['TBL_RETRO_EVENTS'].append(mval)

        return rdata

##########################
    def writeSqlFile(self, rdata, ofile, n2print=10000):
        ''' Writes the data in rdata to the file ofile. Prints every 
        n2print-th value to stdout.
        '''
 
        ofp = open(ofile, 'w')

        pks = ['game_id', 'event_id']

        gdone = {}

        for t in list(rdata.keys()):
            tname = self.TABLE_NAMES[t]
            for i, r in enumerate(rdata[t]):
                ts = 'UPDATE %s SET ' % tname
                ks = list(r.keys())
                for pk in pks:
                    try:
                        ks.remove(pk)
                    except ValueError:
                        pass

                for k in ks[0:-1]:
                    ts += ' %s=%s, ' % (k, str(r[k]))

                k = ks[-1]
                ts += ' %s=%s ' % (k, str(r[k]))
            
                if t=='TBL_RETRO_GAMES':
                    ts += ' WHERE GAME_ID=%s' % r['game_id']
                else:
                    ts += ' WHERE GAME_ID=%s AND EVENT_ID=%d' % (r['game_id'], r['event_id'])

                    
                if t=='TBL_RETRO_GAMES':
                    if r['game_id'] in gdone:
                        continue
                    else:
                        ofp.write('%s ; \n' % ts)
                        gdone[r['game_id']] = 1

                else: 
                    ofp.write('%s ; \n' % ts)

                if i%n2print==0:
                    print(t, 'rdata', i, r)
    
        ofp.close()

##########################
if __name__=='__main__':

    minyr = 2004
    maxyr = 2004
    vbose = 0
    n2print = 10000
    for ia, a in enumerate(sys.argv):
        if a=='-minyr':
            minyr = int(sys.argv[ia+1])
        if a=='-maxyr':
            maxyr = int(sys.argv[ia+1])
        if a=='-vbose':
            vbose = int(sys.argv[ia+1])
        if a=='-n2print':
            n2print = int(sys.argv[ia+1])
            
    now = datetime.datetime.now()
    sdate = now.strftime('%Y%m%d%H%M%S%f')
    ofile = 'VARD_%s.sql' % sdate

    print('initializing the retrosheet db connection...')
    rs = retrosheet_sql()

    print('updating schema...')
    rs.updateSchema(vbose=vbose)

    print('computing the Value Added quantities...')
    rdata = rs.computeValueAdded()

    print('writing output to %s...' % ofile)
    rs.writeSqlFile(rdata, ofile, n2print=n2print)

