from agents.brand_identity_agent import BrandConcept, brand_identity_agent

concept = BrandConcept(
    name="Oak Print Studio",
    tagline="Museum Art & Solid Wood Framing",
    domains=["oakprintstudio.com", "www.oakprintstudio.com"],
    brand_story="Oak Print Studio crafts museum-grade contemporary wall art encased in sustainably harvested solid oak and pine wood frames. Printed on 250 gsm archival paper with 72h local delivery across 32 countries.",
    simplicity_credibility_rationale="'Oak Print Studio' conveys bespoke architectural craftsmanship, European gallery curation, and archival permanence.",
    aesthetic_focus="Japandi, Bauhaus, Antique Botanical, Scandinavian Modern, French Riviera",
    recommended_social_handles={
        "gmail": "oakprintstudio.art@gmail.com",
        "pinterest": "@oakprintstudio",
        "tiktok": "@oakprintstudio",
        "instagram": "@oakprintstudio.art"
    },
    palette=["#1D1B18", "#F7F4EE", "#B8834E", "#E3DCCF", "#40684A"]
)

res = brand_identity_agent.generate_complete_brand_suite(concept)
print("Oak Print Studio Brand Suite Generated Successfully!")
