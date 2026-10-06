-- ============================================================
-- 健診センターシステム Supabase 状態確認（読み取り専用・何も変更しません）
-- Supabase > SQL Editor に貼り付けて Run → 結果の表をそのままコピーして Claude に渡す
-- ============================================================
with app_tables(table_name) as (
  values ('reservations'),('companies'),('patients'),('doctor_overrides'),('locker_overrides'),
         ('slot_overrides'),('exam_type_daily_limits'),('shift_cells'),('shift_wishes'),
         ('shift_staff_memos'),('shift_settings'),('massage_offs'),('passage_records'),
         ('karte_prep'),('pass_station_overrides'),('akiba_days'),('worklists'),
         ('staff_memos'),('change_logs'),('reservation_change_history')
)
select a.table_name,
       case when t.table_name is null then '★テーブルなし' else 'あり' end as status,
       coalesce(string_agg(c.column_name, ', ' order by c.ordinal_position), '') as columns
from app_tables a
left join information_schema.tables t
       on t.table_schema = 'public' and t.table_name = a.table_name
left join information_schema.columns c
       on c.table_schema = 'public' and c.table_name = a.table_name
group by a.table_name, t.table_name
order by status desc, a.table_name;
