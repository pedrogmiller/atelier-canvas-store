from agents.brand_identity_agent import BrandConcept, brand_identity_agent

concept = BrandConcept(
    name="Oak Prints",
    tagline="Museum Art in Handcrafted Wood",
    domains=["oakprints.com", "oakstudioart.com", "oakframed.com"],
    brand_story="Oak Prints crafts museum-grade contemporary wall art encased in sustainably harvested solid oak and pine wood frames. Printed on 250 gsm archival paper with 72h local delivery across 32 countries.",
    simplicity_credibility_rationale="'Oak Prints' is pure, punchy, and instantly establishes real solid wood craftsmanship and archival fine art printing.",
    aesthetic_focus="Japandi, Bauhaus, Antique Botanical, Scandinavian Modern, French Riviera",
    recommended_social_handles={
        "gmail": "oakprints.art@gmail.com",
        "pinterest": "@oakprints",
        "tiktok": "@oakprints",
        "instagram": "@oakprints.art"
    },
    palette=["#1D1B18", "#F7F4EE", "#B8834E", "#E3DCCF", "#40684A"]
)

res = brand_identity_agent.generate_complete_brand_suite(concept)
print("Oak Prints Brand Suite Generated:")
for k, v in res.items():
    print(f"  ✓ {k}: {v}")
