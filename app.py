import streamlit as st
from streamlit.components.v1 import iframe
import chatbot_app as chatbot   # your Cook-E chatbot file
import pandas as pd
import plotly.express as px
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components

# === Neo4j Connection for Dashboard ===
NEO4J_URI = st.secrets["NEO4J_URI"]
NEO4J_USER = st.secrets["NEO4J_USER"]
NEO4J_PASS = st.secrets["NEO4J_PASS"]

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def run_query(cypher, params=None):
    with driver.session() as session:
        result = session.run(cypher, params or {})
        return [r.data() for r in result]

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

    view_mode = st.radio(
        "Choose how to view the dashboard:",
        ["📱 Simple mobile-friendly dashboard", "🧠 Full NeoDash dashboard"],
        help="Use the simple view on phones. Use the full NeoDash view on laptops/desktops."
    )

    # =========================
    # 📱 SIMPLE STREAMLIT DASHBOARD (MOBILE-FRIENDLY)
    # =========================
    if view_mode == "📱 Simple mobile-friendly dashboard":

        # 1️⃣ Header-style summary (matches top of NeoDash)
        st.subheader("🍜 Map of Flavors (Carte des Saveurs)")
        st.caption("Connecting the World Through Ingredients 🌍")

        # 2️⃣ 🌍 Global Dataset Summary
        st.subheader("🌍 Global Dataset Summary")
        kpi_query = """
        MATCH (c:Cuisine)
        WITH count(c) AS cuisines
        MATCH (d:Dish)
        WITH cuisines, count(d) AS dishes
        MATCH (i:Ingredient)
        WITH cuisines, dishes, count(i) AS ingredients
        MATCH (i2:Ingredient)
        WHERE i2.study_food = true
        RETURN cuisines, dishes, ingredients, count(i2) AS study_ingredients
        """
        kpi_res = run_query(kpi_query)
        if kpi_res:
            kpi = kpi_res[0]
            percent_study = (
                round(100 * kpi["study_ingredients"] / kpi["ingredients"], 1)
                if kpi["ingredients"] else 0
            )

            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)
            col1.metric("Total_Cuisines", kpi["cuisines"])
            col2.metric("Total_Dishes", kpi["dishes"])
            col3.metric("Total_Ingredients", kpi["ingredients"])
            col4.metric("Total_Study_Foods", f'{kpi["study_ingredients"]} ({percent_study}%)')

        st.markdown("---")

        # 3️⃣ 🧠🍳Top 10 Ingredients That Help You Study Better
        st.subheader("🧠🍳Top 10 Ingredients That Help You Study Better")
        q_ingredients = """
        MATCH (i:Ingredient)
        WHERE i.study_food = true
        MATCH (:Dish)-[:USES]->(i)
        RETURN i.name AS Ingredient, COUNT(*) AS Frequency
        ORDER BY Frequency DESC
        LIMIT 10
        """
        df_ing = pd.DataFrame(run_query(q_ingredients))
        if not df_ing.empty:
            fig = px.bar(
                df_ing,
                x="Ingredient",
                y="Frequency",
                title="Top 10 Study-Friendly Ingredients"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No study ingredients found in the data.")

        # 4️⃣ 🗺️🥬 Regions Full of Focus-Enhancing Dishes!
        st.subheader("🗺️🥬 Regions Full of Focus-Enhancing Dishes!")
        q_regions = """
        MATCH (r:Region)-[:HAS_CUISINE]->(c:Cuisine)-[:HAS_DISH]->(:Dish)-[:USES]->(i:Ingredient)
        WHERE i.study_food = true
        RETURN r.name AS Region, COUNT(DISTINCT i.name) AS TotalStudyFoods
        ORDER BY TotalStudyFoods DESC
        """
        df_reg = pd.DataFrame(run_query(q_regions))
        if not df_reg.empty:
            fig = px.pie(
                df_reg,
                names="Region",
                values="TotalStudyFoods",
                title="Regions Full of Focus-Enhancing Dishes!"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No region data found.")

        # 5️⃣ 🍱🌍 Cuisines Packed With Brain-Boosting Foods!
        st.subheader("🍱🌍 Cuisines Packed With Brain-Boosting Foods!")
        q_cuisines = """
        MATCH (c:Cuisine)-[:HAS_DISH]->(:Dish)-[:USES]->(i:Ingredient)
        WHERE i.study_food = true
        RETURN c.name AS Cuisine, COUNT(DISTINCT i.name) AS StudyFoods
        ORDER BY StudyFoods DESC
        LIMIT 10
        """
        df_cui = pd.DataFrame(run_query(q_cuisines))
        if not df_cui.empty:
            fig = px.bar(
                df_cui,
                x="Cuisine",
                y="StudyFoods",
                title="Cuisines Packed With Brain-Boosting Foods"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # 6️⃣ 🧠🥗 Top Dishes Packed With Study-Boosting Ingredients
        st.subheader("🧠🥗 Top Dishes Packed With Study-Boosting Ingredients")
        q_dishes = """
        MATCH (d:Dish)-[:USES]->(i:Ingredient)
        WHERE i.study_food = true
        RETURN d.name AS Dish, COUNT(DISTINCT i.name) AS StudyFriendlyIngredients
        ORDER BY StudyFriendlyIngredients DESC
        LIMIT 10
        """
        df_dish = pd.DataFrame(run_query(q_dishes))
        if not df_dish.empty:
            st.table(df_dish)
        else:
            st.info("No dish data found.")

        st.markdown("---")

        # 7️⃣ 🤔 Flavor Fun Facts
        st.subheader("🤔 Flavor Fun Facts")
        st.markdown(
            "- 🥚 **Eggs** contain choline, which helps brain cells communicate more efficiently — perfect before exams!\n"
            "- 🫐 **Blueberries** are rich in antioxidants that support memory and learning."
        )

        # 8️⃣ 🍽️ Flavor Fun Facts (second card)
        st.subheader("🍽️ Flavor Fun Facts")
        st.markdown(
            "- 🥜 A handful of **nuts** a day may improve focus and memory over time.\n"
            "- 🫖 **Green tea** offers gentle caffeine plus L-theanine to keep you calm *and* alert."
        )

        st.markdown("---")

        # 9️⃣ 🥦 Ingredient Explorer (comes BEFORE cuisine explorer now)
        st.subheader("Pick Your Fav Ingredients 💥🧂")

        ing_list_q = """
        MATCH (i:Ingredient)
        WHERE i.study_food = true
        RETURN DISTINCT i.name AS Ingredient
        ORDER BY Ingredient
        """
        df_ing_list = pd.DataFrame(run_query(ing_list_q))
        ing_options = df_ing_list["Ingredient"].tolist() if not df_ing_list.empty else []

        selected_ingredients = st.multiselect(
            "Choose your favourite brain-boosting ingredients:",
            ing_options
        )

        if selected_ingredients:
            # ⭐📊 Ingredient Summary Dashboard
            st.subheader("⭐📊 Ingredient Summary Dashboard")

            rows = []
            for ing in selected_ingredients:
                q_ing_stats = """
                MATCH (i:Ingredient {name:$ing})<-[:USES]-(d:Dish)
                OPTIONAL MATCH (d)<-[:HAS_DISH]-(c:Cuisine)
                OPTIONAL MATCH (c)<-[:HAS_CUISINE]-(r:Region)
                RETURN
                  COUNT(DISTINCT d) AS Dishes,
                  COUNT(DISTINCT c) AS Cuisines,
                  COUNT(DISTINCT r) AS Regions
                """
                res = run_query(q_ing_stats, {"ing": ing})
                if res:
                    stats = res[0]
                    rows.append({
                        "Selected_Ingredient": ing,
                        "Total_Dishes": stats["Dishes"],
                        "Total_Cuisines": stats["Cuisines"],
                        "Total_Regions": stats["Regions"],
                    })
            if rows:
                df_ing_stats = pd.DataFrame(rows)
                st.table(df_ing_stats)

            # 😋🔥 Which Cuisines Love Your Ingredients?
            st.subheader("😋🔥 Which Cuisines Love Your Ingredients?")
            q_ing_cui = """
            MATCH (i:Ingredient)<-[:USES]-(:Dish)<-[:HAS_DISH]-(c:Cuisine)
            WHERE i.name IN $ings
            RETURN c.name AS Cuisine, i.name AS Ingredient, COUNT(*) AS Uses
            ORDER BY Uses DESC
            """
            df_ing_cui = pd.DataFrame(run_query(q_ing_cui, {"ings": selected_ingredients}))
            if not df_ing_cui.empty:
                fig = px.bar(
                    df_ing_cui,
                    x="Cuisine",
                    y="Uses",
                    color="Ingredient",
                    barmode="group",
                    title="Which Cuisines Love Your Ingredients?"
                )
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # 🔟 Cuisine Explorer (after ingredients)
        st.subheader("Where Shall We Eat Today? 😋")

        cuisine_list_q = """
        MATCH (c:Cuisine)
        RETURN DISTINCT c.name AS cuisine
        ORDER BY cuisine
        """
        df_c_list = pd.DataFrame(run_query(cuisine_list_q))
        cuisine_options = df_c_list["cuisine"].tolist() if not df_c_list.empty else []

        selected_cuisine = st.selectbox(
            "Choose a cuisine to explore:",
            ["(pick a cuisine)"] + cuisine_options
        )

        if selected_cuisine != "(pick a cuisine)":
            # 🍽️ Cuisine Summary Dashboard
            st.subheader("🍽️ Cuisine Summary Dashboard")
            q_cui_kpi = """
            MATCH (c:Cuisine {name:$cuisine})-[:HAS_DISH]->(d:Dish)
            WITH c, collect(DISTINCT d) AS allDishes, size(collect(DISTINCT d)) AS totalDishes
            MATCH (c)-[:HAS_DISH]->(d2:Dish)-[:USES]->(i:Ingredient)
            WHERE d2 IN allDishes AND i.study_food = true
            WITH c, totalDishes,
                 COLLECT(DISTINCT d2) AS studyDishes,
                 COLLECT(DISTINCT i) AS studyIngredients
            RETURN
              c.name AS Cuisine,
              totalDishes AS TotalDishes,
              size(studyDishes) AS DishesWithStudyFood,
              size(studyIngredients) AS DistinctStudyIngredients
            """
            df_cui_kpi = pd.DataFrame(run_query(q_cui_kpi, {"cuisine": selected_cuisine}))
            if not df_cui_kpi.empty:
                row = df_cui_kpi.iloc[0]
                k1, k2 = st.columns(2)
                k3, _ = st.columns(2)
                k1.metric("Total_Dishes", row["TotalDishes"])
                k2.metric("Dishes_with_Study_Foods", row["DishesWithStudyFood"])
                k3.metric("Distinct_Study_Ingredients", row["DistinctStudyIngredients"])

            # ⭐ Signature Flavors of Selected Cuisine
            st.subheader("⭐ Signature Flavors of Selected Cuisine")
            q_cui_ing = """
            MATCH (c:Cuisine {name:$cuisine})-[:HAS_DISH]->(d:Dish)-[:USES]->(i:Ingredient)
            WHERE i.study_food = true
            RETURN i.name AS Ingredient, COUNT(DISTINCT d) AS Frequency
            ORDER BY Frequency DESC
            LIMIT 15
            """
            df_cui_ing = pd.DataFrame(run_query(q_cui_ing, {"cuisine": selected_cuisine}))
            if not df_cui_ing.empty:
                fig = px.bar(
                    df_cui_ing,
                    x="Ingredient",
                    y="Frequency",
                    title=f"Signature Flavors of {selected_cuisine}"
                )
                st.plotly_chart(fig, use_container_width=True)

            st.info("For the full 🧬 Flavor Network - Click to explore! view, use the NeoDash dashboard on desktop. 💻")

        st.info("This view is optimised for mobile phones. Use the NeoDash view for full graph visuals on desktop. 💻")

    # =========================
    # 🧠 FULL NEODASH DASHBOARD (DESKTOP)
    # =========================
    else:
        st.markdown("""
        Explore the full interactive NeoDash dashboard with network graphs and filters.  
        Best experienced on a laptop or desktop. 💻
        """)

        st.markdown("### 🔐 Dashboard Login (for viewers)")
        st.markdown("👤 **Hostname:**")
        st.code("985a5cea.databases.neo4j.io", language=None)

        st.markdown("🔑 **Password:**")
        st.code("hx16lNc8kwMK5KEUYraRvCTpmmA8g9rKl6toAatnNgw", language=None)

        neodash_url = "https://neodash.graphapp.io/?database=neo4j+s://985a5cea.databases.neo4j.io&dashboard=Map%20of%20Flavors&embed=true"
        iframe(neodash_url, height=850, scrolling=True)

# === PAGE 4: CHATBOT ===
elif page == "🤖 Chatbot (Cook-E)":
    chatbot.main()












