# Conversational AI voice hub

A voice assistant in Swedish that you talk to like a person: ask questions,
play games, take notes, and control the house. It runs on the same Home
Assistant (HA) box as everything else.

```
"Okay Nabu" ─► Voice satellite ─► Speech-to-text ─► Local HA intents ──► done (lights, heat…)
               (wake word on        (HA Cloud,         │ not a home command
                the device)          Swedish)          ▼
                                                    Claude (Anthropic) ─► notes, games, web search
                                                       │
               Speaker ◄────────── Text-to-speech ◄────┘
                                   (HA Cloud, Swedish voice)
```

## The choices, and why

| Part | Choice | Why |
|---|---|---|
| Hub | **Home Assistant Green** (already recommended in [INTEGRATIONS.md](INTEGRATIONS.md)) | Speech and the AI run in the cloud, so the hub only routes audio. A Pi 4 would also work, but local speech on either box is too slow and too weak in Swedish for free conversation. |
| Microphone + speaker | **Home Assistant Voice Preview Edition** (one per room) | Made for HA: wake word runs on the device, good far-field mics, a mute switch, and it listens again on its own when the assistant asks a question back (needed for games). Its built-in speaker is small; plug a powered speaker into its 3.5 mm output if you want music-quality sound. |
| Wake word | **"Okay Nabu"** (or "Hey Jarvis" / "Hey Mycroft") | Runs on the device, no audio leaves the room until it hears it. There is no Swedish wake word yet; the wake word is English but everything after it is Swedish. |
| Speech-to-text and text-to-speech | **Home Assistant Cloud** (Nabu Casa) | Fast and good at Swedish. You also need it for "Hey Google" control (see INTEGRATIONS.md), so one subscription covers both, plus remote access. |
| Brain | **Claude** through the built-in **Anthropic** integration | Good Swedish, good at running games, and it calls the scripts in this repo as tools. Built-in web search answers questions about news, weather and opening hours. |
| Home commands | **"Prefer handling commands locally"** on | "Tänd i köket" is handled by HA's own Swedish intents: instant and free. Only everything else goes to Claude. |
| Notes | A **Local To-do** list called **Anteckningar** | Stored on the HA box, visible and editable in the HA app, and no extra service. |

