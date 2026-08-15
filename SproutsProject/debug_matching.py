from app import create_app
from app.services.hungarian_matching import HungarianMatchingService
from app.models import Intern, Restaurant

app = create_app()
app.app_context().push()

service = HungarianMatchingService()
interns = Intern.query.all()
restaurants = Restaurant.query.all()

print(f"Interns: {len(interns)}")
print(f"Restaurants: {len(restaurants)}")

if interns and restaurants:
    intern = interns[0]
    restaurant = restaurants[0]
    
    print(f"\nIntern: {intern.user.full_name}")
    print(f"Intern availability exists: {bool(intern.availability)}")
    
    if intern.availability:
        avail = intern.availability
        print(f"Monday AM: {avail.monday_am}, PM: {avail.monday_pm}")
        print(f"Tuesday AM: {avail.tuesday_am}, PM: {avail.tuesday_pm}")
        print(f"Wednesday AM: {avail.wednesday_am}, PM: {avail.wednesday_pm}")
    
    print(f"\nRestaurant: {restaurant.name}")
    print(f"Restaurant address: {restaurant.get_full_address()}")
    print(f"Intern address: {intern.get_full_address()}")
    
    # Test availability parsing
    intern_avail = service._parse_intern_availability(intern)
    restaurant_avail = service._parse_restaurant_availability(restaurant)
    
    print(f"\nParsed intern availability: {list(intern_avail.keys())}")
    print(f"Parsed restaurant availability: {list(restaurant_avail.keys())}")
    
    # Test weekly overlap calculation
    total_hours, schedule = service._calculate_weekly_overlap(intern_avail, restaurant_avail)
    print(f"\nTotal overlap hours: {total_hours}")
    print(f"Schedule: {schedule}")
    
    # Test commute calculation
    try:
        commute = service.commute_cache.get_commute(
            intern.transportation_method or 'driving',
            intern.get_full_address(),
            restaurant.get_full_address()
        )
        print(f"Commute: {commute.minutes} minutes")
    except Exception as e:
        print(f"Commute error: {e}")
