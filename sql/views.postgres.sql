drop view if exists vw_games;

create view vw_games as
select
	*,	
	case
		when length(game_dt::text) = 3 then ('000'||game_dt::text)::date
		when length(game_dt::text) = 4 then ('00'||game_dt::text)::date
		when length(game_dt::text) = 5 then ('0'||game_dt::text)::date
		else game_dt::text::date
	end as game_date
from games;