"""
Tests for the "Top 3 Recommended" weekly-schedule column.

Business rule: interns target 12 hours/week at a single restaurant, delivered
as either 2 days x 6 hours or 3 days x 4 hours (the same pattern referenced
elsewhere in the codebase — see the 'schedule_suggestions' logic in
app/main/matching_routes.py and the 12-hour trim logic in
app/services/hungarian_matching.py).

For each intern, we look across all 7 days of restaurant options (already
computed by find_intern_restaurant_overlaps) and, per restaurant, find the
best achievable weekly plan: prefer 2x6h, then 3x4h, then best-effort with
whatever days are available. Restaurants are ranked by whether they hit the
12h target, then by average commute, and the top 3 are recommended.

Run with: python -m pytest test_weekly_recommendations.py -v
"""

from run_local import (
    compute_weekly_plan,
    compute_top_weekly_recommendations,
    describe_plan,
    format_commute_minutes,
    run_matching,
)
from test_pre_matched_interns import make_chef_row, make_intern_row


# ---------------------------------------------------------------------------
# compute_weekly_plan — pure function over {day: {'hours', 'commute_minutes'}}
# ---------------------------------------------------------------------------

def test_two_six_hour_days_produces_2x6_plan():
    day_options = {
        'Monday': {'hours': 6.0, 'commute_minutes': 20.0},
        'Wednesday': {'hours': 6.0, 'commute_minutes': 25.0},
    }
    plan = compute_weekly_plan(day_options)
    assert plan is not None
    assert set(plan['days']) == {'Monday', 'Wednesday'}
    assert plan['total_hours'] == 12.0
    assert plan['meets_target'] is True


def test_prefers_2x6_over_3x4_when_both_available():
    # Three days at 4h+ AND two days at 6h+ — 2x6h should win (fewer days,
    # same total hours, matches the preferred pattern).
    day_options = {
        'Monday': {'hours': 6.0, 'commute_minutes': 10.0},
        'Tuesday': {'hours': 6.0, 'commute_minutes': 10.0},
        'Wednesday': {'hours': 4.0, 'commute_minutes': 10.0},
    }
    plan = compute_weekly_plan(day_options)
    assert len(plan['days']) == 2
    assert plan['total_hours'] == 12.0


def test_three_four_hour_days_produces_3x4_plan_when_no_six_hour_days():
    day_options = {
        'Monday': {'hours': 4.0, 'commute_minutes': 15.0},
        'Tuesday': {'hours': 4.0, 'commute_minutes': 15.0},
        'Friday': {'hours': 4.0, 'commute_minutes': 15.0},
    }
    plan = compute_weekly_plan(day_options)
    assert plan is not None
    assert len(plan['days']) == 3
    assert plan['total_hours'] == 12.0
    assert plan['meets_target'] is True


def test_longer_single_day_overlap_gets_trimmed_to_pattern_hours():
    # A day with an 8-hour overlap should be trimmed to 6h for a 2x6h plan,
    # not counted in full (matches the "exactly 12h" convention).
    day_options = {
        'Monday': {'hours': 8.0, 'commute_minutes': 10.0},
        'Tuesday': {'hours': 6.0, 'commute_minutes': 10.0},
    }
    plan = compute_weekly_plan(day_options)
    assert plan['total_hours'] == 12.0
    assert plan['per_day_hours']['Monday'] == 6.0


def test_only_one_qualifying_day_is_not_a_viable_weekly_plan():
    day_options = {'Monday': {'hours': 6.0, 'commute_minutes': 10.0}}
    plan = compute_weekly_plan(day_options)
    assert plan is None


def test_zero_days_is_not_viable():
    assert compute_weekly_plan({}) is None


def test_two_days_under_six_hours_each_is_best_effort_partial():
    # Not enough for a clean pattern, but still worth surfacing as an
    # under-target option rather than hiding it entirely.
    day_options = {
        'Monday': {'hours': 4.0, 'commute_minutes': 10.0},
        'Tuesday': {'hours': 4.0, 'commute_minutes': 10.0},
    }
    plan = compute_weekly_plan(day_options)
    assert plan is not None
    assert plan['total_hours'] == 8.0
    assert plan['meets_target'] is False


# ---------------------------------------------------------------------------
# describe_plan — human-readable text for the CSV cell
# ---------------------------------------------------------------------------

def test_describe_plan_labels_2x6_pattern():
    plan = {
        'restaurant': 'Arquet', 'days': ['Monday', 'Wednesday'],
        'per_day_hours': {'Monday': 6.0, 'Wednesday': 6.0},
        'total_hours': 12.0, 'avg_commute_minutes': 20.0, 'meets_target': True,
    }
    text = describe_plan(plan)
    assert 'Arquet' in text
    assert '2×6h' in text
    assert '12h/wk' in text
    assert 'Mon' in text and 'Wed' in text


