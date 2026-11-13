-- Database: kerdoiv

-- DROP DATABASE IF EXISTS kerdoiv;

CREATE TABLE api_keys (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        text        NOT NULL UNIQUE,
    key_hash    text        NOT NULL UNIQUE,
    active      boolean     NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE questionnaire_versions (
    questionnaire_id text        NOT NULL CHECK (questionnaire_id ~ '^[a-z0-9_]+$'),
    version          text        NOT NULL,
    name             jsonb       NOT NULL,          -- {"en": "...", "hu": "..."}
    hash             text        NOT NULL,
    languages        text[]      NOT NULL CHECK (cardinality(languages) >= 1),
    definition       jsonb       NOT NULL,          -- the full questionnaire JSON
    created_at       timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (questionnaire_id, version)
);

CREATE TABLE items (
    id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    questionnaire_id text    NOT NULL,
    version          text    NOT NULL,
    item_id          text    NOT NULL,              -- the "id" from the JSON
    page_id          text    NOT NULL,
    position         integer NOT NULL,
    type             text    NOT NULL CHECK (type IN (
        'info','likert','matrix','semantic_differential','slider','vas',
        'pictorial','single_choice','multi_choice','dropdown','numeric',
        'text_short','text_long','datetime','ranking','pairwise')),
    required         boolean NOT NULL DEFAULT false,
    definition       jsonb   NOT NULL,
    FOREIGN KEY (questionnaire_id, version)
        REFERENCES questionnaire_versions (questionnaire_id, version) ON DELETE CASCADE,
    UNIQUE (questionnaire_id, version, item_id)
);

CREATE TABLE responses (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_pseudonym text    NOT NULL,
    session_ref           text,
    group_ref             text,
    questionnaire_id      text    NOT NULL,
    version               text    NOT NULL,
    occasion              text    NOT NULL CHECK (occasion IN ('pre','post','between_cycles')),
    cycle_number          integer CHECK (cycle_number >= 1),
    language              text    NOT NULL,
    seed                  bigint  NOT NULL,
    item_order            jsonb   NOT NULL DEFAULT '{}',
    status                text    NOT NULL DEFAULT 'in_progress'
                                  CHECK (status IN ('in_progress','completed','aborted')),
    started_at            timestamptz NOT NULL DEFAULT now(),
    ended_at              timestamptz,
    api_key_id            integer NOT NULL REFERENCES api_keys (id),
    answers               jsonb   NOT NULL DEFAULT '[]' CHECK (jsonb_typeof(answers) = 'array'),
    FOREIGN KEY (questionnaire_id, version)
        REFERENCES questionnaire_versions (questionnaire_id, version),
    CHECK ((occasion = 'between_cycles') = (cycle_number IS NOT NULL)),
    CHECK ((status = 'in_progress') = (ended_at IS NULL))
);

CREATE INDEX responses_group_ref_idx   ON responses (group_ref);
CREATE INDEX responses_group_quest_idx ON responses (group_ref, questionnaire_id);
CREATE INDEX responses_pseudonym_idx   ON responses (participant_pseudonym);

CREATE TABLE response_events (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    response_id uuid   NOT NULL REFERENCES responses (id) ON DELETE CASCADE,
    t_utc_ns    bigint NOT NULL,
    t_mono_ns   bigint NOT NULL,
    type        text   NOT NULL CHECK (type IN (
        'questionnaire_start','page_shown','item_answered',
        'page_submitted','questionnaire_end','questionnaire_aborted')),
    payload     jsonb  NOT NULL DEFAULT '{}'
);

CREATE INDEX response_events_resp_idx ON response_events (response_id, id);