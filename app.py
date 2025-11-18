import streamlit as st
from streamlit.components.v1 import iframe
import chatbot_app as chatbot   # your Cook-E chatbot file

st.set_page_config(page_title="Map of Flavors", page_icon="🍳", layout="wide")

# === Sidebar Navigation ===
page = st.sidebar.radio(
    "🍽️ Choose a section",
    ["🏠 Home", "🎯 What Cuisine Are You? Personality Quiz", "📊 Map of Flavors Dashboard", "🤖 Chatbot (Cook-E)"]
)

# === PAGE 1: HOME ===
if page == "🏠 Home":
    st.title("🍳 Map of Flavors (Carte des Saveurs)")
    st.markdown("""
    Welcome to **Temasek Polytechnic’s Map of Flavors**, an interactive experience where  
    **flavour and data collide! 🍜📊**  

    Learn how foods and cuisines from around the world can improve your **concentration, memory, and study energy**.  
    Discover the foods that maintain your motivation and mental health! 💪🧠

    ### 👣 How to Explore:
    1️⃣ **Take the Personality Quiz** to discover which cuisine matches your study style.  
    2️⃣ **Explore the Dashboard** to see which regions and ingredients are best for concentration.  
    3️⃣ **Chat with Cook-E 🤖**, our friendly TP data-chef who turns brain food data into fun insights!  

    ---
    """)
    st.image("cutout.png", width=300)
    st.markdown("""
    <p style='text-align:center; color:gray; font-size:18px;'>
    Created by <b>Diploma in Big Data & Analytics</b>, Temasek Polytechnic 💻🍴  
    </p>
    """, unsafe_allow_html=True)

# === PAGE 2: QUIZ ===
elif page == "🎯 What Cuisine Are You? Personality Quiz":
    st.title("🎯 What Cuisine Are You?")
    st.markdown("""
    ⚡Discover which international cuisine best fits your study style and what meals can boost your energy, focus, and memory by taking this little quiz! 🧠🍱
    """)
    iframe("https://forms.fillout.com/t/pDTHqQYcZrus", height=800, scrolling=True)

# === PAGE 3: DASHBOARD ===
elif page == "📊 Map of Flavors Dashboard":
    st.title("📊 Map of Flavors Dashboard")
    st.markdown("""
    Discover ingredient trends, cuisine relationships, and brand associations using our live NeoDash visualization.
    """)
    neodash_url = "http://neodash.graphapp.io/?share&type=database&id=70514bc9-89cb-4584-b03d-ad58c7d6d61c&dashboardDatabase=neo4j"
    iframe(neodash_url, height=850, scrolling=True)

# === PAGE 4: CHATBOT ===
elif page == "🤖 Chatbot (Cook-E)":
    chatbot.main()


