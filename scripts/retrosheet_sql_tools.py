#!/usr/bin/env python

import sqlalchemy
#import MySQLdb
import ConfigParser
import os, sys
import datetime
import decimal
import numpy as np

class retrosheet_sql:

##########################
    def __init__(self, vbose=0, config=None):

        self.vbose = vbose

        config = ConfigParser.ConfigParser()
        config.readfp(open('config.ini'))
    
        try:
            self.conn = self.dbConnect(config)
        except Exception, e:
            print('Cannot connect to database: %s' % e)
            raise SystemExit

        self.config=config
        self.mysql_db = config.get('database', 'database')

        self.cursor = self.conn.connection.cursor()
#        self.cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)

        self.TABLE_NAMES = {}

        self.TABLE_NAMES['TBL_RETRO_PARKCODE'] = '%s.parkcode' % self.mysql_db
        self.TABLE_NAMES['TBL_RETRO_EVENTS'] = '%s.events' % self.mysql_db
        self.TABLE_NAMES['TBL_RETRO_GAMES'] = '%s.games' % self.mysql_db
        self.TABLE_NAMES['TBL_RETRO_LAST_DAY'] = '%s.last_day' % self.mysql_db
        self.TABLE_NAMES['TBL_FGGUTS'] = 'mlb.fgGuts'

        self.nbases = 3
        self.nouts = 3
        self.state2int = {}
        self.int2state = {}
        self.initEnumerateStates()

        self.stateToAbv = {
            'Alabama': 'AL',
            'Alaska': 'AK',
            'Arizona': 'AZ',
            'Arkansas': 'AR',
            'California': 'CA',
            'Colorado': 'CO',
            'Connecticut': 'CT',
            'Delaware': 'DE',
            'Florida': 'FL',
            'Georgia': 'GA',
            'Hawaii': 'HI',
            'Idaho': 'ID',
            'Illinois': 'IL',
            'Indiana': 'IN',
            'Iowa': 'IA',
            'Kansas': 'KS',
            'Kentucky': 'KY',
            'Louisiana': 'LA',
            'Maine': 'ME',
            'Maryland': 'MD',
            'Massachusetts': 'MA',
            'Michigan': 'MI',
            'Minnesota': 'MN',
            'Mississippi': 'MS',
            'Missouri': 'MO',
            'Montana': 'MT',
            'Nebraska': 'NE',
            'Nevada': 'NV',
            'New Hampshire': 'NH',
            'New Jersey': 'NJ',
            'New Mexico': 'NM',
            'New York': 'NY',
            'North Carolina': 'NC',
            'North Dakota': 'ND',
            'Ohio': 'OH',
            'Oklahoma': 'OK',
            'Oregon': 'OR',
            'Pennsylvania': 'PA',
            'Rhode Island': 'RI',
            'South Carolina': 'SC',
            'South Dakota': 'SD',
            'Tennessee': 'TN',
            'Texas': 'TX',
            'Utah': 'UT',
            'Vermont': 'VT',
            'Virginia': 'VA',
            'Washington': 'WA',
            'West Virginia': 'WV',
            'Wisconsin': 'WI',
            'Wyoming': 'WY',
            }

        self.abvToState = {}
        for k, v in self.stateToAbv.items():
            self.abvToState[v] = k


##########################
    def __str__(self):
        print self.config
        return ''

###############
    def dbConnect(self, config):
        try:
            ENGINE = config.get('database', 'engine')
            DATABASE = config.get('database', 'database')
            
            HOST = None if not config.has_option('database', 'host') else config.get('database', 'host')
            USER = None if not config.has_option('database', 'user') else config.get('database', 'user')
            SCHEMA = None if not config.has_option('database', 'schema') else config.get('database', 'schema')
            PASSWORD = None if not config.has_option('database', 'password') else config.get('database', 'password')
        except ConfigParser.NoOptionError:
            print 'Need to define engine, user, password, host, and database parameters'
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
    def initEnumerateStates(self):
        nb = self.nbases
        nstate = 0
        for i in range(2**(self.nbases)):
            s = bin(i).split('b')[1]
            for j in range(self.nbases-len(s)+1-1):
                s = '0'+s
            for o in range(self.nouts):
                k = s + '_%02d' % o
                if self.vbose>=1:
                    print nstate, i, s, k
                self.state2int[k] = nstate
                self.int2state[nstate] = k
                nstate += 1

        allStates = self.state2int.keys()
        allStates.sort()
        self.allStates = allStates


