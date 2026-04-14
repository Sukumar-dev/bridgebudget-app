const currency = new Intl.NumberFormat("en-US", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0
});

const form = document.getElementById("budgetForm");
const debtList = document.getElementById("debtList");
const debtTemplate = document.getElementById("debtTemplate");
const addDebtButton = document.getElementById("addDebtButton");
const submitButton = document.getElementById("submitButton");
const savePlanButton = document.getElementById("savePlanButton");
const formStatus = document.getElementById("formStatus");
const saveStatus = document.getElementById("saveStatus");
const errorBox = document.getElementById("errorBox");
const resultsSection = document.getElementById("results");
const overviewGrid = document.getElementById("overviewGrid");
const actionPlan = document.getElementById("actionPlan");
const debtStrategy = document.getElementById("debtStrategy");
const resourceList = document.getElementById("resourceList");
const stressBadge = document.getElementById("stressBadge");
const previewStress = document.getElementById("previewStress");
const previewEssentials = document.getElementById("previewEssentials");
const previewDebt = document.getElementById("previewDebt");
const themeToggle = document.getElementById("themeToggle");

let lastPayload = null;
let lastAnalysis = null;

function getApiBase() {
  const configured = document
    .querySelector('meta[name="bridgebudget-api-base"]')
    ?.content.trim();

  if (configured) {
    return configured.replace(/\/$/, "");
  }

  if (window.location.protocol === "file:") {
    return "http://127.0.0.1:8000";
  }

  if (["127.0.0.1", "localhost"].includes(window.location.hostname) && window.location.port !== "8000") {
    return "http://127.0.0.1:8000";
  }

  return window.location.origin.replace(/\/$/, "");
}

function setTheme(theme) {
  document.body.dataset.theme = theme;
  localStorage.setItem("bridgebudget-theme", theme);
  themeToggle.textContent = theme === "dark" ? "Light mode" : "Dark mode";
}

function initializeTheme() {
  const stored = localStorage.getItem("bridgebudget-theme");
  const preferredDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  setTheme(stored || (preferredDark ? "dark" : "light"));
}

function addDebtRow(values = {}) {
  const fragment = debtTemplate.content.cloneNode(true);
  const row = fragment.querySelector(".debt-row");
  row.querySelector('[name="debt_name"]').value = values.name || "";
  row.querySelector('[name="debt_balance"]').value = values.balance || "";
  row.querySelector('[name="debt_apr"]').value = values.apr || "";
  row.querySelector('[name="debt_minimum"]').value = values.minimum_payment || "";
  row.querySelector(".remove-debt").addEventListener("click", () => {
    row.remove();
    updatePreview();
  });

  row.querySelectorAll("input").forEach((input) => {
    input.addEventListener("input", updatePreview);
  });

  debtList.appendChild(fragment);
}

function getNumberValue(name) {
  return Number.parseFloat(form.elements[name].value) || 0;
}

function showError(message) {
  errorBox.textContent = message;
  errorBox.classList.remove("hidden");
}

function hideError() {
  errorBox.textContent = "";
  errorBox.classList.add("hidden");
}

function updatePreview() {
  const essentials =
    getNumberValue("housing") +
    getNumberValue("utilities") +
    getNumberValue("food") +
    getNumberValue("transport") +
    getNumberValue("healthcare") +
    getNumberValue("childcare") +
    getNumberValue("insurance") +
    getNumberValue("other_essentials");

  const debtMinimums = Array.from(debtList.querySelectorAll(".debt-row")).reduce((sum, row) => {
    return sum + (Number.parseFloat(row.querySelector('[name="debt_minimum"]').value) || 0);
  }, 0);

  const income = getNumberValue("monthly_income");
  const totalNeeds = essentials + debtMinimums;
  const gap = income - totalNeeds;

  previewEssentials.textContent = currency.format(essentials);
  previewDebt.textContent = currency.format(debtMinimums);
  previewStress.textContent =
    gap < 0 ? "Projected shortfall" : gap < 250 ? "Little margin" : "Some breathing room";
}

function collectDebts() {
  return Array.from(debtList.querySelectorAll(".debt-row"))
    .map((row) => ({
      name: row.querySelector('[name="debt_name"]').value.trim(),
      balance: Number.parseFloat(row.querySelector('[name="debt_balance"]').value) || 0,
      apr: Number.parseFloat(row.querySelector('[name="debt_apr"]').value) || 0,
      minimum_payment: Number.parseFloat(row.querySelector('[name="debt_minimum"]').value) || 0
    }))
    .filter((debt) => debt.name && debt.minimum_payment >= 0);
}

