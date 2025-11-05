-- ============================================
-- MIGRATION 002: Create Dictionary Tables
-- Description: Create tables for storing Shuar-Spanish dictionary
-- ============================================

-- ============================================
-- PALABRAS_DETALLADAS TABLE (Main Dictionary)
-- ============================================
CREATE TABLE IF NOT EXISTS public.palabras_detalladas (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Word information
    palabra_shuar VARCHAR(200) NOT NULL,
    traduccion_espanol VARCHAR(500) NOT NULL,
    
    -- Phonological information (crucial for Shuar)
    pronunciacion_ipa VARCHAR(300), -- International Phonetic Alphabet
    silabas VARCHAR(200), -- Syllable breakdown: ya-wa, nu-kur
    acento_posicion INTEGER, -- Stress position (1=first syllable, 2=second, etc.)
    tipos_vocales_presentes VARCHAR(20)[], -- Array: normal, larga, glotalizada
    estructura_silabica VARCHAR(100), -- Pattern: CV-CV, CVC-CV, etc.
    analisis_fonologico JSONB, -- Detailed phonological analysis
    
    -- Grammatical information
    categoria_gramatical VARCHAR(50) NOT NULL, -- noun, verb, adjective, etc.
    subcategoria VARCHAR(100), -- transitive, intransitive, etc.
    genero VARCHAR(20), -- masculine, feminine, neutral
    numero VARCHAR(20), -- singular, plural
    
    -- Morphological analysis
    raiz VARCHAR(100), -- Root word
    prefijos VARCHAR(200), -- Prefixes
    sufijos VARCHAR(200), -- Suffixes
    morfemas JSONB, -- Detailed morpheme breakdown
    
    -- Semantic information
    definicion_detallada TEXT,
    sinonimos TEXT[], -- Array of synonyms
    antonimos TEXT[], -- Array of antonyms
    campo_semantico VARCHAR(100), -- Semantic field
    
    -- Usage and context
    nivel_formalidad VARCHAR(50) DEFAULT 'neutral', -- formal, informal, neutral
    registro VARCHAR(50), -- ceremonial, daily, technical
    dialecto VARCHAR(50), -- Shuar dialect variation
    region_uso VARCHAR(100), -- Geographic usage
    
    -- Cultural context
    significado_cultural TEXT,
    contexto_uso TEXT,
    ejemplos_uso JSONB, -- Examples with translations
    
    -- Frequency and difficulty
    frecuencia_uso INTEGER DEFAULT 1 CHECK (frecuencia_uso >= 1 AND frecuencia_uso <= 10),
    nivel_dificultad INTEGER DEFAULT 1 CHECK (nivel_dificultad >= 1 AND nivel_dificultad <= 5),
    
    -- Quality and verification
    verificado_por_hablante BOOLEAN DEFAULT false,
    verificado_por_experto BOOLEAN DEFAULT false,
    confiabilidad_score DECIMAL(3,2) DEFAULT 0.50 CHECK (confiabilidad_score >= 0.0 AND confiabilidad_score <= 1.0),
    
    -- Source information
    fuente VARCHAR(200), -- Dictionary source, informant, etc.
    fecha_registro DATE DEFAULT CURRENT_DATE,
    notas_linguisticas TEXT,
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'deprecated', 'under_review', 'archived')),
    
    -- Metadata
    created_by UUID REFERENCES auth.users(id),
    updated_by UUID REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_shuar_word_meaning UNIQUE (palabra_shuar, traduccion_espanol, categoria_gramatical)
);

-- Indexes for efficient searching
CREATE INDEX idx_palabras_shuar ON public.palabras_detalladas(palabra_shuar);
CREATE INDEX idx_palabras_espanol ON public.palabras_detalladas(traduccion_espanol);
CREATE INDEX idx_palabras_categoria ON public.palabras_detalladas(categoria_gramatical);
CREATE INDEX idx_palabras_status ON public.palabras_detalladas(status);
CREATE INDEX idx_palabras_frecuencia ON public.palabras_detalladas(frecuencia_uso DESC);
CREATE INDEX idx_palabras_verificado ON public.palabras_detalladas(verificado_por_hablante, verificado_por_experto);
CREATE INDEX idx_palabras_dialecto ON public.palabras_detalladas(dialecto);
CREATE INDEX idx_palabras_campo_semantico ON public.palabras_detalladas(campo_semantico);

