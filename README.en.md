# Deep Codebase Learning

**Study a real codebase through detailed, beginner-friendly notes, then prove understanding through independent work.**

[中文](README.md) · [Usage](docs/usage.md) · [Design](docs/design.md) · [Validation](docs/validation.md) · [Contributing](CONTRIBUTING.md)

Version 1.8.1. This Agent Skill plans a repository-specific route, teaches real execution flows, and saves durable memory in the target project's `.codelearn/`. Detailed notes are the default complete lesson. Chat gives a brief scope and clickable note link, with direct answers whenever you ask questions. Keep one conversation or resume in a new one.

> Flow before files. Understanding before coverage. Evidence before mastery. Reconstruction before completion.

## Start learning

Use an Agent Skills compatible host that can read your local checkout, write learning memory, and access relevant official documentation. Open a conversation in the project to study. Static study does not require installing the target application's dependencies; unrun behavior stays unverified. The skill has no runtime scripts, services, databases, or model requirements. The optional [Skills CLI](https://github.com/vercel-labs/skills) needs Node.js/npm:

```bash
npx skills add zgozh/deep-codebase --skill deep-codebase-learning -g -a codex
```

`-g` installs for your user; omit it for project-local installation. `-a codex` selects Codex; select your host when using another agent. Preview available skills with `npx skills add zgozh/deep-codebase --list`. Manual installation copies the entire `deep-codebase-learning/` folder to a directory your host discovers, including references and templates. See the Chinese [usage guide](docs/usage.md) for Windows/manual steps and discovery details.

In your source repository say:

```text
Help me deeply learn this codebase.
```

Later:

```text
Continue learning.
```

For explicit selection in Codex: `Use $deep-codebase-learning to teach me this project from zero.` You do not need a background questionnaire, a list of unknown terms, or a correct answer to an unfamiliar quiz. The tutor owns the route: problem → capabilities → architecture → a real feature or system event → progressively annotated source → other features and horizontal audit → independent reconstruction.

## Notes first, questions welcome

Every lesson produces a self-contained technical article, not a file-responsibility overview or chat summary. It explains currently needed concepts in plain language at their first relevant use, expands acronyms accurately, gives concrete examples, and traces who calls whom, when execution happens, where values come from, how state changes, and who consumes results. A frontend flow returns to the visible UI; non-UI projects trace the relevant caller or output.

Real source excerpts include project-relative paths, symbols, and reliable original line locations. Every meaningful statement in a complete source responsibility segment is explained after the code by original line or small semantic group: syntax, concrete values, state changes, reasons, and consumers. Inline teaching comments are supplementary. Added comments are identified and do not modify the project source. You may follow locations to inspect the repository, but the lesson cannot rely on that action to fill missing explanations.

Framework and browser APIs are explained where they intervene: what they provide, how the project connects to them, when they act, and what they manage or call afterward. Helpful official documentation must actually be read for the applicable version. The tutor explains its concrete rules and mechanisms, maps them to project code, states what they can and cannot establish, and then provides a direct section link. Readers do not have to research documentation to complete the lesson.

One concrete input runs through the current lesson's data/state/URL changes to its result. Actual important error, cancellation, rejection, retry, timeout, or fallback branches are explained when present. Source facts, documentation rules, static inference, observed execution, hypothetical example values, and unknowns remain distinct. Private source and personal records must not be uploaded or used in external searches.

