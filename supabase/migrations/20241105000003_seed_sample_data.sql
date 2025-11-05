-- ============================================
-- MIGRATION 003: Seed Sample Dictionary Data
-- Description: Insert sample Shuar vocabulary for testing
-- ============================================

-- Sample Shuar words with detailed linguistic information
INSERT INTO public.palabras_detalladas (
    palabra_shuar, traduccion_espanol, categoria_gramatical, subcategoria,
    pronunciacion_ipa, silabas, tipos_vocales_presentes, estructura_silabica,
    analisis_fonologico, definicion_detallada, campo_semantico, nivel_formalidad, 
    frecuencia_uso, nivel_dificultad, verificado_por_hablante, confiabilidad_score, 
    fuente, ejemplos_uso
) VALUES 

-- Basic family terms
('apa', 'padre', 'sustantivo', 'parentesco', 'apa', 'a-pa', ARRAY['normal'], 'V-CV',
 '{"vocales": [{"posicion": 1, "vocal": "a", "tipo": "normal"}, {"posicion": 2, "vocal": "a", "tipo": "normal"}], "consonantes": [{"posicion": 2, "consonante": "p"}], "patron_acentual": "grave"}'::jsonb,
 'Padre, progenitor masculino en la familia shuar', 'familia', 'neutral', 10, 1, 
 true, 0.95, 'Diccionario Shuar-Castellano Salesiano',
 '[{"shuar": "Winia apa puujui", "espanol": "Mi padre está trabajando", "contexto": "conversación familiar"}]'::jsonb),

('nukur', 'madre', 'sustantivo', 'parentesco', 'nukur', 'nu-kur', ARRAY['normal'], 'CV-CVC',
 '{"vocales": [{"posicion": 1, "vocal": "u", "tipo": "normal"}, {"posicion": 2, "vocal": "u", "tipo": "normal"}], "consonantes": [{"posicion": 1, "consonante": "n"}, {"posicion": 2, "consonante": "k"}, {"posicion": 3, "consonante": "r"}], "patron_acentual": "grave"}'::jsonb,
 'Madre, progenitora femenina en la familia shuar', 'familia', 'neutral', 10, 1,
 true, 0.95, 'Diccionario Shuar-Castellano Salesiano',
 '[{"shuar": "Nukur yurumkan najanawai", "espanol": "La madre está cocinando", "contexto": "actividad doméstica"}]'::jsonb),

('yachi', 'hijo/hija', 'sustantivo', 'parentesco', 'jatʃi', 'ya-chi', ARRAY['normal'], 'CV-CV',
 '{"vocales": [{"posicion": 1, "vocal": "a", "tipo": "normal"}, {"posicion": 2, "vocal": "i", "tipo": "normal"}], "consonantes": [{"posicion": 1, "consonante": "y"}, {"posicion": 2, "consonante": "ch"}], "patron_acentual": "grave"}'::jsonb,
 'Hijo o hija, descendiente directo', 'familia', 'neutral', 9, 1,
 true, 0.90, 'Diccionario Shuar-Castellano Salesiano',
 '[{"shuar": "Yachi unuimiatai wakeruiti", "espanol": "El hijo quiere estudiar", "contexto": "educación"}]'::jsonb),

-- Animals
('yawa', 'perro', 'sustantivo', 'animal doméstico', 'jawa', 'ya-wa', 'normal',
 'Perro doméstico, compañero de caza y guardián', 'animales', 'neutral', 8, 1,
 true, 0.95, 'Observación directa',
 '[{"shuar": "Yawa kuntinian wekayi", "espanol": "El perro fue a cazar", "contexto": "actividad de caza"}]'::jsonb),

('namak', 'pez', 'sustantivo', 'animal acuático', 'namak', 'na-mak', 'normal',
 'Pez de río, importante fuente de proteína', 'animales', 'neutral', 7, 1,
 true, 0.90, 'Diccionario Shuar-Castellano Salesiano',
 '[{"shuar": "Namak achiktin ajasai", "espanol": "Vamos a pescar", "contexto": "invitación a pescar"}]'::jsonb),

('kuntin', 'sachavaca, tapir', 'sustantivo', 'animal selvático', 'kuntin', 'kun-tin', 'normal',
 'Tapir amazónico, animal de caza mayor muy valorado', 'animales', 'neutral', 4, 2,
 true, 0.85, 'Conocimiento tradicional',
 '[{"shuar": "Kuntin achuar wekayi", "espanol": "Fue a cazar tapir", "contexto": "caza mayor"}]'::jsonb),

