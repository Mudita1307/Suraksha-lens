from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from dataclasses import dataclass, field


PLACEHOLDER_RE = re.compile(r"\{[^{}]*\}|%\([^)]*\)s|%s|%d")

URL_RE = re.compile(r"https?://[^\s\"'<>()]+")


NATIVE_DIGIT_RANGES = [
    ("Devanagari (hi)", 0x0966, 0x096F),
    ("Bengali (bn)", 0x09E6, 0x09EF),
    ("Kannada (kn)", 0x0CE6, 0x0CEF),
    ("Malayalam (ml)", 0x0D66, 0x0D6F),
    ("Sinhala (si)", 0x0DE6, 0x0DEF),
    ("Tamil (ta)", 0x0BE6, 0x0BEF),
]


@dataclass
class ValidationResult:
    locale: str
    missing_keys: list = field(default_factory=list)
    extra_keys: list = field(default_factory=list)
    placeholder_mismatches: list = field(default_factory=list)
    url_mismatches: list = field(default_factory=list)
    numeral_violations: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not (
            self.missing_keys
            or self.extra_keys
            or self.placeholder_mismatches
            or self.url_mismatches
            or self.numeral_violations
        )


def _flatten(d: dict, prefix: str = "") -> dict:
    """Flatten a nested dict into {"a.b.c": value} for leaf strings only."""
    out = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            out.update(_flatten(v, key))
        else:
            out[key] = v
    return out


def _placeholders(s: str) -> set:
    return set(PLACEHOLDER_RE.findall(s)) if isinstance(s, str) else set()


def _urls(s: str) -> set:
    return set(URL_RE.findall(s)) if isinstance(s, str) else set()


def _native_digit_violations(s: str) -> list:
    if not isinstance(s, str):
        return []
    hits = []
    for label, lo, hi in NATIVE_DIGIT_RANGES:
        for ch in s:
            if lo <= ord(ch) <= hi:
                hits.append(f"{label} digit '{ch}' (U+{ord(ch):04X})")
    return hits


def validate_locale(reference_flat: dict, locale_name: str, locale_flat: dict) -> ValidationResult:
    result = ValidationResult(locale=locale_name)

    ref_keys = set(reference_flat)
    loc_keys = set(locale_flat)

    result.missing_keys = sorted(ref_keys - loc_keys)
    result.extra_keys = sorted(loc_keys - ref_keys)

    for key in sorted(ref_keys & loc_keys):
        ref_val = reference_flat[key]
        loc_val = locale_flat[key]

        ref_ph = _placeholders(ref_val)
        loc_ph = _placeholders(loc_val)
        if ref_ph != loc_ph:
            result.placeholder_mismatches.append(
                {"key": key, "expected": sorted(ref_ph), "found": sorted(loc_ph)}
            )

        ref_urls = _urls(ref_val)
        if ref_urls:
            loc_urls = _urls(loc_val)
            if ref_urls != loc_urls:
                result.url_mismatches.append(
                    {"key": key, "expected": sorted(ref_urls), "found": sorted(loc_urls)}
                )

        digit_hits = _native_digit_violations(loc_val)
        if digit_hits:
            result.numeral_violations.append({"key": key, "violations": digit_hits})

    return result


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run(directory: str, reference_filename: str, pattern: str) -> bool:
    ref_path = os.path.join(directory, reference_filename)
    if not os.path.isfile(ref_path):
        print(f"ERROR: reference file not found: {ref_path}", file=sys.stderr)
        return False

    reference = _flatten(load_json(ref_path))

    locale_paths = sorted(glob.glob(os.path.join(directory, pattern)))
    locale_paths = [p for p in locale_paths if os.path.basename(p) != reference_filename]

    if not locale_paths:
        print(f"ERROR: no locale files matched {pattern!r} in {directory}", file=sys.stderr)
        return False

    all_ok = True
    for path in locale_paths:
        name = os.path.basename(path)
        try:
            locale_data = _flatten(load_json(path))
        except json.JSONDecodeError as e:
            print(f"[FAIL] {name}: invalid JSON — {e}")
            all_ok = False
            continue

        result = validate_locale(reference, name, locale_data)

        if result.ok:
            print(f"[PASS] {name}  ({len(locale_data)} keys checked)")
            continue

        all_ok = False
        print(f"[FAIL] {name}")
        if result.missing_keys:
            print(f"    missing keys ({len(result.missing_keys)}): {result.missing_keys}")
        if result.extra_keys:
            print(f"    extra keys ({len(result.extra_keys)}): {result.extra_keys}")
        for m in result.placeholder_mismatches:
            print(
                f"    placeholder mismatch @ {m['key']}: "
                f"expected {m['expected']}, found {m['found']}"
            )
        for m in result.url_mismatches:
            print(
                f"    URL mismatch @ {m['key']}: "
                f"expected {m['expected']}, found {m['found']}"
            )
        for m in result.numeral_violations:
            print(f"    numeral convention @ {m['key']}: {m['violations']}")

    return all_ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dir",
        default=os.path.join(os.path.dirname(__file__), "locales"),
        help="Directory containing locale JSON files (default: ./locales)",
    )
    parser.add_argument(
        "--reference",
        default="chatbot_keys.en.json",
        help="Filename of the reference (English) locale within --dir "
             "(default: chatbot_keys.en.json — the new-key bundle; pass "
             "'en.json' to validate the project's full locale files instead)",
    )
    parser.add_argument(
        "--pattern",
        default="chatbot_keys.*.json",
        help="Glob pattern (within --dir) matching locale files to check "
             "(default: chatbot_keys.*.json; pass '*.json' for full locale files)",
    )
    args = parser.parse_args()

    ok = run(args.dir, args.reference, args.pattern)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()