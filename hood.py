import streamlit as st
import requests  # Add this line
import json 
import pandas as pd
import folium
from streamlit_folium import st_folium
import sqlite3
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# ----- DATABASE SETUP -----
conn = sqlite3.connect("reviews.db", check_same_thread=False)
c = conn.cursor()
c.execute(
    """
    CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        neighborhood TEXT,
        review TEXT,
        score INTEGER,
        security INTEGER,
        address TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
)
conn.commit()

# Ensure the timestamp column exists (for older versions of the table)
try:
    c.execute("ALTER TABLE reviews ADD COLUMN timestamp DATETIME DEFAULT CURRENT_TIMESTAMP")
    conn.commit()
except sqlite3.OperationalError:
    # Column 'timestamp' likely already exists
    pass

# ======== ENHANCED CSS ========
# ...existing code...
# ======== ENHANCED CSS ========
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://cdn.jsdelivr.net/npm/lucide-static@0.16.29/font/lucide.css');
    
    :root {
        --primary: #7653ff;
        --primary-dark: #4433bb;
        --accent: #ec4899;
        --background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        --glass: rgba(255, 255, 255, 0.95);
        --text: #1e293b;
        --shadow: 0 24px 48px -12px rgba(0,0,0,0.1);
    }
    
    * {
        font-family: 'Inter', sans-serif;
        box-sizing: border-box;
    }
    
    body {
        background: var(--background);
        color: var(--text);
    }
    
    /* Gradient Buttons - Used in Sidebar Navigation etc. */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        color: white !important;
        border: none !important;
        padding: 1rem 2rem !important;
        border-radius: 20px !important;
        font-weight: bold !important;
        box-shadow: 0px 5px 10px rgba(0,0,0,0.15);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0px 8px 16px rgba(0,0,0,0.25);
    }
    
    /* Optionally, style the Sidebar header */
    [data-testid="stSidebar"] .css-1d391kg {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# ...existing code...

# ======== HERO SECTION ========
st.markdown(
    """
    <div class="hero">
        <h1>Neighborhood Excellence</h1>
        <p>Discover and share premium living experiences</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ======== REVIEW CARD COMPONENT ========
def luxury_review_card(review):
    initials = "".join([name[0] for name in review[1].split()[:2]]).upper()
    return f"""
    <div class="glass-card">
        <div class="review-header">
            <div class="review-avatar">{initials}</div>
            <div>
                <h3 style="margin:0;color:var(--text)">{review[1]}</h3>
                <div style="display:flex;gap:1rem;margin-top:0.5rem">
                    <div style="display:flex;align-items:center;gap:0.25rem">
                        <i class="lucide lucide-star" style="color:#fbbf24"></i>
                        {review[3]}/5
                    </div>
                    <div style="display:flex;align-items:center;gap:0.25rem">
                        <i class="lucide lucide-shield" style="color:#3b82f6"></i>
                        {review[4]}/5
                    </div>
                </div>
            </div>
        </div>
        <p style="color:var(--text);line-height:1.7">{review[2]}</p>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-top:1.5rem">
            <div style="display:flex;align-items:center;gap:0.5rem;color:var(--primary)">
                <i class="lucide lucide-map-pin"></i>
                {review[5]}
            </div>
            <small style="color:#64748b">{review[6]}</small>
        </div>
    </div>
    """

def display_review(review):
    """Display review in a beautiful card format"""
    st.markdown(f"""
    <div class="review-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
            <h3 style="margin: 0; color: var(--text);">{review[1]}</h3>
            <div style="display: flex; gap: 1rem;">
                <div class="rating-badge">
                    ⭐ {review[3]}/5
                </div>
                <div class="rating-badge">
                    🛡️ {review[4]}/5
                </div>
            </div>
        </div>
        <p style="color: #555; line-height: 1.7; margin-bottom: 1rem;">{review[2]}</p>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="color: var(--primary); font-weight: 500;">📍 {review[5]}</div>
            <small style="color: #888;">{review[6]}</small>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ======== NAVIGATION STYLING ========
st.markdown(
    """
    <style>
    .nav-button {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        padding: 0.75rem 1.5rem;
        margin: 0.5rem 0;
        width: 100%;
        border: none;
        border-radius: 12px;
        background: rgba(99, 102, 241, 0.1);
        color: var(--text);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .nav-button:hover {
        background: rgba(99, 102, 241, 0.2);
        transform: translateX(5px);
    }
    
    .nav-button.active {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white !important;
        box-shadow: 0 5px 15px rgba(99, 102, 241, 0.3);
    }
    
    .nav-button i {
        font-size: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

url = "https://api.openai.com/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer "
}
data = {
    "model": "gpt-4o-mini", 
    "messages": [
        {"role": "system", "content": "You are assistant that helps users with neighborhood reviews.Answer the questions and provide information based on the reviews in the database."},
    ],
    "max_tokens": 6000,
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# ======== NAVIGATION LOGIC ========
if 'page' not in st.session_state:
    st.session_state.page = "read"

def set_page(page):
    st.session_state.page = page
    st.rerun()
#this function wasnt working well before now


with st.sidebar:
    st.markdown("## Navigation")
    if st.button("📖 Read Reviews", key="read"):
        set_page("read")
    if st.button("📝 Create Review", key="create"):
        set_page("create")
    if st.button("🛠️ Manage Reviews", key="manage"):
        set_page("manage")
    if st.button("AI Assistant", key="ai"):
        set_page("ai")

# ======== MAIN APP CODE ========

if st.session_state.page == "create":
    with st.container():
        with st.form("review_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                neighborhood = st.text_input("🏙️ Neighborhood Name", placeholder="Enter neighborhood...")
                # Pre-fill the review field if auto_review exists
                review = st.text_area("📝 Your Review", placeholder="Share your experience...", height=150, value=st.session_state.get("auto_review", ""))
            with col2:
                st.markdown("### Ratings")
                score = st.select_slider(
                    "⭐ Overall Score",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: "⭐" * x
                )
                security = st.select_slider(
                    "🛡️ Safety Rating",
                    options=[1, 2, 3, 4, 5],
                    value=3,
                    format_func=lambda x: "🛡️" * x
                )
            with st.container():
                map_obj = folium.Map(location=[51.1175, 71.4617], zoom_start=12)
                map_data = st_folium(map_obj, height=300)
            if map_data.get("last_clicked"):
                lat, lon = map_data["last_clicked"]["lat"], map_data["last_clicked"]["lng"]
                geolocator = Nominatim(user_agent="neighborhood_app")
                try:
                    location = geolocator.reverse((lat, lon), timeout=10)
                    address = location.address
                except Exception:
                    address = f"{lat:.4f}, {lon:.4f}"
                st.success(f"Selected Location: {address}")
            else:
                address = None
                st.warning("Please select a location on the map")
            if st.form_submit_button("🚀 Submit Review"):
                if neighborhood and review and address:
                    c.execute("INSERT INTO reviews (neighborhood, review, score, security, address) VALUES (?, ?, ?, ?, ?)",
                              (neighborhood, review, score, security, address))
                    conn.commit()
                    st.success("Review submitted successfully!")
                else:
                    st.error("Please fill all required fields.")

elif st.session_state.page == "read":
    st.markdown('<div class="section-header">Neighborhood Reviews</div>', unsafe_allow_html=True)
 
    with st.expander("🔍 Search & Filter", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("Search reviews", placeholder="Enter keywords...")
        with col2:
            min_score = st.slider("Minimum average score", 1, 5, 1)
        with col3:
            sort_option = st.selectbox("Sort by", ["Newest first", "Highest rated", "Most reviewed locations"])
 
    c.execute("SELECT * FROM reviews ORDER BY timestamp DESC")
    reviews = c.fetchall()
 
    if reviews:
        df_reviews = pd.DataFrame(
            reviews, 
            columns=["ID", "Neighborhood", "Review", "Score", "Security", "Address", "Timestamp"]
        )
        # Average is calculated on a scale of 5.
        df_reviews["Average"] = (df_reviews["Score"] + df_reviews["Security"]) / 2
 
        if search_query:
            df_reviews = df_reviews[df_reviews.apply(lambda row: 
                search_query.lower() in row["Neighborhood"].lower() or 
                search_query.lower() in row["Review"].lower() or
                search_query.lower() in row["Address"].lower(), axis=1)]
 
        df_reviews = df_reviews[df_reviews["Average"] >= min_score]
 
        if sort_option == "Newest first":
            df_reviews = df_reviews.sort_values("Timestamp", ascending=False)
        elif sort_option == "Highest rated":
            df_reviews = df_reviews.sort_values("Average", ascending=False)
        elif sort_option == "Most reviewed locations":
            location_counts = df_reviews["Address"].value_counts().to_dict()
            df_reviews["ReviewCount"] = df_reviews["Address"].map(location_counts)
            df_reviews = df_reviews.sort_values("ReviewCount", ascending=False)
 
        if len(df_reviews) == 0:
            st.markdown("""
                <div style="text-align: center; padding: 3rem; color: #666;">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="#9e9e9e"/>
                        <path d="M11 16H13V18H11V16ZM12 6C9.79 6 8 7.79 8 10H10C10 8.9 10.9 8 12 8C13.1 8 14 8.9 14 10C14 12 11 11.75 11 15H13C13 12.75 16 12.5 16 10C16 7.79 14.21 6 12 6Z" fill="#9e9e9e"/>
                    </svg>
                    <h3 style="color: #555; margin-top: 1rem;">No reviews match your criteria</h3>
                    <p>Try adjusting your search or filters</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            for _, row in df_reviews.iterrows():
                # Calculate stars based on a 5 point scale.
                full_stars = int(round(row["Average"]))
                stars = "★" * full_stars
                empty_stars = "☆" * (5 - full_stars)
 
                st.markdown(f"""
                    <div class="review-card" style="animation: fadeIn 0.5s ease-out;">
                        <div class="review-neighborhood">{row["Neighborhood"]}</div>
                        <div class="review-rating" style="margin-bottom: 0.5rem;">
                            <span style="color: #ffc107; font-size: 1.2rem;">{stars + empty_stars}</span>
                            <span style="color: #777; font-size: 0.9rem; margin-left: 0.5rem;">{row["Average"]:.1f}/5</span>
                        </div>
                        <div class="review-text">{row["Review"]}</div>
                        <div class="review-meta">
                            <div style="display: flex; align-items: center; gap: 0.3rem;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="#777"/>
                                    <path d="M11 7H13V12H11V7ZM11 13H13V15H11V13Z" fill="#777"/>
                                </svg>
                                {pd.to_datetime(row["Timestamp"]).strftime('%b %d, %Y')}
                            </div>
                            <div style="display: flex; align-items: center; gap: 0.3rem;">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                    <path d="M12 2C8.13 2 5 5.13 5 9C5 14.25 12 22 12 22C12 22 19 14.25 19 9C19 5.13 15.87 2 12 2ZM12 11.5C10.62 11.5 9.5 10.38 9.5 9C9.5 7.62 10.62 6.5 12 6.5C13.38 6.5 14.5 7.62 14.5 9C14.5 10.38 13.38 11.5 12 11.5Z" fill="#777"/>
                                </svg>
                                {row["Address"].split(",")[0]}
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
 
            grouped = df_reviews.groupby("Address").agg({
                "Average": "mean",
                "ID": "count"
            }).reset_index().rename(columns={"ID": "ReviewCount"})
 
            review_map = folium.Map(location=[51.169392, 71.449074], zoom_start=12)
            geolocator = Nominatim(user_agent="neighborhood_review_app")
 
            for _, row in grouped.iterrows():
                addr = row["Address"]
                avg = row["Average"]
                count = row["ReviewCount"]
                try:
                    location = geolocator.geocode(addr, timeout=10)
                except Exception:
                    location = None
                if location:
                    lat, lon = location.latitude, location.longitude
                else:
                    continue
 
                color = "#e74c3c" if avg < 4 else "#f39c12" if avg < 7 else "#2ecc71"
 
                icon_html = f"""
                    <div style="
                        background: {color};
                        width: 30px;
                        height: 30px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        border: 2px solid white;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                    ">{count}</div>
                """
 
                folium.Marker(
                    location=[lat, lon],
                    popup=f"""
                        <div style="min-width: 200px;">
                            <h4 style="margin: 0 0 5px 0; color: {color}">
                                {addr.split(",")[0]}
                            </h4>
                            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                                <span style="color: #ffc107; font-size: 1rem;">{"★" * int(round(avg))}</span>
                                <span style="color: #777; font-size: 0.8rem; margin-left: 5px;">{avg:.1f}/5</span>
                            </div>
                            <div style="color: #555; font-size: 0.8rem;">{count} review{'s' if count > 1 else ''}</div>
                        </div>
                    """,
                    icon=folium.DivIcon(html=icon_html)
                ).add_to(review_map)
 
            st.markdown('<div class="map-container">', unsafe_allow_html=True)
            st_folium(review_map, width=None, height=500)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 3rem; color: #666;">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM12 20C7.59 20 4 16.41 4 12C4 7.59 7.59 4 12 4C16.41 4 20 7.59 20 12C20 16.41 16.41 20 12 20Z" fill="#9e9e9e"/>
                    <path d="M11 16H13V18H11V16ZM12 6C9.79 6 8 7.79 8 10H10C10 8.9 10.9 8 12 8C13.1 8 14 8.9 14 10C14 12 11 11.75 11 15H13C13 12.75 16 12.5 16 10C16 7.79 14.21 6 12 6Z" fill="#9e9e9e"/>
                </svg>
                <h3 style="color: #555; margin-top: 1rem;">No reviews yet</h3>
                <p>Be the first to share your neighborhood experience!</p>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "manage":
    st.markdown('<div class="section-header">Manage Your Reviews</div>', unsafe_allow_html=True)
    reviews = c.execute("SELECT * FROM reviews").fetchall()
    if reviews:
        for review in reviews:
            with st.expander(f"{review[1]} - {review[6]}"):
                with st.form(key=f"edit_{review[0]}"):
                    cols = st.columns(2)
                    with cols[0]:
                        new_neighborhood = st.text_input("Neighborhood", value=review[1])
                        new_address = st.text_input("Address", value=review[5])
                    with cols[1]:
                        new_score = st.slider("Overall Rating", 1, 5, value=review[3],
                                              help="Rate the overall quality of the neighborhood")
                        new_security = st.slider("Safety Score", 1, 5, value=review[4],
                                                 help="How safe do you feel in this neighborhood?")
                    new_review = st.text_area("Your Experience", value=review[2], height=200)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save Changes"):
                            c.execute("UPDATE reviews SET neighborhood=?, review=?, score=?, security=?, address=? WHERE id=?",
                                      (new_neighborhood, new_review, new_score, new_security, new_address, review[0]))
                            conn.commit()
                            st.success("Changes saved!")
                    with col2:
                         if st.form_submit_button("🗑️ Delete Review"):
                            c.execute("DELETE FROM reviews WHERE id=?", (review[0],))
                            conn.commit()
                            st.success("Review deleted")
    else:
        st.markdown(
            """
            <div class="empty-state">
                <i class="lucide lucide-compass"></i>
                <h3>No Reviews Found</h3>
                <p>Start by sharing your first review!</p>
            </div>
            """,
            unsafe_allow_html=True
        )
# ai with access to database reviews.db
elif st.session_state.page == "ai":
    st.markdown('<div class="section-header">AI Assistant</div>', unsafe_allow_html=True)

    c.execute("SELECT Neighborhood, Review, Score, Security FROM reviews ORDER BY timestamp DESC LIMIT 50")
    reviews_list = c.fetchall()
    reviews_context = "\n".join([f"{r[0]}: {r[1]} (Score: {r[2]}, Security: {r[3]})" for r in reviews_list])

    if "messages" not in st.session_state or "reviews_context_added" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": f"You're a helpful assistant providing detailed neighborhood insights based on recent reviews. Answer user questions clearly, offer comparisons if relevant, and suggest additional factors they may want to consider. Here’s the latest review data: {reviews_context}"}
        ]
        st.session_state["reviews_context_added"] = True

    if prompt := st.chat_input("Ask the AI about neighborhood reviews..."):
        if prompt.startswith("/create"):    
            review_directive = prompt[len("/create"):].strip()
            messages = [
                {"role": "system", "content": "A concise and objective review of a neighborhood or building, based strictly on the provided information. If reviews from other maps are available, summarize key trends and present a balanced opinion. Do not add assumptions or exaggerations, and maintain a neutral tone. " + review_directive},
                {"role": "user", "content": "Generate a review based on the above directive."}
            ]
            data["messages"] = messages
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                auto_review = response.json()["choices"][0]["message"]["content"]
                st.session_state.auto_review = auto_review
                st.success("AI generated a review. Switching to the create review tab. Please adjust the rating and select a location on the map.")
                set_page("create")
            else:
                st.error("Failed to generate review from the AI model.")
        else:
            st.session_state["messages"].append({"role": "user", "content": prompt})
            data["messages"] = st.session_state["messages"]
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                assistant_message = response.json()["choices"][0]["message"]["content"]
                st.session_state["messages"].append({"role": "assistant", "content": assistant_message})
            else:
                st.error("Failed to fetch response from the API.")

    for message in st.session_state["messages"]:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.write(message["content"])
