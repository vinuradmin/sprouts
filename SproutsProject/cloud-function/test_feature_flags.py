"""
Tests for the on/off flags behind the language-matching and respect-prior-
matches enhancements. Both default to enabled; passing the corresponding
--no-* CLI flag (or the matching run_matching() kwarg) turns that one off so
the algorithm can be run without the enhancement if desired.

Run with: python -m pytest test_feature_flags.py -v
"""

import inspect
import sys

from run_local import parse_args, run_matching
from test_pre_matched_interns import make_chef_row, make_intern_row


# ---------------------------------------------------------------------------
# Defaults — both enhancements must default to ON.
# ---------------------------------------------------------------------------

def test_run_matching_defaults_both_flags_to_true():
    sig = inspect.signature(run_matching)
    assert sig.parameters['enable_language_matching'].default is True
    assert sig.parameters['enable_respect_prior_matches'].default is True


def test_cli_defaults_both_flags_to_true(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['run_local.py', 'Fall 2026'])
    args = parse_args()
    assert args.enable_language_matching is True
    assert args.enable_respect_prior_matches is True


def test_cli_no_language_matching_flag_disables_it(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['run_local.py', 'Fall 2026', '--no-language-matching'])
    args = parse_args()
    assert args.enable_language_matching is False
    assert args.enable_respect_prior_matches is True


def test_cli_no_respect_prior_matches_flag_disables_it(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['run_local.py', 'Fall 2026', '--no-respect-prior-matches'])
    args = parse_args()
    assert args.enable_language_matching is True
    assert args.enable_respect_prior_matches is False


def test_cli_both_flags_can_be_disabled_together(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['run_local.py', 'Fall 2026', '--no-language-matching', '--no-respect-prior-matches'])
    args = parse_args()
    assert args.enable_language_matching is False
    assert args.enable_respect_prior_matches is False


# ---------------------------------------------------------------------------
# enable_language_matching=False — Spanish-only kitchens open to everyone
# ---------------------------------------------------------------------------

def test_language_matching_on_by_default_blocks_non_spanish_intern():
    chef_dicts = [make_chef_row('La Cocina')]
    chef_dicts[0]['What languages do you & your staff speak in the kitchen? Select all that apply. '] = 'Spanish'
    intern_dicts = [make_intern_row('Alice', 'Smith')]  # defaults to English via make_intern_row

    results, _ = run_matching(intern_dicts, chef_dicts, cache={})

    monday_restaurants = {m['restaurant'] for m in results[0]['days']['Monday']}
    assert 'La Cocina *' not in monday_restaurants
    assert monday_restaurants == set()


def test_language_matching_disabled_allows_non_spanish_intern_at_spanish_only_kitchen():
    chef_dicts = [make_chef_row('La Cocina')]
    chef_dicts[0]['What languages do you & your staff speak in the kitchen? Select all that apply. '] = 'Spanish'
    intern_dicts = [make_intern_row('Alice', 'Smith')]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={}, enable_language_matching=False)

    monday_restaurants = {m['restaurant'] for m in results[0]['days']['Monday']}
    # Still shown with the informational asterisk — only the gate is disabled.
    assert 'La Cocina *' in monday_restaurants


# ---------------------------------------------------------------------------
# enable_respect_prior_matches=False — ignore prior placements entirely
# ---------------------------------------------------------------------------

def test_respect_prior_matches_disabled_ignores_fixed_restaurant():
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X')]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={}, enable_respect_prior_matches=False)

    alice = results[0]
    monday_matches = alice['days']['Monday']
    # No longer a single fixed "Already matched" row — runs through the
    # normal algorithm against the full restaurant pool.
    monday_restaurants = {m['restaurant'] for m in monday_matches}
    assert monday_restaurants == {'Arquet', 'Mago'}
    assert all(m['commute'] != 'Already matched' for m in monday_matches)


def test_respect_prior_matches_disabled_does_not_exclude_capacity_filled_restaurants():
    chef_dicts = [make_chef_row('Arquet'), make_chef_row('Mago')]
    intern_dicts = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Bob', 'Jones', pre_matched_restaurant='Arquet', pre_matched_chef='Chef X'),
        make_intern_row('Cara', 'Lee'),
    ]

    results, _ = run_matching(intern_dicts, chef_dicts, cache={}, enable_respect_prior_matches=False)

    cara = next(r for r in results if r['intern_name'] == 'Cara Lee')
    monday_restaurants = {m['restaurant'] for m in cara['days']['Monday']}
    # Arquet would normally be excluded (2 prior matches = full), but with
    # the flag off, prior-match data is ignored entirely.
    assert monday_restaurants == {'Arquet', 'Mago'}


def test_both_flags_disabled_together():
    chef_dicts = [make_chef_row('La Cocina'), make_chef_row('Mago')]
    chef_dicts[0]['What languages do you & your staff speak in the kitchen? Select all that apply. '] = 'Spanish'
    intern_dicts = [
        make_intern_row('Alice', 'Smith', pre_matched_restaurant='La Cocina', pre_matched_chef='Chef X'),
    ]

    results, _ = run_matching(
        intern_dicts, chef_dicts, cache={},
        enable_language_matching=False,
        enable_respect_prior_matches=False,
    )

    alice = results[0]
    monday_restaurants = {m['restaurant'] for m in alice['days']['Monday']}
    assert monday_restaurants == {'La Cocina *', 'Mago'}