-- Plants and food
('yuca', 'yuca', 'sustantivo', 'planta alimenticia', 'juka', 'yu-ca', 'normal',
 'Mandioca, tubérculo base de la alimentación shuar', 'plantas', 'neutral', 10, 1,
 true, 0.95, 'Conocimiento agrícola tradicional',
 '[{"shuar": "Yuca arakmaji", "espanol": "Vamos a sembrar yuca", "contexto": "agricultura"}]'::jsonb),

('nijiamanch', 'plátano', 'sustantivo', 'fruta', 'niχiamanʃ', 'ni-jia-manch', 'normal',
 'Plátano, fruta importante en la dieta shuar', 'plantas', 'neutral', 9, 2,
 true, 0.90, 'Conocimiento agrícola tradicional',
 '[{"shuar": "Nijiamanch yurumai", "espanol": "Está maduro el plátano", "contexto": "cosecha"}]'::jsonb),

-- Verbs - basic actions
('wekasai', 'ir', 'verbo', 'movimiento', 'wekasai', 'we-ka-sai', 'normal',
 'Ir, moverse hacia un lugar', 'movimiento', 'neutral', 10, 1,
 true, 0.95, 'Gramática Shuar',
 '[{"shuar": "Jintia wekajai", "espanol": "Voy al río", "contexto": "movimiento"}]'::jsonb),

('yurumai', 'estar maduro', 'verbo', 'estado', 'jurumai', 'yu-ru-mai', 'normal',
 'Estar en estado de madurez, listo para consumir', 'estado', 'neutral', 6, 2,
 true, 0.85, 'Observación agrícola',
 '[{"shuar": "Uwi yurumai", "espanol": "La fruta está madura", "contexto": "agricultura"}]'::jsonb),

('takasai', 'hacer, trabajar', 'verbo', 'acción', 'takasai', 'ta-ka-sai', 'normal',
 'Realizar una acción, trabajar, hacer algo', 'acción', 'neutral', 9, 1,
 true, 0.90, 'Gramática Shuar',
 '[{"shuar": "Jea najanai takasai", "espanol": "Está haciendo la casa", "contexto": "construcción"}]'::jsonb),

-- Nature and environment
('jintia', 'río', 'sustantivo', 'geografía', 'χintia', 'jin-tia', 'normal',
 'Río, curso de agua importante para la vida shuar', 'naturaleza', 'neutral', 8, 1,
 true, 0.95, 'Conocimiento geográfico',
 '[{"shuar": "Jintia pujutai wakerujai", "espanol": "Quiero vivir cerca del río", "contexto": "ubicación"}]'::jsonb),

('nayaim', 'selva, monte', 'sustantivo', 'geografía', 'najaim', 'na-yaim', 'normal',
 'Selva amazónica, bosque primario', 'naturaleza', 'neutral', 7, 2,
 true, 0.90, 'Conocimiento geográfico',
 '[{"shuar": "Nayaim kuntinian wekayi", "espanol": "Fue a cazar al monte", "contexto": "caza"}]'::jsonb),

-- Cultural concepts
('arutam', 'alma, espíritu', 'sustantivo', 'concepto espiritual', 'arutam', 'a-ru-tam', 'normal',
 'Alma o espíritu que da fuerza y poder a la persona', 'ceremonias', 'formal', 3, 4,
 true, 0.95, 'Conocimiento espiritual tradicional',
 '[{"shuar": "Arutam achiktin wekayi", "espanol": "Fue a buscar visión espiritual", "contexto": "ritual"}]'::jsonb),

('natem', 'ayahuasca', 'sustantivo', 'planta sagrada', 'natem', 'na-tem', 'normal',
 'Planta sagrada usada en ceremonias espirituales', 'ceremonias', 'formal', 2, 5,
 true, 0.95, 'Conocimiento ceremonial',
 '[{"shuar": "Natem umartai", "espanol": "Va a tomar ayahuasca", "contexto": "ceremonia"}]'::jsonb),

-- Adjectives
('pénker', 'bueno', 'adjetivo', 'calificativo', 'penker', 'pén-ker', 'normal',
 'Bueno, de buena calidad, correcto', 'cualidad', 'neutral', 8, 1,
 true, 0.90, 'Uso cotidiano',
 '[{"shuar": "Ju yurumak pénker", "espanol": "Esta comida está buena", "contexto": "evaluación"}]'::jsonb),

