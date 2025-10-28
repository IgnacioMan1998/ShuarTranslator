-- ============================================
-- MIGRATION 001: Create Translation Tables
-- Description: Create new tables for translation system
-- ============================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TRANSLATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.translations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Translation content
    source_text VARCHAR(500) NOT NULL,
    target_text VARCHAR(500) NOT NULL,
    source_language VARCHAR(20) NOT NULL CHECK (source_language IN ('shuar', 'spanish')),
    target_language VARCHAR(20) NOT NULL CHECK (target_language IN ('shuar', 'spanish')),
    
    -- Quality metrics
    confidence_score DECIMAL(3,2) DEFAULT 0.50 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    average_rating DECIMAL(3,2) DEFAULT 0.0 CHECK (average_rating >= 0.0 AND average_rating <= 5.0),
    total_ratings INTEGER DEFAULT 0 CHECK (total_ratings >= 0),
    usage_count INTEGER DEFAULT 0 CHECK (usage_count >= 0),
    
    -- Context information
    context_domain VARCHAR(100),
    context_register VARCHAR(50),
    context_dialect VARCHAR(50),
    cultural_notes TEXT,
    
    -- References to words
    word_references UUID[], -- Array of word IDs
    
    -- Status and approval
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'needs_review')),
    created_by UUID REFERENCES auth.users(id),
    approved_by UUID REFERENCES auth.users(id),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    approved_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT different_languages CHECK (source_language != target_language),
    CONSTRAINT valid_rating_count CHECK (
        (total_ratings = 0 AND average_rating = 0.0) OR 
        (total_ratings > 0 AND average_rating > 0.0)
    )
);

-- Indexes for translations table
CREATE INDEX idx_translations_source_text ON public.translations(source_text);
CREATE INDEX idx_translations_target_text ON public.translations(target_text);
CREATE INDEX idx_translations_source_lang ON public.translations(source_language);
CREATE INDEX idx_translations_target_lang ON public.translations(target_language);
CREATE INDEX idx_translations_status ON public.translations(status);
CREATE INDEX idx_translations_created_by ON public.translations(created_by);
CREATE INDEX idx_translations_approved_by ON public.translations(approved_by);
CREATE INDEX idx_translations_created_at ON public.translations(created_at);
CREATE INDEX idx_translations_confidence ON public.translations(confidence_score DESC);
CREATE INDEX idx_translations_rating ON public.translations(average_rating DESC);
CREATE INDEX idx_translations_usage ON public.translations(usage_count DESC);

-- Full-text search indexes
CREATE INDEX idx_translations_source_fts ON public.translations USING gin(to_tsvector('spanish', source_text));
CREATE INDEX idx_translations_target_fts ON public.translations USING gin(to_tsvector('spanish', target_text));

-- Composite indexes for common queries
CREATE INDEX idx_translations_lang_pair ON public.translations(source_language, target_language);
CREATE INDEX idx_translations_status_created ON public.translations(status, created_at DESC);

-- ============================================
-- TRANSLATION FEEDBACK TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.translation_feedback (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- References
    translation_id UUID NOT NULL REFERENCES public.translations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    
    -- User information
    user_role VARCHAR(20) DEFAULT 'visitor' CHECK (user_role IN ('visitor', 'community_member', 'verified_speaker', 'expert', 'admin')),
    is_from_native_speaker BOOLEAN DEFAULT false,
    
    -- Feedback content
    feedback_type VARCHAR(20) DEFAULT 'rating' CHECK (feedback_type IN ('rating', 'correction', 'suggestion', 'cultural_note', 'pronunciation')),
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comment TEXT CHECK (LENGTH(comment) <= 1000),
    suggested_translation VARCHAR(500),
    cultural_context TEXT CHECK (LENGTH(cultural_context) <= 1000),
    pronunciation_notes VARCHAR(500),
    
    -- Review status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'reviewed', 'approved', 'rejected', 'implemented')),
    expert_notes TEXT CHECK (LENGTH(expert_notes) <= 1000),
    reviewed_by UUID REFERENCES auth.users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT feedback_has_content CHECK (
        rating IS NOT NULL OR 
        comment IS NOT NULL OR 
        suggested_translation IS NOT NULL OR 
        cultural_context IS NOT NULL OR 
        pronunciation_notes IS NOT NULL
    )
);

