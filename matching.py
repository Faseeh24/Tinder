from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def calculate_similarity_sklearn(profile1, profile2):
    # Convert profile data to numerical vectors (feature engineering is key here)
    def profile_to_vector(profile):
        interests = profile.get('interests', '').lower().split(',')
        interests = [i.strip() for i in interests if i.strip()]
        interest_vector = [1 if interest in interests else 0 for interest in all_possible_interests] #all_possible_interests should be a list of all possible interests
        age = profile.get('age', 0)
        location_vector = [1 if profile.get('location', '').lower() == loc.lower() else 0 for loc in all_possible_locations] #all_possible_locations should be a list of all possible locations

        return np.array(interest_vector + [age] + location_vector)

    vector1 = profile_to_vector(profile1)
    vector2 = profile_to_vector(profile2)

    similarity = cosine_similarity(vector1.reshape(1, -1), vector2.reshape(1, -1))[0][0]
    return similarity

# Example usage (needs all_possible_interests and all_possible_locations defined)
all_possible_interests = ['reading', 'hiking', 'cooking', 'travel', 'photography', 'art', 'music', 'history', 'surfing', 'skateboarding', 'beach volleyball', 'rock climbing', 'camping']
all_possible_locations = ['New York City', 'New York', 'Los Angeles', 'London', 'San Francisco']

profile_a = { 'name': 'Alice', 'age': 30, 'location': 'New York City', 'interests': 'reading, hiking, cooking, travel, photography, art', }
profile_b = { 'name': 'Bob', 'age': 32, 'location': 'New York', 'interests': 'travel, photography, cooking, music, history', }

similarity_score = calculate_similarity_sklearn(profile_a, profile_b)
print(f"Similarity using scikit-learn: {similarity_score}")


# import spacy

# nlp = spacy.load("en_core_web_lg") # Load a larger spaCy model for better accuracy

# def bio_similarity(bio1, bio2):
#     doc1 = nlp(bio1)
#     doc2 = nlp(bio2)
#     return doc1.similarity(doc2)

# bio1 = "I enjoy long walks on the beach and reading classic novels."
# bio2 = "I like to read books and take strolls by the ocean."

# similarity = bio_similarity(bio1, bio2)
# print(f"Bio similarity: {similarity}")


# For numerical data and finding similar vectors, scikit-learn's cosine_similarity or nearest neighbors are excellent.
# For fuzzy string matching, TheFuzz is the best choice.
# For more complex text comparisons using semantic meaning, SpaCy is a powerful tool.