drop view if exists vw_games cascade;

create view vw_games as
select

    substring(game_id, 4, 4)::integer as year,
    substring(game_id, 4, 8)::date as game_date,
    *
from games;

create view vw_events as
select
    vw_games.year,
    vw_games.game_date,
    events.*,
    lkup.shortname_tx,
    lkup.longname_tx
from events
inner join lkup_cd_event lkup on events.event_cd::integer = lkup.value_cd
inner join vw_games using (game_id);

/*

select player_id, min(year) as year into temporary table _players from rosters group by player_id;
drop table if exists players;
select player_id, last_name_tx, first_name_tx, bat_hand_cd, pit_hand_cd into table players from _players join rosters using (player_id, year) order by last_name_tx asc;

*/
