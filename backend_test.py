import requests
import sys
import json
from datetime import datetime, timedelta
import uuid

class MovieBookingAPITester:
    def __init__(self, base_url="https://movieseats-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.admin_token = None
        self.user_token = None
        self.worker_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_detail = response.json()
                    print(f"   Error: {error_detail}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"email": "admin@cineplex.com", "password": "admin123"}
        )
        if success and 'token' in response:
            self.admin_token = response['token']
            self.test_data['admin_user'] = response['user']
            print(f"   Admin role: {response['user']['role']}")
            return True
        return False

    def test_user_login(self):
        """Test user login"""
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"email": "user@example.com", "password": "user123"}
        )
        if success and 'token' in response:
            self.user_token = response['token']
            self.test_data['regular_user'] = response['user']
            print(f"   User role: {response['user']['role']}")
            return True
        return False

    def test_user_registration(self):
        """Test new user registration"""
        test_email = f"test-user-{uuid.uuid4().hex[:8]}@example.com"
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email,
                "password": "testpass123",
                "name": "Test User"
            }
        )
        if success and 'token' in response:
            self.test_data['new_user'] = response['user']
            self.test_data['new_user_token'] = response['token']
            print(f"   New user created: {test_email}")
            return True
        return False

    def test_auth_me(self):
        """Test /auth/me endpoint"""
        if not self.user_token:
            print("❌ No user token available for /auth/me test")
            return False
        
        success, response = self.run_test(
            "Auth Me",
            "GET",
            "auth/me",
            200,
            token=self.user_token
        )
        return success

    def test_get_movies(self):
        """Test getting all movies"""
        success, response = self.run_test(
            "Get Movies",
            "GET",
            "movies",
            200
        )
        if success:
            self.test_data['movies'] = response
            print(f"   Found {len(response)} movies")
        return success

    def test_get_movie_detail(self):
        """Test getting movie details"""
        if not self.test_data.get('movies'):
            print("❌ No movies available for detail test")
            return False
        
        if len(self.test_data['movies']) == 0:
            print("❌ No movies in database for detail test")
            return False
        
        movie_id = self.test_data['movies'][0]['id']
        success, response = self.run_test(
            "Get Movie Detail",
            "GET",
            f"movies/{movie_id}",
            200
        )
        if success:
            self.test_data['movie_detail'] = response
        return success

    def test_get_screens(self):
        """Test getting all screens"""
        success, response = self.run_test(
            "Get Screens",
            "GET",
            "screens",
            200
        )
        if success:
            self.test_data['screens'] = response
            print(f"   Found {len(response)} screens")
        return success

    def test_admin_create_movie(self):
        """Test admin creating a movie"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        movie_data = {
            "title": "Test Movie API",
            "description": "A test movie created via API",
            "poster_url": "https://example.com/poster.jpg",
            "duration": 120,
            "genre": "Action",
            "language": "English",
            "rating": "PG-13",
            "now_showing": True
        }
        
        success, response = self.run_test(
            "Admin Create Movie",
            "POST",
            "admin/movies",
            200,
            data=movie_data,
            token=self.admin_token
        )
        if success:
            self.test_data['created_movie'] = response
            print(f"   Created movie: {response['title']}")
        return success

    def test_admin_create_screen(self):
        """Test admin creating a screen"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        screen_data = {
            "name": "Test Screen API",
            "rows": 6,
            "columns": 8,
            "vip_seats": ["A1", "A2", "B1", "B2"]
        }
        
        success, response = self.run_test(
            "Admin Create Screen",
            "POST",
            "admin/screens",
            200,
            data=screen_data,
            token=self.admin_token
        )
        if success:
            self.test_data['created_screen'] = response
            print(f"   Created screen: {response['name']} ({response['total_seats']} seats)")
        return success

    def test_admin_create_showtime(self):
        """Test admin creating a showtime"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        if not self.test_data.get('created_movie') or not self.test_data.get('created_screen'):
            print("❌ Need movie and screen for showtime test")
            return False
        
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        showtime_data = {
            "movie_id": self.test_data['created_movie']['id'],
            "screen_id": self.test_data['created_screen']['id'],
            "showtime": "7:00 PM",
            "date": tomorrow
        }
        
        success, response = self.run_test(
            "Admin Create Showtime",
            "POST",
            "admin/showtimes",
            200,
            data=showtime_data,
            token=self.admin_token
        )
        if success:
            self.test_data['created_showtime'] = response
            print(f"   Created showtime: {response['showtime']} on {response['date']}")
        return success

    def test_get_movie_showtimes(self):
        """Test getting showtimes for a movie"""
        if not self.test_data.get('created_movie'):
            print("❌ No movie available for showtime test")
            return False
        
        movie_id = self.test_data['created_movie']['id']
        success, response = self.run_test(
            "Get Movie Showtimes",
            "GET",
            f"movies/{movie_id}/showtimes",
            200
        )
        if success:
            print(f"   Found {len(response)} showtimes for movie")
        return success

    def test_create_booking(self):
        """Test creating a booking"""
        if not self.user_token:
            print("❌ No user token available")
            return False
        
        if not self.test_data.get('created_showtime'):
            print("❌ No showtime available for booking test")
            return False
        
        booking_data = {
            "showtime_id": self.test_data['created_showtime']['id'],
            "seats": ["C3", "C4"]
        }
        
        success, response = self.run_test(
            "Create Booking",
            "POST",
            "bookings",
            200,
            data=booking_data,
            token=self.user_token
        )
        if success:
            self.test_data['created_booking'] = response
            print(f"   Booking created: {response['booking_number']} for seats {response['seats']}")
        return success

    def test_get_user_bookings(self):
        """Test getting user bookings"""
        if not self.user_token:
            print("❌ No user token available")
            return False
        
        success, response = self.run_test(
            "Get User Bookings",
            "GET",
            "user/bookings",
            200,
            token=self.user_token
        )
        if success:
            print(f"   Found {len(response)} bookings for user")
        return success

    def test_admin_create_worker(self):
        """Test admin creating a worker"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        worker_email = f"test-worker-{uuid.uuid4().hex[:8]}@cineplex.com"
        worker_data = {
            "email": worker_email,
            "password": "worker123",
            "name": "Test Worker"
        }
        
        success, response = self.run_test(
            "Admin Create Worker",
            "POST",
            "admin/workers",
            200,
            data=worker_data,
            token=self.admin_token
        )
        if success:
            self.test_data['created_worker'] = response
            print(f"   Created worker: {response['email']}")
        return success

    def test_admin_get_workers(self):
        """Test admin getting all workers"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        success, response = self.run_test(
            "Admin Get Workers",
            "GET",
            "admin/workers",
            200,
            token=self.admin_token
        )
        if success:
            print(f"   Found {len(response)} workers")
        return success

    def test_admin_get_all_bookings(self):
        """Test admin getting all bookings"""
        if not self.admin_token:
            print("❌ No admin token available")
            return False
        
        success, response = self.run_test(
            "Admin Get All Bookings",
            "GET",
            "admin/bookings",
            200,
            token=self.admin_token
        )
        if success:
            print(f"   Found {len(response)} total bookings")
        return success

def main():
    print("🎬 Starting Movie Booking System API Tests")
    print("=" * 50)
    
    tester = MovieBookingAPITester()
    
    # Test sequence
    tests = [
        # Authentication tests
        ("Admin Login", tester.test_admin_login),
        ("User Login", tester.test_user_login),
        ("User Registration", tester.test_user_registration),
        ("Auth Me", tester.test_auth_me),
        
        # Movie tests
        ("Get Movies", tester.test_get_movies),
        ("Get Movie Detail", tester.test_get_movie_detail),
        
        # Screen tests
        ("Get Screens", tester.test_get_screens),
        
        # Admin movie management
        ("Admin Create Movie", tester.test_admin_create_movie),
        ("Admin Create Screen", tester.test_admin_create_screen),
        ("Admin Create Showtime", tester.test_admin_create_showtime),
        
        # Showtime tests
        ("Get Movie Showtimes", tester.test_get_movie_showtimes),
        
        # Booking tests
        ("Create Booking", tester.test_create_booking),
        ("Get User Bookings", tester.test_get_user_bookings),
        
        # Worker management
        ("Admin Create Worker", tester.test_admin_create_worker),
        ("Admin Get Workers", tester.test_admin_get_workers),
        
        # Admin booking management
        ("Admin Get All Bookings", tester.test_admin_get_all_bookings),
    ]
    
    # Run all tests
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} - Exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 FINAL RESULTS: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All API tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())