# Water, Retinol, Hexyl Cinnamal, Jojoba Oil, Tea Tree Oil, Glycerin
import time
import streamlit as st
from PIL import Image
import pytesseract
import base64
from openai import OpenAI
from analysis import analyze_ingredients

query_params = st.query_params
page = query_params.get("page", "home")

client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key="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"
)

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def clean_ingredients_with_gpt(ocr_text):
    prompt = (
        "You are a skincare analysis assistant. The following is raw OCR text from a skincare product. "
        "Extract the list of ingredients from the text below. "
        "Correct any spelling mistakes, and normalize ingredient names to standard skincare terms "
        "(e.g., correct 'gylciren' to 'Glycerin', 'hyaluronik acid' to 'Hyaluronic Acid'). "
        "Return only the cleaned, comma-separated ingredient list. "
        "Ignore all marketing, descriptions, or instructions.\n\n"
        f"Raw OCR Text:\n{ocr_text}\n\nIngredients:"
    )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skincare expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Error calling GPT: {str(e)}"


def run_analysis(cleaned_text):
    placeholder = st.empty()
    placeholder.markdown("""
    <div style='
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
        margin-top: 2rem;
    '>
        <div class='loader'></div>
    </div>

    <style>
    .loader {
    border: 5px solid #e0e0e0;
    border-top: 5px solid #000000;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    }
    @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

    time.sleep(2.5)
    placeholder.empty()

    ingredient_list = [i.strip().lower()
                       for i in cleaned_text.split(",") if i.strip()]
    result = analyze_ingredients(ingredient_list)

    st.markdown("<div class='section-heading'>Per-Ingredient Summary</h4>",
                unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, item in enumerate(result["found"]):
        summary = (
            f"<b><span style='font-size:1.25rem;'>{item['Ingredient'].title()}</span></b><br>"
            f"<b>Safe for:</b> {' '.join([s for s in ['Dry' if item['Dry_Skin_Safe'] else '', 'Oily' if item['Oily_Skin_Safe'] else '', 'Acne-Prone' if item['Acne_Prone_Safe'] else ''] if s])}<br>"
            f"<b>Comedogenic:</b> {'Yes' if item['Comedogenic'] else 'No'}<br>"
            f"<b>Safety Score:</b> {item['Safety_Score']}/10<br>"
            f"<b>Description:</b> {item['Description']}"
        )
        with cols[idx % 2]:
            st.markdown(f"""
                <div style='
                    background-color: #000000;
                    border-radius: 15px; 
                    padding: 1rem; 
                    box-shadow: 
                        inset 0 0 20px #ededed, 
                        0 0 30px 10px #ffffff;
                    margin-bottom: 1.5rem; 
                    margin-left: 1.4rem;
                '>
                    <div style='
                        margin: 0; 
                        font-family: Segoe UI, sans-serif; 
                        font-size: 0.92rem; 
                        color: #F5EFE7;
                        text-shadow: 0 0 0 #F2F2F2, 0 0 0 #F2F2F2;
                    '>{summary}</div>
                </div>
            """, unsafe_allow_html=True)

    if result["missing"]:
        st.markdown(
            "<h4 style='color:#CC444B;'>⚠️ Missing Ingredients</h4>", unsafe_allow_html=True)
        for miss in result["missing"]:
            st.warning(f"❗️ {miss} not found in database.")

    st.markdown("<div class='section-heading'>Overall Product Analysis</div>",
                unsafe_allow_html=True)

    placeholder = st.empty()
    placeholder.markdown("""
    <div style='
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
        margin-top: 2rem;
    '>
        <div class='loader'></div>
    </div>

    <style>
    .loader {
    border: 5px solid #e0e0e0;
    border-top: 5px solid #000000;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    animation: spin 1s linear infinite;
    }
    @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

    time.sleep(4)
    placeholder.empty()

    st.markdown(f"""
    <div style="
        max-width: 700px;
        margin: 2rem auto;
        padding: 0 1.2rem;
        font-family: 'Segoe UI', sans-serif;
        font-size: 1.15rem;
        line-height: 2;
        font-weight: 500;
        color: #1a1a1a;
        background-color: transparent;
    ">
        The product has a <b>GlowScore of {result['glow_score']} / 10</b>, meaning it shows {"great" if result['glow_score'] >= 8 else "average" if result['glow_score'] >= 5 else "poor"} overall skin-friendliness.<br><br>
        • <b>{result['dry_safe_pct']}%</b> ingredients safe for dry skin<br>
        • <b>{result['oily_safe_pct']}%</b> ingredients safe for oily skin<br>
        • <b>{result['acne_safe_pct']}%</b> ingredients safe for acne-prone skin<br>
        • <b>{result['comedogenic_count']}</b> comedogenic ingredient(s)<br>
        • <b>{len(result['missing'])}</b> ingredient(s) not found in database
    </div>
    """, unsafe_allow_html=True)

    bar_width = result['glow_score'] * 10
    st.markdown(f"""
        <style>
        @keyframes fillBounce {{
            0%    {{ width: 0%; }}
            70%   {{ width: {bar_width * 0.999}%; }}
            75%   {{ width: {bar_width * 1.001}%; }}
            85%   {{ width: {bar_width * 0.985}%; }}
            92%   {{ width: {bar_width * 1.008}%; }}
            97%   {{ width: {bar_width * 0.997}%; }}
            100%  {{ width: {bar_width}%; }}
        }}

        </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <style>
    .glowbar-container {{
        margin-top: 2rem;
        margin-left: 0.15rem;
        text-align: center;
    }}

    .glowbar-track {{
        width: 90%;
        height: 20px;
        background: linear-gradient(to right, #e74c3c, #f1c40f, #2ecc71);
        border-radius: 12px;
        margin: 0 auto;
        box-shadow: inset 0 0 6px #aaa;
        position: relative;
        overflow: hidden;
    }}

    .glowbar-fill {{
        height: 100%;
        background-color: rgba(0, 0, 0, 0.9);
        border-radius: 0px;
        box-shadow: 0 0 10px rgba(0,0,0,0.4);
        width: 0%;
        animation: fillBounce 1.9s cubic-bezier(0.25, 1, 0.5, 1) forwards;
        animation-delay: 1.2s;
    }}

    .glowbar-labels {{
        display: flex;
        justify-content: space-between;
        margin: 4px auto 0 auto;
        width: 89%;
        font-size: 0.95rem;
        font-weight: 650;
        color: #444;
        font-family: Segoe UI, sans-serif;
    }}
    </style>

    <div class='glowbar-container'>
        <div class='glowbar-track'>
            <div class='glowbar-fill'></div>
        </div>
        <div class='glowbar-labels'>
            <span>Unsafe</span>
            <span>Average</span>
            <span>Safe</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.session_state.result = result
    st.session_state.glowscore = result.get("glow_score", "?")


def show_final_results(cleaned_text, quiz_answers=None):
    result = st.session_state.get("result")
    glowscore = st.session_state.get("glowscore")
    if not result:
        st.error("❌ No result data found.")
        return
    if not quiz_answers:
        st.error("❌ No skin quiz data found.")
        return

    st.markdown("""
    <div class="section-heading">Product Ingredients</div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .ingredient-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 1.5rem;
        max-width: 850px;
        margin: 0rem auto 2.5rem;
        padding: 0.5rem;
        font-family: 'Segoe UI', sans-serif;
    }
    .ingredient-item {
        background-color: transparent;
        border-radius: 0;
        padding: 0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #111;
        font-family: 'Segoe UI', sans-serif;
        box-shadow: none;
    }
    </style>
    <div class="ingredient-grid">
    """, unsafe_allow_html=True)

    cols = st.columns(2)
    for idx, item in enumerate(result.get("found", [])):
        name = item.get("Ingredient", "Unknown").title()
        description = item.get("Description", "No description available.")
        safe_for = ' '.join([
            'Dry' if item.get('Dry_Skin_Safe') else '',
            'Oily' if item.get('Oily_Skin_Safe') else '',
            'Acne-Prone' if item.get('Acne_Prone_Safe') else ''
        ]).strip()
        comedogenic = "Yes" if item.get("Comedogenic") else "No"
        safety_score = item.get("Safety_Score", "?")

        summary = f"""
        <b style='font-size:1.2rem;'>{name}</b><br>
        <b>Safe for:</b> {safe_for or 'None'}<br>
        <b>Comedogenic:</b> {comedogenic}<br>
        <b>Safety Score:</b> {safety_score}/10<br>
        <b>Description:</b> {description}
        """

        with cols[idx % 2]:
            st.markdown(f"""
            <div style='
                padding: 0.5rem;
                font-size: 0.95rem;
                font-family: Segoe UI, sans-serif;
                color: #111;
            '>{summary}</div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="section-heading">Ask your Skincare Coach :D</div>
    """, unsafe_allow_html=True)

    questions = [
        "How should I use this product in my routine?",
        "Is this safe for my skin type and sensitivity?",
        "Does this address my main skin concerns?",
        "Can I use this every day or only at night?",
        "Do I need to apply sunscreen with this?"
    ]

    default_text = "\n".join(f"• {q}" for q in questions)
    user_question = st.text_area(
        label="Type your question or query:",
        placeholder="e.g., • How should I use this product in my routine?\n          • Is this safe for my skin type and sensitivity?\n          • Does this address my main skin concerns?\n          • Can I use this every day or only at night?\n          • Do I need to apply sunscreen with this?",
        value="",
        height=140,
        label_visibility="visible"
    )

    if user_question and not user_question.strip().startswith("•"):
        coach_response = generate_coach_answer(
            cleaned_text, quiz_answers, user_question)
        st.markdown(f"""
        <div style="
            max-width: 750px;            
            margin: 1rem auto 1rem 1.1rem; 
            padding: 1rem;               
            background-color: #FFFFFF; 
            border: 2px solid #F5EFE7;   
            border-radius: 15px;        
            box-shadow: 2px 4px 10px rgba(33,53,85,0.2);  
            font-family: 'Segoe UI', sans-serif;
            font-size: 1.05rem;
            line-height: 1.7;
            color: #111;
        ">
            {coach_response}
        </div>
        """, unsafe_allow_html=True)


def generate_coach_answer(cleaned_text, quiz_answers, question):
    prompt = f"""
You are a friendly, knowledgeable skincare coach.

A user has a product with these ingredients:
{cleaned_text}

Their quiz results:
- Skin Type: {quiz_answers['skin_type']}
- Sensitivity: {quiz_answers['skin_sensitivity']}
- Concerns: {', '.join(quiz_answers['concerns'])}
- Allergies: {quiz_answers['allergies']}
- Reactions: {quiz_answers['previous_reactions']}
- Routine Frequency: {quiz_answers['routine_frequency']}
- Treating Condition: {quiz_answers['is_treating_condition']}

Now, respond in a short 4-5 line paragraph (markdown, no headings), answering:
"{question}"

Be friendly but expert. Always be helpful and accurate. Dont ask questions.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skincare coach AI."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=400
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ GPT error: {e}"


st.set_page_config(page_title="GlowScore", layout="centered")

if "mode" not in st.session_state:
    st.session_state.mode = None


st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Black&display=swap');

    body {
        background-color: #F2F2F2;
    }

    .stApp {
        background-color: transparent;
    }

    .main-title {
        text-align: center;
        color: #000000;
        font-family: 'Archivo Black', sans-serif;
        font-size: 3.2rem;
        font-weight: normal;
        margin-top: 0rem;
        margin-bottom: 0.2rem;
        letter-spacing: 1px;
        text-shadow: 
            0 0 5px #ffffff,
            0 0 10px #ffffff,
            0 0 5px #ffffff,
            0 0 10px #ffffff,
            0 0 20px #ffffff,
            0 0 30px #ffffff,
            0 0 40px #ffffff;
    }
            
    .section-heading {
        text-align: center;
        color: #000000;
        font-family: 'Archivo Black', sans-serif;
        font-size: 1.7rem;
        font-weight: normal;
        margin-top: 1.5rem;
        margin-bottom: 2rem;
        letter-spacing: 0.3px;
        text-shadow: 2px 4px 4px rgba(33, 53, 85, 0.2);
    }


    .description {
        text-align: center;
        max-width: 700px;
        margin: auto;
        color: #000000;
        font-size: 1.1rem;
        line-height: 1.6;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 500;
        padding-top: 0.5rem;
    }

    div[data-testid="stButton"] > button {
        background-color: #000000;
        color: white !important;
        font-weight: 600;
        border-radius: 15px;
        padding: 0.7rem 1.5rem;
        margin-top: 4.5rem;
        margin-bottom: 2.4rem;
        margin-left: 5.25rem;
        box-shadow: 2px 4px 7px rgba(62, 88, 121, 0.25);
        transition: all 0.3s ease-in-out;
        font-family: 'Segoe UI', sans-serif;
        border: none;
        outline: none;
        text-decoration: none !important;
    }
            
    @keyframes shimmer {
    0% {
        background-position: -200% 0;
        }
    100% {
            background-position: 200% 0;
        }
    }

    div[data-testid="stButton"] > button:hover {
        text-decoration: none !important;
        border: none !important;
        outline: none !important;
        position: relative;
        background-image: linear-gradient(
            110deg,
            #000000 40%,
            rgba(245, 239, 231, 0.2) 50%,
            #000000 60%
        );
        background-size: 200% 100%;
        animation: shimmer 1.6s infinite linear;
        transform: scale(1.07);
        box-shadow: 0 6px 14px rgba(33, 53, 85, 0.3);
        cursor: pointer;
        color: #F5EFE7 !important;
    }

    div[data-testid="stButton"] > button:focus,
    div[data-testid="stButton"] > button:active {
        color: #F5EFE7 !important;
        box-shadow: 0 6px 14px rgba(33, 53, 85, 0.3);
        text-decoration: none !important;
        border: none !important;
        outline: none !important;
    }
            
    div[data-testid="stButton"] > button:active {
        color: #000000 !important;
        transform: scale(0.97); /* <- Press effect */
        background-color: #1A2F45;
        box-shadow: 0 3px 6px rgba(33, 53, 85, 0.2);
        border: none !important;
        outline: none !important;
        text-decoration: none !important;
    } 
            
    div[data-testid="stFileUploader"] {
        background-color: #000000 !important;
        border: 2px #F5EFE7 !important;
        border-radius: 15px;
        padding: 1rem;
        margin-left: 1.2rem;
        color: #F5EFE7 !important;
        font-family: 'Segoe UI', sans-serif;
        box-shadow: 2px 4px 10px rgba(33, 53, 85, 0.2);
    }

    div[data-testid="stFileUploader"] label,
    div[data-testid="stFileUploader"] span,
    div[data-testid="stFileUploader"] p {
        color: #F5EFE7 !important;
        font-weight: 500;
        font-size: 1rem;
    }

    div[data-testid="stTextArea"] {
        background-color: #000000 !important;
        border: 2px #F5EFE7 !important;
        border-radius: 15px;
        padding: 1rem;
        margin-left: 1.1rem;
        color: #F5EFE7 !important;
        font-family: 'Segoe UI', sans-serif;
        box-shadow: 2px 4px 10px rgba(33, 53, 85, 0.2);
    }
    
    div[data-baseweb="textarea"] + div {
        display: none !important;
    }

    div[data-testid="stTextArea"] textarea {
        background-color: transparent !important;
        color: #000000 !important;
        font-size: 1rem !important;
        font-family: 'Segoe UI', sans-serif' !important;
        border: none !important;
        resize: vertical !important;
        outline: none !important;
    }
            
    div[data-testid="stTextArea"] label {
        color: #F5EFE7 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        font-family: 'Segoe UI', sans-serif !important;
        margin-bottom: 0.5rem !important;
    }
            
    div[data-testid="stTextArea"] label,
    div[data-testid="stTextArea"] span,
    div[data-testid="stTextArea"] p {
        color: #F5EFE7 !important;
        font-weight: 500 !important;
        font-size: 1rem !important;
        font-family: 'Segoe UI', sans-serif !important;
    }
        

    </style>
""", unsafe_allow_html=True)

if page == "home":

    st.markdown('<div class="main-title">GlowScore</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="description">
    GlowScore is your gentle guide to smarter skincare. <br>
    Upload a product label or type in ingredients — and uncover what each one really means for your skin.
    From clean beauty insights to hidden irritants, we help you glow with clarity and confidence. <br>
    GlowScore analyzes the 120+ most researched skincare ingredients to give you trusted, science-backed summaries.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("\U0001F4F7 Upload Image"):
            st.session_state.mode = "upload"

    with col2:
        if st.button("\U0001F4DD Type Ingredients"):
            st.session_state.mode = "manual"

    if st.session_state.mode == "upload":
        uploaded_file = st.file_uploader(
            "Upload your skincare label", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image_bytes = uploaded_file.read()
            encoded_image = base64.b64encode(image_bytes).decode()

            st.markdown(f"""
                <div style='text-align: center;'>
                    <img src='data:image/png;base64,{encoded_image}' width='350' style='border-radius: 15px; box-shadow: 0 4px 10px rgba(33, 53, 85, 0.15);margin-bottom: 2rem; margin-top: 1.5rem;' />
                </div>
            """, unsafe_allow_html=True)
            try:
                image = Image.open(uploaded_file)
                extracted_text = pytesseract.image_to_string(image)
                extracted_text = '\n'.join(
                    [line.strip() for line in extracted_text.splitlines() if line.strip()])
                cleaned_ingredients = clean_ingredients_with_gpt(
                    extracted_text)

                st.text_area(
                    label="Ingredients extracted from image:",
                    value=cleaned_ingredients,
                    height=80,
                    label_visibility="visible"
                )
                run_analysis(cleaned_ingredients)

                if "show_quiz" not in st.session_state:
                    st.session_state.show_quiz = False

                col1, col2, col3 = st.columns(
                    [0.6675, 2, 1])
                with col2:
                    if st.button("Still confused? Take a Skin Quiz for personalized advice"):
                        st.session_state.show_quiz = True
                if st.session_state.get("show_quiz", False):
                    left_col, main_col = st.columns(
                        [0.0098, 0.85])
                    with main_col:
                        with st.expander("Answer a few quick questions:", expanded=True):
                            skin_type = st.selectbox("What's your overall skin type?", [
                                "Dry", "Oily", "Combination", "Sensitive", "Normal"
                            ])

                            skin_sensitivity = st.select_slider("How sensitive is your skin usually?", [
                                "Not Sensitive", "Mildly Sensitive", "Very Sensitive"
                            ])

                            concerns = st.multiselect("Current skin concerns?", [
                                "Acne", "Redness", "Dark Spots", "Wrinkles",
                                "Dryness", "Oiliness", "Sensitivity", "Dullness", "Uneven Texture"
                            ])

                            allergies = st.text_input(
                                "Any known allergies? (optional)")
                            previous_reactions = st.text_input(
                                "Bad reactions to skincare products? (optional)")

                            routine_frequency = st.selectbox("How often do you plan to use this product?", [
                                "Once in a while", "2–3 times a week", "Daily", "Multiple times a day"
                            ])

                            is_treating_condition = st.radio("Currently treating any skin condition?", [
                                "No", "Yes – Acne", "Yes – Eczema", "Yes – Rosacea", "Yes – Other"
                            ])

                            other_condition = ""
                            if is_treating_condition == "Yes – Other":
                                other_condition = st.text_input(
                                    "Please specify your skin condition:")

                            full_condition = other_condition if is_treating_condition == "Yes – Other" else is_treating_condition
                            c1, c2, c3 = st.columns([0.825, 1, 1])
                            with c2:
                                if st.button("Submit"):
                                    st.session_state.quiz_answers = {
                                        "skin_type": skin_type,
                                        "skin_sensitivity": skin_sensitivity,
                                        "concerns": concerns,
                                        "allergies": allergies,
                                        "previous_reactions": previous_reactions,
                                        "routine_frequency": routine_frequency,
                                        "is_treating_condition": full_condition
                                    }

                                    result = analyze_ingredients(
                                        [i.strip().lower() for i in cleaned_ingredients.split(",") if i.strip()])
                                    st.session_state.result = result
                                    st.session_state.cleaned_text = cleaned_ingredients

                                    st.query_params["page"] = "results"

            except Exception as e:
                st.error(f"❌ Error processing image: {e}")

    elif st.session_state.mode == "manual":
        manual_input = st.text_area(
            label="Enter ingredients list here:",
            placeholder="e.g., Aqua, Glycerin, Niacinamide, Dimethicone, Parfum",
            height=80,
            label_visibility="visible",
            key="manual_ingredients"
        )

        if manual_input.strip():
            cleaned_manual = clean_ingredients_with_gpt(manual_input)

            st.text_area(
                label="Ingredients you input:",
                value=cleaned_manual,
                height=80,
                label_visibility="visible"
            )
            run_analysis(cleaned_manual)

            if "show_quiz" not in st.session_state:
                st.session_state.show_quiz = False

            col1, col2, col3 = st.columns(
                [0.6675, 2, 1])
            with col2:
                if st.button("Still confused? Take a Skin Quiz for personalized advice"):
                    st.session_state.show_quiz = True
            if st.session_state.get("show_quiz", False):
                left_col, main_col = st.columns(
                    [0.0098, 0.85])
                with main_col:
                    with st.expander("Answer a few quick questions:", expanded=True):
                        skin_type = st.selectbox("What's your overall skin type?", [
                            "Dry", "Oily", "Combination", "Sensitive", "Normal"
                        ])

                        skin_sensitivity = st.select_slider("How sensitive is your skin usually?", [
                            "Not Sensitive", "Mildly Sensitive", "Very Sensitive"
                        ])

                        concerns = st.multiselect("Current skin concerns?", [
                            "Acne", "Redness", "Dark Spots", "Wrinkles",
                            "Dryness", "Oiliness", "Sensitivity", "Dullness", "Uneven Texture"
                        ])

                        allergies = st.text_input(
                            "Any known allergies? (optional)")
                        previous_reactions = st.text_input(
                            "Bad reactions to skincare products? (optional)")

                        routine_frequency = st.selectbox("How often do you plan to use this product?", [
                            "Once in a while", "2–3 times a week", "Daily", "Multiple times a day"
                        ])

                        is_treating_condition = st.radio("Currently treating any skin condition?", [
                            "No", "Yes – Acne", "Yes – Eczema", "Yes – Rosacea", "Yes – Other"
                        ])

                        other_condition = ""
                        if is_treating_condition == "Yes – Other":
                            other_condition = st.text_input(
                                "Please specify your skin condition:")

                        full_condition = other_condition if is_treating_condition == "Yes – Other" else is_treating_condition
                        c1, c2, c3 = st.columns([0.825, 1, 1])
                        with c2:
                            if st.button("Submit"):
                                st.session_state.quiz_answers = {
                                    "skin_type": skin_type,
                                    "skin_sensitivity": skin_sensitivity,
                                    "concerns": concerns,
                                    "allergies": allergies,
                                    "previous_reactions": previous_reactions,
                                    "routine_frequency": routine_frequency,
                                    "is_treating_condition": full_condition
                                }

                                result = analyze_ingredients(
                                    [i.strip().lower() for i in cleaned_manual.split(",") if i.strip()])
                                st.session_state.result = result
                                st.session_state.cleaned_text = cleaned_manual

                                st.query_params["page"] = "results"

elif page == "results":
    result = st.session_state.get("result")
    quiz = st.session_state.get("quiz_answers")
    if not result:
        st.error("❌ No analysis result found.")
    else:
        show_final_results(st.session_state.cleaned_text, quiz)
