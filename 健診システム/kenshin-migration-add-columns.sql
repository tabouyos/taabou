-- ============================================================
-- 健診センターシステム 追加マイグレーション
-- 既存Supabase（project: tpndfvpjmfhwbmrcvthd）に対して実行
-- Supabase > SQL Editor に貼り付けて Run
-- 冪等（IF NOT EXISTS / 例外吸収）なので何度流しても安全です
-- ============================================================

-- ------------------------------------------------------------
-- 1) 既存テーブルへの列追加
-- ------------------------------------------------------------
-- 予約：事前問診の発送状況（発送済/再発送不要/不要）と 初回/リピーター
alter table reservations add column if not exists pre_monshin_status text;
alter table reservations add column if not exists first_visit boolean default false;

-- 通過管理：各検査のメモ・臥床採血
alter table passage_records add column if not exists note text;
alter table passage_records add column if not exists recumbent boolean default false;

-- ドクター変更：担当外も含めた「お休みの医師」リスト（JSON文字列）
alter table doctor_overrides add column if not exists off_doctors text;

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

-- ============================================================
-- 確認用（任意）
-- ============================================================
-- select table_name, column_name, data_type
-- from information_schema.columns
-- where table_name in ('reservations','passage_records','doctor_overrides','karte_prep','pass_station_overrides')
-- order by table_name, column_name;
