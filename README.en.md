# Deep Codebase Learning

**Study a real codebase through detailed, beginner-friendly notes, then prove understanding through independent work.**

[中文](README.md) · [Usage](docs/usage.md) · [Design](docs/design.md) · [Validation](docs/validation.md) · [Contributing](CONTRIBUTING.md)

Open a conversation in the real project directory and say “Help me deeply learn this codebase.” Later, say “Continue learning” in the same or a new conversation.

Detailed, independently readable notes are the default lesson; chat gives the scope and note link, with direct answers whenever you ask. Records live in the project's `.codelearn/`. Use the default single session or choose [principal planning and independent review with a delegated author](deep-codebase-learning/references/authoring.md#首次选择与所有权). The [complete source-unit example](deep-codebase-learning/references/source-unit-example.md) is the default writing reference; consult the [older complete feature example](deep-codebase-learning/references/quality-example.md) when needed for full-lesson layout.

v1.12 writes with a unit loop and a prose gate. Each 5.x unit alternates a contiguous source segment (5–15 meaningful lines), its original-line heading, and full explanatory prose; the author runs `assemble_note.py --check` after each unit and repairs only the reported `thin_blocks`. After the lesson is complete, one read-through and one batched repair round precede assembly. Publication requires passing the [content gate](deep-codebase-learning/SKILL.md#整课交付硬约束): total teaching prose, prose per code line, and explanation after each long code block. Physical line counts and the former 2,000/3,000-line thresholds are gone, as are the draft/expand/finalize stages. The v1.11.31 assisted lesson and the frozen automatic-FAIL record remain as history; see [evidence and limits](docs/validation.md) and the [changelog](CHANGELOG.md).

## Start learning

Use an Agent Skills compatible host that can read your local checkout, write learning memory, and access relevant official documentation. Open a conversation in the project to study. Reading source and answering questions do not require running the target environment; unrun behavior stays unverified. Default local source rendering, full-lesson assembly and the prose content gate require Python 3.10+ already available in the host, used by the agent. If Python or safe file submission is unavailable, existing raw-file capabilities may save prepared drafts while questions continue. The agent must report that formal delivery remains incomplete, preserve the lesson content and saving requirements, and install no new tools. The optional [Skills CLI](https://github.com/vercel-labs/skills) needs Node.js/npm:

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

Each complete lesson follows ten teaching chapters: business goal; system position and architecture; prerequisites; end-to-end flow and scope; detailed source reading; mechanisms and official documentation; one dataset through normal and failure paths; tradeoffs and usage/extension; common confusions and answered review; learning outcome, evidence limits and next lesson. These are a lesson's learning structure, not ten business steps or fixed project stages; actual process steps belong in chapter 5's causal units, numbered 5.x. Their order and purpose remain stable while the feature route adapts to the repository. The first landscape lesson adapts this structure truthfully using system/business maps and actual repository evidence rather than claiming a completed code trace. Local chat questions need no ten-chapter treatment.

Every new term receives a brief explanation before first use, including architecture introductions, then sufficient teaching: full name and plain meaning, problem solved, mechanism, project use, concrete example, distinctions and analogy limits. A one-sentence definition is not completion. Chapter six deepens mechanisms; it cannot postpone foundations needed to read chapter five.

Chapter five is the substance: each causal unit follows problem/caller/input → complete real method or cohesive responsibility → detailed prose after the code for every displayed line → boundaries and local replay → usage/upstream/downstream and actual registration where relevant. Explain syntax, concrete values, execution, conditions, state, returns, reasons and consumers. Long methods may use consecutive labeled blocks, preserving relevant lines and matching structure; do not substitute fragments or synthetic closing lines for original source. License, blank and repetitive closing lines may be grouped. Inline teaching comments supplement prose. Explain implementation ideas, mechanisms, alternatives, tradeoffs and concrete failure paths with evidence, building engineering and architecture judgment alongside beginner foundations.

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

Repairs retain a recoverable baseline, correct source and necessary explanations, and reorganize affected units rather than appending repeated paragraphs. One semantic read-through covers every chapter and every behavior unit; brief review records do not permit sampling. A successful hard example or full flow cannot establish other units' quality. Judge source/knowledge facts and teaching depth separately; reread local repairs and affected dependencies, with full rereading for broad changes. The current example is available for reading after every chapter and behavior unit was reviewed, specific defects were repaired and affected sections were reread. See [validation](docs/validation.md) for the actual scope and withdrawn historical acceptance. This does not establish user approval, runtime success, long-term model stability or real learning outcomes.

Version 1.10.0 retains ten chapters and explains each involved actor's boundary, ownership, lifetime and contract, the real path to a visible result, and how framework intervention changes runtime behavior. Before the source, establish the problem, actual input and a complete clickable locator; inside it, preserve cohesive original code with teaching annotations; after it, use readable small sections to explain every displayed line, replay values and reason about design. These layers serve distinct purposes; long methods may use continuous blocks, each followed immediately by its explanation. Version 1.11.3 scopes the [example](deep-codebase-learning/references/quality-example.md) to a small complete feature, not a large full-stack representative lesson or a size limit. For a first lesson or major feedback, read the sections relevant to the chapter being written; read the whole example only when needed and reuse unchanged material already read. One semantic read-through judges factual correctness and beginner comprehension independently. The user rejected the previous example's depth and layout despite earlier static review; this correction and any structural checks do not establish general teaching quality or learning outcomes. No new gate tools, check matrices or runtime dependencies are added.

## Update and boundaries

For a CLI installation, update only this skill with `npx skills update deep-codebase-learning -g`, or `-p` for project-local installation. Follow installer/host discovery rules. Manual updates replace only installed skill files, never the target project's `.codelearn/`; re-read the latest skill in a conversation that already loaded old instructions.

- Generated notes are candidates to check. Article quality and scoped source/runtime verification are separate; self-review or subagent review is not proof of actual learning or deployment behavior.
- Teaching does not authorize arbitrary edits, dependency installation, paid external calls, uploads, or production experiments.
- The skill works when invoked, without a background scheduler, atomic multi-file transaction, or concurrent shared-state writers. You decide whether to commit or ignore learning memory.
- Current behavior evidence is bounded and described in [validation](docs/validation.md). The latest prompt/document checks do not prove model compliance, success for all projects, or long-term learner outcomes.

The installable package is [deep-codebase-learning/](deep-codebase-learning/SKILL.md). Repository docs and maintainer checks are separate. See [current acceptance examples](docs/examples.md#l-v160-笔记优先与可选委派验收), [changelog](CHANGELOG.md), and [design provenance](docs/inspirations.md).

Design references include [learn-codebase](https://github.com/ktaletsk/learn-codebase), [learning-codebases](https://github.com/Eijnewgnaw/learning-codebases), [tutor](https://github.com/kevinnio/tutor), [code-learn-skill](https://github.com/yumeiriowl/code-learn-skill), and [repo-learner-suite](https://github.com/PranitMohnot/repo-learner-suite). No upstream code/templates are copied and none is a runtime dependency. [MIT License](LICENSE). [Issues](https://github.com/zgozh/deep-codebase/issues).