('yajasma', 'malo', 'adjetivo', 'calificativo', 'jaχasma', 'ya-jas-ma', 'normal',
 'Malo, de mala calidad, incorrecto', 'cualidad', 'neutral', 6, 2,
 true, 0.85, 'Uso cotidiano',
 '[{"shuar": "Ju natem yajasma", "espanol": "Esta medicina está mala", "contexto": "evaluación"}]'::jsonb),

-- Numbers
('chikichik', 'uno', 'numeral', 'cardinal', 'tʃikitʃik', 'chi-ki-chik', 'normal',
 'Número uno, unidad', 'números', 'neutral', 9, 1,
 true, 0.95, 'Sistema numérico tradicional',
 '[{"shuar": "Chikichik yawa", "espanol": "Un perro", "contexto": "conteo"}]'::jsonb),

('jimiar', 'dos', 'numeral', 'cardinal', 'χimiar', 'ji-miar', 'normal',
 'Número dos', 'números', 'neutral', 8, 1,
 true, 0.95, 'Sistema numérico tradicional',
 '[{"shuar": "Jimiar nukur", "espanol": "Dos madres", "contexto": "conteo"}]'::jsonb),

-- Time concepts
('yamaikia', 'ahora', 'adverbio', 'temporal', 'jamaikia', 'ya-mai-kia', 'normal',
 'En este momento, ahora', 'tiempo', 'neutral', 8, 2,
 true, 0.90, 'Expresiones temporales',
 '[{"shuar": "Yamaikia wekasai", "espanol": "Ahora voy", "contexto": "tiempo presente"}]'::jsonb),

('kashin', 'mañana', 'adverbio', 'temporal', 'kaʃin', 'ka-shin', 'normal',
 'El día siguiente, mañana', 'tiempo', 'neutral', 7, 2,
 true, 0.85, 'Expresiones temporales',
 '[{"shuar": "Kashin takatnuitjai", "espanol": "Mañana trabajaré", "contexto": "planificación"}]'::jsonb);

-- Insert word variants
INSERT INTO public.variantes_palabras (palabra_principal_id, variante, tipo_variante, dialecto, contexto_uso) VALUES
((SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'yawa'), 'yau', 'dialectal', 'Achuar', 'Variante achuar del término'),
((SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'nukur'), 'nukuch', 'dialectal', 'Shiwiar', 'Variante shiwiar'),
((SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'jintia'), 'entsa', 'dialectal', 'Achuar', 'Término achuar para río');

-- Insert word relations (synonyms, antonyms, etc.)
INSERT INTO public.relaciones_palabras (palabra_origen_id, palabra_destino_id, tipo_relacion, fuerza_relacion) VALUES
((SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'pénker'), 
 (SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'yajasma'), 
 'antonimo', 0.95),
((SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'apa'), 
 (SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'nukur'), 
 'familia_lexica', 0.80);

-- Update semantic fields for the inserted words
UPDATE public.palabras_detalladas SET campo_semantico = 'familia' 
WHERE palabra_shuar IN ('apa', 'nukur', 'yachi');

UPDATE public.palabras_detalladas SET campo_semantico = 'animales' 
WHERE palabra_shuar IN ('yawa', 'namak', 'kuntin');

UPDATE public.palabras_detalladas SET campo_semantico = 'plantas' 
WHERE palabra_shuar IN ('yuca', 'nijiamanch');

UPDATE public.palabras_detalladas SET campo_semantico = 'naturaleza' 
WHERE palabra_shuar IN ('jintia', 'nayaim');

UPDATE public.palabras_detalladas SET campo_semantico = 'ceremonias' 
WHERE palabra_shuar IN ('arutam', 'natem');

-- Insert some sample translations based on the dictionary
INSERT INTO public.translations (
    source_text, target_text, source_language, target_language,
    confidence_score, status, word_references
) VALUES
('yawa', 'perro', 'shuar', 'spanish', 0.95, 'approved', 
 ARRAY[(SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'yawa')]),
('nukur', 'madre', 'shuar', 'spanish', 0.95, 'approved',
 ARRAY[(SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'nukur')]),
('perro', 'yawa', 'spanish', 'shuar', 0.95, 'approved',
 ARRAY[(SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'yawa')]),
('madre', 'nukur', 'spanish', 'shuar', 0.95, 'approved',
 ARRAY[(SELECT id FROM public.palabras_detalladas WHERE palabra_shuar = 'nukur')]);