-- Indexes for translation_feedback table
CREATE INDEX idx_feedback_translation_id ON public.translation_feedback(translation_id);
CREATE INDEX idx_feedback_user_id ON public.translation_feedback(user_id);
CREATE INDEX idx_feedback_user_role ON public.translation_feedback(user_role);
CREATE INDEX idx_feedback_type ON public.translation_feedback(feedback_type);
CREATE INDEX idx_feedback_status ON public.translation_feedback(status);
CREATE INDEX idx_feedback_rating ON public.translation_feedback(rating);
CREATE INDEX idx_feedback_native_speaker ON public.translation_feedback(is_from_native_speaker);
CREATE INDEX idx_feedback_reviewed_by ON public.translation_feedback(reviewed_by);
CREATE INDEX idx_feedback_created_at ON public.translation_feedback(created_at DESC);

-- Composite indexes
CREATE INDEX idx_feedback_translation_status ON public.translation_feedback(translation_id, status);
CREATE INDEX idx_feedback_pending_review ON public.translation_feedback(status, created_at) WHERE status = 'pending';
CREATE INDEX idx_feedback_native_pending ON public.translation_feedback(is_from_native_speaker, status) WHERE is_from_native_speaker = true;

-- ============================================
-- TRANSLATION USAGE LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS public.translation_usage_log (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- References
    translation_id UUID NOT NULL REFERENCES public.translations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id),
    
    -- Usage context
    source_text VARCHAR(500) NOT NULL,
    detected_language VARCHAR(20),
    user_agent TEXT,
    ip_address INET,
    
    -- Timestamps
    used_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for usage log
CREATE INDEX idx_usage_log_translation_id ON public.translation_usage_log(translation_id);
CREATE INDEX idx_usage_log_user_id ON public.translation_usage_log(user_id);
CREATE INDEX idx_usage_log_used_at ON public.translation_usage_log(used_at DESC);
CREATE INDEX idx_usage_log_detected_lang ON public.translation_usage_log(detected_language);

-- Partitioning by month for usage log (optional, for high volume)
-- CREATE TABLE public.translation_usage_log_y2024m01 PARTITION OF public.translation_usage_log
-- FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- ============================================
-- FUNCTIONS AND TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
CREATE TRIGGER update_translations_updated_at 
    BEFORE UPDATE ON public.translations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_updated_at 
    BEFORE UPDATE ON public.translation_feedback 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to update translation rating when feedback is added
CREATE OR REPLACE FUNCTION update_translation_rating()
RETURNS TRIGGER AS $$
BEGIN
    -- Only update if feedback has a rating
    IF NEW.rating IS NOT NULL THEN
        UPDATE public.translations 
        SET 
            total_ratings = (
                SELECT COUNT(*) 
                FROM public.translation_feedback 
                WHERE translation_id = NEW.translation_id 
                AND rating IS NOT NULL
            ),
            average_rating = (
                SELECT AVG(rating::DECIMAL) 
                FROM public.translation_feedback 
                WHERE translation_id = NEW.translation_id 
                AND rating IS NOT NULL
            ),
            updated_at = NOW()
        WHERE id = NEW.translation_id;
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to update translation rating
CREATE TRIGGER update_translation_rating_trigger
    AFTER INSERT OR UPDATE ON public.translation_feedback
    FOR EACH ROW EXECUTE FUNCTION update_translation_rating();

-- Function to log translation usage
CREATE OR REPLACE FUNCTION log_translation_usage(
    p_translation_id UUID,
    p_user_id UUID DEFAULT NULL,
    p_source_text VARCHAR DEFAULT NULL,
    p_detected_language VARCHAR DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_ip_address INET DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    -- Insert usage log
    INSERT INTO public.translation_usage_log (
        translation_id, user_id, source_text, detected_language, user_agent, ip_address
    ) VALUES (
        p_translation_id, p_user_id, p_source_text, p_detected_language, p_user_agent, p_ip_address
    );
    
    -- Update usage count
    UPDATE public.translations 
    SET 
        usage_count = usage_count + 1,
        updated_at = NOW()
    WHERE id = p_translation_id;
END;
$$ language 'plpgsql';

-- Function to get translation statistics
CREATE OR REPLACE FUNCTION get_translation_statistics()
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_translations', (SELECT COUNT(*) FROM public.translations),
        'approved_translations', (SELECT COUNT(*) FROM public.translations WHERE status = 'approved'),
        'pending_translations', (SELECT COUNT(*) FROM public.translations WHERE status = 'pending'),
        'total_feedback', (SELECT COUNT(*) FROM public.translation_feedback),
        'average_rating', (SELECT AVG(average_rating) FROM public.translations WHERE total_ratings > 0),
        'total_usage', (SELECT SUM(usage_count) FROM public.translations),
        'native_speaker_feedback', (SELECT COUNT(*) FROM public.translation_feedback WHERE is_from_native_speaker = true),
        'by_language_pair', (
            SELECT json_object_agg(
                source_language || '_to_' || target_language, 
                count
            )
            FROM (
                SELECT 
                    source_language, 
                    target_language, 
                    COUNT(*) as count
                FROM public.translations 
                GROUP BY source_language, target_language
            ) lang_pairs
        )
    ) INTO result;
    
    RETURN result;
