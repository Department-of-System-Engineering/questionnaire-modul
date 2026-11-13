-- Dummy data for the kerdoiv database
-- Runs after schema.sql (name it 02_seed.sql inside the container)

-- API keys ------------------------------------------------------------
INSERT INTO api_keys (name, key_hash, active) VALUES
    ('test-client',   'dummyhash123', true),
    ('unity-client',  'dummyhash456', true),
    ('old-client',    'dummyhash789', false);

-- Questionnaire versions ---------------------------------------------
INSERT INTO questionnaire_versions (questionnaire_id, version, name, hash, languages, definition) VALUES
    ('demo_questionnaire', '1.0',
     '{"en": "Demo questionnaire", "hu": "Demó kérdőív"}',
     'hash_demo_10', ARRAY['en','hu'], '{"pages": [{"id": "p1"}]}'),
    ('demo_questionnaire', '1.1',
     '{"en": "Demo questionnaire", "hu": "Demó kérdőív"}',
     'hash_demo_11', ARRAY['en','hu'], '{"pages": [{"id": "p1"}, {"id": "p2"}]}'),
    ('sus_usability', '1.0',
     '{"en": "System Usability Scale", "hu": "Rendszerhasználhatósági skála"}',
     'hash_sus_10', ARRAY['en','hu'], '{"pages": [{"id": "p1"}]}'),
    ('nasa_tlx', '1.0',
     '{"en": "NASA Task Load Index", "hu": "NASA munkaterhelés index"}',
     'hash_tlx_10', ARRAY['en'], '{"pages": [{"id": "p1"}]}');

-- Items ----------------------------------------------------------------
INSERT INTO items (questionnaire_id, version, item_id, page_id, position, type, required, definition) VALUES
    -- demo 1.0
    ('demo_questionnaire', '1.0', 'q1', 'p1', 1, 'likert',     true,  '{"text": {"en": "I feel comfortable", "hu": "Kényelmesen érzem magam"}, "scale": 5}'),
    ('demo_questionnaire', '1.0', 'q2', 'p1', 2, 'text_short', false, '{"text": {"en": "Any comments?", "hu": "Van megjegyzése?"}}'),
    -- demo 1.1
    ('demo_questionnaire', '1.1', 'q1', 'p1', 1, 'likert',     true,  '{"text": {"en": "I feel comfortable", "hu": "Kényelmesen érzem magam"}, "scale": 7}'),
    ('demo_questionnaire', '1.1', 'q2', 'p1', 2, 'text_short', false, '{"text": {"en": "Any comments?", "hu": "Van megjegyzése?"}}'),
    ('demo_questionnaire', '1.1', 'q3', 'p2', 1, 'single_choice', true, '{"text": {"en": "Preferred device", "hu": "Előnyben részesített eszköz"}, "options": ["VR", "Desktop", "Tablet"]}'),
    -- SUS
    ('sus_usability', '1.0', 's1', 'p1', 1, 'likert', true, '{"text": {"en": "I would use this system frequently", "hu": "Gyakran használnám ezt a rendszert"}, "scale": 5}'),
    ('sus_usability', '1.0', 's2', 'p1', 2, 'likert', true, '{"text": {"en": "The system was unnecessarily complex", "hu": "A rendszer feleslegesen bonyolult volt"}, "scale": 5}'),
    ('sus_usability', '1.0', 's3', 'p1', 3, 'likert', true, '{"text": {"en": "The system was easy to use", "hu": "A rendszer könnyen használható volt"}, "scale": 5}'),
    ('sus_usability', '1.0', 's4', 'p1', 4, 'likert', true, '{"text": {"en": "I needed technical support", "hu": "Technikai segítségre volt szükségem"}, "scale": 5}'),
    ('sus_usability', '1.0', 's5', 'p1', 5, 'likert', true, '{"text": {"en": "The functions were well integrated", "hu": "A funkciók jól illeszkedtek"}, "scale": 5}'),
    -- NASA TLX
    ('nasa_tlx', '1.0', 'mental',      'p1', 1, 'vas', true, '{"text": {"en": "Mental demand"}, "min": 0, "max": 100}'),
    ('nasa_tlx', '1.0', 'physical',    'p1', 2, 'vas', true, '{"text": {"en": "Physical demand"}, "min": 0, "max": 100}'),
    ('nasa_tlx', '1.0', 'temporal',    'p1', 3, 'vas', true, '{"text": {"en": "Temporal demand"}, "min": 0, "max": 100}'),
    ('nasa_tlx', '1.0', 'performance', 'p1', 4, 'vas', true, '{"text": {"en": "Performance"}, "min": 0, "max": 100}'),
    ('nasa_tlx', '1.0', 'effort',      'p1', 5, 'vas', true, '{"text": {"en": "Effort"}, "min": 0, "max": 100}'),
    ('nasa_tlx', '1.0', 'frustration', 'p1', 6, 'vas', true, '{"text": {"en": "Frustration"}, "min": 0, "max": 100}');