function validatePayload(payload) {
  const rawDebtRows = Array.from(debtList.querySelectorAll(".debt-row")).map((row) => ({
    name: row.querySelector('[name="debt_name"]').value.trim(),
    balance: row.querySelector('[name="debt_balance"]').value.trim(),
    apr: row.querySelector('[name="debt_apr"]').value.trim(),
    minimum: row.querySelector('[name="debt_minimum"]').value.trim()
  }));

  if (!/^\d{5}$/.test(payload.location_zip)) {
    return "Please enter a valid 5-digit ZIP code.";
  }

  if (payload.monthly_income <= 0) {
    return "Monthly income must be greater than zero.";
  }

  if (payload.household_size < 1 || payload.household_size > 10) {
    return "Household size must be between 1 and 10.";
  }

  const incompleteDebt = rawDebtRows.find((row) => {
    const hasAnyValue = row.name || row.balance || row.apr || row.minimum;
    return hasAnyValue && (!row.name || !row.minimum);
  });

  if (incompleteDebt) {
    return "Each debt row needs at least a debt name and minimum payment, or it should be removed.";
  }

  if (payload.debts.some((debt) => !debt.name || debt.name.length < 2)) {
    return "Each debt entry needs a clear name.";
  }

  return "";
}

function buildPayload() {
  return {
    location_zip: form.elements.location_zip.value.trim(),
    household_size: Number.parseInt(form.elements.household_size.value, 10),
    monthly_income: getNumberValue("monthly_income"),
    savings: getNumberValue("savings"),
    housing: getNumberValue("housing"),
    utilities: getNumberValue("utilities"),
    food: getNumberValue("food"),
    transport: getNumberValue("transport"),
    healthcare: getNumberValue("healthcare"),
    childcare: getNumberValue("childcare"),
    insurance: getNumberValue("insurance"),
    other_essentials: getNumberValue("other_essentials"),
    debts: collectDebts()
  };
}

function clearNode(node) {
  while (node.firstChild) {
    node.removeChild(node.firstChild);
  }
}

function makeOverviewItem(label, value) {
  const item = document.createElement("div");
  item.className = "overview-item";

  const labelEl = document.createElement("span");
  labelEl.textContent = label;
  const valueEl = document.createElement("strong");
  valueEl.textContent = value;

  item.append(labelEl, valueEl);
  return item;
}

function renderList(items, className = "recommendation-list") {
  const list = document.createElement("ul");
  list.className = className;
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  });
  return list;
}

function renderActionPlan(plan) {
  clearNode(actionPlan);

  [["In the next 24 hours", plan.next_24_hours], ["Within 7 days", plan.next_7_days], ["Within 30 days", plan.next_30_days]].forEach(
    ([title, items]) => {
      const group = document.createElement("section");
      group.className = "timeline-group";
      const heading = document.createElement("h4");
      heading.textContent = title;
      group.append(heading, renderList(items));
      actionPlan.appendChild(group);
    }
  );
}

function renderDebtStrategy(strategy) {
  clearNode(debtStrategy);

  const summary = document.createElement("p");
  summary.textContent = strategy.summary;

  const focus = document.createElement("p");
  const focusLabel = document.createElement("strong");
  focusLabel.textContent = "Primary focus: ";
  focus.append(focusLabel, document.createTextNode(strategy.primary_focus));

  const method = document.createElement("p");
  const methodLabel = document.createElement("strong");
  methodLabel.textContent = "Recommended method: ";
  method.append(methodLabel, document.createTextNode(strategy.method));

  debtStrategy.append(summary, focus, method, renderList(strategy.steps, "strategy-list"));
}

function renderResources(resources) {
  clearNode(resourceList);

  resources.forEach((resource) => {
    const card = document.createElement("article");
    card.className = "resource-card";

    const title = document.createElement("h4");
    title.textContent = resource.name;

    const description = document.createElement("p");
    description.textContent = resource.description;

    const reason = document.createElement("p");
    const reasonLabel = document.createElement("strong");
    reasonLabel.textContent = "Why it fits: ";
    reason.append(reasonLabel, document.createTextNode(resource.reason));

    const link = document.createElement("a");
    link.href = resource.url;
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = "Visit resource";

    card.append(title, description, reason, link);
    resourceList.appendChild(card);
  });
}

