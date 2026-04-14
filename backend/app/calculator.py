from __future__ import annotations

from math import ceil

from app.resources import select_resources


def round_money(value: float) -> float:
    return round(value, 2)


def determine_stress_level(monthly_gap: float, essential_coverage_ratio: float, savings_runway_months: float) -> tuple[str, str, str]:
    if monthly_gap < 0 or essential_coverage_ratio < 100:
        return (
            "critical",
            "Critical month",
            "Your current income does not safely cover essentials and minimum debt payments.",
        )

    if monthly_gap < 250 or savings_runway_months < 1:
        return (
            "tight",
            "Tight month",
            "You can cover the month, but you have very little buffer for a surprise cost.",
        )

    return (
        "stable",
        "Stable month",
        "You are currently covering essentials with some room to strengthen savings and debt payoff.",
    )


def build_recommendations(payload: dict, monthly_gap: float, debt_minimum_total: float, stress_level: str) -> tuple[list[str], set[str]]:
    recommendations: list[str] = []
    tags: set[str] = {"budget"}

    income = payload["monthly_income"]
    housing_ratio = payload["housing"] / income if income else 0
    food_ratio = payload["food"] / income if income else 0
    utility_ratio = payload["utilities"] / income if income else 0

    if housing_ratio > 0.4:
        recommendations.append("Housing is taking more than 40% of income, so protect rent or mortgage first and explore hardship options early.")
        tags.add("housing")

    if food_ratio > 0.18:
        recommendations.append("Food costs are relatively high for your income, so grocery assistance or meal planning support could free up cash quickly.")
        tags.add("food")

    if utility_ratio > 0.08:
        recommendations.append("Utility costs are high enough to justify checking for utility hardship and energy-assistance programs.")
        tags.add("utilities")

    if payload["healthcare"] > 0:
        tags.add("healthcare")

    if payload["childcare"] > 0 or payload["household_size"] > 2:
        tags.add("family")

    if debt_minimum_total > 0:
        tags.add("debt")
        debt_ratio = debt_minimum_total / income if income else 0
        if debt_ratio > 0.15:
            recommendations.append("Debt minimums are consuming a meaningful share of income, so hardship calls or nonprofit counseling could help protect cash flow.")

    if monthly_gap < 0:
        tags.add("income")
        recommendations.append("Because the month is short, pause nonessential spending and focus first on housing, utilities, food, transport, and healthcare.")

    if stress_level == "stable":
        recommendations.append("Use your monthly breathing room to build one month of emergency savings before increasing lifestyle spending.")

    return recommendations, tags


def build_action_plan(payload: dict, monthly_gap: float, recommendations: list[str], stress_level: str) -> dict:
    next_24_hours = [
        "List the exact due dates for rent, utilities, debt minimums, and any medical bills.",
        "Protect the essentials first: housing, utilities, food, transport, and healthcare.",
        "Turn off or pause any discretionary subscriptions or nonessential recurring charges.",
    ]

    next_7_days = [
        "Call creditors or service providers before a missed payment and ask about hardship options, payment plans, or due-date changes.",
        "Use a benefits screener or local support directory to reduce near-term food, utility, or healthcare pressure.",
        "Create a cash calendar for the rest of the month so your most urgent bills have a clear order.",
    ]

    next_30_days = [
        "Track the next month of spending against this plan and update numbers as soon as income or bills change.",
        "If debt is still crowding out essentials, contact a nonprofit credit counselor for a structured review.",
        "Build a starter emergency buffer so one surprise bill does not force new debt.",
    ]

    if monthly_gap < 0:
        next_24_hours.append("If cash will not cover essentials, contact 211 or a local support network today rather than waiting for accounts to become delinquent.")
        next_7_days.append("Look for temporary income recovery options such as extra shifts, contract work, or workforce-support services.")

    if payload["savings"] == 0 and stress_level != "critical":
        next_30_days.append("Set up an automatic transfer, even a small one, toward a starter emergency fund.")

    if recommendations:
        next_7_days.append(recommendations[0])

    return {
        "next_24_hours": next_24_hours,
        "next_7_days": next_7_days,
        "next_30_days": next_30_days,
    }


