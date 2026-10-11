# Deep Codebase Learning

**Learn to explain, change, debug, and reconstruct the core of a real codebase with sustained AI guidance.**

[中文](README.md) · [Usage](docs/usage.md) · [Design and memory](docs/design.md) · [Validation](docs/validation.md) · [Contributing](CONTRIBUTING.md)

`deep-codebase-learning` is an Agent Skill that teaches through real feature flows, checks understanding with learner evidence, and stores durable progress in the target project's `.codelearn/` directory. Keep studying in one conversation or resume in a new one. Teaching follows the learner's language; detailed maintainer documentation is currently in Chinese.

> Flow before files. Understanding before coverage. Evidence before mastery. Reconstruction before completion.

## Quick start

Use an Agent Skills compatible coding agent with repository read access and local file write access. The skill itself has no runtime dependencies. The optional [Skills CLI](https://github.com/vercel-labs/skills) requires Node.js/npm:

```bash
npx skills add zgozh/deep-codebase --skill deep-codebase-learning -g
```

Add `-a codex` to target Codex; omit `-g` for a project-local installation. Preview without installing:

```bash
npx skills add zgozh/deep-codebase --list
```

Open a fresh conversation in the repository you want to study:

```text
Help me deeply learn this codebase.
```

In the current conversation or a later one in that same repository:

```text
Continue learning.
```

If automatic selection does not activate the skill, explicitly ask Codex to `Use $deep-codebase-learning to teach me this repository`. Other agents use their own invocation syntax. See [manual installation](docs/usage.md).

If HTTPS access is unavailable and GitHub SSH is already configured, use `git@github.com:zgozh/deep-codebase.git` as the source instead. Downloaded local repositories are also supported.

## How learning works

**The teaching default is always beginner.** Unverified project concepts, features, architecture, language features, frameworks, and underlying principles are explained before they are relied on. The tutor owns a complete, repository-specific learning route and its prerequisites; you do not need to diagnose your gaps or choose the next lesson. Existing independent evidence can reduce repetition for that concept, without assuming expertise in other areas.

**Lessons happen in the conversation; notes are optional review material.** The default starts with the project's problem, capabilities, and overall architecture, then follows a feature into frontend and backend code. The first ordinary learning turn delivers an explanation rather than opening or closing with a quiz, field lookup, or background questionnaire. Later questions need taught prerequisites, supplied material, and a useful learning purpose; answering is not a mandatory turn-by-turn gate.

The agent builds architecture and feature maps, creates a repository-specific roadmap, and starts with a small learning unit. It traces real user actions or events through the system, including the UI return path when a frontend exists. It expands code progressively, explains design trade-offs, and detects prerequisite gaps. Knowledge detours return to the saved source location.

**Source lessons explain implementation, not just file responsibilities.** Each covers one concrete problem using excerpts actually read from the repository, with beginner explanations of syntax, inputs/outputs, execution order, data/state changes, relevant framework behavior, failure or side-effect boundaries, and the return path. Long flows become consecutive lessons with a saved continuation. A pre-send check requires missing explanations to be repaired; paths, class-name arrows, README paraphrases, and note links do not satisfy the source lesson gate. Overview lessons remain focused on the business and architecture. See the [teaching protocol](deep-codebase-learning/references/teaching.md).

**Both conversation lessons and notes are detailed by default.** Every unfamiliar concept, symbol, imported API, and mechanism needed to read the selected code receives a plain explanation, a reason it matters, and a concrete example. Important statements in real excerpts receive teaching comments tracing origins, registration and invocation timing, state changes, and return consumers. A small lesson limits its causal goal, not explanation depth or length. Necessary prerequisites are taught before their use. Detailed teaching preferences persist across lessons; you need not list unfamiliar words. Official documentation is checked against the relevant dependency version and explained through project mappings, examples, and limits before linking the section. Annotations do not alter project source.

Investigated source, prepared lessons, visibly explained content, and learner evidence are separate. Pre-send writing records prepared content; only an actual visible lesson supports explained scope. Notes preserve the same important definitions, annotated code, causal reasoning, examples, and corrections rather than compensating for a compressed classroom. See the [hypothetical teaching examples](docs/examples.md#jv150-详细教学验收示范).

You predict behavior, inspect code, attempt experiments, answer questions, and restate flows. Acknowledgment is not mastery. Coverage, knowledge mastery, and reconstruction ability are tracked separately. Important components outside the main flows are covered by a horizontal audit. Completion requires an independently designed and runnable Mini Version.

Mermaid diagrams must follow the official syntax for their diagram type and be checked before delivery. Available tools should parse or render the final code; untested target rendering stays explicit. Basic syntax is the default when renderer compatibility is unknown. Known syntax errors must be repaired. See the [diagram protocol](deep-codebase-learning/references/diagrams.md).

## Durable learning memory

`.codelearn/` contains state, roadmap, project map, stage contracts, coverage, mastery, journals, knowledge bridges, notes, and reviews. Meaningful exchanges are saved automatically. Resume loads relevant records rather than the entire history.

Journals preserve structured learning events. Notes are technical articles rebuilt from source evidence, questions, misconceptions, experiments, and the learner's own understanding.

### Automatic detailed notes and explicit requests

Each meaningful turn checks for a writing boundary. When an important topic's purpose, mechanism or flow, source evidence, and key limits have been explained and teaching shifts into questions, verification, or the next topic, a detailed topic article is saved in `.codelearn/notes/topics/`. The tutor identifies this boundary without requiring a learner request. Important tracing, detour, or experiment boundaries also trigger it. This works in one continuous conversation and does not wait for a stage to pass. Pending learner verification stays explicit. Related topics accumulating at a natural boundary trigger a reading index and checkpoint update; stage acceptance triggers a comprehensive stage article.

You can also say:

```text
Summarize the current topic in detailed notes.
Write detailed notes on what we just discussed.
Summarize the current stage.
Summarize this learning session.
Recheck this note against its sources.
```

By default, detailed content is written to `.codelearn/notes/`, with a short reply and file link. An unfinished stage can have a draft; pending questions and the next learning action are preserved. Notes explain mechanisms, important code and data changes, design reasons, failure or change impacts, and actual learner questions and corrections, rather than compressing the chat.

**Generated notes are candidates to check, whether automatic or explicitly requested.** Article quality (`draft/validated`) and scoped factual verification (`unverified/source_checked/runtime_checked`) are separate. Tutor self-review is not independent verification, learner mastery, or proof that unrun experiments succeeded. Learning and note quality gates must both pass before a stage completes. See the [note protocol](deep-codebase-learning/references/notes.md).

## Boundaries and validation

- File-protocol simulations have been performed in Codex. Other compatible agents are candidates for use, not equally verified environments.
- Reading source and maintaining learning memory does not authorize arbitrary source edits, dependency installation, external uploads, or production experiments.
- The skill runs only when invoked. It has no background scheduler, atomic multi-file transaction, or concurrent-writer support.
- Simulated learner answers and experiment data do not prove actual learning or runtime behavior. Large-repository scale, long-term outcomes, and all recovery failure paths remain unverified.
- You decide whether to commit or ignore your target project's learning memory. Keep private source and personal records out of public issues.

The installable package is [deep-codebase-learning/](deep-codebase-learning/SKILL.md); repository docs, CI, and maintainer checks are separate. See [examples](docs/examples.md), [validation scope](docs/validation.md), and [changelog](CHANGELOG.md).

## Inspirations and license

The design draws on [learn-codebase](https://github.com/ktaletsk/learn-codebase), [learning-codebases](https://github.com/Eijnewgnaw/learning-codebases), [tutor](https://github.com/kevinnio/tutor), [code-learn-skill](https://github.com/yumeiriowl/code-learn-skill), and [repo-learner-suite](https://github.com/PranitMohnot/repo-learner-suite). See [design provenance](docs/inspirations.md). No upstream code or templates are copied, and none of these projects is a runtime dependency.

[MIT License](LICENSE). Report issues at [zgozh/deep-codebase](https://github.com/zgozh/deep-codebase/issues).