###############
    def processParkCover(self, ifile):
        ifp = open(ifile,'r')
        line = ifp.read()
        lines = line.split('\r')
        
        for il, l in enumerate(lines):
            st = l.split(',')

            if len(st)<=1:
                continue

            if il==0:
                ks = st[:]
                continue
            tmp = {}
            for i, k in enumerate(ks):
                print k, st[i] 
                tmp[k] = st[i]
            q = 'update %s set cover=\'%s\' where parkid=\'%s\' ' % (self.TBL_RETRO_PARKCODE, tmp['Cover'], tmp['parkID'])

        
            print q + ';'
            self.cursor.execute(q)


###############
    def processParkOrientations(self, ifile):
        ifp = open(ifile,'r')
        line = ifp.read()
        lines = line.split('\n')
        
        for il, l in enumerate(lines):
            st = l.split(',')

            if len(st)<=1:
                continue

            if il==0:
                ks = st[:]
                continue
            tmp = {}
            for i, k in enumerate(ks):
                print k, st[i] 
                tmp[k] = st[i]
            q = 'update %s set orientation=%.2f where parkid=\'%s\' ' % (self.TBL_RETRO_PARKCODE, float(tmp['orientation']), tmp['PARKID'])

        
            print q + ';'
            self.cursor.execute(q)


###############
    def processSeamheadsParks(self, ifile):
        ifp = open(ifile,'r')
        line = ifp.read()
        lines = line.split('\r')
        
        for il, l in enumerate(lines):
            st = l.split(',')
            if il==0:
                ks = st[:]
                continue
            tmp = {}
            for i, k in enumerate(ks):
                print k, st[i] 
                tmp[k] = st[i]
            q = 'update %s set latitude=%.6f, longitude=%.6f, altitude=%.2f where parkid=\'%s\' ' % (self.TBL_RETRO_PARKCODE, float(tmp['Latitude']), float(tmp['Longitude']), float(tmp['Altitude']), tmp['PARKID'])

        
            print q + ';'
            self.cursor.execute(q)

###############
    def sqlQueryToArray(self, q, vbose=0):
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        if len(rows)==0:
            return []

        row = rows[0]

        keys = []
        for k in row:
            if vbose>=1:
                print k
            keys.append(k)

        arr = []
        for k in keys:
            x = row[k]
#            print k, x, type(x)
            if type(x)==type(1):
                s = (k, 'i4')
            elif type(x)==type(1L):
                s = (k, 'i8')
            elif type(x)==type(decimal.Decimal(1)):
                s = (k, 'f8')
            elif type(x)==type(1.0):
                s = (k, 'f8')
            else:
                s = (k, 'S256')
            arr.append(s)
#        print arr
        dt = np.dtype(arr)
        data = []
        for row in rows:
            tmp = []
#            print '********************'
            for k in keys:
                x = row[k]
#                print k, row[k]
                tmp.append(x)
            data.append(tuple(tmp))
#        print data
        return np.array(data, dtype=dt)

###############
    def csvToArray(self, csvfile, skeys=[], ikeys=[], fkeys=[], delimiter=',', vbose=0):

        ifp = open(csvfile,'r')
        hd = ifp.next()
        ifp.close()
        keys = hd.split('%s' % delimiter)
        arr = []
        for sk in keys:
            k = sk.strip()
            if k in ikeys:
                s = (k, 'i4')
            elif k in fkeys:
                s = (k, 'f8')
            elif k in skeys:
                s = (k, 'S256')
            else:
                s = (k, 'f8')

            if vbose>=1:
                print 'k', k, 's', s

            arr.append(s)
#        print arr
        try:
            dt = np.dtype(arr)
        except ValueError:
            tmp = []
            for a in arr:
                tmp.append(a[0])
            tmp.sort()
            
            
            print 'dt arr',arr
            print 'dt arr', tmp
            print len(tmp), len(np.unique(tmp))
            print 'dt arr u', np.unique(tmp)
            sys.exit()

        if vbose>=1:
            print dt
        return np.genfromtxt(csvfile, skip_header=1, delimiter=delimiter, dtype=dt)


##########################
    def doStadiaGeocoding(self):
        import pygeocoder
        geo = pygeocoder.Geocoder()
        q = 'select * from %s ' % self.TBL_RETRO_PARKCODE
        data = self.sqlQueryToArray(q)
        for d in data:
            print '*********'
            ks = [d['name'] + ' ' + d['city'] + ' ' + d['state'], d['city'] + ' ' + d['state']]
            for k in ks:
                try:
                    ans = geo.geocode(k)
                    print '---', k, d, ans.coordinates
                except pygeocoder.GeocoderError as x:
                    print 'erro:', x
                    print 'xxx', k, d