-- Full-text search indexes
CREATE INDEX idx_palabras_shuar_fts ON public.palabras_detalladas USING gin(to_tsvector('spanish', palabra_shuar));
CREATE INDEX idx_palabras_espanol_fts ON public.palabras_detalladas USING gin(to_tsvector('spanish', traduccion_espanol));
CREATE INDEX idx_palabras_definicion_fts ON public.palabras_detalladas USING gin(to_tsvector('spanish', definicion_detallada));

-- Trigram indexes for fuzzy matching
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_palabras_shuar_trgm ON public.palabras_detalladas USING gin(palabra_shuar gin_trgm_ops);
CREATE INDEX idx_palabras_espanol_trgm ON public.palabras_detalladas USING gin(traduccion_espanol gin_trgm_ops);

-- Composite indexes for common queries
CREATE INDEX idx_palabras_active_verified ON public.palabras_detalladas(status, verificado_por_hablante) WHERE status = 'active';
CREATE INDEX idx_palabras_search_combo ON public.palabras_detalladas(palabra_shuar, traduccion_espanol, categoria_gramatical) WHERE status = 'active';

-- ============================================
-- VARIANTES_PALABRAS TABLE (Word Variants)
-- ============================================
CREATE TABLE IF NOT EXISTS public.variantes_palabras (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- References
    palabra_principal_id UUID NOT NULL REFERENCES public.palabras_detalladas(id) ON DELETE CASCADE,
    
    -- Variant information
    variante VARCHAR(200) NOT NULL,
    tipo_variante VARCHAR(50) NOT NULL, -- dialectal, phonetic, morphological, orthographic
    dialecto VARCHAR(50),
    region VARCHAR(100),
    
    -- Usage information
    frecuencia_relativa DECIMAL(3,2) DEFAULT 0.50 CHECK (frecuencia_relativa >= 0.0 AND frecuencia_relativa <= 1.0),
    contexto_uso VARCHAR(200),
    notas TEXT,
    
    -- Verification
    verificado BOOLEAN DEFAULT false,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_variant UNIQUE (palabra_principal_id, variante, tipo_variante)
);

-- Indexes for variants
CREATE INDEX idx_variantes_principal ON public.variantes_palabras(palabra_principal_id);
CREATE INDEX idx_variantes_variante ON public.variantes_palabras(variante);
CREATE INDEX idx_variantes_tipo ON public.variantes_palabras(tipo_variante);
CREATE INDEX idx_variantes_dialecto ON public.variantes_palabras(dialecto);

-- ============================================
-- RELACIONES_PALABRAS TABLE (Word Relations)
-- ============================================
CREATE TABLE IF NOT EXISTS public.relaciones_palabras (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- References
    palabra_origen_id UUID NOT NULL REFERENCES public.palabras_detalladas(id) ON DELETE CASCADE,
    palabra_destino_id UUID NOT NULL REFERENCES public.palabras_detalladas(id) ON DELETE CASCADE,
    
    -- Relationship information
    tipo_relacion VARCHAR(50) NOT NULL, -- sinonimo, antonimo, derivada, compuesta, familia_lexica
    fuerza_relacion DECIMAL(3,2) DEFAULT 0.50 CHECK (fuerza_relacion >= 0.0 AND fuerza_relacion <= 1.0),
    direccional BOOLEAN DEFAULT false, -- if true, relation is one-way
    
    -- Context
    contexto VARCHAR(200),
    notas TEXT,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT different_words CHECK (palabra_origen_id != palabra_destino_id),
    CONSTRAINT unique_relation UNIQUE (palabra_origen_id, palabra_destino_id, tipo_relacion)
);

-- Indexes for relations
CREATE INDEX idx_relaciones_origen ON public.relaciones_palabras(palabra_origen_id);
CREATE INDEX idx_relaciones_destino ON public.relaciones_palabras(palabra_destino_id);
CREATE INDEX idx_relaciones_tipo ON public.relaciones_palabras(tipo_relacion);
CREATE INDEX idx_relaciones_fuerza ON public.relaciones_palabras(fuerza_relacion DESC);

