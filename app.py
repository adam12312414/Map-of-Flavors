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
    st.markdown("### 🔐 Dashboard Login (for viewers)")

    st.markdown("👤 **Hostname:**")
    st.code("985a5cea.databases.neo4j.io", language=None)

    st.markdown("🔑 **Password:**")
    st.code("hx16lNc8kwMK5KEUYraRvCTpmmA8g9rKl6toAatnNgw", language=None)

    # 📱 Mobile-only fix for NeoDash iframe responsiveness
    st.markdown("""
    <style>
    @media (max-width: 600px) {
        iframe {
            width: 100% !important;
            max-width: 100% !important;
            transform: scale(0.90);
            transform-origin: top center;
            height: 1400px !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    neodash_url = "https://neodash.graphapp.io/?database=neo4j+s://985a5cea.databases.neo4j.io&dashboard=Map%20of%20Flavors&embed=true"
    iframe(neodash_url, height=850, scrolling=True)

# === PAGE 4: CHATBOT ===
elif page == "🤖 Chatbot (Cook-E)":
    chatbot.main()