#                    sys.exit()

##########################
    def computeWobaPlayer(self, plid=None, yrid=None, 
                          lbat=None, 
                          ibb=False, 
                          lpost=False, 
                          lOBP=False, 
                          lGrouped = False,
                          vbose=False):

        if lbat:
            ptype = 'bat_id'
        else:
            ptype = 'pit_id'

        if lGrouped:
            q = ' select event_cd, event_tx, count(*) n from %s where year_id=%d and %s=\'%s\' ' % (self.TBL_RETRO_EVENTS, yrid, ptype, plid)
        else:
            q = ' select event_cd, event_tx from %s where year_id=%d and %s=\'%s\' ' % (self.TBL_RETRO_EVENTS, yrid, ptype, plid)

        if not lpost:
            q += ' and playoff_flag=0 '

        if lGrouped:
            q += ' group by %s ' % 'event_cd'

        if vbose:
            print q

        self.cursor.execute(q)
        rows = self.cursor.fetchall()

        if lGrouped:
            data = {}
        else:
            data = []

        for row in rows:
            if vbose:
                print row
            if lGrouped:
                data[int(row['event_cd'])] = int(row['n'])
            else:
                data.append(int(row['event_cd']))


        ans = self.computeWoba(data, yrid=yrid, ibb=ibb, lOBP=lOBP, lGrouped=lGrouped, vbose=vbose)
        return ans

##########################
    def doMakePlayoffFlag(self, minyr, maxyr, vbose=False):
        for i in range(minyr, maxyr+1):
            ans = self.makePlayoffFlag(i, vbose=vbose)
#            print ans
            for k in ans['gids']:
                q = ' update %s set PLAYOFF_FLAG=%d where GAME_ID=\'%s\' ' % (self.TBL_RETRO_GAMES, ans['gids'][k], k)
                print q
                self.cursor.execute(q)
                self.conn.commit()

                q = ' update %s set PLAYOFF_FLAG=%d where GAME_ID=\'%s\' ' % (self.TBL_RETRO_EVENTS, ans['gids'][k], k)
                print q
                self.cursor.execute(q)
                self.conn.commit()

            print ans['newtt'].year, ans['newtt'].month, ans['newtt'].day
            q = ' select count(*) n from %s where YEAR_ID=%d ' % (self.TBL_RETRO_LAST_DAY, ans['newtt'].year)
            print q
            self.cursor.execute(q)
            row = self.cursor.fetchone()
            if row['n']==0:
                q = ' insert into %s set YEAR_ID=%d, MN_ID=%d, DAY_ID=%d ' % (self.TBL_RETRO_LAST_DAY, ans['newtt'].year, ans['newtt'].month, ans['newtt'].day)
                print q
                self.cursor.execute(q)
                self.conn.commit()

##########################
    def makePlayoffFlag(self, yrid, vbose=False):
#        datetime.datetime.
        data = {}

        q = 'select a.* from (select game_id, home_team_id, away_team_id, cast(substr(game_id,4,4) as unsigned) as year_id, cast(substr(game_id,8,2) as unsigned) as mn_id, cast(substr(game_id,10,2) as unsigned) as day_id, game_ct from %s group by game_id ) a where year_id=%d order by year_id, mn_id, day_id, game_ct ' % (self.TBL_RETRO_GAMES, yrid)

        tmp = []
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
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

        for k in data:
            tmp.append(data[k]['ngame'])
        tmp = np.array(tmp)
        mm = int(np.median(tmp))

        print '*************'
        print yrid, mm

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
            if vbose:
                print k, data[k]['gid'][-1], ttI, \
                    datetime.datetime.fromordinal(ttI), \
                    newtt.year, newtt.month, newtt.day

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


        ndata['mm'] = mm
        print yr, max_time
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

        if yrid is None:
            q = 'select * from %s where yearid=2012' % self.TBL_FGGUTS
        else:
            q = 'select * from %s where yearid=%d' % (self.TBL_FGGUTS, yrid)

        self.cursor.execute(q)
        row = self.cursor.fetchone()
        
        wpts = 0.0
        pa = 0

        ww = {}
        for k in row.keys():
            if lOBP:
                ww[k] = 1.0
            else:
                ww[k] = row[k]
        if vbose:
            print 'wOBA (OBP) weights: ' , ww

        for ev in indata:
            if lGrouped:
                val = indata[ev]
            else:
                val = 1.0

            if vbose:
                print ev, val
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