def build_debt_strategy(payload: dict, monthly_gap: float) -> dict:
    debts = payload["debts"]
    if not debts:
        return {
            "summary": "You did not enter any debt minimums, so the main focus is keeping essential costs sustainable and building savings resilience.",
            "primary_focus": "Stabilize essentials and grow emergency savings.",
            "method": "Cash buffer first",
            "steps": [
                "Cover core living costs consistently.",
                "Build a small emergency fund to reduce future borrowing.",
                "Review any informal debts or irregular bills monthly."
            ],
        }

    highest_apr = max(debts, key=lambda debt: debt["apr"])
    smallest_balance = min(debts, key=lambda debt: debt["balance"])

    if monthly_gap <= 0:
        return {
            "summary": "Because you are short this month, protecting cash flow matters more than aggressive payoff.",
            "primary_focus": f"Keep minimums current where possible and ask for hardship help on {highest_apr['name']}.",
            "method": "Minimums plus hardship outreach",
            "steps": [
                "Keep essentials funded before making extra debt payments.",
                f"Contact the lender for {highest_apr['name']} and ask about a hardship plan, lower payment, or fee waiver.",
                "Avoid taking on new high-interest debt to solve a recurring monthly gap.",
            ],
        }

    return {
        "summary": "You have some room above minimums, so direct extra cash where it reduces future interest fastest.",
        "primary_focus": f"After minimums, pay extra toward {highest_apr['name']}.",
        "method": "Debt avalanche with a quick-win check",
        "steps": [
            "Keep all minimums current to avoid penalties.",
            f"Put any extra payment toward {highest_apr['name']} because it has the highest APR.",
            f"If motivation matters more right now, consider clearing {smallest_balance['name']} first as a quick win.",
        ],
    }


def analyze_budget(payload: dict) -> dict:
    essentials_total = round_money(
        payload["housing"]
        + payload["utilities"]
        + payload["food"]
        + payload["transport"]
        + payload["healthcare"]
        + payload["childcare"]
        + payload["insurance"]
        + payload["other_essentials"]
    )
    debt_minimum_total = round_money(sum(item["minimum_payment"] for item in payload["debts"]))
    total_needed = round_money(essentials_total + debt_minimum_total)
    monthly_gap = round_money(payload["monthly_income"] - total_needed)
    essential_coverage_ratio = round((payload["monthly_income"] / essentials_total) * 100, 1) if essentials_total else 100.0
    savings_runway_months = round(payload["savings"] / essentials_total, 1) if essentials_total else 0.0
    recommended_buffer = round_money(essentials_total)

    stress_level, stress_level_label, headline = determine_stress_level(
        monthly_gap, essential_coverage_ratio, savings_runway_months
    )

    recommendations, category_tags = build_recommendations(
        payload, monthly_gap, debt_minimum_total, stress_level
    )
    action_plan = build_action_plan(payload, monthly_gap, recommendations, stress_level)
    debt_strategy = build_debt_strategy(payload, monthly_gap)
    resources = select_resources(stress_level, category_tags)

    if not resources:
        resources = select_resources(stress_level, {"budget"})

    debt_load_ratio = round((debt_minimum_total / payload["monthly_income"]) * 100, 1) if payload["monthly_income"] else 0.0
    savings_gap = max(recommended_buffer - payload["savings"], 0)
    months_to_buffer = ceil(savings_gap / max(monthly_gap, 1)) if monthly_gap > 0 and savings_gap > 0 else 0

    return {
        "stress_level": stress_level,
        "stress_level_label": stress_level_label,
        "headline": headline,
        "monthly_gap": monthly_gap,
        "essential_total": essentials_total,
        "debt_minimum_total": debt_minimum_total,
        "total_needed": total_needed,
        "essential_coverage_ratio": essential_coverage_ratio,
        "savings_runway_months": savings_runway_months,
        "recommended_buffer": recommended_buffer,
        "debt_load_ratio": debt_load_ratio,
        "months_to_buffer": months_to_buffer,
        "recommendations": recommendations,
        "action_plan": action_plan,
        "debt_strategy": debt_strategy,
        "resources": resources,
    }
