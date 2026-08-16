"""
Tests for handling interns who are already matched to a restaurant.

The Intern Availabilities sheet records a prior placement decision directly on
the intern's row: column G ('restaurantname') and column N ('chefname'). When
these are filled in, that intern is not up for matching — their restaurant is
fixed, and it should count against that restaurant's capacity so the algorithm
doesn't recommend an already-full restaurant to the remaining unmatched
interns.

Restaurant capacity defaults to 2 interns and is adjustable. A hardcoded list
of exempt restaurants (university/special-program partners that intentionally
take more than 2) bypasses the cap entirely.

Run with: python -m pytest test_pre_matched_interns.py -v
"""

from run_local import (
    Chef,
    InternLocal,
    compute_full_restaurants,
    dedupe_intern_rows,
    partition_pre_matched,
    run_matching,
    DEFAULT_RESTAURANT_CAPACITY,
)


def make_chef_row(restaurant_name, monday_hours='All Day (9AM-9PM)'):
    row = {
        'Restaurant Name': restaurant_name,
        'Restaurant Address': '1 Restaurant Row',
        'Restaurant Location': 'Oakland, CA',
        "Primary Mentor's Full Name (First and Last)": 'Chef Test',
        'Do interns need to be over 18 to work in your kitchen?': 'No',
        'What languages do you & your staff speak in the kitchen? Select all that apply. ': 'English',
    }
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        row[day] = monday_hours if day == 'Monday' else 'Unavailable'
    return row


def make_intern_row(first_name, last_name, pre_matched_restaurant='', pre_matched_chef='', monday_hours='All Day (9AM-9PM)'):
    row = {
        'First Name': first_name,
        'Last Name': last_name,
        'Street Address': '1 Intern Way',
        'City': 'Oakland',
        'Zip Code': '94612',
        'Are you over 18 years old?': 'Yes',
        'What transportation will you use?': 'Driving',
        'What languages do you speak fluently?': 'English',
        'restaurantname': pre_matched_restaurant,
        'chefname': pre_matched_chef,
    }
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        row[day] = monday_hours if day == 'Monday' else 'Unavailable'
    return row


# ---------------------------------------------------------------------------
# InternLocal.pre_matched_restaurant
# ---------------------------------------------------------------------------

def test_intern_with_no_prior_match_has_empty_pre_matched_restaurant():
    intern = InternLocal(make_intern_row('Alice', 'Smith'))
    assert intern.pre_matched_restaurant == ''


