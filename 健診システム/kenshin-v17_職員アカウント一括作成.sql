-- ============================================================
-- 健診センター予約管理 v17：職員アカウントを「職員番号」でまとめて作るSQL
-- 実行場所: Supabase ダッシュボード → SQL Editor → 全文貼り付け → 一覧を書き換え → Run
--
-- ★ 下の「① 職員の一覧」だけを書き換えてください（それ以外は触らない）。
-- ★ 職員はログイン画面で「職員番号」と「パスワード」を入れるだけでログインできます。
--   （中では 職員番号@staff.kenshin.invalid というアカウントになります）
-- ★ すでにある職員番号は作り直さずに飛ばします（何度流しても二重にはなりません）。
-- ★ パスワードを書いたこのSQLは、共有フォルダやチャットに保存・貼り付けしないでください。
--   SQL Editor で実行したら、上書き保存せずに閉じてください。
-- ★ 初めて使うときは、まず1人分だけで試し、その職員番号で v17 にログインできるか確かめてください。
-- ============================================================

DO $$
DECLARE
  r      record;
  uid    uuid;
  em     text;
  made   int := 0;
  skip   int := 0;
BEGIN
  FOR r IN
    SELECT * FROM (VALUES
      -- ① 職員の一覧 ─────────────────────────────────────────
      --  ('職員番号', '初期パスワード', '氏名（任意・メモ用）'),
      --  パスワードは8文字以上を推奨。最後の行の後ろには「,」を付けない
      ('12345', 'Kenshin-2026a', '見本 太郎'),
      ('12346', 'Kenshin-2026b', '見本 花子')
      -- ──────────────────────────────────────────────────────
    ) AS v(staff_no, pw, staff_name)
  LOOP
    em := lower(trim(r.staff_no)) || '@staff.kenshin.invalid';

    IF EXISTS (SELECT 1 FROM auth.users WHERE email = em) THEN
      RAISE NOTICE '既にあるため飛ばしました: %', r.staff_no;
      skip := skip + 1;
      CONTINUE;
    END IF;

    uid := gen_random_uuid();

    INSERT INTO auth.users (
      instance_id, id, aud, role, email, encrypted_password,
      email_confirmed_at, raw_app_meta_data, raw_user_meta_data,
      created_at, updated_at,
      confirmation_token, recovery_token, email_change_token_new, email_change
    ) VALUES (
      '00000000-0000-0000-0000-000000000000', uid, 'authenticated', 'authenticated', em,
      extensions.crypt(r.pw, extensions.gen_salt('bf')),
      now(),
      '{"provider":"email","providers":["email"]}'::jsonb,
      jsonb_build_object('staff_no', r.staff_no, 'name', coalesce(r.staff_name, '')),
      now(), now(),
      '', '', '', ''
    );

    INSERT INTO auth.identities (
      id, user_id, provider_id, identity_data, provider, last_sign_in_at, created_at, updated_at
    ) VALUES (
      gen_random_uuid(), uid, uid::text,
      jsonb_build_object('sub', uid::text, 'email', em, 'email_verified', true),
      'email', now(), now(), now()
    );

    made := made + 1;
  END LOOP;

  RAISE NOTICE '作成: % 件 / 既存のため飛ばした: % 件', made, skip;
END $$;

-- ② 結果の確認：職員アカウントの一覧（パスワードは表示されません）
SELECT
  replace(email, '@staff.kenshin.invalid', '')   AS "職員番号",
  raw_user_meta_data->>'name'                   AS "氏名",
  to_char(created_at AT TIME ZONE 'Asia/Tokyo', 'YYYY/MM/DD HH24:MI') AS "作成日時",
  CASE WHEN email_confirmed_at IS NOT NULL THEN '✓' ELSE '×' END AS "確認済"
FROM auth.users
WHERE email LIKE '%@staff.kenshin.invalid'
ORDER BY email;
