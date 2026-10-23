-- ============================================================
-- 健診センター予約管理 v17：職員のパスワードを再設定するSQL（パスワードを忘れたとき）
-- 実行場所: Supabase ダッシュボード → SQL Editor → 全文貼り付け → 2か所を書き換え → Run
--
-- ★ 書き換えるのは「職員番号」と「仮パスワード」の2か所だけです。
-- ★ 職員が次にログインすると、自分のパスワードへの変更を求められます。
-- ★ パスワードを書いたこのSQLは保存せずに閉じてください。
-- ============================================================

UPDATE auth.users
SET encrypted_password = extensions.crypt('仮パスワード', extensions.gen_salt('bf')),
    raw_user_meta_data = coalesce(raw_user_meta_data, '{}'::jsonb) - 'pw_changed',   -- 次回ログイン時に本人が変更する
    updated_at = now()
WHERE email = lower('12345') || '@staff.kenshin.invalid';   -- ← '12345' を職員番号に

-- 「UPDATE 1」と出れば再設定できています（「UPDATE 0」は職員番号の間違い）