Small lessons limit causal scope, not explanation depth. Large flows become consecutive lessons with explicit boundaries, omitted internals, and a precise continuation. No arbitrary word target, long upfront glossary, repeated conclusions, or link-list homework. The [lesson reading requirements](deep-codebase-learning/references/notes.md#note-quality-gate) require missing explanations to be repaired before delivery, alongside readback, local Markdown links and relevant JSON checks. Writing notes does not automatically run application tests or builds.

Ask any question in chat and receive an answer deep enough to resolve it; a local question does not automatically become a whole class. A real omission, error, or ambiguity triggers a corresponding note/index/progress repair. A clarification alone need not rewrite a complete article. Full lessons appear in chat only when explicitly requested. Reading notes is not gated by quizzes, acknowledgment, or a reply of “continue.”

## Choose an authoring workflow

The first use in a learning project offers one choice:

| Mode | Behavior |
|---|---|
| Single conversation, default | The current model plans, writes a complete lesson, reads it through, repairs gaps, and saves it for delivery |
| Principal planning/review with subagent authoring | The principal defines one bounded lesson; a subagent writes its exclusive draft; the principal independently reviews the content, requests repairs, and publishes it |

No answer means single conversation, not permission to delegate. A previous explicit choice is restored rather than asked again. If subagents are unavailable, single-conversation teaching continues. No fixed model, reasoning setting, extra service, or installation is required. Delegation can cost more time/resources and does not guarantee correctness. Only the principal writes shared learning state and indexes; authors cannot modify project source or other agents' drafts. See [workflow rules](deep-codebase-learning/references/authoring.md).

Useful requests:

```text
Continue by writing the next detailed lesson.
Use a single conversation to write the materials.
Use principal planning and review, with a subagent writing each lesson.
Explain this line here in chat.
Teach this whole lesson in chat.
Summarize the current topic, stage, or session.
This is too shallow; repair the missing concepts and annotated execution steps.
Reload the latest $deep-codebase-learning instructions, retain my progress, and continue.
Switch to development and save the learning return point.
```

## Memory and organization

State, roadmap, project map, stage contracts, coverage, mastery, journal, knowledge bridges, notes, and reviews live in `.codelearn/`. Meaningful changes are saved automatically. Resume loads current relevant records rather than all history.

Notes use Chinese content names by default even though teaching follows the learner's language; explicit naming preferences take precedence. Stable stage/topic IDs and source identifiers are retained:

```text
.codelearn/notes/
  索引.md
  S00-项目全景/
    S00-T01-项目问题与业务能力.md
    S00-阶段总览.md
  S01-登录与权限/
    S01-T01-01-从输入到登录请求.md
    S01-T01-02-身份校验与页面返回.md
  会话/
  项目总览.md
  重建复盘.md
```

Categories follow the actual project, not a fixed syllabus or a single generic topics folder. Existing notes migrate within the affected scope with index, stage, state, journal, review and inter-note references updated; history and evidence are retained. Conflicting or locked destinations are not overwritten or forcibly deleted.

Investigated source, prepared drafts, delivered lessons, explanation depth, and learner evidence remain separate. A complete lesson can be delivered after an actual read-through, gap repair, necessary document checks, saving, and indexing. Single-conversation lessons may be ready/self_review; validated is reserved for a real independent review of a stated scope, which is optional. Drafts are not sufficient prior teaching. Ready lessons support coverage only where the actual explanation is sufficient. Neither writing nor reading raises mastery or proves runtime behavior.

Lessons may continue while stage ability remains unverified. Final completion still requires important horizontal components, independent answers and experiments, stage reviews, and an independently designed, runnable Mini Version. A finished roadmap or complete set of articles cannot set PROJECT_COMPLETE.

Repairs retain a recoverable previous version and preserve correct, necessary explanations. Read the complete initial lesson once; then reread local repairs and affected dependencies. Broad rewrites, major source changes, or unclear impact warrant another full read. Keep a brief method/scope/gaps record rather than per-paragraph reports or lesson hashes. Detailed syntax, mechanisms, scenarios and reasons remain essential. Evidence does not establish that rule length alone caused quality problems, or that this workflow guarantees speed or compliance.

The lesson template now guides each step from necessary context through a complete annotated source segment, variable origins, syntax/values/reasons, a concrete replay, and its actual consumer. Check whether the caller really awaits; retain JSX and branch boundaries. Repairs briefly record additions, changes, moves and removals while preserving necessary explanations. Keep current revision records aligned without overwriting the active learning position when repairing an older lesson. Record the skill version actually loaded, not merely installed. No fixed chapter layout or runtime tool is added.

## Update and boundaries

For a CLI installation, update only this skill with `npx skills update deep-codebase-learning -g`, or `-p` for project-local installation. Follow installer/host discovery rules. Manual updates replace only installed skill files, never the target project's `.codelearn/`; re-read the latest skill in a conversation that already loaded old instructions.

- Generated notes are candidates to check. Article quality and scoped source/runtime verification are separate; self-review or subagent review is not proof of actual learning or deployment behavior.
- Teaching does not authorize arbitrary edits, dependency installation, paid external calls, uploads, or production experiments.
- The skill works when invoked, without a background scheduler, atomic multi-file transaction, or concurrent shared-state writers. You decide whether to commit or ignore learning memory.
- Current behavior evidence is bounded and described in [validation](docs/validation.md). The latest prompt/document checks do not prove model compliance, success for all projects, or long-term learner outcomes.

The installable package is [deep-codebase-learning/](deep-codebase-learning/SKILL.md). Repository docs and maintainer checks are separate. See [current acceptance examples](docs/examples.md#l-v160-笔记优先与可选委派验收), [changelog](CHANGELOG.md), and [design provenance](docs/inspirations.md).

Design references include [learn-codebase](https://github.com/ktaletsk/learn-codebase), [learning-codebases](https://github.com/Eijnewgnaw/learning-codebases), [tutor](https://github.com/kevinnio/tutor), [code-learn-skill](https://github.com/yumeiriowl/code-learn-skill), and [repo-learner-suite](https://github.com/PranitMohnot/repo-learner-suite). No upstream code/templates are copied and none is a runtime dependency. [MIT License](LICENSE). [Issues](https://github.com/zgozh/deep-codebase/issues).
