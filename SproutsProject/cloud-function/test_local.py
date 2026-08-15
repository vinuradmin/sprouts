"""
Local testing script for the Cloud Function
Run this to test the matching algorithm locally before deploying
"""

import json
from main import app

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    with app.test_client() as client:
        response = client.get('/health')
        print(f"Status: {response.status_code}")
        print(f"Response: {response.get_json()}")
        print()

def test_matching(cohort="Spring 2026"):
    """Test matching endpoint"""
    print(f"Testing matching for cohort: {cohort}")
    with app.test_client() as client:
        response = client.post(
            '/run-matching',
            data=json.dumps({'cohort': cohort}),
            content_type='application/json'
        )
        print(f"Status: {response.status_code}")
        
        result = response.get_json()
        print(f"Success: {result.get('success')}")
        
        if result.get('success'):
            print(f"Intern count: {result.get('intern_count')}")
            print(f"Chef count: {result.get('chef_count')}")
            print(f"Results count: {len(result.get('results', []))}")
            
            # Show sample result
            if result.get('results'):
                sample = result['results'][0]
                print(f"\nSample result for: {sample['intern_name']}")
                for day, matches in sample['matches_by_day'].items():
                    if matches:
                        print(f"  {day}: {len(matches)} matches")
                        if matches:
                            print(f"    Top match: {matches[0]['restaurant']} ({matches[0]['commute_text']})")
        else:
            print(f"Error: {result.get('error')}")
        
        print()

if __name__ == '__main__':
    print("="*80)
    print("LOCAL TESTING - SPROUTS MATCHING CLOUD FUNCTION")
    print("="*80)
    print()
    
    # Test health
    test_health()
    
    # Test matching
    test_matching("Spring 2026")
    
    print("="*80)
    print("TESTING COMPLETE")
    print("="*80)
