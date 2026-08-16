#!/usr/bin/env python3
"""
Local development runner for the Sprouts matching algorithm.

Pulls live data from Google Sheets, runs the same algorithm as the cloud function,
and writes results to a local CSV instead of pushing back to Sheets.

Usage:
    python run_local.py                                     # uses current/upcoming cohort
    python run_local.py "Fall 2026"                         # specific cohort
    python run_local.py "Fall 2026" --no-language-matching  # run without Spanish-only kitchen gating
    python run_local.py "Fall 2026" --no-respect-prior-matches  # ignore prior placements, re-run everyone

Both enhancements default to ON; pass the --no-* flag to opt out for a run.

Credentials (one of):
    - Place service-account-key.json in this directory
    - Set GOOGLE_SERVICE_ACCOUNT_KEY env var with the JSON content

Also reads GOOGLE_MAPS_API_KEY from a local .env file in this directory if present
(see .env.example). Real values in .env are gitignored.
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def _load_dotenv():
    """Minimal .env loader — avoids adding python-dotenv as a dependency.

    Only sets variables not already present in the environment, so an explicit
    `export` still takes precedence.
    """
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key, value = key.strip(), value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_credentials(scopes):
    from google.oauth2 import service_account

    key_path = Path(__file__).parent / 'service-account-key.json'

    if key_path.exists():
        return service_account.Credentials.from_service_account_file(
            str(key_path), scopes=scopes
        )

    env_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_KEY')
    if env_json:
        info = json.loads(env_json)
        return service_account.Credentials.from_service_account_info(info, scopes=scopes)

    raise FileNotFoundError(
        "No service account credentials found.\n"
        "Either place service-account-key.json in this directory or set the "
        "GOOGLE_SERVICE_ACCOUNT_KEY environment variable."
    )


# ---------------------------------------------------------------------------
# Sheets helpers (mirrors cloud function logic)
# ---------------------------------------------------------------------------

SPREADSHEET_ID = '1c1A-FY8I16Jmq5FhXWEXiOvz9_eybAZNBXMqHVIAB-M'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


def get_sheets_service():
    from googleapiclient.discovery import build
    creds = get_credentials(SCOPES)
    return build('sheets', 'v4', credentials=creds)


def read_sheet(service, sheet_name):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=sheet_name
    ).execute()
    return result.get('values', [])


def filter_by_cohort(data, cohort_name):
    if not data or len(data) < 2:
        return []

    header_row_idx = None
    season_col = None

    for i, row in enumerate(data):
        for j, cell in enumerate(row):
            if str(cell).strip() == 'Season/Year':
                header_row_idx = i
                season_col = j
                break
        if header_row_idx is not None:
            break

    if header_row_idx is None:
        return []

    filtered = [data[header_row_idx]]
    for row in data[header_row_idx + 1:]:
        if len(row) > season_col and str(row[season_col]).strip() == cohort_name:
            filtered.append(row)

    return filtered


def rows_to_dicts(rows):
    if not rows or len(rows) < 2:
        return []
    headers = rows[0]
    result = []
    for row in rows[1:]:
        d = {headers[i]: (row[i] if i < len(row) else '') for i in range(len(headers))}
        result.append(d)
    return result


# ---------------------------------------------------------------------------
# Commute cache (local JSON, mirrors GCS version)
# ---------------------------------------------------------------------------

CACHE_PATH = Path(__file__).parent.parent / 'cached_commute.json'


def load_cache():
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache):
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2)


# ---------------------------------------------------------------------------
# Core classes (copied from main.py so this file is self-contained)
# ---------------------------------------------------------------------------

import re

GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def get_day_availability_raw(row: dict, day: str) -> str:
    """
    Read a day's raw availability string from a sheet row.

    The Chef/Intern Availability forms have been edited over time, which orphans
    the original short-named columns (e.g. 'Monday') in favor of new long-named
    ones (e.g. '...Scroll across to view more times.  [Monday]' or
    '...[Tuesday ]' with a stray trailing space before the bracket). Older rows
    may only have the short column populated; current rows only have the long
    one. Prefer the short column when present, otherwise search for any header
    ending in a bracketed day name.
    """
    short_value = row.get(day, '').strip()
    if short_value:
        return short_value

    pattern = re.compile(rf'\[\s*{re.escape(day)}\s*\]\s*$', re.IGNORECASE)
    for key, value in row.items():
        if pattern.search(key) and value and value.strip():
            return value.strip()

    return ''


def find_column_value(row: dict, name_substring: str) -> str:
    """Find a row value by a distinctive substring of its column header.

    Sheet question text carries incidental whitespace/punctuation drift across
    form edits, so match on a stable substring rather than the full header.
    """
    for key, value in row.items():
        if name_substring.lower() in key.lower():
            return (value or '').strip()
    return ''


def parse_languages(raw: str) -> list:
    """Split a 'Select all that apply' language answer into normalized parts."""
    if not raw:
        return []
    return [part.strip() for part in re.split(r'[,/]', raw) if part.strip()]


class Slot:
    def __init__(self, string='Unavailable'):
        self.start = 0
        self.end = 0
        self._from_string(string)

    def _from_string(self, s):
        s = s.strip()
        if s == 'All Day (9AM-9PM)':
            self.start, self.end = 9, 21
        elif s in ('', 'Unavailable'):
            pass
        else:
            parts = s.split('-')
            self.start = self._to24(parts[0])
            self.end = self._to24(parts[1])

    @staticmethod
    def _to24(s):
        s = s.strip()
        if 'AM' in s:
            return int(s.replace('AM', ''))
        elif s == '12PM':
            return 12
        else:
            return 12 + int(s.replace('PM', ''))

    def duration(self):
        return self.end - self.start

    def is_all_day(self):
        return self.start == 9 and self.end == 21

    def is_adjacent(self, other):
        return self.end == other.start or self.start == other.end

    def add_and_combine(self, other):
        if self.end == other.start:
            self.end = other.end
        else:
            self.start = other.start

    def get_overlap(self, other):
        o = Slot('')
        o.start = max(self.start, other.start)
        o.end = min(self.end, other.end)
        return o

    def __str__(self):
        return f'{self.start}-{self.end}'

    def __repr__(self):
        return str(self)

    @staticmethod
    def combine_slots(day_str):
        slots = []
        prev = Slot()
        for part in day_str.split(','):
            new = Slot(part)
            if new.is_all_day():
                return [new]
            if prev.is_adjacent(new):
                prev.add_and_combine(new)
                continue
            if prev.duration() >= 4:
                slots.append(prev)
            prev = new
        if prev.duration() >= 4:
            slots.append(prev)
        return slots


class Commute:
    def __init__(self, text, value):
        self.text = text
        self.value = value

    @staticmethod
    def from_dict(d):
        return Commute(d['text'], d['value'])

    def to_dict(self):
        return {'text': self.text, 'value': self.value}

    @staticmethod
    def get_commute_time(origin, destination):
        if not GOOGLE_MAPS_API_KEY:
            raise RuntimeError(
                'GOOGLE_MAPS_API_KEY is not set — refusing to fabricate a commute time. '
                'Set the environment variable before running.'
            )
        import googlemaps
        client = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
        try:
            res = client.distance_matrix(origin, destination, mode='transit')
            if res['status'] == 'OK':
                el = res['rows'][0]['elements'][0]
                if 'duration' in el:
                    return Commute(el['duration']['text'], el['duration']['value'])
        except Exception as e:
            print(f'[WARN] Commute API error: {e}')
        return Commute('Error', 100_000)

    def __str__(self):
        return self.text


class Chef:
    # Col BC: "What languages do you & your staff speak in the kitchen? Select all that apply."
    LANGUAGE_COLUMN_HINT = 'languages do you & your staff speak in the kitchen'

    def __init__(self, row):
        self.restaurant_name = row.get('Restaurant Name', '').strip()
        self.restaurant_address = row.get('Restaurant Address', '').strip()
        self.restaurant_location = row.get('Restaurant Location', '').strip()
        self.chef_name = row.get("Primary Mentor's Full Name (First and Last)", '').strip()
        self.over_18_only = row.get(
            'Do interns need to be over 18 to work in your kitchen?', ''
        ).strip().lower() != 'no'
        self.languages = parse_languages(find_column_value(row, self.LANGUAGE_COLUMN_HINT))
        self.availability = {
            day: Slot.combine_slots(get_day_availability_raw(row, day))
            for day in DAYS
        }

    def get_full_address(self):
        return f"{self.restaurant_address}, {self.restaurant_location}"

    def is_spanish_only(self):
        """True only when Spanish is the sole language listed for the kitchen."""
        langs = {lang.lower() for lang in self.languages}
        return langs == {'spanish'}

    def display_name(self):
        return f"{self.restaurant_name} *" if self.is_spanish_only() else self.restaurant_name


class InternLocal:
    # Col BP: "What languages do you speak fluently?"
    LANGUAGE_COLUMN_HINT = 'languages do you speak fluently'

    def __init__(self, row):
        self.first_name = row.get('First Name', '').strip()
        self.last_name = row.get('Last Name', '').strip()
        self.full_name = f"{self.first_name} {self.last_name}".strip()
        self.address = row.get('Street Address', '').strip()
        self.city = row.get('City', '').strip()
        self.zip_code = row.get('Zip Code', '').strip()
        self.over_18 = row.get('Are you over 18 years old?', '').strip().lower() == 'yes'
        self.transportation = row.get('What transportation will you use?', '').strip()
        self.languages = parse_languages(find_column_value(row, self.LANGUAGE_COLUMN_HINT))
        # Col G: 'restaurantname' — set when this intern was already placed in
        # a prior matching round. A non-empty value means this intern is not
        # up for matching; their restaurant is fixed.
        self.pre_matched_restaurant = row.get('restaurantname', '').strip()
        self.availability = {
            day: Slot.combine_slots(get_day_availability_raw(row, day))
            for day in DAYS
        }

    @property
    def speaks_spanish(self):
        return 'spanish' in {lang.lower() for lang in self.languages}

    def get_full_address(self):
        return f"{self.address}, {self.city}, {self.zip_code}"

    def __str__(self):
        return self.full_name


# ---------------------------------------------------------------------------
# Language constraint
# ---------------------------------------------------------------------------

def language_constraint_passes(chef: Chef, intern: InternLocal) -> bool:
    """Spanish-only kitchens may only host Spanish-speaking interns."""
    if chef.is_spanish_only():
        return intern.speaks_spanish
    return True


# ---------------------------------------------------------------------------
# Pre-matched interns and restaurant capacity
# ---------------------------------------------------------------------------

DEFAULT_RESTAURANT_CAPACITY = 2

# Restaurants exempt from the capacity cap — university/special-program
# partners that intentionally host more interns than a normal kitchen.
# No sheet column currently identifies these, so this is a hardcoded list
# pending a real data source; pass a different set via
# run_matching(..., capacity_exempt_restaurants=...) to override.
CAPACITY_EXEMPT_RESTAURANTS = set()


def partition_pre_matched(interns: dict):
    """Split interns into (already placed, still need matching), preserving order."""
    pre_matched = []
    unmatched = []
    for intern in interns.values():
        if intern.pre_matched_restaurant:
            pre_matched.append(intern)
        else:
            unmatched.append(intern)
    return pre_matched, unmatched


def compute_full_restaurants(pre_matched: list, capacity: int, exempt: set) -> set:
    """Restaurant names that have hit capacity purely from fixed (pre-matched)
    assignments, and so shouldn't be offered as a new option to remaining
    unmatched interns. Exempt restaurants are never considered full."""
    counts = {}
    for intern in pre_matched:
        name = intern.pre_matched_restaurant
        counts[name] = counts.get(name, 0) + 1

    return {
        name for name, count in counts.items()
        if count >= capacity and name not in exempt
    }


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def find_intern_restaurant_overlaps(chefs, intern, day, intern_slots, cache, enable_language_matching=True):
    overlaps = {}
    cache_dirty = False

    for chef in chefs.values():
        if chef.over_18_only and not intern.over_18:
            continue

        if enable_language_matching and not language_constraint_passes(chef, intern):
            print(f"  {intern.full_name} skipped {chef.restaurant_name} (Spanish-only kitchen)")
            continue

        for chef_slot in chef.availability.get(day, []):
            for intern_slot in intern_slots:
                overlap = chef_slot.get_overlap(intern_slot)
                if overlap.duration() < 4:
                    continue

                cache_key = f"{intern.get_full_address()}|{chef.get_full_address()}"

                if cache_key in cache:
                    commute = Commute.from_dict(cache[cache_key])
                else:
                    commute = Commute.get_commute_time(
                        intern.get_full_address(), chef.get_full_address()
                    )
                    # Don't persist failed lookups (e.g. an expired API key) —
                    # doing so would permanently poison the cache with bogus
                    # "no commute possible" results for that pair.
                    if commute.text != 'Error':
                        cache[cache_key] = commute.to_dict()
                        cache_dirty = True

                if commute.value > 10_800:  # 3 hours in seconds
                    continue

                name = chef.display_name()
                if name not in overlaps:
                    overlaps[name] = {'commute': commute}
                overlaps[name].setdefault(day, []).append(overlap)

    sorted_overlaps = dict(sorted(overlaps.items(), key=lambda x: x[1]['commute'].value))
    return sorted_overlaps, cache_dirty


# ---------------------------------------------------------------------------
# Weekly schedule recommendations
#
# Interns target 12 hours/week at a single restaurant, delivered as either
# 2 days x 6 hours or 3 days x 4 hours (the same pattern used elsewhere in
# this codebase — see the schedule_suggestions logic in
# app/main/matching_routes.py and the 12-hour trim logic in
# app/services/hungarian_matching.py). Rather than showing every raw overlap
# per day, this surfaces the top 3 restaurants that can actually deliver a
# full week's schedule, ranked by whether they hit 12h and by commute.
# ---------------------------------------------------------------------------

TARGET_WEEKLY_HOURS = 12.0


def format_commute_minutes(minutes: float) -> str:
    """Compact commute text, e.g. '45m' or '1h14m'."""
    total = round(minutes)
    hours, mins = divmod(total, 60)
    return f"{hours}h{mins}m" if hours else f"{mins}m"


def _short_day(day: str) -> str:
    return day[:3]


def _format_hour_12(hour: int) -> str:
    period = 'AM' if hour < 12 else 'PM'
    display_hour = hour % 12 or 12
    return f"{display_hour}{period}"


def format_slot_time(slot: Slot) -> str:
    """Human-readable time range, e.g. '5PM-9PM' instead of '17-21'."""
    return f"{_format_hour_12(slot.start)}-{_format_hour_12(slot.end)}"


def compute_weekly_plan(day_options: dict, target_hours: float = TARGET_WEEKLY_HOURS):
    """
    day_options: {day: {'hours': float, 'commute_minutes': float}} for one
    restaurant — only days where that restaurant is otherwise a valid option
    for the intern (age/language/commute-cutoff already applied upstream).

    Prefers 2 days x 6h, then 3 days x 4h (trimming a longer overlap down to
    the pattern's hours, matching the "exactly 12h" convention used
    elsewhere). Falls back to a best-effort combination of whatever days are
    available when neither clean pattern fits. Returns None when fewer than
    2 days are available — a single day isn't a viable weekly placement.
    """
    days_by_length = sorted(day_options.keys(), key=lambda d: -day_options[d]['hours'])

    def build(selected_days, per_day_hours):
        total = sum(per_day_hours.values())
        avg_commute = sum(day_options[d]['commute_minutes'] for d in selected_days) / len(selected_days)
        return {
            'days': selected_days,
            'per_day_hours': per_day_hours,
            'total_hours': total,
            'avg_commute_minutes': avg_commute,
            'meets_target': total >= target_hours - 1e-9,
        }

    two_day_candidates = [d for d in days_by_length if day_options[d]['hours'] >= 6]
    if len(two_day_candidates) >= 2:
        chosen = two_day_candidates[:2]
        return build(chosen, {d: 6.0 for d in chosen})

    if len(days_by_length) >= 3:
        chosen = days_by_length[:3]
        return build(chosen, {d: 4.0 for d in chosen})

    if len(days_by_length) >= 2:
        chosen = days_by_length
        return build(chosen, {d: day_options[d]['hours'] for d in chosen})

    return None


def describe_plan(plan: dict) -> str:
    """Human-readable text for a weekly plan, for the CSV cell."""
    per_day = plan['per_day_hours']
    if len(plan['days']) == 2 and all(h == 6 for h in per_day.values()):
        pattern = '2×6h'
    elif len(plan['days']) == 3 and all(h == 4 for h in per_day.values()):
        pattern = '3×4h'
    else:
        pattern = f"{plan['total_hours']:g}h"

    days_str = ', '.join(_short_day(d) for d in plan['days'])
    commute = format_commute_minutes(plan['avg_commute_minutes'])
    target_note = '' if plan['meets_target'] else ' (under 12h target)'

    return f"{plan['restaurant']} — {plan['total_hours']:g}h/wk ({pattern}: {days_str}) · avg {commute}{target_note}"


def compute_top_weekly_recommendations(chefs: dict, intern, cache: dict,
                                        enable_language_matching: bool = True, top_n: int = 3):
    """
    For one intern, find the best weekly plan per restaurant across all 7
    days and return the top N, ranked by whether they hit the 12h target
    (yes before no) and then by average commute (lower is better).

    Returns (plans, cache_dirty).
    """
    by_restaurant = {}
    cache_dirty = False

    for day, slots in intern.availability.items():
        day_overlaps, dirty = find_intern_restaurant_overlaps(
            chefs, intern, day, slots, cache, enable_language_matching=enable_language_matching,
        )
        cache_dirty = cache_dirty or dirty

        for name, info in day_overlaps.items():
            day_slots = info.get(day, [])
            if not day_slots:
                continue
            best_slot = max(day_slots, key=lambda s: s.duration())
            by_restaurant.setdefault(name, {})[day] = {
                'hours': best_slot.duration(),
                'commute_minutes': info['commute'].value / 60,
            }

    plans = []
    for name, day_options in by_restaurant.items():
        plan = compute_weekly_plan(day_options)
        if plan:
            plan['restaurant'] = name
            plans.append(plan)

    plans.sort(key=lambda p: (not p['meets_target'], p['avg_commute_minutes']))

    return plans[:top_n], cache_dirty


def dedupe_intern_rows(intern_dicts: list):
    """Parse intern rows into a name-keyed dict, resolving duplicate rows.

    The sheet sometimes has two rows for the same person after whitespace
    normalization (e.g. a stray leading/trailing space on First/Last Name from
    a re-submitted form). When that happens, prefer whichever row has a
    non-empty pre-matched restaurant over a blank one — an already-made
    placement decision shouldn't be silently discarded because of a blank
    duplicate. If both rows have a restaurant and they disagree, that's a real
    conflict that needs a human, so we keep the first one and flag it loudly
    rather than guessing.

    Returns (interns, notes) where notes maps full_name -> a note describing
    any judgment call made, to be surfaced in the output.
    """
    interns = {}
    notes = {}

    for row in intern_dicts:
        try:
            intern = InternLocal(row)
        except Exception as e:
            print(f'[WARN] Intern row error: {e}')
            continue

        if not intern.full_name.strip():
            continue

        existing = interns.get(intern.full_name)
        if existing is None:
            interns[intern.full_name] = intern
            continue

        # Duplicate row for this name — decide which one is authoritative.
        if existing.pre_matched_restaurant and intern.pre_matched_restaurant:
            if existing.pre_matched_restaurant != intern.pre_matched_restaurant:
                note = (
                    f"CONFLICT: duplicate rows list different restaurants "
                    f"({existing.pre_matched_restaurant!r} vs {intern.pre_matched_restaurant!r}) "
                    f"— kept {existing.pre_matched_restaurant!r}, needs manual review"
                )
                notes[intern.full_name] = note
                print(f'[WARN] {intern.full_name}: {note}')
            # Same restaurant on both — harmless duplicate, nothing to flag.
            continue

        if intern.pre_matched_restaurant and not existing.pre_matched_restaurant:
            note = (
                f"Duplicate row detected — kept the row with a restaurant "
                f"assignment ({intern.pre_matched_restaurant!r}), ignored a blank duplicate"
            )
            notes[intern.full_name] = note
            print(f'[WARN] {intern.full_name}: {note}')
            interns[intern.full_name] = intern
            continue

        if existing.pre_matched_restaurant and not intern.pre_matched_restaurant:
            note = (
                f"Duplicate row detected — kept the row with a restaurant "
                f"assignment ({existing.pre_matched_restaurant!r}), ignored a blank duplicate"
            )
            notes[intern.full_name] = note
            print(f'[WARN] {intern.full_name}: {note}')
            continue

        # Both blank — harmless duplicate, nothing to flag.

    return interns, notes


def _fixed_row_for_pre_matched(intern: InternLocal, chefs: dict, note: str = '') -> dict:
    """Build a result row for an intern whose restaurant is already decided.

    Every day shows the same fixed restaurant — there's no algorithm decision
    to make. If the decided restaurant isn't in this cohort's current chef
    list (e.g. it dropped out), report the name exactly as the sheet has it
    rather than fabricating or silently dropping it.
    """
    chef = chefs.get(intern.pre_matched_restaurant)
    display_name = chef.display_name() if chef else intern.pre_matched_restaurant

    fixed_match = {'restaurant': display_name, 'commute': 'Already matched', 'slots': ''}
    return {
        'intern_name': intern.full_name,
        'days': {day: [fixed_match] for day in DAYS},
        'weekly_recommendations': [f'Already matched: {display_name}'],
        'notes': note,
    }


def run_matching(intern_dicts, chef_dicts, cache,
                  restaurant_capacity=DEFAULT_RESTAURANT_CAPACITY,
                  capacity_exempt_restaurants=None,
                  enable_language_matching=True,
                  enable_respect_prior_matches=True):
    """
    enable_language_matching: gate Spanish-only kitchens to Spanish-speaking
        interns. When False, all kitchens are open to all interns regardless
        of language (the Spanish-only '*' marker still displays either way —
        it's informational, not the enforcement).
    enable_respect_prior_matches: treat interns with a decided restaurant
        (col G 'restaurantname') as fixed placements, and exclude restaurants
        that prior matches have filled from new recommendations. When False,
        prior-match data is ignored entirely and every intern goes through
        the normal algorithm with the full restaurant pool.

    TODO: once wired into the deployed cloud function, expose both of these
    as checkboxes in the HTML popup (cloud-function/main.py), defaulted to
    checked, so a user can opt out of either enhancement for a given run.
    """
    exempt = capacity_exempt_restaurants if capacity_exempt_restaurants is not None else CAPACITY_EXEMPT_RESTAURANTS

    chefs = {}
    for row in chef_dicts:
        try:
            chef = Chef(row)
            if chef.restaurant_name:
                chefs[chef.restaurant_name] = chef
        except Exception as e:
            print(f'[WARN] Chef row error: {e}')

    interns, notes = dedupe_intern_rows(intern_dicts)

    print(f"Loaded {len(chefs)} restaurants, {len(interns)} interns")

    if enable_respect_prior_matches:
        pre_matched, unmatched = partition_pre_matched(interns)
        full_restaurants = compute_full_restaurants(pre_matched, restaurant_capacity, exempt)
        if full_restaurants:
            print(f"Restaurants at capacity from prior matches (excluded from new matches): {sorted(full_restaurants)}")
    else:
        pre_matched, full_restaurants = [], set()

    available_chefs = {name: c for name, c in chefs.items() if name not in full_restaurants}

    results = []
    cache_dirty = False

    for intern in interns.values():
        if enable_respect_prior_matches and intern.pre_matched_restaurant:
            print(f"\n{intern}: already matched to {intern.pre_matched_restaurant}")
            results.append(_fixed_row_for_pre_matched(intern, chefs, notes.get(intern.full_name, '')))
            continue

        print(f"\nProcessing: {intern}")
        row_result = {'intern_name': intern.full_name, 'days': {}, 'notes': notes.get(intern.full_name, '')}

        for day, slots in intern.availability.items():
            day_overlaps, dirty = find_intern_restaurant_overlaps(
                available_chefs, intern, day, slots, cache,
                enable_language_matching=enable_language_matching,
            )
            cache_dirty = cache_dirty or dirty

            matches = []
            for restaurant_name, info in day_overlaps.items():
                day_slots = info.get(day, [])
                matches.append({
                    'restaurant': restaurant_name,
                    'commute': info['commute'].text,
                    'slots': ', '.join(format_slot_time(s) for s in day_slots),
                })
            row_result['days'][day] = matches

        weekly_plans, dirty = compute_top_weekly_recommendations(
            available_chefs, intern, cache, enable_language_matching=enable_language_matching,
        )
        cache_dirty = cache_dirty or dirty
        row_result['weekly_recommendations'] = [describe_plan(p) for p in weekly_plans]

        results.append(row_result)

    return results, cache_dirty


# ---------------------------------------------------------------------------
# Local CSV output
# ---------------------------------------------------------------------------

DAY_CELL_DISPLAY_LIMIT = 3


def write_local_csv(results, cohort_name):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{cohort_name.replace(' ', '_').lower()}_matches_local_{timestamp}.csv"
    output_path = Path(__file__).parent / filename

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    header = ['Intern Name', 'Top 3 Recommended'] + days + ['Notes']

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for r in results:
            row = [r['intern_name']]
            row.append('\n'.join(r.get('weekly_recommendations', [])))
            for day in days:
                matches = r['days'].get(day, [])
                # Already sorted by commute time; keep the CSV scannable by
                # capping each cell and noting how many more exist rather
                # than dumping every option into one wall of text.
                shown = matches[:DAY_CELL_DISPLAY_LIMIT]
                lines = [f"{m['restaurant']} · {m['commute']} · {m['slots']}" for m in shown]
                if len(matches) > DAY_CELL_DISPLAY_LIMIT:
                    lines.append(f"+{len(matches) - DAY_CELL_DISPLAY_LIMIT} more")
                row.append('\n'.join(lines))
            row.append(r.get('notes', ''))
            writer.writerow(row)

    print(f"\nOutput: {output_path}")
    return output_path


# ---------------------------------------------------------------------------
# Cohort auto-detection
# ---------------------------------------------------------------------------

def current_cohort():
    now = datetime.now()
    m = now.month
    y = now.year
    if m <= 5:
        return f"Spring {y}"
    elif m <= 8:
        return f"Fall {y}"
    else:
        return f"Fall {y}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(description='Sprouts local matching runner')
    parser.add_argument('cohort', nargs='?', default=None, help='e.g. "Fall 2026" (default: current/upcoming cohort)')
    parser.add_argument(
        '--no-language-matching', dest='enable_language_matching', action='store_false',
        help='Disable Spanish-only kitchen gating — run without the language matching enhancement'
    )
    parser.add_argument(
        '--no-respect-prior-matches', dest='enable_respect_prior_matches', action='store_false',
        help='Ignore prior placements — re-run matching for every intern regardless of a decided restaurant'
    )
    parser.set_defaults(enable_language_matching=True, enable_respect_prior_matches=True)
    return parser.parse_args()


def main():
    if not GOOGLE_MAPS_API_KEY:
        print(
            "ERROR: GOOGLE_MAPS_API_KEY is not set.\n"
            "Commute times cannot be fabricated — export a real key before running:\n"
            "  export GOOGLE_MAPS_API_KEY='...'\n"
        )
        sys.exit(1)

    args = parse_args()
    cohort = args.cohort or current_cohort()
    print(f"{'='*60}")
    print(f"Sprouts Local Runner — cohort: {cohort}")
    print(f"  Language matching: {'ON' if args.enable_language_matching else 'OFF'}")
    print(f"  Respect prior matches: {'ON' if args.enable_respect_prior_matches else 'OFF'}")
    print(f"{'='*60}\n")

    cache = load_cache()
    print(f"Loaded {len(cache)} cached commutes")

    print("Connecting to Google Sheets...")
    service = get_sheets_service()

    print("Reading Intern Availabilities...")
    intern_data = read_sheet(service, 'Intern Availabilities')

    print("Reading Chef Availabilities...")
    chef_data = read_sheet(service, 'Chef Availabilities')

    print(f"Filtering for cohort: {cohort}")
    intern_rows = filter_by_cohort(intern_data, cohort)
    chef_rows = filter_by_cohort(chef_data, cohort)

    if not intern_rows or len(intern_rows) < 2:
        print(f"No intern data found for cohort '{cohort}'")
        print("Available cohorts:", _list_cohorts(intern_data))
        sys.exit(1)

    if not chef_rows or len(chef_rows) < 2:
        print(f"No chef data found for cohort '{cohort}'")
        sys.exit(1)

    print(f"Found {len(intern_rows)-1} interns, {len(chef_rows)-1} restaurants\n")

    intern_dicts = rows_to_dicts(intern_rows)
    chef_dicts = rows_to_dicts(chef_rows)

    results, cache_dirty = run_matching(
        intern_dicts, chef_dicts, cache,
        enable_language_matching=args.enable_language_matching,
        enable_respect_prior_matches=args.enable_respect_prior_matches,
    )

    if cache_dirty:
        save_cache(cache)
        print(f"Cache updated: {CACHE_PATH}")

    write_local_csv(results, cohort)

    print(f"\nDone — matched {len(results)} interns")


def _list_cohorts(data):
    cohorts = set()
    for row in data:
        for i, cell in enumerate(row):
            if str(cell).strip() == 'Season/Year':
                for r in data:
                    if len(r) > i and r[i] and r[i] != 'Season/Year':
                        cohorts.add(r[i])
                return sorted(cohorts)
    return []


if __name__ == '__main__':
    main()