##########################
    def makeCareer(self):
        bdata = {}
        pdata = {}

#####
        tbl = 'mlb.Batting'

        q = 'drop table if exists blahB '
        self.cursor.execute(q)

        q = 'create table blahB ' \
            'select playerID, count(*) as yrs from ' \
            '(select playerID ' \
            'from %s ' \
            'group by playerID, yearID) a ' \
            'group by playerID ' \
            % tbl

        print q
        self.cursor.execute(q)
        
        q = 'select * from blahB '
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        for row in rows:
            print row

        q = 'create index ipl on blahB(playerID)' ;
        print q
        self.cursor.execute(q)

        q = 'drop table if exists BattingCareer '
        self.cursor.execute(q)

        q = 'create table BattingCareer select ' \
            'a.playerId, ' \
            'min(yearID) as minYr,' \
            'max(yearID) as maxYr,' \
            'b.yrs, ' \
            'sum(g) as g, ' \
            'sum(g_batting) as g_batting, ' \
            'sum(ab) as ab, ' \
            'sum(r) as r, ' \
            'sum(h) as h, ' \
            'sum(2b) as 2b,' \
            'sum(3b) as 3b,' \
            'sum(hr) as hr,' \
            'sum(rbi) as rbi,' \
            'sum(sb) as sb,' \
            'sum(cs) as cs,' \
            'sum(bb) as bb,' \
            'sum(so) as so,' \
            'sum(ibb) as ibb,' \
            'sum(hbp) as hbp,' \
            'sum(sh) as sh,' \
            'sum(sf) as sf,' \
            'sum(gidp) as gidp ' \
            'from %s a, %s b ' \
            'where a.playerID=b.playerID ' \
            'group by playerID ' % (tbl, 'blahB')
        print q
        self.cursor.execute(q)

#####
        tbl = 'mlb.Pitching'

        q = 'drop table if exists blahP '
        self.cursor.execute(q)

        q = 'create table blahP ' \
            'select playerID, count(*) as yrs from ' \
            '(select playerID ' \
            'from %s ' \
            'group by playerID, yearID) a ' \
            'group by playerID ' \
            % tbl

        print q

        self.cursor.execute(q)
        
        q = 'select * from blahP '
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        for row in rows:
            print row

        q = 'create index ipl on blahP(playerID)' ;
        print q
        self.cursor.execute(q)

        q = 'select playerID, yearID, stint, ' \
            'h, bfp, bb, hbp ' \
            'from %s ' \
            'where bfp is not null ' % tbl
        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        for row in rows:
            print row
            q = 'select * from %s where ' \
                'playerID=\'%s\' and yearID=%d and stint=%d ' \
                % (tbl, row['playerID'], row['yearID'], row['stint'])
            print q

            if row['hbp'] is None:
                print 'none '
                hbp = 0
#                sys.exit()
            else:
                hbp = row['hbp']
            
            myab = row['bfp']-row['bb']-hbp
            if myab>0:
                mybaopp = row['h']/(1.0*myab)
            else:
                mybaopp = -1

            if myab==0:
                q = 'update %s set myab=%d, mybaopp=null where ' \
                    'playerID=\'%s\' and yearID=%d and stint=%d ' \
                    % (tbl, 
                       myab, 
                       row['playerID'], row['yearID'], row['stint'])
            else:
                q = 'update %s set myab=%d, mybaopp=%.3f where ' \
                    'playerID=\'%s\' and yearID=%d and stint=%d ' \
                    % (tbl, 
                       myab, mybaopp, 
                       row['playerID'], row['yearID'], row['stint'])
            print q
            self.cursor.execute(q)
