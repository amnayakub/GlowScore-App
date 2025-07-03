import json

# Load the ingredient database
with open("ingredient_data.json", "r", encoding="utf-8") as f:
    ingredient_db = json.load(f)

# Create a quick-access lookup dictionary
ingredient_lookup = {item["Ingredient"].lower(): item for item in ingredient_db}

def compute_ingredient_score(ingredient):
    score = ingredient["Safety_Score"]
    score += int(ingredient["Dry_Skin_Safe"])
    score += int(ingredient["Oily_Skin_Safe"])
    score += int(ingredient["Acne_Prone_Safe"])
    if ingredient["Comedogenic"]:
        score -= 1.5
    return round(min(max(score, 0), 10), 2)

def analyze_ingredients(input_ingredients):
    found = []
    missing = []
    dry_safe = oily_safe = acne_safe = total_score = comedogenic_count = 0

    for name in input_ingredients:
        key = name.strip().lower()
        if key in ingredient_lookup:
            data = ingredient_lookup[key]
            data = data.copy()  # don't overwrite the original
            data["GlowIngredientScore"] = compute_ingredient_score(data)
            found.append(data)
            total_score += data["Safety_Score"]
            dry_safe += int(data["Dry_Skin_Safe"])
            oily_safe += int(data["Oily_Skin_Safe"])
            acne_safe += int(data["Acne_Prone_Safe"])
            comedogenic_count += int(data["Comedogenic"])
        else:
            missing.append(name)

    total_found = len(found)
    if total_found == 0:
        glow_score = 0
    else:
        glow_score = round(total_score / total_found, 2)

    return {
        "found": found,
        "missing": missing,
        "glow_score": glow_score,
        "dry_safe_pct": round(dry_safe / total_found * 100) if total_found else 0,
        "oily_safe_pct": round(oily_safe / total_found * 100) if total_found else 0,
        "acne_safe_pct": round(acne_safe / total_found * 100) if total_found else 0,
        "comedogenic_count": comedogenic_count,
        "total_checked": total_found,
    }

# # Sample run
# if __name__ == "__main__":
#     sample_ingredients = [
#         "Niacinamide", "Glycerin", "retinol", "rose water", "cetearyl alcohol"
#     ]

#     result = analyze_ingredients(sample_ingredients)

#     print("\n🌟 Per-Ingredient Breakdown:")
#     for item in result["found"]:
#         print(f"\nIngredient: {item['Ingredient']}")
#         print(f"Description: {item['Description']}")
#         print(f"✅ Safe for: "
#               f"{'Dry ' if item['Dry_Skin_Safe'] else ''}"
#               f"{'Oily ' if item['Oily_Skin_Safe'] else ''}"
#               f"{'Acne-Prone' if item['Acne_Prone_Safe'] else ''}")
#         print(f"🔐 Comedogenic? {'Yes' if item['Comedogenic'] else 'No'}")
#         print(f"🔢 Safety Score: {item['Safety_Score']} / 10")
#         print(f"✨ GlowScore: {item['GlowIngredientScore']} / 10")

#     print("\n🚨 Missing Ingredients:")
#     for miss in result["missing"]:
#         print(f"❗️ {miss} — not in database.")

#     print("\n🔮 Whole Product Analysis:")
#     print(f"GlowScore: ⭐️ {result['glow_score']} / 10")
#     print(f"✅ {result['dry_safe_pct']}% ingredients safe for dry skin")
#     print(f"✅ {result['oily_safe_pct']}% ingredients safe for oily skin")
#     print(f"✅ {result['acne_safe_pct']}% ingredients safe for acne-prone skin")
#     print(f"❌ {result['comedogenic_count']} comedogenic ingredient(s)")
#     print(f"⚠️ {len(result['missing'])} ingredient(s) not found in database")
