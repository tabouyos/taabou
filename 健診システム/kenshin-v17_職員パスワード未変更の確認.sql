-- ============================================================
-- 健診センター予約管理 v17：まだ初回ログイン（パスワード変更）をしていない職員の一覧
-- 実行場所: Supabase ダッシュボード → SQL Editor → 全文貼り付け → Run（読み取りのみ・何も変更しません）
--
-- ★ ここに出る職員は、まだ共通の仮パスワードのままです。早めにログインしてもらってください。
--   しばらく使わない職員は、再設定SQLでその人だけ別の仮パスワードにしておくと安全です。
-- ============================================================
SELECT
  replace(email, '@staff.kenshin.invalid', '')   AS "職員番号",
  raw_user_meta_data->>'name'                   AS "氏名",
  to_char(created_at AT TIME ZONE 'Asia/Tokyo', 'YYYY/MM/DD') AS "作成日",
  coalesce(to_char(last_sign_in_at AT TIME ZONE 'Asia/Tokyo', 'YYYY/MM/DD HH24:MI'), '一度もなし') AS "最後のログイン"
FROM auth.users
WHERE email LIKE '%@staff.kenshin.invalid'
  AND coalesce(raw_user_meta_data->>'pw_changed', '') <> 'true'
ORDER BY email;
