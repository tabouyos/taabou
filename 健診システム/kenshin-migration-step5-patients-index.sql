-- ============================================================
-- 受診者マスタ（医事課の全患者・約14万件）を速く検索するための索引（2026/10）
-- 実行場所: Supabase ダッシュボード → SQL Editor → 全文貼り付け → Run
-- データには触れません。冪等なので何度流しても安全。CSV取込の前でも後でもOK。
-- ============================================================
-- カルテ番号で探す（取込の照合にも使う）。すでに主キー／一意制約があれば何も起きません
create unique index if not exists patients_karte_number_uidx on patients (karte_number);
-- カナ（表記ゆれ吸収後）で探す
create index if not exists patients_kana_norm_idx on patients (kana_norm);
