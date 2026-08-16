"""
Tests for the language-matching constraint: Spanish-only kitchens (Column BC)
may only be matched with Spanish-speaking interns (Column BP), and Spanish-only
kitchens should be visually flagged in output.

Also covers the day-availability column fallback, since the live Chef/Intern
Availability sheets have drifted: form edits orphaned the original short-named
day columns ('Monday') in favor of new long-named ones, and current rows only
populate the long form.

Run with: python -m pytest test_language_constraint.py -v
"""

from run_local import (
    Chef,
    InternLocal,
    Slot,
    get_day_availability_raw,
    language_constraint_passes,
    parse_languages,
)

# Real header text pulled from the live "Chef Availabilities" / "Intern Availabilities"
# sheets (SPREADSHEET_ID in run_local.py), including their actual whitespace quirks.

CHEF_DAY_PREFIX = (
    'Please select ALL HOURS that you are available to host an intern for shifts '
    'each day. Please see the below example of how to input your availability. '
    '\n\nIf you can host from 9-4pm and 6-9pm, check ALL boxes from 9AM to 4PM and '
    '6PM to 9PM. If you are closed/unable to host on a certain day click '
    '"Unavailable."\n\nPlease Note: We only schedule shifts within the hours of '
    '9AM-9PM. \n\nScroll across to view more times.  '
)

# Note the inconsistent trailing space before the closing bracket on some days —
# this is exactly how the live sheet has it.
CHEF_DAY_COLUMNS = {
    'Monday': CHEF_DAY_PREFIX + '[Monday]',
    'Tuesday': CHEF_DAY_PREFIX + '[Tuesday ]',
    'Wednesday': CHEF_DAY_PREFIX + '[Wednesday]',
    'Thursday': CHEF_DAY_PREFIX + '[Thursday]',
    'Friday': CHEF_DAY_PREFIX + '[Friday ]',
    'Saturday': CHEF_DAY_PREFIX + '[Saturday]',
    'Sunday': CHEF_DAY_PREFIX + '[Sunday]',
}

CHEF_LANGUAGE_COLUMN = (
    'What languages do you & your staff speak in the kitchen? Select all that apply. '
)

INTERN_DAY_PREFIX = (
    'Please select all times that you are available for shifts each day.\n\n'
    'Please take into account school end times, after-school activities, '
    'recurring meetings, sports, etc.  \n\nFor example - If you have school '
    'ending at 3pm and can start work at 4pm select all hours from 4PM to 9PM. '
    'If you can\'t work on a certain day click "Unavailable."\n\nPlease scroll '
    'over to view more times and view the example below. '
)

INTERN_DAY_COLUMNS = {
    'Monday': INTERN_DAY_PREFIX + '[Monday]',
    'Tuesday': INTERN_DAY_PREFIX + '[Tuesday]',
    'Wednesday': INTERN_DAY_PREFIX + '[Wednesday]',
    'Thursday': INTERN_DAY_PREFIX + '[Thursday]',
    'Friday': INTERN_DAY_PREFIX + '[Friday]',
    'Saturday': INTERN_DAY_PREFIX + '[Saturday]',
    'Sunday': INTERN_DAY_PREFIX + '[Sunday]',
}

INTERN_LANGUAGE_COLUMN = 'What languages do you speak fluently?'


def make_chef_row(restaurant_name, languages, monday_hours='All Day (9AM-9PM)', over_18='No'):
    row = {
        'Restaurant Name': restaurant_name,
        'Restaurant Address': '123 Main St',
        'Restaurant Location': 'Oakland, CA',
        "Primary Mentor's Full Name (First and Last)": 'Chef Test',
        'Do interns need to be over 18 to work in your kitchen?': over_18,
        CHEF_LANGUAGE_COLUMN: languages,
    }
    for day, column in CHEF_DAY_COLUMNS.items():
        row[column] = monday_hours if day == 'Monday' else 'Unavailable'
    return row


def make_intern_row(first_name, last_name, languages, monday_hours='All Day (9AM-9PM)'):
    row = {
        'First Name': first_name,
        'Last Name': last_name,
        'Street Address': '456 Oak Ave',
        'City': 'Oakland',
        'Zip Code': '94612',
        'Are you over 18 years old?': 'Yes',
        'What transportation will you use?': 'Driving',
        INTERN_LANGUAGE_COLUMN: languages,
    }
    for day, column in INTERN_DAY_COLUMNS.items():
        row[column] = monday_hours if day == 'Monday' else 'Unavailable'
    return row


# ---------------------------------------------------------------------------
# parse_languages
# ---------------------------------------------------------------------------

def test_parse_languages_comma_separated():
    assert parse_languages('English, Spanish') == ['English', 'Spanish']


def test_parse_languages_single():
    assert parse_languages('Spanish') == ['Spanish']


def test_parse_languages_empty():
    assert parse_languages('') == []
    assert parse_languages(None) == []


# ---------------------------------------------------------------------------
# Chef.is_spanish_only / display_name
# ---------------------------------------------------------------------------

def test_chef_spanish_only_kitchen_is_flagged():
    chef = Chef(make_chef_row('La Cocina', 'Spanish'))
    assert chef.is_spanish_only() is True
    assert chef.display_name() == 'La Cocina *'


def test_chef_bilingual_kitchen_is_not_spanish_only():
    chef = Chef(make_chef_row('The Grill', 'English, Spanish'))
    assert chef.is_spanish_only() is False
    assert chef.display_name() == 'The Grill'


