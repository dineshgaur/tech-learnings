from typing import List, Dict, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from threading import Lock

# Data Layer
@dataclass
class Seat:
    category: str
    price: float
    is_booked: bool = False

@dataclass
class Screen:
    screen_id: int
    seats: Dict[str, List[Seat]]
    movie: Optional[str] = None
    schedule: Optional[Dict[str, str]] = None

@dataclass
class Multiplex:
    name: str
    location: str
    screens: List[Screen]

@dataclass
class Booking:
    multiplex: str
    screen_id: int
    movie: str
    seat_category: str
    seat_number: int

# Service Layer
class MultiplexService:
    def __init__(self):
        self.multiplexes: List[Multiplex] = []

    def add_multiplex(self, multiplex: Multiplex):
        self.multiplexes.append(multiplex)

    def get_multiplexes(self):
        return self.multiplexes

class BookingService:
    def __init__(self, multiplex_service: MultiplexService):
        self.bookings: List[Booking] = []
        self.multiplex_service = multiplex_service
        self.lock = Lock()  

    def check_availability(self, movie: Optional[str] = None, multiplex: Optional[str] = None):
        available_shows = []
        for multiplex_obj in self.multiplex_service.get_multiplexes():
            if multiplex and multiplex_obj.name != multiplex:
                continue

            for screen in multiplex_obj.screens:
                if movie and screen.movie != movie:
                    continue

                for category, seats in screen.seats.items():
                    available_seats = sum(1 for seat in seats if not seat.is_booked)
                    if available_seats > 0:
                        available_shows.append({
                            "Multiplex": multiplex_obj.name,
                            "Screen": screen.screen_id,
                            "Movie": screen.movie,
                            "Category": category,
                            "Available Seats": available_seats,
                            "Price": seats[0].price if seats else 0
                        })
        return available_shows

    def book_seat(self, multiplex_name: str, screen_id: int, category: str, seat_number: int):
        with self.lock: 
            for multiplex in self.multiplex_service.get_multiplexes():
                if multiplex.name == multiplex_name:
                    for screen in multiplex.screens:
                        if screen.screen_id == screen_id:
                            seats = screen.seats.get(category, [])
                            if 0 <= seat_number < len(seats):
                                if not seats[seat_number].is_booked:
                                    seats[seat_number].is_booked = True
                                    booking = Booking(multiplex_name, screen_id, screen.movie, category, seat_number)
                                    self.bookings.append(booking)
                                    print(f"Debug: Seat {seat_number} in category {category} booked successfully.")
                                    return "Booking Successful!"
                                else:
                                    print(f"Debug: Seat {seat_number} in category {category} is already booked.")
                                    return "Seat already booked."
                            else:
                                print(f"Debug: Invalid seat number {seat_number} for category {category}.")
                                return "Invalid seat number."
        print(f"Debug: Multiplex {multiplex_name} or screen {screen_id} not found.")
        return "Seat not available or invalid details."

class Filter(ABC):
    @abstractmethod
    def apply(self, shows: List[Dict]) -> List[Dict]:
        pass

class MovieFilter(Filter):
    def __init__(self, movie_title: str):
        self.movie_title = movie_title

    def apply(self, shows: List[Dict]) -> List[Dict]:
        return [show for show in shows if show["Movie"] == self.movie_title]

class MultiplexFilter(Filter):
    def __init__(self, multiplex_name: str):
        self.multiplex_name = multiplex_name

    def apply(self, shows: List[Dict]) -> List[Dict]:
        return [show for show in shows if show["Multiplex"] == self.multiplex_name]

class Sorter(ABC):
    @abstractmethod
    def apply(self, shows: List[Dict]) -> List[Dict]:
        pass

class CheapestShowSorter(Sorter):
    def apply(self, shows: List[Dict]) -> List[Dict]:
        return sorted(shows, key=lambda x: x["Price"])

# Unit Tests
class TestBookingSystem:
    def __init__(self):
        self.multiplex_service = MultiplexService()
        self.booking_service = BookingService(self.multiplex_service)

    def setup(self):
        # Reset state for each test
        self.multiplex_service = MultiplexService()
        self.booking_service = BookingService(self.multiplex_service)

        central_mall = Multiplex(
            name="Central Mall",
            location="Mumbai",
            screens=[
                Screen(
                    screen_id=1,
                    seats={
                        "Silver": [Seat(category="Silver", price=150) for _ in range(50)],
                        "Gold": [Seat(category="Gold", price=200) for _ in range(30)],
                        "Platinum": [Seat(category="Platinum", price=250) for _ in range(20)],
                    },
                    movie="Inception",
                    schedule={"start": "2 PM", "end": "5 PM"}
                )
            ]
        )
        self.multiplex_service.add_multiplex(central_mall)

    def run_tests(self):
        print("Running Tests...")

        self.setup()
        # Test 1: Check availability without filters
        shows = self.booking_service.check_availability()
        assert len(shows) > 0, "Test Failed: No shows available."

        self.setup()
        # Test 2: Apply movie filter
        shows = self.booking_service.check_availability()
        movie_filter = MovieFilter(movie_title="Inception")
        filtered_shows = movie_filter.apply(shows)
        assert all(show["Movie"] == "Inception" for show in filtered_shows), "Test Failed: Movie filter not applied correctly."

        self.setup()
        # Test 3: Book a seat
        result = self.booking_service.book_seat("Central Mall", 1, "Silver", 5)
        assert result == "Booking Successful!", "Test Failed: Booking failed."

        self.setup()
        # Test 4: Double booking prevention
        self.booking_service.book_seat("Central Mall", 1, "Silver", 5)
        result = self.booking_service.book_seat("Central Mall", 1, "Silver", 5)
        assert result == "Seat already booked.", "Test Failed: Double booking allowed."

        print("All Tests Passed!")

# Driver Code
def main():
    multiplex_service = MultiplexService()
    booking_service = BookingService(multiplex_service)

    # Create sample data
    central_mall = Multiplex(
        name="Central Mall",
        location="Mumbai",
        screens=[
            Screen(
                screen_id=1,
                seats={
                    "Silver": [Seat(category="Silver", price=150) for _ in range(50)],
                    "Gold": [Seat(category="Gold", price=200) for _ in range(30)],
                    "Platinum": [Seat(category="Platinum", price=250) for _ in range(20)],
                },
                movie="Inception",
                schedule={"start": "2 PM", "end": "5 PM"}
            )
        ]
    )
    multiplex_service.add_multiplex(central_mall)

    shows = booking_service.check_availability()

    # Apply filters and sorters
    movie_filter = MovieFilter(movie_title="Inception")
    multiplex_filter = MultiplexFilter(multiplex_name="Central Mall")
    cheapest_sorter = CheapestShowSorter()

    filtered_shows = movie_filter.apply(shows)
    filtered_shows = multiplex_filter.apply(filtered_shows)
    sorted_shows = cheapest_sorter.apply(filtered_shows)

    # Display sorted shows
    for show in sorted_shows:
        print(show)

    # Book a seat
    print(booking_service.book_seat("Central Mall", 1, "Silver", 5))

    # Run tests
    tester = TestBookingSystem()
    tester.run_tests()

if __name__ == "__main__":
    main()