END;
$$ language 'plpgsql';

-- Function to get feedback summary for a translation
CREATE OR REPLACE FUNCTION get_feedback_summary(p_translation_id UUID)
RETURNS JSON AS $$
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_feedback', COUNT(*),
        'average_rating', AVG(rating),
        'rating_distribution', json_object_agg(rating, rating_count),
        'feedback_types', json_object_agg(feedback_type, type_count),
        'native_speaker_count', SUM(CASE WHEN is_from_native_speaker THEN 1 ELSE 0 END),
        'expert_feedback_count', SUM(CASE WHEN user_role IN ('expert', 'admin') THEN 1 ELSE 0 END)
    ) INTO result
    FROM (
        SELECT 
            rating,
            feedback_type,
            is_from_native_speaker,
            user_role,
            COUNT(*) OVER (PARTITION BY rating) as rating_count,
            COUNT(*) OVER (PARTITION BY feedback_type) as type_count
        FROM public.translation_feedback 
        WHERE translation_id = p_translation_id
    ) feedback_data;
    
    RETURN result;
END;
$$ language 'plpgsql';

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on tables
ALTER TABLE public.translations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.translation_feedback ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.translation_usage_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies for translations
CREATE POLICY "Approved translations visible to all" ON public.translations
    FOR SELECT USING (status = 'approved' OR auth.uid() = created_by);

CREATE POLICY "Users can create translations" ON public.translations
    FOR INSERT WITH CHECK (auth.uid() = created_by);

CREATE POLICY "Users can update own translations" ON public.translations
    FOR UPDATE USING (auth.uid() = created_by);

CREATE POLICY "Experts can manage all translations" ON public.translations
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM auth.users 
            WHERE id = auth.uid() 
            AND raw_user_meta_data->>'role' IN ('expert', 'admin')
        )
    );

-- RLS Policies for feedback
CREATE POLICY "All feedback visible to translation owners and experts" ON public.translation_feedback
    FOR SELECT USING (
        auth.uid() = user_id OR
        EXISTS (
            SELECT 1 FROM public.translations t 
            WHERE t.id = translation_id AND t.created_by = auth.uid()
        ) OR
        EXISTS (
            SELECT 1 FROM auth.users 
            WHERE id = auth.uid() 
            AND raw_user_meta_data->>'role' IN ('expert', 'admin')
        )
    );

CREATE POLICY "Users can submit feedback" ON public.translation_feedback
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own feedback" ON public.translation_feedback
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Experts can manage all feedback" ON public.translation_feedback
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM auth.users 
            WHERE id = auth.uid() 
            AND raw_user_meta_data->>'role' IN ('expert', 'admin')
        )
    );

-- RLS Policies for usage log
CREATE POLICY "Users can view own usage" ON public.translation_usage_log
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "System can log usage" ON public.translation_usage_log
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Experts can view all usage" ON public.translation_usage_log
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM auth.users 
            WHERE id = auth.uid() 
            AND raw_user_meta_data->>'role' IN ('expert', 'admin')
        )
    );

-- ============================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================

COMMENT ON TABLE public.translations IS 'Translation pairs between Shuar and Spanish with quality metrics';
COMMENT ON TABLE public.translation_feedback IS 'Community feedback and ratings for translations';
COMMENT ON TABLE public.translation_usage_log IS 'Log of translation usage for analytics';

COMMENT ON COLUMN public.translations.confidence_score IS 'Algorithmic confidence in translation quality (0.0-1.0)';
COMMENT ON COLUMN public.translations.average_rating IS 'Community average rating (0.0-5.0)';
COMMENT ON COLUMN public.translations.word_references IS 'Array of UUIDs referencing palabras_detalladas table';
COMMENT ON COLUMN public.translation_feedback.is_from_native_speaker IS 'Whether feedback comes from verified native Shuar speaker';
COMMENT ON COLUMN public.translation_feedback.feedback_type IS 'Type of feedback: rating, correction, suggestion, cultural_note, pronunciation';

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert sample translation (commented out for production)
/*
INSERT INTO public.translations (
    source_text, target_text, source_language, target_language,
    confidence_score, status, created_by
) VALUES (
    'yawa', 'perro', 'shuar', 'spanish',
    0.95, 'approved', (SELECT id FROM auth.users LIMIT 1)
);
*/