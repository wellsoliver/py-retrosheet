drop table if exists events;
drop table if exists games;
drop table if exists rosters;
drop table if exists teams;
drop table if exists parkcodes;
drop table if exists lkup_cd_bases;
drop table if exists lkup_cd_battedball;
drop table if exists lkup_cd_event;
drop table if exists lkup_cd_fld;
drop table if exists lkup_cd_h;
drop table if exists lkup_cd_hand;
drop table if exists lkup_cd_park_daynight;
drop table if exists lkup_cd_park_field;
drop table if exists lkup_cd_park_precip;
drop table if exists lkup_cd_park_sky;
drop table if exists lkup_cd_park_wind_direction;
drop table if exists lkup_cd_recorder_method;
drop table if exists lkup_cd_recorder_pitches;
drop table if exists lkup_id_base;
drop table if exists lkup_id_home;
drop table if exists lkup_id_last;

CREATE TABLE games (
	game_id text primary key
	,game_dt integer
	,game_ct integer
	,game_dy text
	,start_game_tm integer
	,dh_fl text
	,daynight_park_cd text
	,away_team_id text
	,home_team_id text
	,park_id text
	,away_start_pit_id text
	,home_start_pit_id text
	,base4_ump_id text
	,base1_ump_id text
	,base2_ump_id text
	,base3_ump_id text
	,lf_ump_id text
	,rf_ump_id text
	,attend_park_ct integer
	,scorer_record_id text
	,translator_record_id text
	,inputter_record_id text
	,input_record_ts text
	,edit_record_ts text
	,method_record_cd text
	,pitches_record_cd text
	,temp_park_ct integer
	,wind_direction_park_cd integer
	,wind_speed_park_ct integer
	,field_park_cd integer
	,precip_park_cd integer
	,sky_park_cd integer
	,minutes_game_ct integer
	,inn_ct integer
	,away_score_ct integer
	,home_score_ct integer
	,away_hits_ct integer
	,home_hits_ct integer
	,away_err_ct integer
	,home_err_ct integer
	,away_lob_ct integer
	,home_lob_ct integer
	,win_pit_id text
	,lose_pit_id text
	,save_pit_id text
	,gwrbi_bat_id text
	,away_lineup1_bat_id text
	,away_lineup1_fld_cd integer
	,away_lineup2_bat_id text
	,away_lineup2_fld_cd integer
	,away_lineup3_bat_id text
	,away_lineup3_fld_cd integer
	,away_lineup4_bat_id text
	,away_lineup4_fld_cd integer
	,away_lineup5_bat_id text
	,away_lineup5_fld_cd integer
	,away_lineup6_bat_id text
	,away_lineup6_fld_cd integer
	,away_lineup7_bat_id text
	,away_lineup7_fld_cd integer
	,away_lineup8_bat_id text
	,away_lineup8_fld_cd integer
	,away_lineup9_bat_id text
	,away_lineup9_fld_cd integer
	,home_lineup1_bat_id text
	,home_lineup1_fld_cd integer
	,home_lineup2_bat_id text
	,home_lineup2_fld_cd integer
	,home_lineup3_bat_id text
	,home_lineup3_fld_cd integer
	,home_lineup4_bat_id text
	,home_lineup4_fld_cd integer
	,home_lineup5_bat_id text
	,home_lineup5_fld_cd integer
	,home_lineup6_bat_id text
	,home_lineup6_fld_cd integer
	,home_lineup7_bat_id text
	,home_lineup7_fld_cd integer
	,home_lineup8_bat_id text
	,home_lineup8_fld_cd integer
	,home_lineup9_bat_id text
	,home_lineup9_fld_cd integer
	,away_finish_pit_id text
	,home_finish_pit_id text
);

