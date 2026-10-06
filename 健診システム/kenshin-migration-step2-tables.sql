-- ============================================================
-- 同期 ステップ2：新しいテーブル作成（全PCを修正版 kenshin-v16.html に入れ替えた後に実行）
-- karte_prep・pass_station_overrides・diaries（日誌）を作成
-- 先に実行すると、古い版のPCで「カルテ準備」「当日キャンセル/追加」の端末内記録が消えます。
-- 冪等なので何度流しても安全。
-- ============================================================

-- ------------------------------------------------------------
-- 2) 新規テーブル（全PC同期用）
-- ------------------------------------------------------------
-- カルテ準備 済/未（日付ごと）
create table if not exists karte_prep (
  date        text primary key,
  done        boolean default true,
  changed_by  text,
  changed_at  text
);

-- 通過管理の当日キャンセル/追加（受診者×検査ごと）
create table if not exists pass_station_overrides (
  reservation_id text not null,
  station        text not null,
  mode           text not null,          -- 'add'（追加） または 'cancel'（対象外）
  changed_by     text,
  changed_at     text,
  primary key (reservation_id, station)
);

-- 健診センター日誌（日付ごと。日誌の中身はJSONでまとめて保存）
create table if not exists diaries (
  date        text primary key,
  data        jsonb,
  updated_by  text,
  updated_at  text
);

-- ------------------------------------------------------------
-- 3) RLS（行レベルセキュリティ）
--    ※ 既存テーブルと同じ運用に合わせてください。
--      下は「院内利用・anonキー前提」で全操作を許可する例です。
-- ------------------------------------------------------------
alter table karte_prep enable row level security;
drop policy if exists "karte_prep_all" on karte_prep;
create policy "karte_prep_all" on karte_prep for all using (true) with check (true);

alter table pass_station_overrides enable row level security;
drop policy if exists "pass_station_overrides_all" on pass_station_overrides;
create policy "pass_station_overrides_all" on pass_station_overrides for all using (true) with check (true);

alter table diaries enable row level security;
drop policy if exists "diaries_all" on diaries;
create policy "diaries_all" on diaries for all using (true) with check (true);

-- ------------------------------------------------------------
-- 4) リアルタイム配信（他PCへ即時反映するために必要）
--    既に追加済みでもエラーにならないよう例外を吸収します
-- ------------------------------------------------------------
do $$ begin
  alter publication supabase_realtime add table karte_prep;
exception when duplicate_object then null; end $$;

do $$ begin
  alter publication supabase_realtime add table pass_station_overrides;
exception when duplicate_object then null; end $$;

do $$ begin
  alter publication supabase_realtime add table diaries;
exception when duplicate_object then null; end $$;

-- ============================================================
-- 確認用（任意）
-- ============================================================
-- select table_name, column_name, data_type
-- from information_schema.columns
-- where table_name in ('reservations','passage_records','doctor_overrides','karte_prep','pass_station_overrides','diaries')
-- order by table_name, column_name;
