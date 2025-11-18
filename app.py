import streamlit as st
from streamlit.components.v1 import iframe
import chatbot_app as chatbot

# ==============================
# 📱 MOBILE-OPTIMIZED SETTINGS
# ==============================
st.set_page_config(
    page_title="Map of Flavors",
    page_icon="🍳",
    layout="centered",        # Better for mobile
    initial_sidebar_state="expanded"
)

# ==============================
# 📱 MOBILE CSS STYLING
# ==============================
st.markdown("""
<style>

/* Make all iframes mobile responsive */
iframe {
    width: 100% !important;
    max-width: 100% !important;
}

/* Reduce padding on mobile */
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
}

/* Header sizes (mobile friendly) */
h1 { font-size: 1.8rem !important; }
h2 { font-size: 1.4rem !important; }
h3 { font-size: 1.2rem !important; }

/* Sidebar text spacing */
.sidebar .sidebar-content {
    padding: 1rem 0.5rem;
}

</style>
""", unsafe_allow_html=True)


# ======================================
# 🎛️ SIDEBAR NAVIGATION (Mobile Safe)
# ======================================
page = st.sidebar.radio(
    "🍽️ Choose a section",
    ["🏠 Home", "🍎 What Cuisine Are You? Personality Quiz", "📊 Map of Flavors Dashboard", "🤖 Chatbot (Cook-E)"]
)

# ======================================
# 🏠 PAGE 1 — HOME
# ======================================
if page == "🏠 Home":
    st.title("🍳 Map of Flavors (Carte des Saveurs)")
    
    st.markdown("""
    Welcome to **Temasek Polytechnic’s Map of Flavors**, where  
    **data meets deliciousness — anytime, anywhere! 📱🍜**

    Explore global cuisines, brain-boosting foods, and interactive visualizations  
    designed specially for secondary school students.  
    """)

# ======================================
# 🍎 PAGE 2 — QUIZ
# ======================================
elif page == "🍎 What Cuisine Are You? Personality Quiz":
    st.title("🍎 What Cuisine Are You?")
    st.markdown("""
    🔥 Discover which cuisine matches your study style and energy needs!  
    Take this short personality quiz to find your flavor identity.
    """)

    iframe("https://forms.fillout.com/t/pDTIHQ0YCzrus", height=900, scrolling=True)

# ======================================
# 📊 PAGE 3 — DASHBOARD
# ======================================
elif page == "📊 Map of Flavors Dashboard":
    st.title("📊 Map of Flavors Dashboard")
    st.markdown("""
    Discover ingredient trends, cuisine networks, and brain-boosting foods  
    using our live **NeoDash interactive visualization**.
    """)

    # ⭐ Replace this with the correct EMBED version once you give me your dashboard name
    neodash_url = "https://neodash.graphapp.io/?database=neo4j+s://985a5cea.databases.neo4j.io&dashboard=Map%20of%20Flavors&embed=true"

    iframe(neodash_url, height=900, scrolling=True)

# ======================================
# 🤖 PAGE 4 — CHATBOT
# ======================================
elif page == "🤖 Chatbot (Cook-E)":
    st.title("🤖 Chatbot — Cook-E")
    chatbot.main()