def test_intern_with_prior_match_has_pre_matched_restaurant_set():
    intern = InternLocal(make_intern_row('Bob', 'Jones', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'))
    assert intern.pre_matched_restaurant == 'Arquet'


# ---------------------------------------------------------------------------
# partition_pre_matched
# ---------------------------------------------------------------------------

def test_partition_with_zero_pre_matched():
    interns = {
        'Alice Smith': InternLocal(make_intern_row('Alice', 'Smith')),
        'Bob Jones': InternLocal(make_intern_row('Bob', 'Jones')),
    }
    pre_matched, unmatched = partition_pre_matched(interns)
    assert pre_matched == []
    assert [i.full_name for i in unmatched] == ['Alice Smith', 'Bob Jones']


def test_partition_with_some_pre_matched():
    interns = {
        'Alice Smith': InternLocal(make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet')),
        'Bob Jones': InternLocal(make_intern_row('Bob', 'Jones')),
        'Cara Lee': InternLocal(make_intern_row('Cara', 'Lee', pre_matched_restaurant='Mago')),
    }
    pre_matched, unmatched = partition_pre_matched(interns)
    assert [i.full_name for i in pre_matched] == ['Alice Smith', 'Cara Lee']
    assert [i.full_name for i in unmatched] == ['Bob Jones']


def test_partition_with_all_pre_matched():
    interns = {
        'Alice Smith': InternLocal(make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet')),
        'Bob Jones': InternLocal(make_intern_row('Bob', 'Jones', pre_matched_restaurant='Mago')),
    }
    pre_matched, unmatched = partition_pre_matched(interns)
    assert len(pre_matched) == 2
    assert unmatched == []


# ---------------------------------------------------------------------------
# compute_full_restaurants — capacity accounting from fixed (pre-matched)
# assignments only
# ---------------------------------------------------------------------------

def test_restaurant_under_capacity_is_not_full():
    pre_matched = [InternLocal(make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet'))]
    full = compute_full_restaurants(pre_matched, capacity=2, exempt=set())
    assert 'Arquet' not in full


def test_restaurant_at_capacity_is_full():
    pre_matched = [
        InternLocal(make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet')),
        InternLocal(make_intern_row('Bob', 'Jones', pre_matched_restaurant='Arquet')),
    ]
    full = compute_full_restaurants(pre_matched, capacity=2, exempt=set())
    assert 'Arquet' in full


def test_capacity_is_adjustable():
    pre_matched = [InternLocal(make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet'))]
    full = compute_full_restaurants(pre_matched, capacity=1, exempt=set())
    assert 'Arquet' in full


def test_exempt_restaurant_never_counted_as_full():
    pre_matched = [
        InternLocal(make_intern_row('Alice', 'Smith', pre_matched_restaurant='Stanford Partner Kitchen')),
        InternLocal(make_intern_row('Bob', 'Jones', pre_matched_restaurant='Stanford Partner Kitchen')),
        InternLocal(make_intern_row('Cara', 'Lee', pre_matched_restaurant='Stanford Partner Kitchen')),
    ]
    full = compute_full_restaurants(pre_matched, capacity=2, exempt={'Stanford Partner Kitchen'})
    assert 'Stanford Partner Kitchen' not in full


def test_default_capacity_is_two():
    assert DEFAULT_RESTAURANT_CAPACITY == 2


# ---------------------------------------------------------------------------
# run_matching — end-to-end: pre-matched interns are fixed, remaining
# restaurants/interns go through the normal algorithm, full restaurants are
# excluded from new recommendations.
# ---------------------------------------------------------------------------

def test_pre_matched_intern_keeps_fixed_restaurant_in_output():
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X')]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    assert len(results) == 1
    alice = results[0]
    assert alice['intern_name'] == 'Alice Smith'
    # Every day should show the fixed restaurant, not algorithm-computed options.
    for day, matches in alice['days'].items():
        assert len(matches) == 1
        assert matches[0]['restaurant'] == 'Arquet'


def test_unmatched_interns_still_get_normal_algorithm_matches():
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [make_intern_row('Bob', 'Jones')]  # no prior match

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    bob = results[0]
    monday_restaurants = {m['restaurant'] for m in bob['days']['Monday']}
    assert monday_restaurants == {'Arquet', 'Mago'}


def test_restaurant_filled_by_pre_matched_interns_excluded_from_remaining_pool():
    # Arquet has capacity 2, filled entirely by pre-matched interns.
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Bob', 'Jones', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Cara', 'Lee'),  # unmatched — should NOT be offered Arquet
    ]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={}, restaurant_capacity=2)

    cara = next(r for r in results if r['intern_name'] == 'Cara Lee')
    monday_restaurants = {m['restaurant'] for m in cara['days']['Monday']}
    assert 'Arquet' not in monday_restaurants
    assert monday_restaurants == {'Mago'}


def test_restaurant_under_capacity_still_offered_to_remaining_pool():
    # Arquet capacity 2, only 1 pre-matched intern — still has room.
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Cara', 'Lee'),
    ]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={}, restaurant_capacity=2)

    cara = next(r for r in results if r['intern_name'] == 'Cara Lee')
    monday_restaurants = {m['restaurant'] for m in cara['days']['Monday']}
    assert monday_restaurants == {'Arquet', 'Mago'}


def test_capacity_adjustable_end_to_end():
    # With capacity=1, a single pre-matched intern already fills the restaurant.
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Cara', 'Lee'),
    ]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={}, restaurant_capacity=1)

    cara = next(r for r in results if r['intern_name'] == 'Cara Lee')
    monday_restaurants = {m['restaurant'] for m in cara['days']['Monday']}
    assert 'Arquet' not in monday_restaurants
    assert monday_restaurants == {'Mago'}


def test_exempt_restaurant_stays_available_despite_being_over_capacity():
    chef_dicts = [make_chef_row('Stanford Partner Kitchen'), make_chef_row('Mago')]
    intern_dicts = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='Stanford Partner Kitchen', pre_matched_chef='Chef X'),
        make_intern_row('Bob', 'Jones', pre_matched_restaurant='Stanford Partner Kitchen', pre_matched_chef='Chef X'),
        make_intern_row('Cara', 'Lee', pre_matched_restaurant='Stanford Partner Kitchen', pre_matched_chef='Chef X'),
        make_intern_row('Dev', 'Patel'),  # unmatched
    ]

    results, _ = run_matching(
        intern_dicts, chef_dicts, cache={},
        restaurant_capacity=2,
        capacity_exempt_restaurants={'Stanford Partner Kitchen'},
    )

    dev = next(r for r in results if r['intern_name'] == 'Dev Patel')
    monday_restaurants = {m['restaurant'] for m in dev['days']['Monday']}
    assert 'Stanford Partner Kitchen' in monday_restaurants


def test_zero_pre_matched_interns_runs_normally():
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [make_intern_row('Alice', 'Smith'), make_intern_row('Bob', 'Jones')]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    assert len(results) == 2
    for r in results:
        monday_restaurants = {m['restaurant'] for m in r['days']['Monday']}
        assert monday_restaurants == {'Arquet', 'Mago'}


