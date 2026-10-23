-- ============================================================
-- 健診センター予約管理 v17：データを「ログインした職員だけ」に限定するSQL
-- 実行場所: Supabase ダッシュボード → SQL Editor → 全文貼り付け → Run
--
-- ★ 実行するのは、全PCを v17 に切り替えて、全員がログインできることを確かめた「あと」です。
--   実行した瞬間から、v16 以前（ログインなし）のアプリはデータを読み書きできなくなります。
-- ★ データ（予約・受診者など）には一切触れません。変えるのは「誰が読み書きできるか」の決まりだけです。
-- ★ 元に戻すときは kenshin-v17_RLS_元に戻す.sql を実行してください。
-- ============================================================

DO $$
DECLARE
  t   record;
  p   record;
BEGIN
  FOR t IN
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    -- 1. RLS を必ず有効にする（すでに有効なら何も変わらない）
    EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t.tablename);

    -- 2. 今ある決まり（ログインなしでも全操作OK など）をすべて外す
    FOR p IN
      SELECT policyname FROM pg_policies WHERE schemaname = 'public' AND tablename = t.tablename
    LOOP
      EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', p.policyname, t.tablename);
    END LOOP;

    -- 3. 「ログインした職員（authenticated）だけ」全操作OK、という決まりを付ける
    EXECUTE format(
      'CREATE POLICY kenshin_staff_only ON public.%I FOR ALL TO authenticated USING (true) WITH CHECK (true)',
      t.tablename
    );
  END LOOP;
END $$;

-- 4.（おまけ）セキュリティ診断の警告「Function Search Path Mutable」への対応
DO $$ BEGIN
  ALTER FUNCTION public.update_updated_at() SET search_path = public;
EXCEPTION WHEN undefined_function THEN NULL; END $$;

-- 5. 結果の確認：すべてのテーブルが「RLS 有効」「kenshin_staff_only / authenticated」になっていればOK
SELECT
  c.relname                         AS "テーブル",
  CASE WHEN c.relrowsecurity THEN '✓ 有効' ELSE '× 無効' END AS "RLS",
  COALESCE(string_agg(p.policyname || '（' || array_to_string(p.roles, ',') || '）', ' / '), '（決まりなし）') AS "決まり"
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace AND n.nspname = 'public'
LEFT JOIN pg_policies p ON p.schemaname = 'public' AND p.tablename = c.relname
WHERE c.relkind = 'r'
GROUP BY c.relname, c.relrowsecurity
ORDER BY c.relname;