#        sys.exit()

        q = 'drop table if exists PitchingCareer '
        self.cursor.execute(q)

        q = 'create table PitchingCareer select ' \
            'a.playerId, ' \
            'min(yearID) as minYr,' \
            'max(yearID) as maxYr,' \
            'b.yrs, ' \
            'sum(w) as w, ' \
            'sum(l) as l, ' \
            'sum(g) as g, ' \
            'sum(gs) as gs,' \
            'sum(cg) as cg,' \
            'sum(sho) as sho,' \
            'sum(sv) as sv,' \
            'sum(IPouts) as IPouts,' \
            'sum(h) as h,' \
            'sum(er) as er,' \
            'sum(hr) as hr,' \
            'sum(bb) as bb,' \
            'sum(so) as so,' \
            'sum(h)/sum(h/baopp) as baopp,' \
            'sum(h)/sum(myab) as mybaopp,' \
            '27.0*sum(er)/sum(ipouts) as era,' \
            'sum(ibb) as ibb,' \
            'sum(wp) as wp,' \
            'sum(hbp) as hbp,' \
            'sum(bk) as bk,' \
            'sum(bfp) as bfp,' \
            'sum(myab) as myab,' \
            'sum(gf) as gf,' \
            'sum(r) as r ' \
            'from %s a, %s b ' \
            'where a.playerID=b.playerID ' \
            'group by playerID ' % (tbl, 'blahP')
        print q
        self.cursor.execute(q)