def test_all_pre_matched_interns_produces_no_algorithm_matches_needed():
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Bob', 'Jones', pre_matched_restaurant='Mago', pre_matched_chef='Chef Y'),
    ]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    assert len(results) == 2
    fixed = {r['intern_name']: r['days']['Monday'][0]['restaurant'] for r in results}
    assert fixed == {'Alice Smith': 'Arquet', 'Bob Jones': 'Mago'}


def test_pre_matched_restaurant_not_found_in_current_chef_list_is_reported_as_is():
    # The intern's decided restaurant may have dropped out of this cohort's
    # chef list. We should still show what the sheet says, not fabricate or
    # silently drop it.
    chef_dicts = [make_chef_row('Mago')]
    intern_dicts = [make_intern_row('Alice', 'Smith', pre_matched_restaurant='Closed Restaurant', pre_matched_chef='Chef Z')]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    alice = results[0]
    assert alice['days']['Monday'][0]['restaurant'] == 'Closed Restaurant'


# ---------------------------------------------------------------------------
# dedupe_intern_rows — duplicate/near-duplicate rows for the same person.
#
# Discovered on live Summer 2026 data: "Amani Alawlaqi" had two rows (one with
# First Name='Amani', one with First Name='Amani ' — a stray trailing space)
# that both normalize to the same full_name. One row had a real placement
# (restaurantname='Cafe Commerce'); the other was blank. A plain dict
# assignment would let whichever row is processed last silently win,
# potentially discarding a real placement decision.
# ---------------------------------------------------------------------------

def test_no_duplicates_passes_through_unchanged():
    rows = [make_intern_row('Alice', 'Smith'), make_intern_row('Bob', 'Jones')]
    interns, notes = dedupe_intern_rows(rows)
    assert set(interns.keys()) == {'Alice Smith', 'Bob Jones'}
    assert notes == {}


def test_duplicate_prefers_filled_row_when_filled_comes_first():
    rows = [
        make_intern_row('Amani', 'Alawlaqi', pre_matched_restaurant='Cafe Commerce', pre_matched_chef='Chef X'),
        make_intern_row('Amani ', 'Alawlaqi'),  # blank duplicate, trailing space on first name
    ]
    interns, notes = dedupe_intern_rows(rows)
    assert len(interns) == 1
    assert interns['Amani Alawlaqi'].pre_matched_restaurant == 'Cafe Commerce'
    assert 'Amani Alawlaqi' in notes
    assert 'blank duplicate' in notes['Amani Alawlaqi']


def test_duplicate_prefers_filled_row_when_blank_comes_first():
    # Same scenario, opposite row order — the live data actually had the
    # blank row appear AFTER the filled one, but order shouldn't matter.
    rows = [
        make_intern_row('Amani ', 'Alawlaqi'),  # blank duplicate first
        make_intern_row('Amani', 'Alawlaqi', pre_matched_restaurant='Cafe Commerce', pre_matched_chef='Chef X'),
    ]
    interns, notes = dedupe_intern_rows(rows)
    assert len(interns) == 1
    assert interns['Amani Alawlaqi'].pre_matched_restaurant == 'Cafe Commerce'
    assert 'Amani Alawlaqi' in notes


def test_duplicate_both_blank_no_note_needed():
    rows = [make_intern_row('Alice', 'Smith'), make_intern_row('Alice ', 'Smith')]
    interns, notes = dedupe_intern_rows(rows)
    assert len(interns) == 1
    assert interns['Alice Smith'].pre_matched_restaurant == ''
    assert notes == {}


def test_duplicate_both_filled_same_restaurant_no_note_needed():
    rows = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Alice ', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
    ]
    interns, notes = dedupe_intern_rows(rows)
    assert len(interns) == 1
    assert notes == {}


def test_duplicate_both_filled_different_restaurants_flags_conflict():
    rows = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Alice ', 'Smith', pre_matched_restaurant='Mago', pre_matched_chef='Chef Y'),
    ]
    interns, notes = dedupe_intern_rows(rows)
    assert len(interns) == 1
    assert 'Alice Smith' in notes
    assert 'CONFLICT' in notes['Alice Smith']
    # Keeps the first-seen restaurant rather than guessing.
    assert interns['Alice Smith'].pre_matched_restaurant == 'Arquet'


def test_notes_flow_through_to_run_matching_output():
    chef_dicts = [make_chef_row('Cafe Commerce')]
    intern_dicts = [
        make_intern_row('Amani', 'Alawlaqi', pre_matched_restaurant='Cafe Commerce', pre_matched_chef='Chef X'),
        make_intern_row('Amani ', 'Alawlaqi'),
    ]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    assert len(results) == 1
    amani = results[0]
    assert amani['days']['Monday'][0]['restaurant'] == 'Cafe Commerce'
    assert 'blank duplicate' in amani['notes']


def test_no_duplicate_means_empty_notes_in_output():
    chef_dicts = [make_chef_row('Arquet')]
    intern_dicts = [make_intern_row('Alice', 'Smith')]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    assert results[0]['notes'] == ''
