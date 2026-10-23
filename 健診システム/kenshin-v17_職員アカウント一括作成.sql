-- ============================================================
-- 健診センター予約管理 v17：職員アカウントを「職員番号」でまとめて作るSQL
-- 実行場所: Supabase ダッシュボード → SQL Editor → 全文貼り付け → 一覧を書き換え → Run
--
-- ★ 書き換えるのは「① 共通の仮パスワード」と「② 職員の一覧」の2か所だけです。
-- ★ 全員同じ仮パスワードで作ります。各職員は初回ログイン時に自分のパスワードへ変更します
--   （変更するまで先に進めません。同じ文字だけのパスワードは新しいパスワードに使えません）。
-- ★ すでにある職員番号は作り直さずに飛ばします（職員が増えたら追加分だけ書いて流せばOK）。
-- ★ 仮パスワードは紙に印刷せず、口頭で伝えてください。
--   アカウントを作ったら、なるべく早く本人に初回ログイン（パスワード変更）をしてもらってください。
-- ============================================================

DO $$
DECLARE
  -- ① 共通の仮パスワード（8文字以上）─────────────────────
  temp_pw text := '88888888';
  -- ────────────────────────────────────────────────────
  r      record;
  uid    uuid;
  em     text;
  made   int := 0;
  skip   int := 0;
BEGIN
  FOR r IN
    SELECT * FROM (VALUES

      -- ② 職員の一覧 ▼▼▼ ここを書き換える（'職員番号', '氏名'）。1人1行 ▼▼▼
      --    最後の行の後ろには「,」を付けない
      ('12345', '見本 太郎'),
      ('12346', '見本 花子')
      -- ▲▲▲ ここまで ▲▲▲

    ) AS v(staff_no, staff_name)
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
      extensions.crypt(temp_pw, extensions.gen_salt('bf')),
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

-- 結果の確認：職員アカウントの一覧（パスワードは表示されません）
SELECT
  replace(email, '@staff.kenshin.invalid', '')   AS "職員番号",
  raw_user_meta_data->>'name'                   AS "氏名",
  to_char(created_at AT TIME ZONE 'Asia/Tokyo', 'YYYY/MM/DD HH24:MI') AS "作成日時",
  CASE WHEN (raw_user_meta_data->>'pw_changed') = 'true' THEN '✓ 変更済' ELSE '未（仮パスワードのまま）' END AS "パスワード"
FROM auth.users
WHERE email LIKE '%@staff.kenshin.invalid'
ORDER BY email;
