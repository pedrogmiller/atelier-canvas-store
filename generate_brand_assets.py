from agents.brand_identity_agent import brand_identity_agent

if __name__ == "__main__":
    concepts = brand_identity_agent.propose_brand_names()
    print(f"Loaded {len(concepts)} high-credibility brand concepts.")
    for idx, c in enumerate(concepts, 1):
        print(f"{idx}. {c.name} | Tagline: '{c.tagline}' | Domains: {', '.join(c.domains)}")
    
    # Generate suite for primary concept
    res = brand_identity_agent.generate_complete_brand_suite(concepts[0])
    print("\nBrand suite generated successfully:")
    for k, v in res.items():
        print(f"  - {k}: {v}")