def test_chef_english_only_kitchen_is_not_spanish_only():
    chef = Chef(make_chef_row('Downtown Diner', 'English'))
    assert chef.is_spanish_only() is False
    assert chef.display_name() == 'Downtown Diner'


# ---------------------------------------------------------------------------
# InternLocal.speaks_spanish
# ---------------------------------------------------------------------------

def test_intern_speaks_spanish_only():
    intern = InternLocal(make_intern_row('Maria', 'Lopez', 'Spanish'))
    assert intern.speaks_spanish is True


def test_intern_bilingual_speaks_spanish():
    intern = InternLocal(make_intern_row('Alex', 'Chen', 'English, Spanish'))
    assert intern.speaks_spanish is True


def test_intern_english_only_does_not_speak_spanish():
    intern = InternLocal(make_intern_row('Alice', 'Smith', 'English'))
    assert intern.speaks_spanish is False


# ---------------------------------------------------------------------------
# language_constraint_passes — the core matching rule
# ---------------------------------------------------------------------------

def test_spanish_only_kitchen_blocks_english_only_intern():
    chef = Chef(make_chef_row('La Cocina', 'Spanish'))
    intern = InternLocal(make_intern_row('Alice', 'Smith', 'English'))
    assert language_constraint_passes(chef, intern) is False


def test_spanish_only_kitchen_allows_spanish_speaking_intern():
    chef = Chef(make_chef_row('La Cocina', 'Spanish'))
    intern = InternLocal(make_intern_row('Maria', 'Lopez', 'Spanish'))
    assert language_constraint_passes(chef, intern) is True


def test_spanish_only_kitchen_allows_bilingual_intern():
    chef = Chef(make_chef_row('La Cocina', 'Spanish'))
    intern = InternLocal(make_intern_row('Alex', 'Chen', 'English, Spanish'))
    assert language_constraint_passes(chef, intern) is True


def test_bilingual_kitchen_allows_english_only_intern():
    chef = Chef(make_chef_row('The Grill', 'English, Spanish'))
    intern = InternLocal(make_intern_row('Alice', 'Smith', 'English'))
    assert language_constraint_passes(chef, intern) is True


def test_english_only_kitchen_allows_spanish_speaking_intern():
    # Spanish speakers can go anywhere; the constraint is one-directional.
    chef = Chef(make_chef_row('Downtown Diner', 'English'))
    intern = InternLocal(make_intern_row('Maria', 'Lopez', 'Spanish'))
    assert language_constraint_passes(chef, intern) is True


# ---------------------------------------------------------------------------
# Day-availability column drift: short 'Monday' column is orphaned on the live
# sheet; current rows only populate the long-named column.
# ---------------------------------------------------------------------------

def test_day_availability_falls_back_to_long_form_column():
    row = {CHEF_DAY_COLUMNS['Monday']: 'All Day (9AM-9PM)'}
    assert get_day_availability_raw(row, 'Monday') == 'All Day (9AM-9PM)'


def test_day_availability_handles_trailing_space_quirk():
    # Tuesday's real header has a stray space before the closing bracket.
    row = {CHEF_DAY_COLUMNS['Tuesday']: 'All Day (9AM-9PM)'}
    assert get_day_availability_raw(row, 'Tuesday') == 'All Day (9AM-9PM)'


def test_day_availability_prefers_short_column_when_present():
    row = {'Monday': '9AM-5PM', CHEF_DAY_COLUMNS['Monday']: 'All Day (9AM-9PM)'}
    assert get_day_availability_raw(row, 'Monday') == '9AM-5PM'


def test_day_availability_missing_returns_empty():
    assert get_day_availability_raw({}, 'Monday') == ''


def test_chef_availability_parses_from_live_column_shape():
    chef = Chef(make_chef_row('La Cocina', 'Spanish', monday_hours='All Day (9AM-9PM)'))
    assert [str(s) for s in chef.availability['Monday']] == ['9-21']
    assert chef.availability['Tuesday'] == []


def test_intern_availability_parses_from_live_column_shape():
    intern = InternLocal(make_intern_row('Maria', 'Lopez', 'Spanish', monday_hours='All Day (9AM-9PM)'))
    assert [str(s) for s in intern.availability['Monday']] == ['9-21']
    assert intern.availability['Tuesday'] == []


# ---------------------------------------------------------------------------
# Regression: find_intern_restaurant_overlaps was appending each overlap
# twice (once via .append(), once via a redundant reassignment reading the
# just-updated list) — every match showed the same time slot duplicated,
# e.g. "5PM-9PM, 5PM-9PM" on live output.
# ---------------------------------------------------------------------------

def test_single_overlap_is_not_duplicated():
    from run_local import find_intern_restaurant_overlaps, Slot

    chef = Chef(make_chef_row('The Grill', 'English', monday_hours='5PM-9PM'))
    intern = InternLocal(make_intern_row('Alice', 'Smith', 'English', monday_hours='5PM-9PM'))
    chefs = {chef.restaurant_name: chef}

    overlaps, _ = find_intern_restaurant_overlaps(
        chefs, intern, 'Monday', intern.availability['Monday'], cache={}
    )

    day_slots = overlaps['The Grill']['Monday']
    assert len(day_slots) == 1
    assert str(day_slots[0]) == '17-21'
