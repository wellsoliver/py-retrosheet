drop view if exists vw_games cascade;

create view vw_games as
select
	case
		when length(game_dt::text) = 3 then ('000'||game_dt::text)::date
		when length(game_dt::text) = 4 then ('00'||game_dt::text)::date
		when length(game_dt::text) = 5 then ('0'||game_dt::text)::date
		else game_dt::text::date
	end as game_date,
	*
from games;

create view vw_events as
select
	extract(year from vw_games.game_date) as year,
	vw_games.game_date,
	events.*,
	lkup.shortname_tx,
	lkup.longname_tx
from events
inner join lkup_cd_event lkup on events.event_cd = lkup.value_cd
inner join vw_games using (game_id);