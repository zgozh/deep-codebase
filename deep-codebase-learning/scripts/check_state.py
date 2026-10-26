"""Read-only v1 state shape checks; no migration, source verification or mastery assessment."""

import argparse
import json
from pathlib import Path


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate_key")
        value[key] = item
    return value


def check_state(state):
    errors = []
    nullable_text = (str, type(None))

    def fields(value, expected, where):
        for key, types in expected.items():
            if key not in value or type(value[key]) not in types:
                errors.append(where + "." + key)

    def refs(value, where):
        if type(value) is not list:
            return
        for index, ref in enumerate(value):
            location = where + "[" + str(index) + "]"
            if type(ref) is not dict:
                errors.append(location)
                continue
            fields(ref, {"path": (str,), "symbol": nullable_text,
                         "evidence_kind": (str,)}, location)
            if "revision" not in ref and "hash" not in ref:
                errors.append(location + ".revision/hash")
            if "revision" in ref and type(ref["revision"]) not in (str, dict, type(None)):
                errors.append(location + ".revision")
            if "hash" in ref and type(ref["hash"]) not in nullable_text:
                errors.append(location + ".hash")

    if type(state) is not dict:
        return ["$"]
    fields(state, {"schema_version": (int,), "skill_version": (str,),
                   "project": (dict,), "learner": (dict,), "mode": (str,), "phase": (str,),
                   "current": (dict,), "next_action": (dict,), "journal": (dict,),
                   "return_points": (list,), "focus_files": (list,), "open_loops": (list,),
                   "awaiting": (dict, type(None)), "pending_commit": (str, dict, type(None)),
                   "updated_at": nullable_text}, "$")
    if type(state.get("schema_version")) is int and state["schema_version"] != 1:
        errors.append("$.schema_version")
    project = state.get("project")
    if type(project) is dict:
        fields(project, {"name": nullable_text, "root_hint": (str,),
                         "revision": (dict, type(None)), "identity_sources": (list,)}, "$.project")
        if type(project.get("revision")) is dict:
            fields(project["revision"], {"branch": nullable_text, "commit": nullable_text}, "$.project.revision")
    learner = state.get("learner")
    if type(learner) is dict:
        fields(learner, {"goal": (str,), "background": (str,), "language": nullable_text}, "$.learner")
    current = state.get("current")
    if type(current) is dict:
        fields(current, {"stage": nullable_text, "topic": nullable_text, "source_refs": (list,)}, "$.current")
        refs(current.get("source_refs"), "$.current.source_refs")
    next_action = state.get("next_action")
    if type(next_action) is dict:
        fields(next_action, {"type": (str,), "target": (str,), "reason": (str,),
                             "load": (list,), "completion_condition": (str,)}, "$.next_action")
        if type(next_action.get("load")) is list:
            for index, path in enumerate(next_action["load"]):
                if type(path) is not str:
                    errors.append("$.next_action.load[" + str(index) + "]")
    journal = state.get("journal")
    if type(journal) is dict:
        fields(journal, {"active_file": nullable_text, "last_event": nullable_text,
                         "next_sequence": (int,)}, "$.journal")
        if type(journal.get("next_sequence")) is int and journal["next_sequence"] < 1:
            errors.append("$.journal.next_sequence")
    if type(state.get("focus_files")) is list:
        for index, path in enumerate(state["focus_files"]):
            if type(path) is not str:
                errors.append("$.focus_files[" + str(index) + "]")
    awaiting = state.get("awaiting")
    if type(awaiting) is dict:
        fields(awaiting, {"kind": (str,), "prompt": (str,), "topic": nullable_text,
                          "source_refs": (list,), "issued_event": nullable_text,
                          "rubric_ref": nullable_text}, "$.awaiting")
        refs(awaiting.get("source_refs"), "$.awaiting.source_refs")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state", type=Path)
    args = parser.parse_args()
    try:
        errors = check_state(json.loads(args.state.read_bytes().decode("utf-8-sig"),
                                        object_pairs_hook=unique_object))
    except (OSError, ValueError, UnicodeError):
        errors = ["$"]
    print(json.dumps({"valid": not errors, "errors": errors}))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
