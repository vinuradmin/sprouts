#!/usr/bin/env python3
"""
Local development runner for the Sprouts matching algorithm.

Pulls live data from Google Sheets, runs the same algorithm as the cloud function,
and writes results to a local CSV instead of pushing back to Sheets.

Usage:
    python run_local.py                        # uses current/upcoming cohort
    python run_local.py "Fall 2026"            # specific cohort
    python run_local.py "Fall 2026" --cohort   # same

Credentials (one of):
    - Place service-account-key.json in this directory
    - Set GOOGLE_SERVICE_ACCOUNT_KEY env var with the JSON content

Also reads GOOGLE_MAPS_API_KEY from a local .env file in this directory if present
(see .env.example). Real values in .env are gitignored.
"""

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
# Matching
# ---------------------------------------------------------------------------

def find_intern_restaurant_overlaps(chefs, intern, day, intern_slots, cache):
    overlaps = {}
    cache_dirty = False

    for chef in chefs.values():
        if chef.over_18_only and not intern.over_18:
            continue

        if not language_constraint_passes(chef, intern):
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
                overlaps.setdefault(name, {}).setdefault(day, []).append(overlap)
                overlaps[name][day] = overlaps[name].get(day, []) + [overlap]

    sorted_overlaps = dict(sorted(overlaps.items(), key=lambda x: x[1]['commute'].value))
    return sorted_overlaps, cache_dirty


def run_matching(intern_dicts, chef_dicts, cache):
    chefs = {}
    for row in chef_dicts:
        try:
            chef = Chef(row)
            if chef.restaurant_name:
                chefs[chef.restaurant_name] = chef
        except Exception as e:
            print(f'[WARN] Chef row error: {e}')

    interns = {}
    for row in intern_dicts:
        try:
            intern = InternLocal(row)
            if intern.full_name.strip():
                interns[intern.full_name] = intern
        except Exception as e:
            print(f'[WARN] Intern row error: {e}')

    print(f"Loaded {len(chefs)} restaurants, {len(interns)} interns")

    results = []
    cache_dirty = False

    for intern in interns.values():
        print(f"\nProcessing: {intern}")
        row_result = {'intern_name': intern.full_name, 'days': {}}

        for day, slots in intern.availability.items():
            day_overlaps, dirty = find_intern_restaurant_overlaps(chefs, intern, day, slots, cache)
            cache_dirty = cache_dirty or dirty

            matches = []
            for restaurant_name, info in day_overlaps.items():
                matches.append({
                    'restaurant': restaurant_name,
                    'commute': info['commute'].text,
                    'slots': str(info.get(day, [])),
                })
            row_result['days'][day] = matches

        results.append(row_result)

    return results, cache_dirty


# ---------------------------------------------------------------------------
# Local CSV output
# ---------------------------------------------------------------------------

def write_local_csv(results, cohort_name):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{cohort_name.replace(' ', '_').lower()}_matches_local_{timestamp}.csv"
    output_path = Path(__file__).parent / filename

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    header = ['Intern Name'] + days

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for r in results:
            row = [r['intern_name']]
            for day in days:
                matches = r['days'].get(day, [])
                cell = '\n'.join(
                    f"{m['restaurant']} ({m['commute']}): {m['slots']}" for m in matches
                )
                row.append(cell)
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

def main():
    if not GOOGLE_MAPS_API_KEY:
        print(
            "ERROR: GOOGLE_MAPS_API_KEY is not set.\n"
            "Commute times cannot be fabricated — export a real key before running:\n"
            "  export GOOGLE_MAPS_API_KEY='...'\n"
        )
        sys.exit(1)

    cohort = sys.argv[1] if len(sys.argv) > 1 else current_cohort()
    print(f"{'='*60}")
    print(f"Sprouts Local Runner — cohort: {cohort}")
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

    results, cache_dirty = run_matching(intern_dicts, chef_dicts, cache)

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