CREATE TABLE events (
    game_id text not null,
    away_team_id text,
    inn_ct integer,
    bat_home_id text,
    outs_ct integer,
    balls_ct integer,
    strikes_ct integer,
    pitch_seq_tx text,
    away_score_ct integer,
    home_score_ct integer,
    bat_id text,
    bat_hand_cd text,
    resp_bat_id text,
    resp_bat_hand_cd text,
    pit_id text,
    pit_hand_cd text,
    resp_pit_id text,
    resp_pit_hand_cd text,
    pos2_fld_id text,
    pos3_fld_id text,
    pos4_fld_id text,
    pos5_fld_id text,
    pos6_fld_id text,
    pos7_fld_id text,
    pos8_fld_id text,
    pos9_fld_id text,
    base1_run_id text,
    base2_run_id text,
    base3_run_id text,
    event_tx text,
    leadoff_fl text,
    ph_fl text,
    bat_fld_cd text,
    bat_lineup_id text,
    event_cd text,
    bat_event_fl text,
    ab_fl text,
    h_cd text,
    sh_fl text,
    sf_fl text,
    event_outs_ct integer,
    dp_fl text,
    tp_fl text,
    rbi_ct integer,
    wp_fl text,
    pb_fl text,
    fld_cd text,
    battedball_cd text,
    bunt_fl text,
    foul_fl text,
    battedball_loc_tx text,
    err_ct integer,
    err1_fld_cd text,
    err1_cd text,
    err2_fld_cd text,
    err2_cd text,
    err3_fld_cd text,
    err3_cd text,
    bat_dest_id text,
    run1_dest_id text,
    run2_dest_id text,
    run3_dest_id text,
    bat_play_tx text,
    run1_play_tx text,
    run2_play_tx text,
    run3_play_tx text,
    run1_sb_fl text,
    run2_sb_fl text,
    run3_sb_fl text,
    run1_cs_fl text,
    run2_cs_fl text,
    run3_cs_fl text,
    run1_pk_fl text,
    run2_pk_fl text,
    run3_pk_fl text,
    run1_resp_pit_id text,
    run2_resp_pit_id text,
    run3_resp_pit_id text,
    game_new_fl text,
    game_end_fl text,
    pr_run1_fl text,
    pr_run2_fl text,
    pr_run3_fl text,
    removed_for_pr_run1_id text,
    removed_for_pr_run2_id text,
    removed_for_pr_run3_id text,
    removed_for_ph_bat_id text,
    removed_for_ph_bat_fld_cd text,
    po1_fld_cd text,
    po2_fld_cd text,
    po3_fld_cd text,
    ass1_fld_cd text,
    ass2_fld_cd text,
    ass3_fld_cd text,
    ass4_fld_cd text,
    ass5_fld_cd text,
    event_id text,
    home_team_id text,
    bat_team_id text,
    fld_team_id text,
    bat_last_id text,
    inn_new_fl text,
    inn_end_fl text,
    start_bat_score_ct integer,
    start_fld_score_ct integer,
    inn_runs_ct integer,
    game_pa_ct integer,
    inn_pa_ct integer,
    pa_new_fl text,
    pa_trunc_fl text,
    start_bases_cd text,
    end_bases_cd text,
    bat_start_fl text,
    resp_bat_start_fl text,
    bat_on_deck_id text,
    bat_in_hold_id text,
    pit_start_fl text,
    resp_pit_start_fl text,
    run1_fld_cd text,
    run1_lineup_cd text,
    run1_origin_event_id text,
    run2_fld_cd text,
    run2_lineup_cd text,
    run2_origin_event_id text,
    run3_fld_cd text,
    run3_lineup_cd text,
    run3_origin_event_id text,
    run1_resp_cat_id text,
    run2_resp_cat_id text,
    run3_resp_cat_id text,
    pa_ball_ct integer,
    pa_called_ball_ct integer,
    pa_intent_ball_ct integer,
    pa_pitchout_ball_ct integer,
    pa_hitbatter_ball_ct integer,
    pa_other_ball_ct integer,
    pa_strike_ct integer,
    pa_called_strike_ct integer,
    pa_swingmiss_strike_ct integer,
    pa_foul_strike_ct integer,
    pa_inplay_strike_ct integer,
    pa_other_strike_ct integer,
    event_runs_ct integer,
    fld_id text,
    base2_force_fl text,
    base3_force_fl text,
    base4_force_fl text,
    bat_safe_err_fl text,
    bat_fate_id text,
    run1_fate_id text,
    run2_fate_id text,
    run3_fate_id text,
    fate_runs_ct integer,
    ass6_fld_cd text,
    ass7_fld_cd text,
    ass8_fld_cd text,
    ass9_fld_cd text,
    ass10_fld_cd text,
    unknown_out_exc_fl text,
    uncertain_play_exc_fl text,
    primary key (game_id, event_id)
);

CREATE TABLE teams (
	 team_id text primary key
	,lg_id text
	,loc_team_tx text
	,name_team_tx text
);

CREATE TABLE rosters (
	 year integer
	,player_id text
	,last_name_tx text
	,first_name_tx text
	,bat_hand_cd text
	,pit_hand_cd text
	,team_tx text references teams(team_id)
	,pos_tx text
	,primary key (year, player_id, team_tx)
);

CREATE TABLE parkcodes (
	park_id text not null primary key,
	name text default null,
	aka text default null,
	city text default null,
	state text default null,
	start text default null,
	"end" text default null,
	league text default null,
	notes text default null
);

