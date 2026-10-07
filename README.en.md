# Deep Codebase Learning

**Learn to explain, change, debug, and reconstruct the core of a real codebase with sustained AI guidance.**

[中文](README.md) · [Usage](docs/usage.md) · [Design and memory](docs/design.md) · [Validation](docs/validation.md) · [Contributing](CONTRIBUTING.md)

`deep-codebase-learning` is an Agent Skill that teaches through real feature flows, checks understanding with learner evidence, and stores durable progress in the target project's `.codelearn/` directory. Teaching follows the learner's language; detailed maintainer documentation is currently in Chinese.

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

In a later conversation in that same repository:

```text
Continue learning.
```

If automatic selection does not activate the skill, explicitly ask Codex to `Use $deep-codebase-learning to teach me this repository`. Other agents use their own invocation syntax. See [manual installation](docs/usage.md).

If HTTPS access is unavailable and GitHub SSH is already configured, use `git@github.com:zgozh/deep-codebase.git` as the source instead. Downloaded local repositories are also supported.

## How learning works

The agent builds architecture and feature maps, creates a repository-specific roadmap, and starts with a small learning unit. It traces real user actions or events through the system, including the UI return path when a frontend exists. It expands code progressively, explains design trade-offs, and detects prerequisite gaps. Knowledge detours return to the saved source location.

You predict behavior, inspect code, attempt experiments, answer questions, and restate flows. Acknowledgment is not mastery. Coverage, knowledge mastery, and reconstruction ability are tracked separately. Important components outside the main flows are covered by a horizontal audit. Completion requires an independently designed and runnable Mini Version.

## Durable learning memory

`.codelearn/` contains state, roadmap, project map, stage contracts, coverage, mastery, journals, knowledge bridges, notes, and reviews. Meaningful exchanges are saved automatically. Resume loads relevant records rather than the entire history.

Journals preserve structured learning events. Stage notes are technical articles rebuilt from source evidence, questions, misconceptions, experiments, and the learner's own understanding. Learning and note quality gates must both pass before a stage completes.

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