-- Responses (fixed UUIDs so events can reference them) ------------------
INSERT INTO responses (id, participant_pseudonym, session_ref, group_ref, questionnaire_id, version,
                       occasion, cycle_number, language, seed, item_order, status,
                       started_at, ended_at, api_key_id, answers)
VALUES
    -- SUS, pre, group_a
    ('00000000-0000-0000-0000-000000000001', 'P001', 'S01', 'group_a', 'sus_usability', '1.0', 'pre', NULL, 'en', 1001,
     '{"p1": ["s3","s1","s5","s2","s4"]}', 'completed', now() - interval '10 days', now() - interval '10 days' + interval '4 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"s1","value":4},{"item_id":"s2","value":2},{"item_id":"s3","value":4},{"item_id":"s4","value":1},{"item_id":"s5","value":4}]'),
    ('00000000-0000-0000-0000-000000000002', 'P002', 'S01', 'group_a', 'sus_usability', '1.0', 'pre', NULL, 'en', 1002,
     '{"p1": ["s1","s2","s3","s4","s5"]}', 'completed', now() - interval '10 days', now() - interval '10 days' + interval '5 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"s1","value":3},{"item_id":"s2","value":3},{"item_id":"s3","value":3},{"item_id":"s4","value":2},{"item_id":"s5","value":3}]'),
    ('00000000-0000-0000-0000-000000000003', 'P003', 'S01', 'group_a', 'sus_usability', '1.0', 'pre', NULL, 'hu', 1003,
     '{"p1": ["s5","s4","s3","s2","s1"]}', 'completed', now() - interval '10 days', now() - interval '10 days' + interval '3 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"s1","value":5},{"item_id":"s2","value":1},{"item_id":"s3","value":5},{"item_id":"s4","value":1},{"item_id":"s5","value":5}]'),
    ('00000000-0000-0000-0000-000000000004', 'P004', 'S01', 'group_a', 'sus_usability', '1.0', 'pre', NULL, 'hu', 1004,
     '{"p1": ["s2","s1","s4","s3","s5"]}', 'completed', now() - interval '10 days', now() - interval '10 days' + interval '6 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"s1","value":2},{"item_id":"s2","value":4},{"item_id":"s3","value":2},{"item_id":"s4","value":4},{"item_id":"s5","value":2}]'),

    -- SUS, post, group_a
    ('00000000-0000-0000-0000-000000000005', 'P001', 'S02', 'group_a', 'sus_usability', '1.0', 'post', NULL, 'en', 2001,
     '{"p1": ["s1","s2","s3","s4","s5"]}', 'completed', now() - interval '3 days', now() - interval '3 days' + interval '4 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"s1","value":5},{"item_id":"s2","value":1},{"item_id":"s3","value":5},{"item_id":"s4","value":1},{"item_id":"s5","value":5}]'),
    ('00000000-0000-0000-0000-000000000006', 'P002', 'S02', 'group_a', 'sus_usability', '1.0', 'post', NULL, 'en', 2002,
     '{"p1": ["s4","s3","s2","s1","s5"]}', 'completed', now() - interval '3 days', now() - interval '3 days' + interval '5 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"s1","value":4},{"item_id":"s2","value":2},{"item_id":"s3","value":4},{"item_id":"s4","value":2},{"item_id":"s5","value":4}]'),

    -- NASA TLX, between cycles
    ('00000000-0000-0000-0000-000000000007', 'P001', 'S01', 'group_a', 'nasa_tlx', '1.0', 'between_cycles', 1, 'en', 3001,
     '{"p1": ["mental","physical","temporal","performance","effort","frustration"]}', 'completed',
     now() - interval '9 days', now() - interval '9 days' + interval '2 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"mental","value":60},{"item_id":"physical","value":30},{"item_id":"temporal","value":45},{"item_id":"performance","value":70},{"item_id":"effort","value":55},{"item_id":"frustration","value":20}]'),
    ('00000000-0000-0000-0000-000000000008', 'P001', 'S01', 'group_a', 'nasa_tlx', '1.0', 'between_cycles', 2, 'en', 3002,
     '{"p1": ["frustration","effort","performance","temporal","physical","mental"]}', 'completed',
     now() - interval '9 days' + interval '30 minutes', now() - interval '9 days' + interval '33 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"mental","value":50},{"item_id":"physical","value":35},{"item_id":"temporal","value":40},{"item_id":"performance","value":80},{"item_id":"effort","value":50},{"item_id":"frustration","value":10}]'),
    ('00000000-0000-0000-0000-000000000009', 'P002', 'S01', 'group_a', 'nasa_tlx', '1.0', 'between_cycles', 1, 'en', 3003,
     '{"p1": ["mental","physical","temporal","performance","effort","frustration"]}', 'completed',
     now() - interval '9 days', now() - interval '9 days' + interval '3 minutes',
     (SELECT id FROM api_keys WHERE name = 'test-client'),
     '[{"item_id":"mental","value":75},{"item_id":"physical","value":25},{"item_id":"temporal","value":65},{"item_id":"performance","value":50},{"item_id":"effort","value":70},{"item_id":"frustration","value":40}]'),
    -- in progress (ended_at must be NULL)
    ('00000000-0000-0000-0000-000000000010', 'P002', 'S01', 'group_a', 'nasa_tlx', '1.0', 'between_cycles', 2, 'en', 3004,
     '{"p1": ["mental","physical","temporal","performance","effort","frustration"]}', 'in_progress',
     now() - interval '5 minutes', NULL,
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"mental","value":55}]'),

    -- SUS, group_b: one aborted, one completed
    ('00000000-0000-0000-0000-000000000011', 'P005', 'S03', 'group_b', 'sus_usability', '1.0', 'pre', NULL, 'en', 4001,
     '{"p1": ["s1","s2","s3","s4","s5"]}', 'aborted', now() - interval '7 days', now() - interval '7 days' + interval '1 minute',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"s1","value":3}]'),
    ('00000000-0000-0000-0000-000000000012', 'P005', 'S03', 'group_b', 'sus_usability', '1.0', 'pre', NULL, 'en', 4002,
     '{"p1": ["s3","s2","s1","s5","s4"]}', 'completed', now() - interval '7 days' + interval '10 minutes', now() - interval '7 days' + interval '14 minutes',
     (SELECT id FROM api_keys WHERE name = 'unity-client'),
     '[{"item_id":"s1","value":3},{"item_id":"s2","value":3},{"item_id":"s3","value":4},{"item_id":"s4","value":2},{"item_id":"s5","value":3}]'),

    -- demo questionnaire v1.1, group_b, Hungarian
    ('00000000-0000-0000-0000-000000000013', 'P006', 'S03', 'group_b', 'demo_questionnaire', '1.1', 'pre', NULL, 'hu', 5001,
     '{"p1": ["q2","q1"], "p2": ["q3"]}', 'completed', now() - interval '6 days', now() - interval '6 days' + interval '2 minutes',
     (SELECT id FROM api_keys WHERE name = 'test-client'),
     '[{"item_id":"q1","value":6},{"item_id":"q2","value":"Minden rendben"},{"item_id":"q3","value":"VR"}]'),
    ('00000000-0000-0000-0000-000000000014', 'P006', 'S04', 'group_b', 'demo_questionnaire', '1.1', 'post', NULL, 'hu', 5002,
     '{"p1": ["q1","q2"], "p2": ["q3"]}', 'completed', now() - interval '1 day', now() - interval '1 day' + interval '2 minutes',
     (SELECT id FROM api_keys WHERE name = 'test-client'),
     '[{"item_id":"q1","value":7},{"item_id":"q2","value":"Jobb volt, mint vártam"},{"item_id":"q3","value":"Desktop"}]');