**Not recommended:** Google Nest speakers cannot be HA voice satellites (they
only run Google Assistant). Local Whisper + Piper is possible later for
privacy, but on a Green or Pi 4 a question takes several seconds just to
transcribe and small Whisper models get a lot of Swedish wrong.
Speech-to-Phrase (HA's fast local option) only understands fixed home
commands, not open questions or games.

## What you need to buy and set up yourself

| Item | Cost (approx., Nov 2026) | Notes |
|---|---|---|
| Home Assistant Voice Preview Edition | ~700–800 kr each | Sold at Kjell & Company, Inet, Komplett. Start with one in the kitchen or living room. Needs a USB-C power supply (5 V / 2 A) if you don't have one. |
| Optional powered speaker with 3.5 mm input | 300–1,000 kr | Only if the built-in speaker is too quiet. |
| Home Assistant Cloud | ~€7.50/month or €75/year | Free 31-day trial. Sign up in HA under Settings > Home Assistant Cloud. |
| Anthropic API key | Pay per use, see below | Create an account at console.anthropic.com, add a card and buy credits (minimum US$5), create an API key. **Set a monthly spend limit** in the console (e.g. US$10). This is separate from any Claude.ai subscription. |

Your phone works as a voice remote for free: the HA Companion app has an Assist
button, so you can try everything before buying a satellite.

### What the AI costs

You pay Anthropic per token (roughly per word read and written). Each question
sends the instructions plus the list of exposed devices, so the cost is mostly
input. A rough guess for 30 AI questions or game turns a day (about 900 a
month):

| Model | Price per million tokens (in / out) | Rough monthly cost | When to pick it |
|---|---|---|---|
| **Claude Opus 5.5** (`claude-opus-5-5`) | $4 / $20 | 30–250 kr, mostly depending on how well caching works | The default: best answers, best at games and Swedish. |
| Claude Sonnet 5.5 (`claude-sonnet-5-5`) | $2 / $10 | 15–120 kr | Middle ground. |
| Claude Haiku 5.5 (`claude-haiku-5-5`) | $0.10 / $0.50 | under 10 kr | Cheapest and fastest replies; fine for notes and simple quizzes. |

Web searches cost an extra US$10 per 1,000 searches (about 0.10 kr each).
Home commands handled locally cost nothing. Turn on **Caching strategy: Full**
(below); during a game the repeated parts are then billed at a fraction of
the price. Check real spend in the Anthropic console after the first week and
switch model in the integration settings if needed.

## Setup, step by step

Do this after HA is running ([INTEGRATIONS.md](INTEGRATIONS.md) steps 1–2),
so the `homeassistant/` folder from this repo, including
`packages/voice_assistant.yaml`, is on the box.

1. **Notes list.** Settings > Devices & services > Add integration >
   **Local To-do** > name: `Anteckningar`. Check that the entity is
   `todo.anteckningar` (Settings > Entities). The built-in **Shopping list**
   integration is worth adding too, for "lägg till mjölk på inköpslistan".
2. **Home Assistant Cloud.** Settings > Home Assistant Cloud > sign in or
   start the trial. Under *Text-to-speech*, set language **Svenska (Sverige)**
   and pick a voice, e.g. *Sofie* or *Mattias*; play a sample to choose.
3. **Claude.** Settings > Devices & services > Add integration > **Anthropic**
   > paste the API key. On the integration, open the conversation agent
   (or *Add conversation agent*) and set:
   - **Instructions:** paste the contents of
     [`homeassistant/voice/claude_instruktioner.txt`](../homeassistant/voice/claude_instruktioner.txt).
   - **AI tools:** *Device control* (only exposed entities; do not pick the
     full "Home Assistant" access).
   - Untick **Recommended settings** to see the rest:
     - **Model:** `claude-opus-5-5` (or Sonnet / Haiku, see costs above).
     - **Maximum tokens to return in response:** 1024.
     - **Effort:** Low (keeps replies quick; raise to Medium if answers are
       too shallow).
     - **Thinking type:** Adaptive.
     - **Caching strategy:** Full.
     - **Enable web search:** on, **Maximum web searches:** 3,
       **Include home location:** on (for local weather and opening hours).
     - Leave code execution and web fetch off.
4. **Expose entities to the assistant.** Settings > Voice assistants >
   *Expose* tab. Expose the lights, heaters and switches you want to talk to
   (expose fewer rather than more: every exposed entity is sent with each
   question and costs tokens), plus these from this repo:
   `script.ai_spara_anteckning`, `script.ai_las_anteckningar`,
   `script.ai_bocka_av_anteckning`, `script.ai_slumpa`,
   `script.ai_quizrekord`, `todo.anteckningar`, `input_number.quiz_rekord`.
   Give rooms and devices Swedish names and aliases ("taklampan",
   "golvvärmen i badrummet") so they are easy to say.
5. **Voice pipeline.** Settings > Voice assistants > *Add assistant*:
   - Name: `Hemma`, language: **Svenska**.
   - Conversation agent: the **Claude** agent from step 3, with
     **Prefer handling commands locally** turned on.
   - Speech-to-text: **Home Assistant Cloud**, Svenska.
   - Text-to-speech: **Home Assistant Cloud**, Svenska, your chosen voice.
   - Wake word: left as is (the Voice PE detects it on the device).
   - Then ⋮ > *Set as preferred*.
6. **Voice Preview Edition.** Plug it in. In HA, Settings > Devices &
   services shows it as discovered (ESPHome) > *Configure*, or set it up from
   the HA phone app over Bluetooth to give it Wi-Fi. The setup wizard asks
   for the room, wake word and assistant: pick **Hemma**.
7. **Phone.** In the HA Companion app, Settings > Companion app > Assist:
   pick **Hemma**, so the phone uses the same assistant.

## Try it

Say "Okay Nabu", wait for the light ring, then for example:

- **Questions:** "Hur långt är det till månen?", "Vad blir vädret i helgen?",
  "Har Ica Maxi öppet nu?"
- **Notes:** "Anteckna att vi ska boka tvättstugan på torsdag",
  "Vad har jag antecknat?", "Bocka av tvättstugan".
- **Games:** "Kan vi köra ett quiz om djur för barn?", "Vi spelar tjugo
  frågor, du tänker på något", "Ordkedja!", "Ge mig en gåta", "Slå två
  tärningar", "Vem har quizrekordet?". During a game you don't need the wake
  word: the satellite keeps listening while the assistant is waiting for an
  answer.
- **Home:** "Släck i vardagsrummet", "Sätt golvvärmen i badrummet till 24
  grader". These are handled locally and are instant.

## How the pieces in this repo work

- `homeassistant/packages/voice_assistant.yaml`: five scripts Claude uses as
  tools, plus the quiz-record helpers. Claude decides when to call them from
  each script's `description`, so edit those (in Swedish) to change its
  behaviour.
  - `ai_spara_anteckning`, `ai_las_anteckningar`, `ai_bocka_av_anteckning`:
    add, read and tick off notes in `todo.anteckningar`.
  - `ai_slumpa`: real random numbers for dice, coin flips and picking who
    starts. Language models are bad at being random, so the prompt tells
    Claude to always use this.
  - `ai_quizrekord`: keeps the household quiz record in
    `input_number.quiz_rekord` and `input_text.quiz_rekordhallare`, so it
    survives between games and restarts.
- `homeassistant/voice/claude_instruktioner.txt`: the instructions for
  Claude (in Swedish): short spoken replies, safety rules for locks and house
  modes, how notes work, and the rules for each game. The Anthropic
  integration stores its settings in the UI, not in YAML, so this file is the
  copy to paste and to keep under version control. Add a new game by adding a
  line under *Spel*.

## Troubleshooting

- **It says it did something but nothing happened**, or replies stop
  mid-sentence: raise *Maximum tokens to return in response*.
- **It doesn't use the notes or dice scripts:** check they are exposed
  (step 4), then reload the conversation agent.
- **Replies are slow:** lower *Effort*, switch to Haiku or Sonnet, or expose
  fewer entities. Check Settings > Voice assistants > Hemma > ⋮ > *Debug* to
  see how long each stage takes.
- **Misheard words:** speak after the light ring turns on; check the debug
  view to see what speech-to-text heard.
- **Costs higher than expected:** check *Caching strategy* is Full and the
  exposed entity list is short; set or lower the spend limit in the
  Anthropic console.
