import streamlit as st
from streamlit.components.v1 import iframe
import chatbot_app as chatbot 
import pandas as pd
import plotly.express as px
from neo4j import GraphDatabase
from pyvis.network import Network
import streamlit.components.v1 as components

# Neo4j Connection for Dashboard
NEO4J_URI = st.secrets["NEO4J_URI"]
NEO4J_USER = st.secrets["NEO4J_USER"]
NEO4J_PASS = st.secrets["NEO4J_PASS"]

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

def run_query(cypher, params=None):
    with driver.session() as session:
        result = session.run(cypher, params or {})
        return [r.data() for r in result]

st.set_page_config(page_title="Map of Flavors", page_icon="🍳", layout="wide")

# Sidebar Navigation
page = st.sidebar.radio(
    "🍽️ Choose a section",
    ["🏠 Home", "🎯 What Cuisine Are You? Personality Quiz", "📊 Map of Flavors Dashboard", "🤖 Chatbot (Cook-E)"]
)

# PAGE 1: HOME
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

# PAGE 2: QUIZ
elif page == "🎯 What Cuisine Are You? Personality Quiz":
    st.title("🎯 What Cuisine Are You?")
    st.markdown("""
    ⚡Discover which international cuisine best fits your study style and what meals can boost your energy, focus, and memory by taking this little quiz! 🧠🍱
    """)
    iframe("https://forms.fillout.com/t/pDTHqQYcZrus", height=800, scrolling=True)