-- Events ---------------------------------------------------------------
-- Detailed event trail for the first response
INSERT INTO response_events (response_id, t_utc_ns, t_mono_ns, type, payload) VALUES
    ('00000000-0000-0000-0000-000000000001', 1700000000000000000, 1000000000, 'questionnaire_start', '{}'),
    ('00000000-0000-0000-0000-000000000001', 1700000000500000000, 1500000000, 'page_shown',          '{"page_id": "p1"}'),
    ('00000000-0000-0000-0000-000000000001', 1700000020000000000, 21000000000, 'item_answered',      '{"item_id": "s3", "value": 4}'),
    ('00000000-0000-0000-0000-000000000001', 1700000045000000000, 46000000000, 'item_answered',      '{"item_id": "s1", "value": 4}'),
    ('00000000-0000-0000-0000-000000000001', 1700000200000000000, 201000000000, 'page_submitted',    '{"page_id": "p1"}'),
    ('00000000-0000-0000-0000-000000000001', 1700000201000000000, 202000000000, 'questionnaire_end', '{}');

-- A start event for every other response
INSERT INTO response_events (response_id, t_utc_ns, t_mono_ns, type)
SELECT id,
       (extract(epoch FROM started_at) * 1000000000)::bigint,
       0,
       'questionnaire_start'
FROM responses
WHERE id <> '00000000-0000-0000-0000-000000000001';

-- An end event for completed responses (except the first, handled above)
INSERT INTO response_events (response_id, t_utc_ns, t_mono_ns, type)
SELECT id,
       (extract(epoch FROM ended_at) * 1000000000)::bigint,
       (extract(epoch FROM ended_at - started_at) * 1000000000)::bigint,
       'questionnaire_end'
FROM responses
WHERE status = 'completed'
  AND id <> '00000000-0000-0000-0000-000000000001';

-- An abort event for aborted responses
INSERT INTO response_events (response_id, t_utc_ns, t_mono_ns, type)
SELECT id,
       (extract(epoch FROM ended_at) * 1000000000)::bigint,
       (extract(epoch FROM ended_at - started_at) * 1000000000)::bigint,
       'questionnaire_aborted'
FROM responses
WHERE status = 'aborted';