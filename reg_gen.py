import random

def generate_random_number_plate():
    # Define valid characters and their respective weights
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    
    # First two letters (area code)
    area_code = random.choice(characters) + random.choice(characters)
    
    # Year identifier (last two digits of the current year)
    current_year = 2023  # Update this to the current year
    year_identifier = str(current_year)[-2:]
    
    # Random three-digit group
    random_group = "".join(random.choice(digits) for _ in range(3))
    
    # Combine the components to create the number plate
    number_plate = f"{area_code}{year_identifier}{random_group}"
    
    return number_plate

# Generate and print a random UK number plate
random_plate = generate_random_number_plate()

for i in range(10):
    random_plate = generate_random_number_plate()
    print(random_plate)