-- ============================================
-- CATEGORIAS_GRAMATICALES TABLE (Grammar Categories)
-- ============================================
CREATE TABLE IF NOT EXISTS public.categorias_gramaticales (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Category information
    nombre VARCHAR(100) NOT NULL UNIQUE,
    nombre_shuar VARCHAR(100),
    descripcion TEXT,
    
    -- Hierarchy
    categoria_padre_id UUID REFERENCES public.categorias_gramaticales(id),
    nivel INTEGER DEFAULT 1,
    
    -- Properties
    propiedades JSONB, -- Grammatical properties specific to this category
    ejemplos TEXT[],
    
    -- Metadata
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert basic grammatical categories
INSERT INTO public.categorias_gramaticales (nombre, nombre_shuar, descripcion) VALUES
('sustantivo', 'nayaimpiniam', 'Palabras que nombran personas, lugares, cosas o conceptos'),
('verbo', 'takakmatniam', 'Palabras que expresan acciones, estados o procesos'),
('adjetivo', 'penkeratniam', 'Palabras que describen o califican sustantivos'),
('adverbio', 'itiur takakmatniam', 'Palabras que modifican verbos, adjetivos u otros adverbios'),
('pronombre', 'naari etserin', 'Palabras que sustituyen a los sustantivos'),
('preposición', 'yajauch chicham', 'Palabras que relacionan elementos en la oración'),
('conjunción', 'iruntrar chicham', 'Palabras que conectan palabras, frases u oraciones'),
('interjección', 'untsumatniam', 'Expresiones de emoción o exclamación'),
('partícula', 'uchich chicham', 'Elementos gramaticales sin significado léxico independiente');

-- ============================================
-- CAMPOS_SEMANTICOS TABLE (Semantic Fields)
-- ============================================
CREATE TABLE IF NOT EXISTS public.campos_semanticos (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Field information
    nombre VARCHAR(100) NOT NULL UNIQUE,
    nombre_shuar VARCHAR(100),
    descripcion TEXT,
    
    -- Hierarchy
    campo_padre_id UUID REFERENCES public.campos_semanticos(id),
    nivel INTEGER DEFAULT 1,
    
    -- Cultural context
    importancia_cultural INTEGER DEFAULT 1 CHECK (importancia_cultural >= 1 AND importancia_cultural <= 5),
    contexto_cultural TEXT,
    
    -- Metadata
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert basic semantic fields relevant to Shuar culture
INSERT INTO public.campos_semanticos (nombre, nombre_shuar, descripcion, importancia_cultural) VALUES
('naturaleza', 'nunka', 'Elementos del mundo natural', 5),
('familia', 'shuara', 'Relaciones familiares y parentesco', 5),
('animales', 'yawa', 'Fauna de la región amazónica', 5),
('plantas', 'numi', 'Flora medicinal y alimentaria', 5),
('ceremonias', 'natemamu', 'Rituales y ceremonias tradicionales', 5),
('caza', 'maaniamu', 'Actividades de caza y pesca', 4),
('agricultura', 'arakmamu', 'Cultivo y agricultura tradicional', 4),
('medicina', 'tsumarnamu', 'Medicina tradicional y plantas curativas', 4),
('música', 'nampet', 'Instrumentos y expresiones musicales', 3),
('artesanía', 'najanamu', 'Trabajos manuales y artesanías', 3),
('tiempo', 'tsawan', 'Conceptos temporales', 3),
('espacio', 'nunka', 'Conceptos espaciales y geográficos', 3),
('emociones', 'enentaimtus', 'Estados emocionales y sentimientos', 3),
('colores', 'yamaram', 'Colores y tonalidades', 2),
('números', 'namantu', 'Sistema numérico', 2);

-- ============================================
-- FUNCTIONS FOR DICTIONARY OPERATIONS
-- ============================================

-- Function to search words with fuzzy matching
CREATE OR REPLACE FUNCTION buscar_palabras(
    p_termino VARCHAR,
    p_idioma VARCHAR DEFAULT 'ambos', -- 'shuar', 'espanol', 'ambos'
    p_limite INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    palabra_shuar VARCHAR,
    traduccion_espanol VARCHAR,
    categoria_gramatical VARCHAR,
    similitud REAL
) AS $
BEGIN
    RETURN QUERY
    SELECT 
        pd.id,
        pd.palabra_shuar,
        pd.traduccion_espanol,
        pd.categoria_gramatical,
        CASE 
            WHEN p_idioma = 'shuar' THEN similarity(pd.palabra_shuar, p_termino)
            WHEN p_idioma = 'espanol' THEN similarity(pd.traduccion_espanol, p_termino)
            ELSE GREATEST(
                similarity(pd.palabra_shuar, p_termino),
                similarity(pd.traduccion_espanol, p_termino)
            )
        END as similitud
    FROM public.palabras_detalladas pd
    WHERE pd.status = 'active'
    AND (
        CASE 
            WHEN p_idioma = 'shuar' THEN pd.palabra_shuar % p_termino
            WHEN p_idioma = 'espanol' THEN pd.traduccion_espanol % p_termino
            ELSE (pd.palabra_shuar % p_termino OR pd.traduccion_espanol % p_termino)
        END
    )
    ORDER BY similitud DESC
    LIMIT p_limite;
END;
$ language 'plpgsql';

-- Function to get word statistics
CREATE OR REPLACE FUNCTION estadisticas_diccionario()
RETURNS JSON AS $
DECLARE
    result JSON;
BEGIN
    SELECT json_build_object(
        'total_palabras', (SELECT COUNT(*) FROM public.palabras_detalladas WHERE status = 'active'),
        'palabras_verificadas', (SELECT COUNT(*) FROM public.palabras_detalladas WHERE verificado_por_hablante = true),
        'por_categoria', (
            SELECT json_object_agg(categoria_gramatical, count)
            FROM (
                SELECT categoria_gramatical, COUNT(*) as count
                FROM public.palabras_detalladas 
                WHERE status = 'active'
                GROUP BY categoria_gramatical
            ) cats
        ),
        'por_campo_semantico', (
            SELECT json_object_agg(campo_semantico, count)
            FROM (
                SELECT campo_semantico, COUNT(*) as count
                FROM public.palabras_detalladas 
                WHERE status = 'active' AND campo_semantico IS NOT NULL
                GROUP BY campo_semantico
            ) campos
        ),
        'por_dialecto', (
            SELECT json_object_agg(dialecto, count)
            FROM (
                SELECT dialecto, COUNT(*) as count
                FROM public.palabras_detalladas 
                WHERE status = 'active' AND dialecto IS NOT NULL
                GROUP BY dialecto
            ) dialectos
        )
    ) INTO result;
    
    RETURN result;
END;
$ language 'plpgsql';

-- ============================================
-- TRIGGERS
-- ============================================

-- Trigger for updated_at
CREATE TRIGGER update_palabras_updated_at 
    BEFORE UPDATE ON public.palabras_detalladas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

-- Enable RLS
ALTER TABLE public.palabras_detalladas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.variantes_palabras ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.relaciones_palabras ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.categorias_gramaticales ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.campos_semanticos ENABLE ROW LEVEL SECURITY;

-- RLS Policies for dictionary (read access for all, write for experts)
CREATE POLICY "Dictionary visible to all" ON public.palabras_detalladas
    FOR SELECT USING (status = 'active');

CREATE POLICY "Experts can manage dictionary" ON public.palabras_detalladas
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM auth.users 
            WHERE id = auth.uid() 
            AND raw_user_meta_data->>'role' IN ('expert', 'admin')
        )
    );

