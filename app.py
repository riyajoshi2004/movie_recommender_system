import streamlit as st
import pickle
import requests
import time

# Hardcoded for local testing - replace with st.secrets in production
API_KEY = 'cc2c617fa02ed9616dfed5c93dae0914'

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})


def fetch_poster(movie_id, max_retries=3):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US'
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/original/" + poster_path
            return None
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry
                continue
            st.error(f"Failed to fetch poster for movie ID {movie_id} after {max_retries} attempts: {e}")
            return None


def recommend(movie):
    try:
        idx_list = ml[ml['title'] == movie].index
    except KeyError:
        st.error("Dataset missing 'title' column - check pickle file.")
        return [], []

    if len(idx_list) == 0:
        st.warning(f"Movie '{movie}' not found in dataset!")
        return [], []

    movie_index = idx_list[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), key=lambda x: x[1], reverse=True)[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        row = ml.iloc[i[0]]
        # Try 'movie_id' or fallback to 'id' (common in TMDB datasets)
        movie_id = row.get('movie_id') or row.get('id')
        if not movie_id:
            st.error(f"Missing movie ID for {row['title']}")
            continue
        title = row['title']
        recommended_movies.append(title)
        poster = fetch_poster(movie_id)
        recommended_movies_posters.append(poster)
        time.sleep(0.5)  # Rate limit delay

    return recommended_movies, recommended_movies_posters


# Load models with error handling
try:
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    ml = pickle.load(open('movies.pkl', 'rb'))
    m_l = ml['title'].values
except (FileNotFoundError, pickle.UnpicklingError) as e:
    st.error(
        f"Failed to load pickle files: {e}. Ensure files exist and match your environment (e.g., install scikit-learn).")
    st.stop()

st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie:",
    m_l
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)
    if not names:
        st.info("No recommendations available.")
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.text(names[0])
            if posters[0]:
                st.image(posters[0])
            else:
                st.write("Poster unavailable")
        with col2:
            st.text(names[1])
            if posters[1]:
                st.image(posters[1])
            else:
                st.write("Poster unavailable")
        with col3:
            st.text(names[2])
            if posters[2]:
                st.image(posters[2])
            else:
                st.write("Poster unavailable")
        with col4:
            st.text(names[3])
            if posters[3]:
                st.image(posters[3])
            else:
                st.write("Poster unavailable")
        with col5:
            st.text(names[4])
            if posters[4]:
                st.image(posters[4])
            else:
                st.write("Poster unavailable")