##########################
    def getData(self, type, criteria=None, vbose=False):
        ''' type is one of:
        Batting
        BattingCareer
        Pitching
        PitchingCareer
        WAR_bat
        WAR_pitch
        games
        teams
        WAR_bat_sum
        fgGuts
        parkcode
        '''

        print type
        data = []
        if type=='Batting':
            strKeys = ['playerID', 'teamID', 'lgID']
            intKeys = ['yearID', 'stint', 'g', 'g_batting', 
                       'ab', 'r', 'h', '2b', '3b', 'hr', 'rbi', 
                       'sb', 'cs', 'bb', 'so', 'ibb', 'hbp', 
                       'sh', 'sf', 'gidp', 'pa']
            floatKeys = []
            tbl = 'mlb.Batting'
        elif type=='BattingCareer':
            strKeys = ['playerID']
            intKeys = ['minYr', 'maxYr', 'yrs', 'g', 'g_batting', 
                       'ab', 'r', 'h', '2b', '3b', 'hr', 'rbi', 
                       'sb', 'cs', 'bb', 'so', 'ibb', 'hbp', 
                       'sh', 'sf', 'gidp', 'pa']
            floatKeys = []
            tbl = 'mlb.BattingCareer'
        elif type=='Pitching':
            strKeys = ['playerID', 'teamID', 'lgID']
            intKeys = ['yearID', 'stint', 'w', 'l', 'g'
                       ,'gs', 'cg', 'sho', 'sv', 'ipouts'
                       ,'h', 'er', 'hr', 'bb', 'so'
                       ,'ibb', 'wp', 'hbp', 'bk'
                       ,'bfp', 'myab', 'gf', 'r'
                       ]
            floatKeys = ['baopp', 'mybaopp', 'era']
            tbl = 'mlb.Pitching'
        elif type=='PitchingCareer':
            strKeys = ['playerID']
            intKeys = ['minYr', 'maxYr', 'yrs', 'w', 'l', 'g'
                       ,'gs', 'cg', 'sho', 'sv', 'ipouts'
                       ,'h', 'er', 'hr', 'bb', 'so'
                       ,'ibb', 'wp', 'hbp', 'bk'
                       ,'bfp', 'myab', 'gf', 'r'
                       ]
            floatKeys = ['baopp', 'mybaopp', 'era']
            tbl = 'mlb.PitchingCareer'
        elif type=='games':
            strKeys = ['GAME_ID', 'PARK_ID'
                       ,'AWAY_TEAM_ID', 'HOME_TEAM_ID'
                       ,'AWAY_START_PIT_ID', 'HOME_START_PIT_ID'

                       ]

            intKeys = ['GAME_DT' 
                       ,'TEMP_PARK_CT'
                       ,'AWAY_SCORE_CT', 'HOME_SCORE_CT'
                       ,'PLAYOFF_FLAG'

                       ]
            floatKeys = []
            tbl = 'retrosheet.games'
        elif type=='teams':
            strKeys = ['lgID', 'teamID',
                       'franchID', 'divID', 'name',
                       'park', 
                       'teamIDbr', 'teamIDlahman45', 'teamIDretro',
                       'DivWin', 'LgWin', 'WSWin'
                       ]

            intKeys = ['yearID', 'Rank', 'G', 'W', 'L',
                       'R', 'AB', 'H', '2B', '3B', 'HR', 
                       'BB', 'SO', 'SB', 'CS', 'HBP', 
                       'SF', 'RA', 'ER', 'CG', 'SHO', 'SV', 'IPouts',
                       'HA', 'HRA', 'BBA', 'SOA', 'E', 'DP', 'FP', 
                       'attendance', 'BPF'
                       ]
            floatKeys = ['ERA']
            tbl = 'mlb.teams'
        elif type=='WAR_bat':
            strKeys = ['name_common', 'player_ID', 
                       'team_ID', 'lg_ID', 'pitcher']
            intKeys = ['stint_ID','age', 'year_ID', 'PA', 'G']

            floatKeys = ['Inn' 
                         ,'runs_bat'
                         , 'runs_br' 
                         , 'runs_dp' 
                         , 'runs_field'
                         , 'runs_infield'
                         , 'runs_outfield'
                         , 'runs_catcher' 
                         , 'runs_good_plays'
                         , 'runs_defense'   
                         , 'runs_position'  
                         , 'runs_position_p'
                         , 'runs_replacement'
                         , 'runs_above_rep'  
                         , 'runs_above_avg'  , 
                         'runs_above_avg_off', 
                         'runs_above_avg_def', 'WAA', 'WAA_off', 
                         'WAA_def', 'WAR', 'WAR_def', 'WAR_off', 
                         'WAR_rep', 'salary', 'teamRpG', 
                         'oppRpG', 'oppRpPA_rep', 'oppRpG_rep', 
                         'pyth_exponent', 'pyth_exponent_rep', 
                         'waa_win_perc', 
                         'waa_win_perc_off', 
                         'waa_win_perc_def', 'waa_win_perc_rep'
                         ]

            tbl = 'mlb.brWAR_bat'
        elif type=='WAR_pitch':
            strKeys = ['name_common', 'player_ID', 
                       'team_ID', 'lg_ID']
            intKeys = ['stint_ID','age','year_ID', 'G', 'GS',
                       'IPouts','IPouts_start','IPouts_relief']
            floatKeys = ['RA'
                         ,'xRA'
                         ,'xRA_sprp_adj'
                         ,'xRA_def_pitcher'
                         ,'PPF'
                         ,'PPF_custom'
                         ,'xRA_final'
                         ,'BIP'
                         ,'BIP_perc'
                         ,'RS_def_total'
                         ,'runs_above_avg'
                         ,'runs_above_avg_adj'
                         ,'runs_above_rep'
                         ,'RpO_replacement'
                         ,'GR_leverage_index_avg'
                         ,'WAR'
                         ,'salary'
                         ,'teamRpG'
                         ,'oppRpG'
                         ,'pyth_exponent'
                         ,'waa_win_perc'
                         ,'WAA'
                         ,'WAA_adj'
                         ,'oppRpG_rep'
                         ,'pyth_exponent_rep'
                         ,'waa_win_perc_rep'
                         ,'WAR_rep']
            tbl = 'mlb.brWAR_pitch'
        elif type=='fgGuts':
            strKeys = []
            intKeys = ['yearid']
            floatKeys = ['wOBA', 'wOBAscale', 'wBB', 'wHBP'
                         ,'w1B', 'w2B', 'w3B', 'wHR'
                         ,'runsSB', 'runCS'
                         , 'r_pa', 'r_w', 'cFIP'
                         ]
            tbl = self.TBL_FGGUTS
        elif type=='parkcode':
            strKeys = ['parkid']
            intKeys = ['altitude']
            floatKeys = ['latitude', 'longitude']

            tbl = self.TBL_RETRO_PARKCODE
        else:
            raise Exception

        keys = strKeys + intKeys + floatKeys
        q = 'select '
        
        for k in keys[0:-1]:
            q += ' %s , ' % k
        k = keys[-1]
        q += ' %s  ' % k
        q += ' FROM %s ' % tbl 

        if not criteria is None:
            q += ' where ' + criteria

        print q

        tmp = []
        for k in strKeys:
            this = (k, 'S64')
            tmp.append(this)
        for k in intKeys:
            this = (k, 'i4')
            tmp.append(this)
        for k in floatKeys:
            this = (k, 'f4')
            tmp.append(this)
        print 'dtype= ', tmp
        dt = np.dtype(tmp)

        self.cursor.execute(q)
        rows = self.cursor.fetchall()
        for row in rows:
            tmp = []
            for k in keys:
                x = row[k]
                if x is None:
                    x = -1
                tmp.append(x)
            data.append(tuple(tmp))
#        print data
        data = np.array(data, dtype=dt)
        return data

##########################
if __name__=='__main__':
    m = mlb()
    m.makeCareer()
