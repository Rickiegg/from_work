select t1.ord_date as ord_date
       ,t1.call_cnt as call_cnt
       ,t2.answer_cnt as answer_cnt
       ,t3.finish_cnt as finish_cnt
       ,t4.finish_cnt_2d as finish_cnt_2d
       ,t5.finish_cnt_2d as finish_cnt_3d
       ,t6.finish_cnt_2d as finish_cnt_4d
       ,t7.finish_cnt_2d as finish_cnt_5d
       ,t8.finish_cnt_2d as finish_cnt_6d
       ,t9.finish_cnt_2d as finish_cnt_7d

from
--当日呼叫订单量
(     select
            count(distinct order_id) call_cnt --当天呼叫订单量
            ,to_date(a_birth_time) as ord_date
      from ibd_env.cross_border
      where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
     group by to_date(a_birth_time)
)t1
left join
--当日呼叫订单中的应答订单量
(    select
            a.ord_date as ord_date
            ,count(distinct a.order_id) as answer_cnt
from 
      (
          select 
                a1.order_id as order_id
                ,a1.ord_date as ord_date
          from
            (
              select
                    order_id --当天呼叫订单id
                    ,to_date(a_birth_time) as ord_date
              from ibd_env.cross_border
              where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'     
            )a1 
          join
            (
              select
                    order_id --当天应答订单id
                    ,to_date(strive_time) as ord_date
              from ibd_env.cross_border
              where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
            )a2 on a1.order_id=a2.order_id and a1.ord_date=a2.ord_date
      )a
      group by a.ord_date
)t2 on t1.ord_date=t2.ord_date
left join
---当日呼叫订单中的完成订单量
(
      select
            b.ord_date as ord_date
            ,count(distinct b.order_id) as finish_cnt
      from  
        (
          select 
                b1.order_id
                ,b1.ord_date
          from
            (
              select
                    order_id --当天呼叫订单id
                    ,to_date(a_birth_time) as ord_date
              from ibd_env.cross_border
              where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
            )b1
          join
            (
              select
                    order_id --当天应答订单id
                    ,to_date(strive_time) as ord_date
              from ibd_env.cross_border
              where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
            )b2 on b1.order_id=b2.order_id and b1.ord_date=b2.ord_date
          join
            (
              select 
                  order_id  --当天完成订单id
                  ,to_date(finish_time) as ord_date             
              from gulfstream_dwd.dwd_order_make_d
              where CONCAT_WS('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
              and combo_type = 308
              and is_td_finish = 1
            )b3 on b2.order_id = b3.order_id and b1.ord_date=b3.ord_date
        )b
      group by b.ord_date
)t3 on t1.ord_date=t3.ord_date
left join
-----当日呼叫订单中次日完成订单量
(select
      c.ord_date as ord_date
      ,count(distinct c.order_id) as finish_cnt_2d
from  
    (
      select 
           c1.order_id
           ,c1.ord_date
      from
         (
            select
                  order_id --当天呼叫订单idid
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
         )c1
         join
         (
            select
                  order_id --当天应答订单id
                  ,to_date(strive_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
         )c2 on c1.order_id=c2.order_id and c1.ord_date=c2.ord_date
         join
         (
            select 
                  order_id  --当天完成订单id
                  ,to_date(finish_time) as finish_date 
                  ,date_sub(finish_time,1) as ord_date
            from gulfstream_dwd.dwd_order_make_d
            where CONCAT_WS('-', year, month, day) between date_add('${V_DATE}',1) and date_add('${END_DATE}',1)
            and combo_type = 308
            and is_td_finish = 1
        )c3 on c2.order_id=c3.order_id and c2.ord_date=c3.ord_date
         )c
group by c.ord_date
)t4 on t1.ord_date=t4.ord_date
left join
----第3日完成订单量
(select
      d.ord_date as ord_date
      ,count(distinct d.order_id) as finish_cnt_3d
from  
    (
      select 
           d1.order_id
           ,d1.ord_date
      from
         (
            select
                  order_id --当天呼叫订单idid
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}' 
         )d1
         join
         (
            select
                  order_id --当天应答订单id
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
         )d2 on d1.order_id=d2.order_id and d1.ord_date=d2.ord_date
         join
         (
            select 
                  order_id  --当天完成订单id
                  ,to_date(finish_time) as finish_date  
                  ,date_sub(finish_time,2) as ord_date           
            from gulfstream_dwd.dwd_order_make_d
            where CONCAT_WS('-', year, month, day) between date_add('${V_DATE}',2) and date_add('${END_DATE}',2)
            and combo_type = 308
            and is_td_finish = 1
        )d3 on d2.order_id=d3.order_id and d2.ord_date=d3.ord_date
    )d
group by d.ord_date
)t5 on t1.ord_date=t5.ord_date
left join
----第4日完成订单量
(select
      e.ord_date as ord_date
      ,count(distinct e.order_id) as finish_cnt_4d
from  
    (
      select 
           e1.order_id
           ,e1.ord_date
      from
         (
            select
                  order_id --当天呼叫订单idid
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
         )e1
         join
         (
            select
                  order_id --当天应答订单id
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}' 
         )e2 on e1.order_id=e2.order_id and e1.ord_date=e2.ord_date
         join
         (
            select 
                  order_id  --当天完成订单id
                  ,to_date(finish_time) as finish_date  
                  ,date_sub(finish_time,3) as ord_date                        
            from gulfstream_dwd.dwd_order_make_d
            where CONCAT_WS('-', year, month, day)between date_add('${V_DATE}',3) and date_add('${END_DATE}',3)
            and combo_type = 308
            and is_td_finish = 1
        )e3 on e2.order_id=e3.order_id and e2.ord_date=e3.ord_date
    )e
group by e.ord_date
 )t6  on t1.ord_date=t6.ord_date
