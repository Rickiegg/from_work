SELECT t.utc_create_time first_utc_create_time,
t.local_create_time first_local_create_time,a.*
from
(
    SELECT ticket_id,utc_create_time,local_create_time
    FROM
    (
    select ticket_id,utc_create_time,local_create_time,
    row_number() over( partition by ticket_id order by utc_create_time) rn
    from international.dwd_service_ticket_process_global_hi
    where country_code in ('AU','BR','MX','JP')
    -- and source not in ('AU','BR','MX','JP')
    and concat_ws('-',year,month,day) between date_sub('2019-03-01',1) and '2019-03-07'
    and to_date(local_create_time) = '2019-03-01'
    and action in ('ticket_start')
    )a 
    where rn=1
)t
JOIN
(
    select a.*, row_number() over(partition by ticket_id order by utc_create_time,ticket_process_id) rn
    from 
    (
        select ticket_id,ticket_process_id,channel_name,
                -- case when diff_log_from = 5 and diff_log_to = 2 and user_id < 0 then 'processing'
                --     when diff_log_from = 0 and diff_log_to = 5 and user_id < 0 then 'pending' end current_step,
                diff_log_from, diff_log_to, status,
                action, user_id,local_create_time,utc_create_time,
                lag(ticket_process_id,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) ticket_process_id_before,
                lag(diff_log_from,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) diff_log_from_before, 
                lag(diff_log_to,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) diff_log_to_before, 
                lag(action,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) action_before, 
                -- lead(user_id) over (partition by ticket_id order by utc_create_time, ticket_process_id) user_id_next, 
                lag(local_create_time,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) local_create_time_before,
                lag(utc_create_time,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) utc_create_time_before,
                
                lead(ticket_process_id,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) ticket_process_id_next,
                lead(diff_log_from,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) diff_log_from_next, 
                lead(diff_log_to,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) diff_log_to_next, 
                lead(action,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) action_next, 
                -- lead(user_id) over (partition by ticket_id order by utc_create_time, ticket_process_id) user_id_next, 
                lead(local_create_time,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) local_create_time_next,
                lead(utc_create_time,1) over (partition by ticket_id order by utc_create_time, ticket_process_id) utc_create_time_next,
                country_code
        from 
        (
            select timezone,stat_date,stat_hour,current_stat_date,current_stat_hour,ticket_process_id,ticket_id,a_type,channel,channel_name,
                    action,regexp_replace(content,'\n', '') content,diff_log,is_public,user_id,organization_id,status,
                    local_create_time,utc_create_time,a.country_code,year,month,day,hour,
                    split(split(diff_log2,',')[0],':')[1] diff_log_field,
                    split(split(diff_log2,',')[1],':')[1] diff_log_from,
                    split(split(diff_log2,',')[2],':')[1] diff_log_to,
                    split(split(diff_log2,',')[3],':')[1] diff_log_title
            from 
            (
                select timezone,stat_date,stat_hour,current_stat_date,current_stat_hour,ticket_process_id,ticket_id,a_type,channel,
                        action,regexp_replace(content,'\n', '') content,diff_log,is_public,user_id,organization_id,
                        local_create_time,utc_create_time,country_code,status,
                        year,month,day,hour,
                        translate(diff_log2,'<>\"', '') diff_log2
                from international.dwd_service_ticket_process_global_hi
                lateral view explode(split(translate(diff_log,'{}[]', '<>'),'(>,<)')) diff_log as diff_log2
                where country_code in ('BR','AU','MX','JP')
                and concat_ws('-',year,month,day) between date_sub('2019-03-01',1) and date_add('2019-03-01',29)
                and to_date(local_create_time) between '2019-03-01' and date_add('2019-03-01',29)
                and length(ticket_id) > 15
                -- and action in ('ticket_assign','ticket_handle')
                -- and ((status = 5 and action in ('ticket_assign','ticket_handle')) or status = 2)
            )a
            left join
            (
                select channel_id,channel_type, channel_name,country_code
                from international.dim_service_channel_global
                where concat_ws('-',year,month,day) = '2019-03-07'
                and hour = '23'
                and country_code in ('BR','AU','MX','JP')
                group by channel_id, channel_type,channel_name,country_code
            )b on a.channel = channel_id and a.country_code = b.country_code
        where split(split(diff_log2,',')[0],':')[1]  = 'status'   
        )a
    )a
)a on t.ticket_id=a.ticket_id  