function renderResults(analysis, payload) {
  resultsSection.classList.remove("hidden");
  clearNode(overviewGrid);

  const badgeClass =
    analysis.stress_level === "critical"
      ? "stress-critical"
      : analysis.stress_level === "tight"
        ? "stress-tight"
        : "stress-stable";

  stressBadge.className = `result-badge ${badgeClass}`;
  stressBadge.textContent = `${analysis.stress_level_label}: ${analysis.headline}`;

  overviewGrid.append(
    makeOverviewItem("Monthly gap / surplus", currency.format(analysis.monthly_gap)),
    makeOverviewItem("Essential coverage", `${analysis.essential_coverage_ratio}%`),
    makeOverviewItem("Savings runway", `${analysis.savings_runway_months} months`),
    makeOverviewItem("Debt minimums", currency.format(analysis.debt_minimum_total))
  );

  renderActionPlan(analysis.action_plan);
  renderDebtStrategy(analysis.debt_strategy);
  renderResources(analysis.resources);

  savePlanButton.disabled = false;
  saveStatus.textContent = "";
  lastPayload = payload;
  lastAnalysis = analysis;
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json"
    },
    ...options
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong while contacting the server.");
  }
  return data;
}

async function analyzeBudget(payload) {
  formStatus.textContent = "Analyzing your month...";
  submitButton.disabled = true;
  hideError();

  try {
    const data = await requestJson(`${getApiBase()}/api/analyze`, {
      method: "POST",
      body: JSON.stringify(payload)
    });

    formStatus.textContent = "Analysis ready.";
    renderResults(data, payload);
  } catch (error) {
    formStatus.textContent = "";
    showError(error.message);
  } finally {
    submitButton.disabled = false;
  }
}

async function savePlan() {
  if (!lastPayload) {
    return;
  }

  savePlanButton.disabled = true;
  saveStatus.textContent = "Saving your shareable plan...";

  try {
    const data = await requestJson(`${getApiBase()}/api/plans`, {
      method: "POST",
      body: JSON.stringify(lastPayload)
    });

    lastAnalysis = data.analysis;
    saveStatus.textContent = "Saved. ";
    const shareLink = document.createElement("a");
    shareLink.href = data.share_url;
    shareLink.target = "_blank";
    shareLink.rel = "noopener noreferrer";
    shareLink.textContent = "Open your share link";
    saveStatus.appendChild(shareLink);
  } catch (error) {
    saveStatus.textContent = error.message;
  } finally {
    savePlanButton.disabled = false;
  }
}

async function loadSharedPlan() {
  const planId = new URLSearchParams(window.location.search).get("plan");
  if (!planId) {
    return;
  }

  formStatus.textContent = "Loading shared plan...";

  try {
    const data = await requestJson(`${getApiBase()}/api/plans/${encodeURIComponent(planId)}`);
    const payload = data.input;
    form.elements.location_zip.value = payload.location_zip;
    form.elements.household_size.value = payload.household_size;
    form.elements.monthly_income.value = payload.monthly_income;
    form.elements.savings.value = payload.savings;
    form.elements.housing.value = payload.housing;
    form.elements.utilities.value = payload.utilities;
    form.elements.food.value = payload.food;
    form.elements.transport.value = payload.transport;
    form.elements.healthcare.value = payload.healthcare;
    form.elements.childcare.value = payload.childcare;
    form.elements.insurance.value = payload.insurance;
    form.elements.other_essentials.value = payload.other_essentials;

    clearNode(debtList);
    (payload.debts || []).forEach((debt) => addDebtRow(debt));
    if ((payload.debts || []).length === 0) {
      addDebtRow();
    }

    updatePreview();
    renderResults(data.analysis, payload);
    formStatus.textContent = "Shared plan loaded.";
  } catch (error) {
    formStatus.textContent = "";
    showError(error.message);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  hideError();
  const payload = buildPayload();
  const validationMessage = validatePayload(payload);

  if (validationMessage) {
    showError(validationMessage);
    return;
  }

  await analyzeBudget(payload);
});

savePlanButton.addEventListener("click", savePlan);
addDebtButton.addEventListener("click", () => addDebtRow());
themeToggle.addEventListener("click", () => {
  const nextTheme = document.body.dataset.theme === "dark" ? "light" : "dark";
  setTheme(nextTheme);
});

form.querySelectorAll("input").forEach((input) => input.addEventListener("input", updatePreview));

initializeTheme();
addDebtRow({
  name: "Credit card",
  balance: 2800,
  apr: 27.9,
  minimum_payment: 95
});
updatePreview();
loadSharedPlan();