create table lkup_cd_bases		(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_battedball		(value_cd text,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_event		(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_fld		(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_h			(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_hand		(value_cd text,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_park_daynight	(value_cd text,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_park_field		(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_park_precip	(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_park_sky		(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_park_wind_direction(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_recorder_method	(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_cd_recorder_pitches	(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_id_base		(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_id_home		(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );
create table lkup_id_last		(value_cd integer,	shortname_tx text, longname_tx text, description_tx text );

INSERT INTO lkup_cd_bases ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
0, '___', 'Empty', NULL
); 
INSERT INTO lkup_cd_bases ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
1, '1__', '1B only', NULL
); 
INSERT INTO lkup_cd_bases ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
2, '_2_', '2B only', NULL
); 
INSERT INTO lkup_cd_bases ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
3, '12_', '1B & 2B', NULL
); 
INSERT INTO lkup_cd_bases ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
4, '__3', '3B only', NULL
); 
INSERT INTO lkup_cd_bases ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
5, '1_3', '1B & 3B', NULL
); 
INSERT INTO lkup_cd_bases ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
6, '_23', '2B & 3B', NULL
); 
INSERT INTO lkup_cd_bases ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
7, '123', 'Loaded', NULL
); 

INSERT INTO lkup_cd_battedball ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
'F', 'FB', 'Fly Ball', NULL
); 
INSERT INTO lkup_cd_battedball ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
'G', 'GB', 'Ground Ball', NULL
); 
INSERT INTO lkup_cd_battedball ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
'L', 'LD', 'Line Drive', NULL
); 
INSERT INTO lkup_cd_battedball ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
'P', 'PU', 'Pop Up', NULL
); 

INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
2, 'Out', 'Generic Out', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
3, 'K', 'Strikeout', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
4, 'SB', 'Stolen Base', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
5, 'DI', 'Defensive Indifferen', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
6, 'CS', 'Caught Stealing', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
8, 'PK', 'Pickoff', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
9, 'WP', 'Wild Pitch', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
10, 'PB', 'Passed Ball', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
11, 'BK', 'Balk', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
12, 'OA', 'Other Advance', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
13, 'FE', 'Foul Error', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
14, 'NIBB', 'Nonintentional Walk', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
15, 'IBB', 'Intentional Walk', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
16, 'HBP', 'Hit By Pitch', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
17, 'XI', 'Interference', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
18, 'ROE', 'Error', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
19, 'FC', 'Fielder Choice', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
20, '1B', 'Single', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
21, '2B', 'Double', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
22, '3B', 'Triple', NULL
); 
INSERT INTO lkup_cd_event ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
23, 'HR', 'Homerun', NULL
); 

INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
1, 'P', 'Pitcher', NULL
); 
INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
2, 'C', 'Catcher', NULL
); 
INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
3, '1B', 'Firstbase', NULL
); 
INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
4, '2B', 'Secondbase', NULL
); 
INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
5, '3B', 'Thirdbase', NULL
); 
INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
6, 'SS', 'Shortstop', NULL
); 
INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
7, 'LF', 'Leftfield', NULL
); 
INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
8, 'CF', 'Centerfield', NULL
); 
INSERT INTO lkup_cd_fld ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
9, 'RF', 'Rightfield', NULL
); 

INSERT INTO lkup_cd_h ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
1, '1B', 'Single', NULL
); 
INSERT INTO lkup_cd_h ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
2, '2B', 'Double', NULL
); 
INSERT INTO lkup_cd_h ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
3, '3B', 'Triple', NULL
); 
INSERT INTO lkup_cd_h ( value_cd, shortname_tx, longname_tx, description_tx ) VALUES ( 
4, 'HR', 'Homerun', NULL
); 

INSERT INTO LKUP_CD_HAND ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
'?', NULL, 'Unknown', NULL
); 
INSERT INTO LKUP_CD_HAND ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
'F', NULL, 'Unknown', NULL
); 
INSERT INTO LKUP_CD_HAND ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
'L', 'LH', 'Lefthanded', NULL
); 
INSERT INTO LKUP_CD_HAND ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
'R', 'RH', 'Righthanded', NULL
); 

INSERT INTO LKUP_CD_PARK_DAYNIGHT ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
'D', 'D', 'Day', NULL
); 
INSERT INTO LKUP_CD_PARK_DAYNIGHT ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
'N', 'N', 'Night', NULL
); 

