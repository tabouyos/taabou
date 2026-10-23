-- ============================================================
-- 健診センター予約管理 v17：「ログインした職員だけ」の制限を元に戻すSQL（緊急用）
-- 実行場所: Supabase ダッシュボード → SQL Editor → 全文貼り付け → Run
--
-- ★ v17 で問題が起きて、v16 以前（ログインなし）に一時的に戻すときだけ使います。
-- ★ 実行すると、アプリのキーを知っていれば誰でも読み書きできる状態（v16 までと同じ）に戻ります。
--   問題が解決したら、もう一度 kenshin-v17_RLS_職員ログイン限定.sql を実行してください。
-- ★ データには一切触れません。
-- ============================================================

DO $$
DECLARE
  t record;
BEGIN
  FOR t IN
    SELECT tablename FROM pg_tables WHERE schemaname = 'public'
  LOOP
    EXECUTE format('DROP POLICY IF EXISTS kenshin_staff_only ON public.%I', t.tablename);
    EXECUTE format('DROP POLICY IF EXISTS kenshin_public_all ON public.%I', t.tablename);
    EXECUTE format(
      'CREATE POLICY kenshin_public_all ON public.%I FOR ALL TO anon, authenticated USING (true) WITH CHECK (true)',
      t.tablename
    );
  END LOOP;
END $$;

SELECT tablename AS "テーブル", policyname AS "決まり", array_to_string(roles, ',') AS "対象"
FROM pg_policies WHERE schemaname = 'public' ORDER BY tablename;