# PAGE 3: DASHBOARD
elif page == "📊 Map of Flavors Dashboard":
    st.title("📊 Map of Flavors Dashboard")

    view_mode = st.radio(
        "Choose how to view the dashboard:",
        ["📱 Mobile-friendly dashboard", "🧠 Full NeoDash dashboard"],
        help="Use the simple view on phones. Use the full NeoDash view on laptops/desktops."
    )

    # 📱 SIMPLE STREAMLIT DASHBOARD (MOBILE-FRIENDLY)
    if view_mode == "📱 Mobile-friendly dashboard":
        # 🌍 Global Dataset Summary
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
            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Cuisines", f"🌎 {kpi['cuisines']}")
            col2.metric("Total Dishes", f"🍽️ {kpi['dishes']}")
            col3.metric("Total Ingredients", f"🥦 {kpi['ingredients']}")

            percent_study = round(kpi["study_ingredients"] * 100.0 / kpi["ingredients"], 1)

            col4.metric("Study-Food Ingredients", f"🧠 {kpi['study_ingredients']} ({percent_study}%)")

        st.markdown("---")

        # 🧠 Top 10 Ingredients, Regions, Cuisines, Dishes
        st.subheader("🧠🍳Top 10 Ingredients That Help You Study Better")

        q_ingredients = """
        MATCH (i:Ingredient)
        WHERE i.study_food = true
        MATCH (:Dish)-[:USES]->(i)
        RETURN i.name AS Ingredient, COUNT(*) AS Uses
        ORDER BY Uses DESC
        LIMIT 10
        """
        df_ing = pd.DataFrame(run_query(q_ingredients))
        if not df_ing.empty:
            bar_colors = px.colors.qualitative.Vivid + px.colors.qualitative.Pastel + px.colors.qualitative.Bold
        
            #Bar chart with unique colors per bar
            fig = px.bar(
                df_ing,
                x="Ingredient",
                y="Uses",
                title="Top 10 Brain-Boosting Ingredients",
                color="Ingredient",  # color by ingredient
                color_discrete_sequence=bar_colors[:len(df_ing)]
            )
        
            #Match NeoDash dark theme + hide legend
            fig.update_layout(
                margin=dict(t=10, b=50, l=50, r=20),
                plot_bgcolor="#0e1117",
                paper_bgcolor="#0e1117",
                font_color="white",
                xaxis_title="Ingredient",
                yaxis_title="Uses",
                showlegend=False,
                title=""
            )
        
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No study ingredients found in the data.")

        # 🌍 Regions with most study ingredients
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
                title="Regions Full of Focus-Enhancing Foods",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
        
            # Improve label sharpness + font clarity
            fig.update_traces(
                textinfo="percent+label",
                textfont_size=18,       
                textfont_color="white",   
                pull=[0.03] * len(df_reg)  
            )
        
            # 🖤 Match NeoDash dark theme
            fig.update_layout(
                margin=dict(t=10, b=50, l=50, r=20),
                plot_bgcolor="#0e1117",
                paper_bgcolor="#0e1117",
                font_color="white",
                showlegend=True,
                legend_font_size=16,   
                legend_title_text="",      
                title_font_size=22,
                title=""
            )
        
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No region data found.")

        # 🍜 Cuisines packed with study foods
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
            # 🎨 Custom color palette
            bar_colors = px.colors.qualitative.Vivid + px.colors.qualitative.Pastel + px.colors.qualitative.Bold
        
            # Colorful bar chart with no legend
            fig = px.bar(
                df_cui,
                x="Cuisine",
                y="StudyFoods",
                title="Cuisines Packed with Focus-Boosting Ingredients",
                color="Cuisine",
                color_discrete_sequence=bar_colors[:len(df_cui)]
            )
        
            # Dark theme + clean layout
            fig.update_layout(
                margin=dict(t=10, b=50, l=50, r=20),
                plot_bgcolor="#0e1117",
                paper_bgcolor="#0e1117",
                font_color="white",
                xaxis_title="Cuisine",
                yaxis_title="Number of Study Ingredients",
                showlegend=False,
                title=""
            )
        
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cuisine data found.")

        # 🍽️ Top dishes packed with study ingredients
        st.subheader("🧠🥗 Top Dishes Packed With Study-Boosting Ingredients")
        q_dishes = """
        MATCH (d:Dish)-[:USES]->(i:Ingredient {study_food: true})
        WITH d, COUNT(DISTINCT i) AS StudyFriendlyIngredients
        MATCH (d)<-[:HAS_DISH]-(c:Cuisine)
        RETURN d.name AS Dish, c.name AS Cuisine, StudyFriendlyIngredients
        ORDER BY StudyFriendlyIngredients DESC, Dish ASC
        LIMIT 10
        """
        df_dish = pd.DataFrame(run_query(q_dishes))
        if not df_dish.empty:
            st.table(df_dish)
        else:
            st.info("No dish data found.")

        st.markdown("---")
        
        # Flavor Fun Facts (NeoDash-style cards)
        st.subheader("🤔 Flavor Fun Facts")

        st.markdown("""
        <style>
        .fact-card {
            background-color: #111827;
            border: 1px solid #374151;
            padding: 18px;
            border-radius: 12px;
            margin-bottom: 15px;
        }
        .fact-title {
            font-size: 20px;
            font-weight: 600;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .fact-text {
            font-size: 16px;
            line-height: 1.5;
        }
        </style>
        """, unsafe_allow_html=True)

        fun_facts_html = [
            """
            <div class='fact-card'>
                <div class='fact-text'>
                🥚💭 Eggs include choline, an essential vitamin that helps brain cells 
                communicate more quickly and effectively — one of the best foods to eat 
                before studying or an exam! 🎯🧠
                </div>
            </div>
            """,
            """
            <div class='fact-card'>
                <div class='fact-text'>
                🥜🤎 Studies suggest that eating just one handful of nuts a day can 
                improve memory and focus in only a few weeks! 💡⚡
                </div>
            </div>
            """
        ]

        for card in fun_facts_html:
            st.markdown(card, unsafe_allow_html=True)

        st.markdown("---")

        # 🧂 INGREDIENT SECTION 
        st.subheader("Pick Your Fav Ingredients 💥 🧂")
        st.caption("Choose your favourite ingredients:")

        # Ingredient list
        ing_list_q = """
        MATCH (i:Ingredient)
        RETURN DISTINCT i.name AS Ingredient
        ORDER BY Ingredient
        """
        df_ing_list = pd.DataFrame(run_query(ing_list_q))
        ing_options = df_ing_list["Ingredient"].tolist() if not df_ing_list.empty else []

        selected_ingredients = st.multiselect(
            "Start typing to search ingredients:",
            ing_options
        )

        if selected_ingredients:
            # ⭐📊 Ingredient Summary Dashboard
            st.subheader("⭐📊 Ingredient Summary Dashboard")

            q_ing_summary = """
            WITH $ingredients AS selectedIngredients

            // Step 1: Get ingredient nodes
            MATCH (i:Ingredient)
            WHERE i.name IN selectedIngredients
            WITH collect(i) AS ing_list, selectedIngredients AS ing_names

            // Step 2: Count cuisines using these ingredients
            MATCH (c:Cuisine)-[:HAS_DISH]->(d:Dish)-[:USES]->(i:Ingredient)
            WHERE i IN ing_list
            WITH ing_list, ing_names, count(DISTINCT c) AS total_cuisines

            // Step 3: Count dishes using ingredients
            MATCH (d:Dish)-[:USES]->(i:Ingredient)
            WHERE i IN ing_list
            WITH ing_list, ing_names, total_cuisines,
                 count(DISTINCT d) AS total_dishes

            // Step 4: Percent study ingredients
            WITH ing_list, ing_names, total_cuisines, total_dishes,
                 size(ing_list) AS total_selected,
                 size([x IN ing_list WHERE x.study_food = true]) AS total_study_foods

            RETURN
              ing_names AS Selected_Ingredients,
              total_cuisines AS Total_Cuisines,
              total_dishes AS Total_Dishes,
              CASE WHEN total_selected = 0
                   THEN 0.0
                   ELSE ROUND((total_study_foods * 100.0 / total_selected), 1)
              END AS Percent_Study_Ingredients
            """
            df_ing_stats = pd.DataFrame(run_query(q_ing_summary, {"ingredients": selected_ingredients}))
            if not df_ing_stats.empty:
                row = df_ing_stats.iloc[0]

                # ⭐ Replace table with KPI cards
                k1, k2, k3 = st.columns(3)

                # 🌎 Total cuisines using your selected ingredients
                k1.metric(
                    label="Total Cuisines",
                    value=f"🌎 {row['Total_Cuisines']}"
                )

                # 🍽️ Total dishes using your ingredients
                k2.metric(
                    label="Total Dishes",
                    value=f"🍽️ {row['Total_Dishes']}"
                )

                # 🧠 Percent study-food ingredients among selected
                k3.metric(
                    label="Study-Food %",
                    value=f"📊 {row['Percent_Study_Ingredients']}%"
                )

            # 😋🔥 Which Cuisines Love Your Ingredients?
            st.subheader("😋🔥 Which Cuisines Love Your Ingredients?")
            q_ing_cui = """
            WITH $ingredients AS ingredients

            MATCH (i:Ingredient)
            WHERE i.name IN ingredients

            MATCH (c:Cuisine)-[:HAS_DISH]->(d:Dish)-[:USES]->(i)
            RETURN c.name AS Cuisine,
                   COUNT(*) AS ingredient_usage
            ORDER BY ingredient_usage DESC
            """
            df_ing_cui = pd.DataFrame(run_query(q_ing_cui, {"ingredients": selected_ingredients}))
            if not df_ing_cui.empty:
                bar_colors = px.colors.qualitative.Vivid + px.colors.qualitative.Pastel + px.colors.qualitative.Bold
            
                fig = px.bar(
                    df_ing_cui,
                    x="Cuisine",
                    y="ingredient_usage",
                    title="Which Cuisines Love Your Ingredients?",
                    color="Cuisine",
                    color_discrete_sequence=bar_colors[:len(df_ing_cui)]
                )
            
                fig.update_layout(
                    margin=dict(t=10, b=50, l=50, r=20),
                    plot_bgcolor="#0e1117",
                    paper_bgcolor="#0e1117",
                    font_color="white",
                    xaxis_title="Cuisine",
                    yaxis_title="Uses",
                    showlegend=False,
                    title=""
                )
            
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No cuisine data found for your selected ingredients.")

            # 🕸️ Ingredient Spider-Web (network graph)
            st.subheader("🕸️🍽️ Ingredient Spider-Web of Tasty Connections")

            q_net = """
            MATCH (i:Ingredient)<-[:USES]-(d:Dish)<-[:HAS_DISH]-(c:Cuisine)
            WHERE i.name IN $ingredients
            WITH i, d, c
            ORDER BY rand()
            LIMIT 80
            RETURN i.name AS Ingredient, d.name AS Dish, c.name AS Cuisine
            """
            df_net = pd.DataFrame(run_query(q_net, {"ingredients": selected_ingredients}))

            if not df_net.empty:
                net = Network(
                    height="600px",
                    width="100%",
                    bgcolor="#0e1117",
                    font_color="white"
                )
                net.force_atlas_2based()

                for _, row in df_net.iterrows():
                    ing = row["Ingredient"]
                    dish = row["Dish"]
                    cui = row["Cuisine"]

                    net.add_node(ing, label=ing, color="#80ffdb", shape="dot")
                    net.add_node(dish, label=dish, color="#5e60ce", shape="dot")
                    net.add_node(cui, label=cui, color="#64dfdf", shape="dot")

                    net.add_edge(ing, dish)
                    net.add_edge(dish, cui)

                net.save_graph("ingredient_network.html")
                with open("ingredient_network.html", "r", encoding="utf-8") as f:
                    html_graph = f.read()
                components.html(html_graph, height=600, scrolling=True)
            else:
                st.info("No network connections found for the selected ingredients.")

        st.markdown("---")
        
        # 😋 CUISINE SECTION (matches NeoDash order)
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
            MATCH (c:Cuisine)
            WHERE toLower(c.name) = toLower($cuisine)

            // Get all ingredients in the cuisine
            OPTIONAL MATCH (c)-[:HAS_DISH]->(:Dish)-[:USES]->(i_all:Ingredient)
            WITH c, COLLECT(DISTINCT i_all) AS all_ingredients

            // Get all study ingredients
            OPTIONAL MATCH (c)-[:HAS_DISH]->(:Dish)-[:USES]->(i_study:Ingredient)
            WHERE i_study.study_food = true
            WITH c, all_ingredients, COLLECT(DISTINCT i_study) AS study_ingredients

            RETURN
              c.name AS Cuisine,
              SIZE(study_ingredients) AS Total_Study_Ingredients,
              SIZE(all_ingredients) AS Total_Ingredients,
              CASE WHEN SIZE(all_ingredients) = 0
                   THEN 0.0
                   ELSE ROUND((SIZE(study_ingredients) * 100.0 / SIZE(all_ingredients)), 1)
              END AS Percent_Study_Ingredients
            """
            df_cui_kpi = pd.DataFrame(run_query(q_cui_kpi, {"cuisine": selected_cuisine}))
            if not df_cui_kpi.empty:
                row = df_cui_kpi.iloc[0]
                k1, k2, k3 = st.columns(3)

                # 🧠 total study ingredients
                k1.metric(
                    label="Total Study Ingredients",
                    value=f"🧠 {row['Total_Study_Ingredients']}"
                )

                # 🥗 total ingredients
                k2.metric(
                    label="Total Ingredients",
                    value=f"🥗 {row['Total_Ingredients']}"
                )

                # 📊 percent study ingredients
                k3.metric(
                    label="Percent Study Ingredients",
                    value=f"📊 {row['Percent_Study_Ingredients']}%"
                )

            # ⭐ Signature Flavors of Selected Cuisine
            st.subheader("⭐ Signature Flavors of Selected Cuisine")
            q_cui_ing = """
            MATCH (c:Cuisine)
            WHERE toLower(c.name) = toLower($cuisine)
            MATCH (c)-[:HAS_DISH]->(d:Dish)-[:USES]->(i:Ingredient)
            WHERE i.study_food = true
            RETURN i.name AS Ingredient, COUNT(DISTINCT d) AS Frequency
            ORDER BY Frequency DESC
            LIMIT 15
            """
            df_cui_ing = pd.DataFrame(run_query(q_cui_ing, {"cuisine": selected_cuisine}))
            if not df_cui_ing.empty:
                bar_colors = px.colors.qualitative.Vivid + px.colors.qualitative.Pastel + px.colors.qualitative.Bold
            
                fig = px.bar(
                    df_cui_ing,
                    x="Ingredient",
                    y="Frequency",
                    title=f"Signature Flavors of {selected_cuisine}",
                    color="Ingredient",
                    color_discrete_sequence=bar_colors[:len(df_cui_ing)]
                )
            
                # 🖤 Dark theme styling
                fig.update_layout(
                    margin=dict(t=10, b=50, l=50, r=20),
                    plot_bgcolor="#0e1117",
                    paper_bgcolor="#0e1117",
                    font_color="white",
                    xaxis_title="Ingredient",
                    yaxis_title="Frequency",
                    showlegend=False,
                    title=""
                )
            
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No signature flavors found for this cuisine.")

            # 🧬 Flavor Network - Click to explore! (Cuisine network)
            st.subheader("🧬 Flavor Network - Click to explore!")

            q_cui_net = """
            MATCH (c:Cuisine)
            WHERE toLower(c.name) = toLower($cuisine)

            OPTIONAL MATCH (c)-[:HAS_DISH]->(d:Dish)-[:USES]->(i:Ingredient)
            WHERE i.study_food = true
            WITH c, d, i
            WHERE d IS NOT NULL AND i IS NOT NULL
            WITH c, d, i
            ORDER BY rand()
            LIMIT 25

            RETURN c.name AS Cuisine, d.name AS Dish, i.name AS Ingredient
            """
            df_cui_net = pd.DataFrame(run_query(q_cui_net, {"cuisine": selected_cuisine}))
            if not df_cui_net.empty:
                net2 = Network(
                    height="600px",
                    width="100%",
                    bgcolor="#0e1117",
                    font_color="white"
                )
                net2.force_atlas_2based()

                for _, row in df_cui_net.iterrows():
                    cui = row["Cuisine"]
                    dish = row["Dish"]
                    ing = row["Ingredient"]

                    net2.add_node(cui, label=cui, color="#ffd166", shape="dot")
                    net2.add_node(dish, label=dish, color="#5e60ce", shape="dot")
                    net2.add_node(ing, label=ing, color="#80ffdb", shape="dot")

                    net2.add_edge(cui, dish)
                    net2.add_edge(dish, ing)

                net2.save_graph("cuisine_network.html")
                with open("cuisine_network.html", "r", encoding="utf-8") as f:
                    html_graph2 = f.read()
                components.html(html_graph2, height=600, scrolling=True)
            else:
                st.info("No network connections found for this cuisine.")


            # 🍱 Top Study-Boosting Dishes in Selected Cuisine
            st.subheader("🍱 Top Study-Boosting Dishes in Selected Cuisine")
            
            q_dishes = """
            MATCH (c:Cuisine)-[:HAS_DISH]->(d:Dish)-[:USES]->(i:Ingredient)
            WHERE i.study_food = true 
              AND toLower(c.name) = toLower($cuisine)
            WITH d, COUNT(DISTINCT i) AS StudyFriendlyIngredients
            RETURN d.name AS Dish, StudyFriendlyIngredients
            ORDER BY StudyFriendlyIngredients DESC
            LIMIT 10
            """
            
            df_dish = pd.DataFrame(run_query(q_dishes, {"cuisine": selected_cuisine}))
            
            if not df_dish.empty:
                st.table(df_dish)
            else:
                st.info("No dish data found.")

            # 📍 Where to find this cuisine at TP
            st.subheader("🍜 Hungry? Find This Cuisine at TP")
            
            c = selected_cuisine.lower()
            
            tp_locations = {
                "japanese": [
                    "🍱 Japanese Rice Bowl — The Flavours (BLK 4, IIT, Level 2)",
                    "🍣 Japanese — The Designer Pad (BLK 28, Design, Level 1)",
                ],
                "chinese": [
                    "🍗 Chicken Rice — The Flavours (BLK 4, IIT, Level 2)",
                    "🍜 Ban Mian & Fish Soup — The Flavours (BLK 4, IIT, Level 2)",
                    "🥘 A Tangerine Wok — Sprout Canteen (BLK 1A, HSS, Level 2)",
                    "🍗 Chicken Rice — The Business Park (BLK 26, Business, Level 1)",
                    "🍳 Mini Wok — The Business Park (BLK 26, Business, Level 1)",
                    "🍜 Koka Noodles — The Business Park (BLK 26, Business, Level 1)",
                    "🦆 Roasted Delight — Short Circuit (BLK 17, Engineering, Level 1)",
                    "🌶️ Mala Hot Pot — Short Circuit (BLK 17, Engineering, Level 1)",
                    "🍚 Mixed Veg Rice & Bee Hoon — Breadboard (BLK 25, Engineering, Level 1)",
                    "🍗 Chicken Rice — Breadboard (BLK 25, Engineering, Level 1)",
                ],
                "indian": [
                    "🍛 Indian Muslim — The Business Park (BLK 26, Business, Level 1)",
                    "🥘 Indian Cuisine — Breadboard (BLK 25, Engineering, Level 1)",
                ],
                "korean": [
                    "🍗 Fried Chicken — The Business Park (BLK 26, Business, Level 1)",
                    "🍲 Korean — Short Circuit (BLK 17, Engineering, Level 1)",
                    "🥟 Korean Cuisine — Breadboard (BLK 25, Engineering, Level 1)",
                ],
                "thai": [
                    "🍲 Thai — The Business Park (BLK 26, Business, Level 1)",
                    "🍜 Thai Cuisine — Breadboard (BLK 25, Engineering, Level 1)",
                ],
                "italian": [
                    "🍝 Italian Cuisine — The Flavours (BLK 4, IIT, Level 2)",
                ],
            }
            
            if c in tp_locations:
                for loc in tp_locations[c]:
                    st.markdown(f"- {loc}")
            else:
                st.info("ℹ️ This cuisine is not currently available in TP canteens.")

            # 🍽️ Smart dish recommendation (Cuisine + picked ingredients)
            st.subheader("🍽️ Recommendations Based on Your Selected Cuisine & Ingredients")
            st.caption("Tip: Pick 1–3 ingredients above, then choose a cuisine to get better matches.")
            
            q_reco = """
            WITH toLower($cuisine) AS cuisine,
                 coalesce($ingredients, []) AS ingParam
            
            WITH cuisine,
                 [x IN ingParam | toLower(toString(x))] AS picked,
                 size(ingParam) AS pickedCount
            
            OPTIONAL MATCH (c:Cuisine)
            WHERE toLower(c.name) = cuisine
            OPTIONAL MATCH (c)-[:HAS_DISH]->(d:Dish)
            
            OPTIONAL MATCH (d)-[:USES]->(i:Ingredient)
            WITH cuisine, picked, pickedCount, d,
                 collect(DISTINCT toLower(i.name)) AS dishIngs
            
            WITH cuisine, picked, pickedCount, d,
                 [x IN picked WHERE x IN dishIngs] AS matched,
                 size([x IN picked WHERE x IN dishIngs]) AS matchScore
            
            OPTIONAL MATCH (d)-[:USES]->(sf:Ingredient {study_food:true})
            WITH cuisine, picked, pickedCount, d, matched, matchScore,
                 count(DISTINCT sf) AS studyBoost,
                 (matchScore * 10 + count(DISTINCT sf)) AS rankScore
            
            WITH cuisine, picked, pickedCount,
                 collect({
                   dish: coalesce(d.name, "NO_DISH"),
                   matchScore: matchScore,
                   matched: matched,
                   studyBoost: studyBoost,
                   rankScore: rankScore
                 }) AS rows
            
            UNWIND
            CASE
              WHEN pickedCount > 0
               AND size([r IN rows WHERE r.matchScore > 0]) = 0
              THEN
                [{
                  dish: "⚠️ No matching dishes found",
                  matchScore: 0,
                  matched: ["Please change or add ingredients — none match " + cuisine + " dishes in our dataset."],
                  studyBoost: 0,
                  rankScore: 0
                }]
              ELSE
                [r IN rows WHERE r.matchScore > 0]
            END AS r
            
            RETURN
            r.dish AS RecommendedDish,
            r.matchScore AS MatchedPickedIngredients,
            reduce(
              s = "",
              x IN r.matched |
              s + CASE WHEN s = "" THEN "" ELSE ", " END + x
            ) AS MatchedIngredients,
            r.studyBoost AS StudyFriendlyIngredientCount,
            CASE
              WHEN r.dish STARTS WITH "⚠️" THEN "⚠️"
              ELSE "✅"
            END AS Note
            ORDER BY r.rankScore DESC
            LIMIT 5
            """
            
            # ✅ Run only when cuisine is chosen (ingredients can be empty or not)
            df_reco = pd.DataFrame(run_query(q_reco, {
                "cuisine": selected_cuisine,
                "ingredients": selected_ingredients
            }))
            
            if not df_reco.empty:
                df_reco = df_reco[["Note", "RecommendedDish", "MatchedPickedIngredients", "MatchedIngredients", "StudyFriendlyIngredientCount"]]
                st.table(df_reco)
            else:
                st.info("No recommendation data found.")


            st.info("This view is optimised for mobile phones. Use the NeoDash view for full graph visuals on desktop. 💻")

    # 🧠 FULL NEODASH DASHBOARD (DESKTOP)
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

# PAGE 4: CHATBOT
elif page == "🤖 Chatbot (Cook-E)":
    chatbot.main()











































