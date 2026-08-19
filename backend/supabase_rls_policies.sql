-- =============================================================================
-- CareerPilot AI — Supabase PostgreSQL Row-Level Security (RLS) Policies
-- Multi-Tenant Isolation & Least-Privilege Data Access
-- =============================================================================

-- Enable Row Level Security (RLS) on all tables
ALTER TABLE IF EXISTS public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.job_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.readiness_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.certificates ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.career_recommendations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.skill_gap_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.learning_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.chat_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.resume_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.assessment_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS public.interview_sessions ENABLE ROW LEVEL SECURITY;

-- -----------------------------------------------------------------------------
-- 1. Profiles Table RLS Policies
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own profile" ON public.profiles;
CREATE POLICY "Users can view their own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can insert their own profile" ON public.profiles;
CREATE POLICY "Users can insert their own profile"
    ON public.profiles FOR INSERT
    WITH CHECK (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can update their own profile" ON public.profiles;
CREATE POLICY "Users can update their own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

-- -----------------------------------------------------------------------------
-- 2. Job Scores & Readiness History
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can view their own job score" ON public.job_scores;
CREATE POLICY "Users can view their own job score"
    ON public.job_scores FOR SELECT
    USING (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can modify their own job score" ON public.job_scores;
CREATE POLICY "Users can modify their own job score"
    ON public.job_scores FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can view their score progression history" ON public.readiness_history;
CREATE POLICY "Users can view their score progression history"
    ON public.readiness_history FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

-- -----------------------------------------------------------------------------
-- 3. Certificates & Uploads
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can manage their own certificates" ON public.certificates;
CREATE POLICY "Users can manage their own certificates"
    ON public.certificates FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

-- -----------------------------------------------------------------------------
-- 4. Career Recommendations & Skill Gap Reports
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can manage their career recommendations" ON public.career_recommendations;
CREATE POLICY "Users can manage their career recommendations"
    ON public.career_recommendations FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can manage their skill gap reports" ON public.skill_gap_reports;
CREATE POLICY "Users can manage their skill gap reports"
    ON public.skill_gap_reports FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can manage their learning progress" ON public.learning_progress;
CREATE POLICY "Users can manage their learning progress"
    ON public.learning_progress FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

-- -----------------------------------------------------------------------------
-- 5. Chat History
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can manage their chat conversations" ON public.chat_conversations;
CREATE POLICY "Users can manage their chat conversations"
    ON public.chat_conversations FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can manage their chat messages" ON public.chat_messages;
CREATE POLICY "Users can manage their chat messages"
    ON public.chat_messages FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

-- -----------------------------------------------------------------------------
-- 6. Resumes, Assessments & AI Interviews
-- -----------------------------------------------------------------------------
DROP POLICY IF EXISTS "Users can manage their resume versions" ON public.resume_versions;
CREATE POLICY "Users can manage their resume versions"
    ON public.resume_versions FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can manage their assessment records" ON public.assessment_records;
CREATE POLICY "Users can manage their assessment records"
    ON public.assessment_records FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

DROP POLICY IF EXISTS "Users can manage their interview sessions" ON public.interview_sessions;
CREATE POLICY "Users can manage their interview sessions"
    ON public.interview_sessions FOR ALL
    USING (auth.uid() = uid)
    WITH CHECK (auth.uid() = uid);

-- -----------------------------------------------------------------------------
-- 7. Service Role Bypass (Backend Admin Access)
-- -----------------------------------------------------------------------------
-- Note: In Supabase, the `service_role` key automatically bypasses RLS policies
-- when executed through backend servers using SUPABASE_SERVICE_ROLE_KEY.
