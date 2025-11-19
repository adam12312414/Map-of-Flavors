import streamlit as st
import pandas as pd
import json
import plotly.express as px
from neo4j import GraphDatabase
from openai import OpenAI
import random

def main():
    # ✅ Load all secrets safely
    NEO4J_URI = st.secrets["NEO4J_URI"]
    NEO4J_USER = st.secrets["NEO4J_USER"]
    NEO4J_PASS = st.secrets["NEO4J_PASS"]

    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))

    # === OpenAI Setup ===
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    def run_query(cypher):
        with driver.session() as session:
            result = session.run(cypher)
            return [record.data() for record in result]

    # === System Prompt ===
    SYSTEM_PROMPT = """
    You are Cook-E 🤖🍪 — Temasek Polytechnic’s friendly data-chef chatbot who turns FOOD DATA into tasty insights!  

    🎯 Core Mission:
    Help visitors explore the “Map of Flavors” dashboard by explaining cuisines, ingredients, brands, and regions — all based on the real data in the Neo4j graph.

    🧠 Graph Structure:
    (Region)-[:HAS_CUISINE]->(Cuisine)
    (Cuisine)-[:HAS_DISH]->(Dish)
    (Dish)-[:USES]->(Ingredient)
    (Ingredient)-[:ASSOCIATED_WITH]->(Brand)

    ⚠️ Neo4j Version Rule:
    - You MUST use Neo4j 5 syntax.
    - NEVER use size() on a pattern.
    - To count pattern matches, ALWAYS use:
    COUNT { (pattern) }

    Example:
    COUNT { (d:Dish)-[:USES]->(i) } AS usesCount
    
    ⚠️ PERFORMANCE RULES (Neo4j Aura Free Tier):
    - NEVER scan the whole graph.
    - ALWAYS start with the most selective node first (e.g., Ingredient or Cuisine).
    - ALWAYS include LIMIT (10 or fewer) in queries.
    - NEVER do long pattern matching like:
      (r:Region)-[:HAS_CUISINE]->(:Cuisine)-[:HAS_DISH]->(:Dish)-[:USES]->(i)
    - Use COUNT {} instead of size().
    - For study foods, start with Ingredient nodes first:
      MATCH (i:Ingredient {study_food:true}) ...
    - When unsure, choose the simpler query.

    🧩 Data Properties:
    - `Ingredient` nodes have a Boolean property `study_food` which is **true** for ingredients that help with studying (focus, memory, or energy).  
    - Use this property to find brain-boosting or study-enhancing ingredients.  
    - Example:
    MATCH (i:Ingredient)
    WHERE i.study_food = true
    RETURN i.name AS StudyIngredient

    👩‍🍳 Personality:
    - You’re like a TP student host at Open House — friendly, excited, and proud to show your project.  
    - Speak clearly, with light local charm (some “wah”, “leh”, “sia” is fine).  
    - Be curious and a bit cheeky, but still informative and accurate.  
    - Sprinkle in 1–3 relevant emojis 🍜📊🌶️🍪 to keep the chat lively.

    💬 Style Guide:
    - Start with the data insight first, then add personality.  
    e.g., “Italian cuisine has the most unique ingredients 🍝 — wah, so many flavours sia!”  
    - If the question isn’t about food or data, reply playfully but redirect:
    “Eh, that one not in my pantry leh 😅 Ask me about cuisines, dishes, or brands instead!”
    - Keep responses short and fun (2–4 sentences). Don’t sound like a report.
    - Never make up data — base everything on the Neo4j dataset only.

    🧠 Response Types:
    If the user wants numbers, comparisons, or trends:
    {
    "cypher": "<Cypher query>",
    "chart": "<bar | pie | line | table>"
    }

    If the user wants storytelling, summary, or fun interpretation:
    {
    "text": "<short Cook-E style explanation, based on data + 1–3 emojis>"
    }

    If the question is off-topic:
    {
    "cypher": "// Off-topic question. Please ask something about food, cuisines, dishes, ingredients, or brands.",
    "chart": "table"
    }

    💡 Query Rule:
    When filtering by names (like cuisine, ingredient, or brand), always compare **case-insensitively** using:
    `WHERE toLower(c.name) = 'italian'`
    This ensures results match even if the data is stored in lowercase.

    🎨 Chart Suggestion Rules:
    - "bar" → category counts (cuisines, ingredients, brands)
    - "pie" → proportions (brand or ingredient shares)
    - "line" → trends or patterns over time
    - "table" → descriptive tabular results
    - "text" → conversational or summary replies

    🥇 Tone Summary:
    Friendly like a TP student 💬  
    Accurate like a data analyst 📊  
    Fun like a foodie 🤤  

    Let visitors leave saying, “Wah, Cook-E quite steady sia — data also can make so fun one!”
    """

    # === Streamlit Setup ===
    st.set_page_config(page_title="Cook-E's Map of Flavors 🍪", page_icon="🍪", layout="centered")

    st.markdown("""
    <style>
    body {
        background: radial-gradient(circle at top left, #2C1E17, #0F0E0E);
        color: #ffffff;
        font-family: 'Poppins', sans-serif;
    }

    /* Headings */
    h1, h2, h3, h4 {
        color: #FFD166;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #ff7e5f, #feb47b);
        color: white;
        border: none;
        border-radius: 10px;
        font-size: 18px;
        padding: 10px 25px;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(90deg, #ff9966, #ff5e62);
        transform: scale(1.05);
    }

    /* Input box */
    .stTextInput>div>div>input {
        background-color: #222;
        border: 2px solid #ffb347;
        border-radius: 10px;
        color: white;
        font-size: 18px;
        padding: 10px;
    }

    /* Container padding */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    # === Header ===
    st.markdown("""
    <div style="margin-left:-60px;">
    <h1 style="font-size:55px; white-space:nowrap; margin:0;">
        👨‍🍳🍪 Cook-E’s Map of Flavors 🌍✨
    </h1>
    </div>
    <p style='font-size:22px; text-align:center; color:#FFD166;'>Where data meets deliciousness! 🍪📊</p>
    <div style='text-align:center; font-size:20px; color:#FFD166; margin-top:-10px; margin-bottom:30px;'>
    👋 Hi! I’m <b>Cook-E</b>, your friendly data chef. Ask me about cuisines, ingredients, brands or anything yummy from our dataset! 🍳
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Try these study-boosting ideas! 👇")
    col1, col2, col3 = st.columns(3)
    question = None
    if col1.button("🧠 Top Study Foods"):
        question = json.dumps({
            "cypher": """
            MATCH (i:Ingredient)
            WHERE i.study_food = true
            WITH i
            MATCH (:Dish)-[:USES]->(i)
            RETURN i.name AS Ingredient, COUNT(*) AS Uses
            ORDER BY Uses DESC
            LIMIT 10
            """,
            "chart": "bar"
        })
    
    if col2.button("🍽️ Study Cuisines"):
        question = json.dumps({
            "cypher": """
            MATCH (i:Ingredient)
            WHERE i.study_food = true
            WITH i
            MATCH (c:Cuisine)-[:HAS_DISH]->(:Dish)-[:USES]->(i)
            RETURN c.name AS Cuisine, COUNT(DISTINCT i.name) AS StudyIngredientCount
            ORDER BY StudyIngredientCount DESC
            LIMIT 5
            """,
            "chart": "bar"
        })
    
    if col3.button("🌍 Study Regions"):
        question = json.dumps({
            "cypher": """
            MATCH (i:Ingredient)
            WHERE i.study_food = true
            WITH i
            MATCH (c:Cuisine)-[:HAS_DISH]->(:Dish)-[:USES]->(i)
            MATCH (r:Region)-[:HAS_CUISINE]->(c)
            RETURN r.name AS Region, COUNT(DISTINCT i.name) AS StudyIngredientCount
            ORDER BY StudyIngredientCount DESC
            LIMIT 5
            """,
            "chart": "bar"
        })

    user_question = st.text_input("Ask a question here:")
    if question is None and user_question: question = user_question

    # === Main Logic ===
    if question:
        bot_name = "Cook-E 👨‍🍳🍪"
        messages = [
            f"{bot_name}: Stirring up some tasty insights just for you... 🍲",
            f"{bot_name}: Cooking your question into delicious data... 👨‍🍳",
            f"{bot_name}: Gathering global flavors from the data pantry... 🌎",
            f"{bot_name}: Whisking up something insightful... 🥣",
            f"{bot_name}: Preheating the analytics oven... 🔥",
            f"{bot_name}: Mixing a fresh batch of data cookies... 🍪"
        ]
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#ff8c68,#ff4b2b);color:white;padding:22px;
        border-radius:15px;font-size:22px;font-weight:600;text-align:center;
        box-shadow:0 0 20px rgba(255,120,90,0.5);margin-top:10px;">{random.choice(messages)}</div>
        """, unsafe_allow_html=True)

        try:
            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                ]
            )

            raw_output = response.choices[0].message.content.strip()
            try:
                ai_output = json.loads(raw_output)
            except json.JSONDecodeError:
                ai_output = {"text": raw_output}

            # === TEXT OUTPUT ===
            if "text" in ai_output:
                insight = ai_output["text"]

                # 🎓 Context-aware TP analogies (multi-line)
                tp_analogies = {
                    "italian": [
                        "🍝 Italian cuisine is full of creativity — like TP’s Design School sia!",
                        "🎨 Italian food got flair and color — TP Design School confirm love this one!"
                    ],
                    "japanese": [
                        "🍣 Japanese cuisine is precise and balanced — just like our Engineering School students!",
                        "🔧 So meticulous sia — feels like something our Engineering students would master!"
                    ],
                    "indian": [
                        "🌶️ Indian food packs strong flavours, just like the energy at TP’s Business School!",
                        "💼 Wah, the spice level steady lah — Business School students sure can handle it!"
                    ],
                    "french": [
                        "🥐 French cuisine is refined — like TP’s Applied Science students mastering precision!",
                        "🧪 French dishes are elegant and scientific — TP Applied Science vibes confirmed!"
                    ],
                    "thai": [
                        "🍲 Thai cuisine mixes sweet, sour, and spicy — like the lively mix of cultures around TP’s campus!",
                        "🔥 Sweet, spicy, tangy — just like TP’s vibrant student life leh!"
                    ],
                    "korean": [
                        "🍱 Korean cuisine is trendy and bold — just like the students at TP’s IT School leh!",
                        "💻 Korean food got that modern touch — very Tech School energy sia!"
                    ],
                    "chinese": [
                        "🥢 Chinese cuisine blends tradition and innovation — just like TP’s multidisciplinary learning!",
                        "📚 Traditional yet modern — same same like TP’s learning style!"
                    ],
                    "western": [
                        "🍔 You can find Western food at TP’s IT and Engineering canteens — classic comfort food everyone loves!",
                        "🍟 Western cuisine? Confirm a hit near Design School’s café — chill and satisfying vibes!"
                    ]
                }

                lower_text = insight.lower()
                matched_cuisine = next((c for c in tp_analogies if c in lower_text), None)

                if matched_cuisine:
                    insight += f"<br><br>{random.choice(tp_analogies[matched_cuisine])}"
                elif random.random() < 0.2:
                    generic_lines = [
                        "🍜 TP’s campus got flavours from all over the world — just like this dataset!",
                        "🍪 That’s one more tasty insight cooked up by TP’s own Cook-E!"
                    ]
                    insight += f"<br><br>{random.choice(generic_lines)}"

                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#00b4d8,#0077b6);padding:30px;
                border-radius:18px;color:white;font-size:22px;line-height:1.6;
                font-weight:600;text-align:center;box-shadow:0 0 25px rgba(0,183,255,0.6);
                margin-top:15px;">🍪 <b>Cook-E says:</b> {insight}</div>
                """, unsafe_allow_html=True)

            # === CHART OUTPUT ===
            else:
                cypher_query = ai_output.get("cypher", "").strip()
                chart_type = ai_output.get("chart", "table")

                if "off-topic" in cypher_query.lower():
                    st.markdown("""
                    <div style="background:linear-gradient(135deg,#ff416c,#ff4b2b);padding:25px;
                    border-radius:18px;color:white;font-size:22px;font-weight:600;
                    text-align:center;box-shadow:0 0 20px rgba(255,105,97,0.7);
                    margin-top:15px;">👨‍🍳 Cook-E: Oops! That’s not food related lah.<br>
                    🍜 Ask me something about cuisines, ingredients, or dishes! 🌶️🍕🍣</div>
                    """, unsafe_allow_html=True)
                else:
                    import re
                    cypher_query = re.sub(r":'([A-Z][a-z]+)'", lambda m: f":'{m.group(1).lower()}'", cypher_query)

                    st.code(cypher_query, language="cypher")
                    results = run_query(cypher_query)
                    if results:
                        df = pd.DataFrame(results)
                        if chart_type == "bar" and len(df.columns) >= 2:
                            fig = px.bar(df, x=df.columns[0], y=df.columns[1], color=df.columns[0],
                                        title=f"📊 {question.title()}",
                                        color_discrete_sequence=px.colors.qualitative.Vivid)
                            st.plotly_chart(fig, use_container_width=True)
                        elif chart_type == "pie" and len(df.columns) >= 2:
                            fig = px.pie(df, names=df.columns[0], values=df.columns[1],
                                        title=f"🥧 {question.title()}",
                                        color_discrete_sequence=px.colors.qualitative.Bold)
                            st.plotly_chart(fig, use_container_width=True)
                        elif chart_type == "line" and len(df.columns) >= 2:
                            fig = px.line(df, x=df.columns[0], y=df.columns[1],
                                        title=f"📈 {question.title()}", markers=True)
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.table(df)
                    else:
                        st.warning("No matching data found.")

        except Exception as e:
            st.error(f"Query Error: {e}")






