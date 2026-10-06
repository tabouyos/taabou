-- ============================================================
-- 同期 ステップ1：列の追加だけ（PC入れ替え前に実行してOK）
-- 古い版のPCが残っていても、どのPCの記録も消えません。冪等なので何度流しても安全。
-- ============================================================
alter table reservations add column if not exists pre_monshin_status text;
alter table reservations add column if not exists first_visit boolean default false;
alter table passage_records add column if not exists note text;
alter table passage_records add column if not exists recumbent boolean default false;
alter table doctor_overrides add column if not exists off_doctors text;
