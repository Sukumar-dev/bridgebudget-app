RESOURCE_LIBRARY = [
    {
        "name": "211",
        "description": "Connects users to local food, housing, and crisis-support services.",
        "url": "https://www.211.org/",
        "tags": {"critical", "housing", "food", "utilities"},
    },
    {
        "name": "Benefits.gov",
        "description": "Federal portal for public-benefit programs and eligibility guidance.",
        "url": "https://www.benefits.gov/",
        "tags": {"critical", "tight", "food", "healthcare", "family"},
    },
    {
        "name": "FindHelp",
        "description": "Search for local help with food, housing, transit, and bill support.",
        "url": "https://www.findhelp.org/",
        "tags": {"critical", "tight", "housing", "food", "utilities", "transport"},
    },
    {
        "name": "LIHEAP",
        "description": "Energy-bill and utility-assistance program for eligible households.",
        "url": "https://www.acf.hhs.gov/ocs/programs/liheap",
        "tags": {"critical", "tight", "utilities"},
    },
    {
        "name": "SNAP",
        "description": "Nutrition support that can lower food pressure in tight months.",
        "url": "https://www.fns.usda.gov/snap/supplemental-nutrition-assistance-program",
        "tags": {"critical", "tight", "food", "family"},
    },
    {
        "name": "WIC",
        "description": "Nutrition support for pregnant people, infants, and young children.",
        "url": "https://www.fns.usda.gov/wic",
        "tags": {"critical", "tight", "food", "family"},
    },
    {
        "name": "Medicaid",
        "description": "Healthcare coverage support for eligible low-income households.",
        "url": "https://www.medicaid.gov/",
        "tags": {"critical", "tight", "healthcare", "family"},
    },
    {
        "name": "NFCC",
        "description": "Nonprofit credit-counseling network for debt and hardship planning.",
        "url": "https://www.nfcc.org/",
        "tags": {"tight", "stable", "debt"},
    },
    {
        "name": "Consumer Financial Protection Bureau",
        "description": "Trusted guides on debt, budgeting, and dealing with lenders or collectors.",
        "url": "https://www.consumerfinance.gov/consumer-tools/",
        "tags": {"tight", "stable", "debt", "budget"},
    },
    {
        "name": "CareerOneStop",
        "description": "Job-search, training, and wage tools for households needing income recovery.",
        "url": "https://www.careeronestop.org/",
        "tags": {"critical", "tight", "income"},
    },
]


def select_resources(stress_level: str, category_tags: set[str]) -> list[dict]:
    desired_tags = {stress_level, *category_tags}
    prioritized = []

    for resource in RESOURCE_LIBRARY:
        overlap = resource["tags"].intersection(desired_tags)
        if overlap:
            prioritized.append((len(overlap), resource))

    prioritized.sort(key=lambda item: item[0], reverse=True)

    selected = []
    for _, resource in prioritized:
        reason_parts = []
        if "housing" in category_tags and "housing" in resource["tags"]:
            reason_parts.append("it can help protect housing stability")
        if "utilities" in category_tags and "utilities" in resource["tags"]:
            reason_parts.append("it may reduce utility pressure")
        if "food" in category_tags and "food" in resource["tags"]:
            reason_parts.append("it can lower food spending quickly")
        if "healthcare" in category_tags and "healthcare" in resource["tags"]:
            reason_parts.append("it may help keep healthcare affordable")
        if "debt" in category_tags and "debt" in resource["tags"]:
            reason_parts.append("it offers debt and hardship guidance")
        if "income" in category_tags and "income" in resource["tags"]:
            reason_parts.append("it supports income recovery")

        selected.append(
            {
                "name": resource["name"],
                "description": resource["description"],
                "url": resource["url"],
                "reason": ", ".join(reason_parts) if reason_parts else "it matches your current financial pressure",
            }
        )

        if len(selected) == 6:
            break

    return selected