def test_describe_plan_labels_3x4_pattern():
    plan = {
        'restaurant': 'Mago', 'days': ['Monday', 'Tuesday', 'Friday'],
        'per_day_hours': {'Monday': 4.0, 'Tuesday': 4.0, 'Friday': 4.0},
        'total_hours': 12.0, 'avg_commute_minutes': 15.0, 'meets_target': True,
    }
    text = describe_plan(plan)
    assert '3×4h' in text


def test_describe_plan_flags_under_target():
    plan = {
        'restaurant': 'Mago', 'days': ['Monday', 'Tuesday'],
        'per_day_hours': {'Monday': 4.0, 'Tuesday': 4.0},
        'total_hours': 8.0, 'avg_commute_minutes': 15.0, 'meets_target': False,
    }
    text = describe_plan(plan)
    assert 'under 12h target' in text


# ---------------------------------------------------------------------------
# format_commute_minutes
# ---------------------------------------------------------------------------

def test_format_commute_minutes_under_an_hour():
    assert format_commute_minutes(45) == '45m'


def test_format_commute_minutes_over_an_hour():
    assert format_commute_minutes(74) == '1h14m'


def test_format_commute_minutes_exact_hour():
    assert format_commute_minutes(60) == '1h0m'


# ---------------------------------------------------------------------------
# compute_top_weekly_recommendations — ranking across restaurants
# ---------------------------------------------------------------------------

def test_ranks_restaurants_meeting_target_above_those_that_dont():
    chef_dicts = [
        make_chef_row('FullWeek', monday_hours='All Day (9AM-9PM)'),
        # Two days, but only 4h each = 8h total — a valid plan, just under target.
        make_chef_row('PartialWeek', monday_hours='5PM-9PM'),
    ]
    for row in chef_dicts:
        if row['Restaurant Name'] in ('FullWeek', 'PartialWeek'):
            row['Tuesday'] = 'All Day (9AM-9PM)' if row['Restaurant Name'] == 'FullWeek' else '5PM-9PM'

    intern_dicts = [make_intern_row('Alice', 'Smith', monday_hours='All Day (9AM-9PM)')]
    intern_dicts[0]['Tuesday'] = 'All Day (9AM-9PM)'

    from run_local import Chef, InternLocal
    chefs = {}
    for row in chef_dicts:
        chef = Chef(row)
        chefs[chef.restaurant_name] = chef
    intern = InternLocal(intern_dicts[0])

    recs, _ = compute_top_weekly_recommendations(chefs, intern, cache={})

    names_in_order = [r['restaurant'] for r in recs]
    assert names_in_order.index('FullWeek') < names_in_order.index('PartialWeek')


def test_top_n_limits_to_three():
    chef_dicts = []
    for i in range(5):
        row = make_chef_row(f'Restaurant{i}', monday_hours='All Day (9AM-9PM)')
        row['Tuesday'] = 'All Day (9AM-9PM)'
        chef_dicts.append(row)

    intern_row = make_intern_row('Alice', 'Smith', monday_hours='All Day (9AM-9PM)')
    intern_row['Tuesday'] = 'All Day (9AM-9PM)'

    from run_local import Chef, InternLocal
    chefs = {}
    for row in chef_dicts:
        chef = Chef(row)
        chefs[chef.restaurant_name] = chef
    intern = InternLocal(intern_row)

    recs, _ = compute_top_weekly_recommendations(chefs, intern, cache={})
    assert len(recs) == 3


# ---------------------------------------------------------------------------
# End-to-end via run_matching — new column present, positioned before days
# ---------------------------------------------------------------------------

def test_run_matching_attaches_weekly_recommendations_to_unmatched_interns():
    chef_dicts = [make_chef_row('Arquet', monday_hours='All Day (9AM-9PM)')]
    chef_dicts[0]['Tuesday'] = 'All Day (9AM-9PM)'
    intern_dicts = [make_intern_row('Alice', 'Smith', monday_hours='All Day (9AM-9PM)')]
    intern_dicts[0]['Tuesday'] = 'All Day (9AM-9PM)'

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    alice = results[0]
    assert 'weekly_recommendations' in alice
    assert len(alice['weekly_recommendations']) >= 1
    assert 'Arquet' in alice['weekly_recommendations'][0]


def test_pre_matched_intern_gets_fixed_note_not_recommendations():
    chef_dicts = [make_chef_row('Arquet')]
    intern_dicts = [make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X')]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    alice = results[0]
    assert 'weekly_recommendations' in alice
    assert any('Already matched' in r for r in alice['weekly_recommendations'])
