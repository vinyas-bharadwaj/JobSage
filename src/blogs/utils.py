from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Blog
from user_profile.models import Profile

def get_ranked_blogs(profile_id):
    """Ranks blogs based on user profile description"""
    current_user = Profile.objects.get(id=profile_id)
    blogs = Blog.objects.all()

    # Get the relavent text from profile as well as blogs
    documents = [current_user.get_text_for_matching()] + [blog.get_text_for_matching() for blog in blogs]

    # Compute the TF-IDF matrix
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(documents)

    # Compare profile with each blog
    similarities = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1:]).flatten()

    # Combine blogs with their respective similarities
    combined = list(zip(blogs, similarities))

    # Sort blogs based on decreasing order (higher score is more relavent)
    ranked_blogs = sorted(combined, key=lambda x: x[1], reverse=True)

    return [blog for blog, _ in ranked_blogs]


