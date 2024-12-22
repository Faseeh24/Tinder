import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from thefuzz import fuzz, process
from datetime import datetime
from sklearn.preprocessing import StandardScaler

all_possible_interests = ['Sports', 'Music', 'Travel', 'Reading', 'Movies', 'Cooking', 'Fitness', 'Gaming', 'Art', 'Technology', 'Fashion', 'Photography']

def calculate_age(date_of_birth_str):
    try:
        date_of_birth = datetime.strptime(date_of_birth_str, "%Y-%m-%d").date()
        today = datetime.now().date()
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        return age
    except (ValueError, TypeError):  # Handle invalid date or None
        return None

def calculate_similarity(profile1, profile2):
    if not profile1 or not profile2: # Check for empty profiles
        return 0

    def profile_to_vector(profile):
        interests = profile.get('interests', '').lower().split(',')
        interests = [i.strip() for i in interests if i.strip()]
        interest_vector = [1 if interest in all_possible_interests else 0 for interest in all_possible_interests]
        age = calculate_age(profile.get('date_of_birth'))
        return np.array(interest_vector + ([age] if age is not None else [0])) # Handle missing age

    vector1 = profile_to_vector(profile1)
    vector2 = profile_to_vector(profile2)

    #Handle cases where one or both vectors are all zeros (no interests and invalid age)
    if np.all(vector1 == 0) or np.all(vector2 == 0):
        interest_similarity = 0
    else:
        interest_similarity = cosine_similarity(vector1.reshape(1, -1), vector2.reshape(1, -1))[0][0]

    age1 = calculate_age(profile1.get('date_of_birth'))
    age2 = calculate_age(profile2.get('date_of_birth'))

    if age1 is not None and age2 is not None:
        age_similarity = 1 - abs(age1 - age2) / 100 # Original method
    else:
        age_similarity = 0

    location_similarity = fuzz.ratio(profile1.get('location', '').lower(), profile2.get('location', '').lower()) / 100
    about_me_similarity = fuzz.token_set_ratio(profile1.get('about_me', '').lower(), profile2.get('about_me', '').lower()) / 100 # Improved fuzzy matching

    # Profession Similarity (Example)
    profession_similarity = fuzz.ratio(profile1.get('profession', '').lower(), profile2.get('profession', '').lower())/100

    # Education Similarity
    education_similarity = 1 if profile1.get('education_level').lower() == profile2.get('education_level').lower() else 0

    weights = { # Adjust weights as needed
        "interests": 0.3,
        "age": 0.2,
        "location": 0.1,
        "about_me": 0.2,
        "profession": 0.1,
        "education": 0.1
    }

    total_similarity = (
        weights["interests"] * interest_similarity +
        weights["age"] * age_similarity +
        weights["location"] * location_similarity +
        weights["about_me"] * about_me_similarity +
        weights["profession"] * profession_similarity +
        weights["education"] * education_similarity
    )
    return total_similarity