-- Similar policies for related tables
CREATE POLICY "Variants visible to all" ON public.variantes_palabras FOR SELECT USING (true);
CREATE POLICY "Relations visible to all" ON public.relaciones_palabras FOR SELECT USING (true);
CREATE POLICY "Categories visible to all" ON public.categorias_gramaticales FOR SELECT USING (activo = true);
CREATE POLICY "Semantic fields visible to all" ON public.campos_semanticos FOR SELECT USING (activo = true);

-- ============================================
-- COMMENTS
-- ============================================

COMMENT ON TABLE public.palabras_detalladas IS 'Main dictionary table with detailed Shuar-Spanish word pairs';
COMMENT ON TABLE public.variantes_palabras IS 'Dialectal and phonetic variants of dictionary words';
COMMENT ON TABLE public.relaciones_palabras IS 'Semantic and morphological relationships between words';
COMMENT ON TABLE public.categorias_gramaticales IS 'Hierarchical grammatical categories';
COMMENT ON TABLE public.campos_semanticos IS 'Semantic fields for cultural and thematic organization';

COMMENT ON COLUMN public.palabras_detalladas.morfemas IS 'JSON structure with detailed morphological analysis';
COMMENT ON COLUMN public.palabras_detalladas.ejemplos_uso IS 'JSON array of usage examples with context and translations';
COMMENT ON COLUMN public.palabras_detalladas.tipo_vocal IS 'Shuar vocal types: normal, larga (long), glotalizada (glottalized)';