# Atlas Voice Stack Bake-off

## Purpose

Test the production value of three voice-stack candidates against one real Four-Hour Atlas course rather than judging them from feature lists:

1. **VoiceStudio**: bulk/local narration and long-form production.
2. **Voicebox**: local voice profiles, agent speech and dictation.
3. **Pipecat + PhoneLLM**: real-time conversational-agent and tool-call path.

The course under test is **T4H-MC-T04-001 / SUB-T04-001, Identity Proofing**. The canonical Atlas workbook defines four 60-minute modules, a four-hour learning outcome, an executive action brief as the portfolio output, and an assessment criterion. The current repository does not claim that a complete production lesson script already exists, so the benchmark corpus is explicitly marked as test material rather than production course content.

## Evidence boundary

The course is evidence-safe by design. The benchmark preserves the distinction between research questions, working hypotheses, candidate methods and unresolved unknowns. Do not convert benchmark prose into established findings.

## What is measured

### Production

- wall-clock generation time
- successful/failed outputs
- output byte count
- repeatability across four module excerpts
- manual intervention count
- regeneration of a single module

### Conversational

- first-response wall time
- successful responses
- tool-call occurrence and payload
- tool-call latency where exposed
- recovery from an incorrect learner answer
- manual intervention count

### Human QA

Record separately, never infer from HTTP success:

- naturalness
- pronunciation
- terminology handling
- pacing
- continuity across chunks
- assessment-question clarity
- learner comprehension

## Run

The runner uses only standard Python libraries.

```bash
cd voice-bakeoff
python3 run_bakeoff.py
```

Set the relevant environment variables first. A candidate with missing configuration is recorded as `BLOCKED`, not as a failure or success.

### VoiceStudio

VoiceStudio exposes an OpenAI-compatible TTS endpoint at `POST /v1/audio/speech`. Its current implementation accepts a VoiceStudio engine/model, voice, response format and optional language/style controls.

```bash
export VOICESTUDIO_URL=http://127.0.0.1:<PORT>
export VOICESTUDIO_MODEL=omnivoice
export VOICESTUDIO_VOICE=default
```

### Voicebox

Voicebox exposes `POST /speak`, which returns a generation id that can be polled at `GET /generate/{id}/status`.

```bash
export VOICEBOX_URL=http://127.0.0.1:17493
export VOICEBOX_PROFILE=<profile-name-or-id>
export VOICEBOX_ENGINE=<optional-engine>
```

### Pipecat / PhoneLLM

For the first pass, use an OpenAI-compatible chat-completions endpoint for the PhoneLLM brain/tool-call path. This validates the conversational layer independently from STT/TTS transport.

```bash
export PIPECAT_CHAT_URL=https://<endpoint>/v1/chat/completions
export PIPECAT_API_KEY=<token>
export PIPECAT_MODEL=pipecat-ai/phonellm-alpha-1
```

This does **not** claim to measure end-to-end voice latency. That requires the actual Pipecat audio pipeline to be connected and is a separate test stage.

## Acceptance gate

No candidate becomes `REAL` for Atlas production merely because its endpoint returns 200.

The candidate must have:

- a receipt for every requested module output
- observable generation timing
- successful regeneration of one selected module
- human QA recorded against the same corpus
- no unexplained data movement for a local-first test
- tool-call evidence for the conversational path
- a reproducible run record

## Results

Use `RESULTS_TEMPLATE.json` as the schema. The runner writes `results-<run-id>.json` beside the script.

Do not hand-edit observed timings. Human QA belongs in a separate review record.