INSERT INTO LKUP_CD_PARK_FIELD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'Unknown', 'Unknown', NULL
); 
INSERT INTO LKUP_CD_PARK_FIELD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, 'Soaked', 'Soaked', NULL
); 
INSERT INTO LKUP_CD_PARK_FIELD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
2, 'Wet', 'Wet', NULL
); 
INSERT INTO LKUP_CD_PARK_FIELD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
3, 'Damp', 'Damp', NULL
); 
INSERT INTO LKUP_CD_PARK_FIELD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
4, 'Dry', 'Dry', NULL
); 

INSERT INTO LKUP_CD_PARK_PRECIP ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'Unknown', 'Unknown', NULL
); 
INSERT INTO LKUP_CD_PARK_PRECIP ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, 'None', 'None', NULL
); 
INSERT INTO LKUP_CD_PARK_PRECIP ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
2, 'Drizzle', 'Drizzle', NULL
); 
INSERT INTO LKUP_CD_PARK_PRECIP ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
3, 'Showers', 'Showers', NULL
); 
INSERT INTO LKUP_CD_PARK_PRECIP ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
4, 'Rain', 'Rain', NULL
); 
INSERT INTO LKUP_CD_PARK_PRECIP ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
5, 'Snow', 'Snow', NULL
); 

INSERT INTO LKUP_CD_PARK_SKY ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'Unknown', 'Unknown', NULL
); 
INSERT INTO LKUP_CD_PARK_SKY ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, 'Sunny', 'Sunny', NULL
); 
INSERT INTO LKUP_CD_PARK_SKY ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
2, 'Cloudy', 'Cloudy', NULL
); 
INSERT INTO LKUP_CD_PARK_SKY ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
3, 'Overcast', 'Overcast', NULL
); 
INSERT INTO LKUP_CD_PARK_SKY ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
4, 'Night', 'Night', NULL
); 
INSERT INTO LKUP_CD_PARK_SKY ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
5, 'Dome', 'Dome', NULL
); 

INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'Unknown', 'Unknown', NULL
); 
INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, 'tolf', 'To LF', NULL
); 
INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
2, 'tocf', 'To CF', NULL
); 
INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
3, 'torf', 'To RF', NULL
); 
INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
4, 'ltor', 'LF to RF', NULL
); 
INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
5, 'fromlf', 'From LF', NULL
); 
INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
6, 'fromcf', 'From CF', NULL
); 
INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
7, 'fromrf', 'From RF', NULL
); 
INSERT INTO LKUP_CD_PARK_WIND_DIRECTION ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
8, 'rtol', 'RF to LF', NULL
); 

INSERT INTO LKUP_CD_RECORDER_METHOD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'Unknown', 'Unknown', NULL
); 
INSERT INTO LKUP_CD_RECORDER_METHOD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, 'Park', 'Park', NULL
); 
INSERT INTO LKUP_CD_RECORDER_METHOD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
2, 'TV', 'TV', NULL
); 
INSERT INTO LKUP_CD_RECORDER_METHOD ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
3, 'Radio', 'Radio', NULL
); 

INSERT INTO LKUP_CD_RECORDER_PITCHES ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'Unknown', 'Unknown', NULL
); 
INSERT INTO LKUP_CD_RECORDER_PITCHES ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, 'Pitches', 'Pitches', NULL
); 
INSERT INTO LKUP_CD_RECORDER_PITCHES ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
2, 'Count', 'Count', NULL
); 

INSERT INTO LKUP_ID_BASE ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'None', 'None', NULL
); 
INSERT INTO LKUP_ID_BASE ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, '1B', 'Firstbase', NULL
); 
INSERT INTO LKUP_ID_BASE ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
2, '2B', 'Secondbase', NULL
); 
INSERT INTO LKUP_ID_BASE ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
3, '3B', 'Thirdbase', NULL
); 
INSERT INTO LKUP_ID_BASE ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
4, 'ER', 'Earned Run', NULL
); 
INSERT INTO LKUP_ID_BASE ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
5, 'UER', 'Unearned Run', NULL
); 
INSERT INTO LKUP_ID_BASE ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
6, 'TUER', 'Team Unearned Run', NULL
); 

INSERT INTO LKUP_ID_HOME ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'A', 'Away', NULL
); 
INSERT INTO LKUP_ID_HOME ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, 'H', 'Home', NULL
); 

INSERT INTO LKUP_ID_LAST ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
0, 'F', 'First', NULL
); 
INSERT INTO LKUP_ID_LAST ( VALUE_CD, SHORTNAME_TX, LONGNAME_TX, DESCRIPTION_TX ) VALUES ( 
1, 'L', 'Last', NULL
);