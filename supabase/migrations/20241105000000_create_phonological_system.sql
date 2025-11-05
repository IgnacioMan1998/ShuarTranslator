-- ============================================
-- MIGRATION 000: Create Shuar Phonological System
-- Description: Create foundational tables for Shuar alphabet and phonology
-- ============================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Ensure the extension is available in the current session
SET search_path TO public, extensions;

-- ============================================
-- ALFABETO SHUAR - Base del sistema fonológico
-- ============================================
CREATE TABLE IF NOT EXISTS public.alfabeto_shuar (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Letra/fonema
    letra VARCHAR(10) NOT NULL UNIQUE,
    nombre_letra VARCHAR(50),
    
    -- Clasificación fonológica
    tipo_fonema VARCHAR(20) NOT NULL CHECK (tipo_fonema IN ('vocal', 'consonante', 'semiconsonante')),
    categoria_articulatoria VARCHAR(50), -- Para consonantes: oclusiva, fricativa, nasal, etc.
    punto_articulacion VARCHAR(50), -- bilabial, dental, alveolar, etc.
    modo_articulacion VARCHAR(50), -- sonora, sorda, etc.
    
    -- Representación fonética
    simbolo_ipa VARCHAR(10), -- Símbolo en Alfabeto Fonético Internacional
    alofono_principal VARCHAR(10), -- Alófono más común
    alofonos_variantes VARCHAR(100)[], -- Variantes alofónicas
    
    -- Distribución y frecuencia
    posicion_silaba VARCHAR(50)[], -- inicial, media, final
    frecuencia_uso INTEGER DEFAULT 1 CHECK (frecuencia_uso >= 1 AND frecuencia_uso <= 10),
    
    -- Información pedagógica
    dificultad_pronunciacion INTEGER DEFAULT 1 CHECK (dificultad_pronunciacion >= 1 AND dificultad_pronunciacion <= 5),
    notas_pronunciacion TEXT,
    ejemplos_palabras VARCHAR(100)[],
    
    -- Metadata
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- TIPOS DE VOCALES SHUAR - Sistema vocálico específico
-- ============================================
CREATE TABLE IF NOT EXISTS public.tipos_vocales_shuar (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Vocal base
    vocal_base VARCHAR(5) NOT NULL, -- a, e, i, u
    
    -- Tipo específico Shuar
    tipo_vocal VARCHAR(20) NOT NULL CHECK (tipo_vocal IN ('normal', 'larga', 'glotalizada')),
    nombre_tipo VARCHAR(50),
    descripcion TEXT,
    
    -- Representación ortográfica y fonética
    representacion_ortografica VARCHAR(10), -- Como se escribe
    simbolo_ipa VARCHAR(10), -- Representación IPA
    simbolo_practico VARCHAR(10), -- Representación práctica para teclado
    
    -- Características acústicas
    duracion_relativa DECIMAL(3,2), -- Duración relativa (1.0 = normal)
    tono_caracteristico VARCHAR(50), -- alto, bajo, descendente, etc.
    
    -- Distribución fonológica
    posicion_palabra VARCHAR(50)[], -- inicial, media, final
    contextos_aparicion TEXT[], -- Contextos donde aparece
    
    -- Información pedagógica
    dificultad_aprendizaje INTEGER DEFAULT 1 CHECK (dificultad_aprendizaje >= 1 AND dificultad_aprendizaje <= 5),
    consejos_pronunciacion TEXT,
    errores_comunes TEXT[],
    
    -- Ejemplos
    ejemplos_minimos JSONB, -- Pares mínimos que contrastan este tipo
    palabras_ejemplo VARCHAR(100)[],
    
    -- Metadata
    frecuencia_lengua INTEGER DEFAULT 1 CHECK (frecuencia_lengua >= 1 AND frecuencia_lengua <= 10),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT unique_vocal_tipo UNIQUE (vocal_base, tipo_vocal)
);

-- ============================================
-- REGLAS FONOLÓGICAS - Procesos fonológicos del Shuar
-- ============================================
CREATE TABLE IF NOT EXISTS public.reglas_fonologicas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Identificación de la regla
    nombre_regla VARCHAR(100) NOT NULL,
    tipo_regla VARCHAR(50) NOT NULL, -- asimilacion, elisión, inserción, etc.
    descripcion TEXT NOT NULL,
    
    -- Contexto fonológico
    fonema_objetivo VARCHAR(10), -- Fonema que cambia
    fonema_resultado VARCHAR(10), -- Resultado del cambio
    contexto_izquierdo VARCHAR(50), -- Contexto fonológico izquierdo
    contexto_derecho VARCHAR(50), -- Contexto fonológico derecho
    
    -- Condiciones
    obligatoria BOOLEAN DEFAULT true, -- Si la regla es obligatoria u opcional
    dialectos_aplicables VARCHAR(50)[], -- En qué dialectos se aplica
    registro_aplicable VARCHAR(50)[], -- formal, informal, etc.
    
    -- Ejemplos
    ejemplos_aplicacion JSONB, -- Ejemplos de la regla en acción
    contraejemplos JSONB, -- Casos donde no se aplica
    
    -- Información técnica
    orden_aplicacion INTEGER, -- Orden en que se aplica respecto a otras reglas
    productividad INTEGER DEFAULT 1 CHECK (productividad >= 1 AND productividad <= 5),
    
    -- Metadata
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- PATRONES SILÁBICOS - Estructura silábica del Shuar
-- ============================================
CREATE TABLE IF NOT EXISTS public.patrones_silabicos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    
    -- Patrón silábico
    patron VARCHAR(20) NOT NULL UNIQUE, -- CV, CVC, V, etc.
    descripcion VARCHAR(100),
    estructura_detallada VARCHAR(50), -- Consonante + Vocal + Consonante, etc.
    
    -- Frecuencia y distribución
    frecuencia_lengua INTEGER DEFAULT 1 CHECK (frecuencia_lengua >= 1 AND frecuencia_lengua <= 10),
    posicion_palabra VARCHAR(50)[], -- inicial, media, final
    
    -- Restricciones
    consonantes_permitidas_inicio VARCHAR(20)[],
    consonantes_permitidas_final VARCHAR(20)[],
    vocales_permitidas VARCHAR(10)[],
    restricciones_especiales TEXT,
    
    -- Ejemplos
    ejemplos_palabras VARCHAR(100)[],
    
    -- Metadata
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- INSERTAR DATOS DEL ALFABETO SHUAR
-- ============================================

-- Vocales normales
INSERT INTO public.alfabeto_shuar (letra, nombre_letra, tipo_fonema, simbolo_ipa, frecuencia_uso, ejemplos_palabras) VALUES
('a', 'a normal', 'vocal', 'a', 10, ARRAY['apa', 'yawa', 'namak']),
('e', 'e normal', 'vocal', 'e', 7, ARRAY['entsa', 'penker']),
('i', 'i normal', 'vocal', 'i', 9, ARRAY['jintia', 'chikichik']),
('u', 'u normal', 'vocal', 'u', 8, ARRAY['nukur', 'kuntin']);

-- Consonantes
INSERT INTO public.alfabeto_shuar (letra, nombre_letra, tipo_fonema, categoria_articulatoria, punto_articulacion, simbolo_ipa, frecuencia_uso, ejemplos_palabras) VALUES
('ch', 'che', 'consonante', 'africada', 'alveopalatal', 'tʃ', 6, ARRAY['yachi', 'chikichik']),
('j', 'jota', 'consonante', 'fricativa', 'velar', 'χ', 7, ARRAY['jintia', 'jimiar']),
('k', 'ka', 'consonante', 'oclusiva', 'velar', 'k', 8, ARRAY['kuntin', 'nukur']),
('m', 'eme', 'consonante', 'nasal', 'bilabial', 'm', 7, ARRAY['namak', 'yamaikia']),
('n', 'ene', 'consonante', 'nasal', 'alveolar', 'n', 9, ARRAY['nukur', 'nayaim']),
('p', 'pe', 'consonante', 'oclusiva', 'bilabial', 'p', 6, ARRAY['apa', 'penker']),
('r', 'ere', 'consonante', 'vibrante', 'alveolar', 'r', 8, ARRAY['nukur', 'arutam']),
('s', 'ese', 'consonante', 'fricativa', 'alveolar', 's', 7, ARRAY['kashin', 'wekasai']),
('sh', 'she', 'consonante', 'fricativa', 'alveopalatal', 'ʃ', 4, ARRAY['kashin', 'yajasma']),
('t', 'te', 'consonante', 'oclusiva', 'alveolar', 't', 9, ARRAY['natem', 'takasai']),
('ts', 'tse', 'consonante', 'africada', 'alveolar', 'ts', 5, ARRAY['entsa']),
('w', 'we', 'semiconsonante', 'aproximante', 'bilabial', 'w', 8, ARRAY['yawa', 'wekasai']),
('y', 'ye', 'semiconsonante', 'aproximante', 'palatal', 'j', 9, ARRAY['yawa', 'yamaikia']);

-- ============================================
-- INSERTAR TIPOS DE VOCALES SHUAR
-- ============================================

-- Vocales normales (breves)
INSERT INTO public.tipos_vocales_shuar (
    vocal_base, tipo_vocal, nombre_tipo, descripcion, representacion_ortografica, 
    simbolo_ipa, duracion_relativa, frecuencia_lengua, ejemplos_minimos, palabras_ejemplo
) VALUES
('a', 'normal', 'A normal', 'Vocal a de duración normal', 'a', 'a', 1.0, 10, 
 '{"contraste": "a vs aa", "ejemplos": [{"normal": "apa", "larga": "aapa"}]}'::jsonb,
 ARRAY['apa', 'yawa', 'namak']),
 
('e', 'normal', 'E normal', 'Vocal e de duración normal', 'e', 'e', 1.0, 7,
 '{"contraste": "e vs ee", "ejemplos": [{"normal": "entsa", "larga": "eentsa"}]}'::jsonb,
 ARRAY['entsa', 'penker']),
 
('i', 'normal', 'I normal', 'Vocal i de duración normal', 'i', 'i', 1.0, 9,
 '{"contraste": "i vs ii", "ejemplos": [{"normal": "jintia", "larga": "jiintia"}]}'::jsonb,
 ARRAY['jintia', 'chikichik']),
 
('u', 'normal', 'U normal', 'Vocal u de duración normal', 'u', 'u', 1.0, 8,
 '{"contraste": "u vs uu", "ejemplos": [{"normal": "nukur", "larga": "nuukur"}]}'::jsonb,
 ARRAY['nukur', 'kuntin']);

-- Vocales largas
INSERT INTO public.tipos_vocales_shuar (
    vocal_base, tipo_vocal, nombre_tipo, descripcion, representacion_ortografica, 
    simbolo_ipa, simbolo_practico, duracion_relativa, frecuencia_lengua, 
    dificultad_aprendizaje, consejos_pronunciacion, palabras_ejemplo
) VALUES
('a', 'larga', 'A larga', 'Vocal a de duración extendida, aproximadamente el doble', 'aa', 'aː', 'aa', 2.0, 6, 3,
 'Mantener el sonido por más tiempo, como si fueras a decir dos aes seguidas pero sin pausa',
 ARRAY['aapa', 'kaap']),
 
('e', 'larga', 'E larga', 'Vocal e de duración extendida', 'ee', 'eː', 'ee', 2.0, 4, 3,
 'Prolongar el sonido de la e sin cambiar la calidad vocal',
 ARRAY['eent', 'neer']),
 
('i', 'larga', 'I larga', 'Vocal i de duración extendida', 'ii', 'iː', 'ii', 2.0, 5, 3,
 'Estirar el sonido de la i manteniendo la misma altura tonal',
 ARRAY['wiik', 'shiir']),
 
('u', 'larga', 'U larga', 'Vocal u de duración extendida', 'uu', 'uː', 'uu', 2.0, 4, 3,
 'Prolongar la u sin redondear demasiado los labios',
 ARRAY['nuuk', 'tuun']);

-- Vocales glotalizadas
INSERT INTO public.tipos_vocales_shuar (
    vocal_base, tipo_vocal, nombre_tipo, descripcion, representacion_ortografica, 
    simbolo_ipa, simbolo_practico, duracion_relativa, tono_caracteristico,
    frecuencia_lengua, dificultad_aprendizaje, consejos_pronunciacion, 
    errores_comunes, palabras_ejemplo
) VALUES
('a', 'glotalizada', 'A glotalizada', 'Vocal a con cierre glotal, sonido cortado', 'a''', 'aʔ', 'a_', 1.0, 'cortado', 3, 5,
 'Cortar abruptamente el sonido con un cierre en la garganta, como cuando dices "uh-oh"',
 ARRAY['Confundir con vocal normal', 'No hacer el cierre glotal completo'],
 ARRAY['a''pa', 'ya''wa']),
 
('e', 'glotalizada', 'E glotalizada', 'Vocal e con cierre glotal', 'e''', 'eʔ', 'e_', 1.0, 'cortado', 2, 5,
 'Hacer el sonido de e y cortarlo bruscamente cerrando la glotis',
 ARRAY['Hacer una pausa en lugar del cierre glotal', 'Prolongar demasiado antes del corte'],
 ARRAY['e''nt', 'pe''nker']),
 
('i', 'glotalizada', 'I glotalizada', 'Vocal i con cierre glotal', 'i''', 'iʔ', 'i_', 1.0, 'cortado', 2, 5,
 'Producir la i y terminar con un corte seco en la garganta',
 ARRAY['No distinguir del sonido normal', 'Hacer el corte demasiado suave'],
 ARRAY['ji''ntia', 'chi''ki']),
 
('u', 'glotalizada', 'U glotalizada', 'Vocal u con cierre glotal', 'u''', 'uʔ', 'u_', 1.0, 'cortado', 2, 5,
 'Emitir la u y cortarla abruptamente con la glotis',
 ARRAY['Confundir con u normal', 'Hacer una pausa larga en lugar del corte'],
 ARRAY['nu''kur', 'ku''ntin']);

-- ============================================
-- INSERTAR PATRONES SILÁBICOS COMUNES
-- ============================================
INSERT INTO public.patrones_silabicos (
    patron, descripcion, estructura_detallada, frecuencia_lengua, 
    posicion_palabra, ejemplos_palabras
) VALUES
('CV', 'Consonante + Vocal', 'Consonante seguida de vocal', 10, 
 ARRAY['inicial', 'media', 'final'], ARRAY['ya-wa', 'nu-kur', 'a-pa']),
 
('CVC', 'Consonante + Vocal + Consonante', 'Sílaba cerrada por consonante', 8,
 ARRAY['inicial', 'media', 'final'], ARRAY['kun-tin', 'nam-ak']),
 
('V', 'Solo Vocal', 'Vocal sin consonante inicial', 6,
 ARRAY['inicial', 'media'], ARRAY['a-pa', 'i-wi']),
 
('CCV', 'Consonante + Consonante + Vocal', 'Grupo consonántico inicial', 3,
 ARRAY['inicial', 'media'], ARRAY['tsu-mar']),
 
('VC', 'Vocal + Consonante', 'Vocal seguida de consonante', 5,
 ARRAY['media', 'final'], ARRAY['en-tsa', 'ar-utam']);

-- ============================================
-- INSERTAR REGLAS FONOLÓGICAS BÁSICAS
-- ============================================
INSERT INTO public.reglas_fonologicas (
    nombre_regla, tipo_regla, descripcion, fonema_objetivo, fonema_resultado,
    contexto_derecho, obligatoria, ejemplos_aplicacion
) VALUES
('Asimilación nasal', 'asimilacion', 'Las nasales se asimilan al punto de articulación de la consonante siguiente',
 'n', 'm', 'p,b', true,
 '{"ejemplos": [{"input": "anpa", "output": "ampa", "glosa": "padre"}]}'::jsonb),
 
('Elisión vocálica', 'elision', 'Elisión de vocal átona en contacto con otra vocal',
 'a,e,i,u', '∅', 'a,e,i,u', false,
 '{"ejemplos": [{"input": "yawa apa", "output": "yawapa", "glosa": "perro padre"}]}'::jsonb),
 
('Glotalización final', 'insercion', 'Inserción de cierre glotal en final de palabra en ciertos contextos',
 '∅', 'ʔ', '#', false,
 '{"ejemplos": [{"input": "yawa", "output": "yawaʔ", "contexto": "énfasis"}]}'::jsonb);

-- ============================================
-- ÍNDICES PARA BÚSQUEDA EFICIENTE
-- ============================================

-- Índices para alfabeto
CREATE INDEX idx_alfabeto_letra ON public.alfabeto_shuar(letra);
CREATE INDEX idx_alfabeto_tipo ON public.alfabeto_shuar(tipo_fonema);
CREATE INDEX idx_alfabeto_ipa ON public.alfabeto_shuar(simbolo_ipa);

-- Índices para tipos de vocales
CREATE INDEX idx_vocales_base ON public.tipos_vocales_shuar(vocal_base);
CREATE INDEX idx_vocales_tipo ON public.tipos_vocales_shuar(tipo_vocal);
CREATE INDEX idx_vocales_frecuencia ON public.tipos_vocales_shuar(frecuencia_lengua DESC);

-- Índices para patrones silábicos
CREATE INDEX idx_patrones_patron ON public.patrones_silabicos(patron);
CREATE INDEX idx_patrones_frecuencia ON public.patrones_silabicos(frecuencia_lengua DESC);

-- Índices para reglas fonológicas
CREATE INDEX idx_reglas_tipo ON public.reglas_fonologicas(tipo_regla);
CREATE INDEX idx_reglas_activa ON public.reglas_fonologicas(activo) WHERE activo = true;

-- ============================================
-- FUNCIONES PARA ANÁLISIS FONOLÓGICO
-- ============================================

-- Función para analizar la estructura fonológica de una palabra
CREATE OR REPLACE FUNCTION analizar_fonologia_palabra(p_palabra VARCHAR)
RETURNS JSON AS $$
DECLARE
    resultado JSON;
    silabas TEXT[];
    tipos_vocales TEXT[];
    patron_silabico TEXT;
BEGIN
    -- Análisis básico de la palabra
    SELECT json_build_object(
        'palabra', p_palabra,
        'longitud', LENGTH(p_palabra),
        'contiene_vocales_largas', p_palabra ~ '(aa|ee|ii|uu)',
        'contiene_glotalizadas', p_palabra ~ '''',
        'estructura_basica', CASE 
            WHEN p_palabra ~ '^[aeiou]' THEN 'inicia_vocal'
            ELSE 'inicia_consonante'
        END,
        'termina_en', CASE 
            WHEN p_palabra ~ '[aeiou]$' THEN 'vocal'
            ELSE 'consonante'
        END
    ) INTO resultado;
    
    RETURN resultado;
END;
$$ language 'plpgsql';

-- Función para obtener información de un tipo de vocal
CREATE OR REPLACE FUNCTION info_tipo_vocal(p_vocal VARCHAR, p_tipo VARCHAR)
RETURNS JSON AS $$
DECLARE
    info JSON;
BEGIN
    SELECT json_build_object(
        'vocal', vocal_base,
        'tipo', tipo_vocal,
        'representacion', representacion_ortografica,
        'ipa', simbolo_ipa,
        'duracion_relativa', duracion_relativa,
        'dificultad', dificultad_aprendizaje,
        'consejos', consejos_pronunciacion,
        'ejemplos', palabras_ejemplo
    ) INTO info
    FROM public.tipos_vocales_shuar
    WHERE vocal_base = p_vocal AND tipo_vocal = p_tipo;
    
    RETURN info;
END;
$$ language 'plpgsql';

-- ============================================
-- ROW LEVEL SECURITY
-- ============================================

-- Habilitar RLS (solo lectura pública, escritura para expertos)
ALTER TABLE public.alfabeto_shuar ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tipos_vocales_shuar ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reglas_fonologicas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.patrones_silabicos ENABLE ROW LEVEL SECURITY;

-- Políticas de lectura pública
CREATE POLICY "Alfabeto visible para todos" ON public.alfabeto_shuar FOR SELECT USING (activo = true);
CREATE POLICY "Tipos vocales visibles para todos" ON public.tipos_vocales_shuar FOR SELECT USING (activo = true);
CREATE POLICY "Reglas fonológicas visibles para todos" ON public.reglas_fonologicas FOR SELECT USING (activo = true);
CREATE POLICY "Patrones silábicos visibles para todos" ON public.patrones_silabicos FOR SELECT USING (activo = true);

-- ============================================
-- COMENTARIOS PARA DOCUMENTACIÓN
-- ============================================

COMMENT ON TABLE public.alfabeto_shuar IS 'Alfabeto completo del idioma Shuar con información fonológica';
COMMENT ON TABLE public.tipos_vocales_shuar IS 'Sistema vocálico Shuar: normales, largas y glotalizadas';
COMMENT ON TABLE public.reglas_fonologicas IS 'Reglas de procesos fonológicos del Shuar';
COMMENT ON TABLE public.patrones_silabicos IS 'Patrones de estructura silábica permitidos en Shuar';

COMMENT ON COLUMN public.tipos_vocales_shuar.tipo_vocal IS 'Tres tipos: normal (breve), larga (duración extendida), glotalizada (con cierre glotal)';
COMMENT ON COLUMN public.tipos_vocales_shuar.duracion_relativa IS 'Duración relativa: 1.0=normal, 2.0=larga, 1.0=glotalizada';
COMMENT ON COLUMN public.alfabeto_shuar.simbolo_ipa IS 'Representación en Alfabeto Fonético Internacional';