left join
 -----第5日完成订单量
(select
      f.ord_date as ord_date
      ,count(distinct f.order_id) as finish_cnt_5d
from  
    (
      select 
           f1.order_id
           ,f1.ord_date
      from
         (
            select
                  order_id --当天呼叫订单idid
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
         )f1
         join
         (
            select
                  order_id --当天应答订单id
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}' 
         )f2 on f1.order_id=f2.order_id and f1.ord_date=f2.ord_date
         join
         (
            select 
                  order_id  --当天完成订单id
                  ,to_date(finish_time) as finish_date
                  ,date_sub(finish_time,4) as  ord_date            
            from gulfstream_dwd.dwd_order_make_d
            where CONCAT_WS('-', year, month, day) between date_add('${V_DATE}',4) and date_add('${END_DATE}',4)
            and combo_type = 308
            and is_td_finish = 1
        )f3 on f2.order_id=f3.order_id and  f3.ord_date=f2.ord_date
    )f
group by f.ord_date
)t7  on t1.ord_date=t7.ord_date
left join
 -----第6日完成订单量
(select
      g.ord_date as ord_date
      ,count(distinct g.order_id) as finish_cnt_6d
from  
    (
      select 
           g1.order_id
           ,g1.ord_date
      from
         (
            select
                  order_id --当天呼叫订单idid
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}' 
         )g1
         join
         (
            select
                  order_id --当天应答订单id
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
         )g2 on g1.order_id=g2.order_id and g1.ord_date=g2.ord_date
         join
         (
            select 
                  order_id  --当天完成订单id
                  ,to_date(finish_time) as finish_date
                  ,date_sub(finish_time,5) as  ord_date
            from gulfstream_dwd.dwd_order_make_d
            where CONCAT_WS('-', year, month, day) between date_add('${V_DATE}',5) and date_add('${END_DATE}',5)
            and combo_type = 308
            and is_td_finish = 1
        )g3 on g2.order_id=g3.order_id and g2.ord_date=g3.ord_date
    )g
group by g.ord_date
)t8 on t1.ord_date=t8.ord_date
left join
 -----第7日完成订单量
(select
      h.ord_date as ord_date
      ,count(distinct h.order_id) as finish_cnt_7d
from  
    (
      select 
           h1.order_id
           ,h1.ord_date
      from
         (
            select
                  order_id --当天呼叫订单idid
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
         )h1
         join
         (
            select
                  order_id --当天应答订单id
                  ,to_date(a_birth_time) as ord_date
            from ibd_env.cross_border
            where concat_ws('-', year, month, day) between '${V_DATE}' and '${END_DATE}'
         )h2 on h1.order_id=h2.order_id and h1.ord_date=h2.ord_date
         join
         (
            select 
                  order_id  --当天完成订单id
                  ,to_date(finish_time) as finish_date 
                  ,date_sub(finish_time,6) as  ord_date
            from gulfstream_dwd.dwd_order_make_d
            where CONCAT_WS('-', year, month, day) between date_add('${V_DATE}',6) and date_add('${END_DATE}',6)
            and combo_type = 308
            and is_td_finish = 1
        )h3 on h2.order_id=h3.order_id and h3.ord_date=h2.ord_date
    )h
group by h.ord_date
)t9 on t1.ord_date=t9.ord_date


 
