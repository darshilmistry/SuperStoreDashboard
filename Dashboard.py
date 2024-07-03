import pandas as pd
import panel as pn
import matplotlib.pyplot as plt


data = pd.read_csv("salesData.csv")
data["month"] = data["Date"].str.slice(0, 1)
monthMap = {
    "1": "January",
    "2": "February",
    "3": "March",
}
data["month"] = data["month"].map(monthMap)

month_order = ["January", "February", "March"]

data["month"] = pd.Categorical(data["month"], categories=month_order, ordered=True)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# SideBar

logo = pn.pane.Image("store.png", sizing_mode="scale_width")
text_content = """
The growth of supermarkets in most populated cities is increasing and market competition is also high. The dataset consists of historical sales data from a supermarket company recorded across 3 different branches over 3 months. 
Predictive data analytics methods can be easily applied with this dataset.
"""

DataInfo = pn.pane.Markdown(
    text_content,
    styles={"text-align": "justify", "font-size": "16pt", "word-wrap": "break-word"},
)

BranchInfo = pn.pane.Markdown(
    """
## Store Locations
- Branch A, Yangon
- Branch B, Mandalay
- Branch C, Naypyitaw

""",
    styles={"font-size": "16pt"},
)

sideBar = pn.Column(
    logo,
    DataInfo,
    BranchInfo,
    sizing_mode="stretch_height",
    width=320,
    styles={"background-color": "#DADDE2", "padding": "6px"},
)

# -------------------------------------------------------------------------------------------------------------------------
# Revenue Secction

EconomicsHeading = pn.pane.Str(
    "Store Economics",
    styles={
        "font-size": "50px",
        "margin-left": "15px",
        "font-weight": "bold",
    },
)

RevenueAmount = pn.Column(
    pn.indicators.Number(
        name="Net Revenue",
        value=data["gross income"].sum().round(-2) / 1000,
        default_color="white",
        format="${value}k",
    ),
    styles={
        "background-color": "#8685EF",
        "padding": "3px",
        "border-radius": "10px",
        "margin-left": "10px",
    },
    height_policy="max",
    width_policy="min",
)

PurchaseMean = pn.Column(
    pn.indicators.Number(
        name="Mean Billing value",
        value=int(data["Total"].median()),
        default_color="white",
        format="${value}",
    ),
    styles={
        "background-color": "#8685EF",
        "padding": "3px",
        "margin-left": "15px",
        "border-radius": "10px",
    },
    height_policy="max",
)

GrossIncomeMean = pn.Column(
    pn.indicators.Number(
        name="Mean gross income",
        value=int(data["gross income"].median()),
        default_color="white",
        format="${value}",
    ),
    styles={
        "background-color": "#8685EF",
        "padding": "3px",
        "margin-left": "15px",
        "border-radius": "10px",
    },
    height_policy="max",
)

# ------------------------------------------------------------------------------------------------------
# Product Stats (Part 1)

colors = {
    "Electronic accessories": "#0077FF",
    "Fashion accessories": "#FF6F61",
    "Food and beverages": "#B5AC49",
    "Health and beauty": "#FFDAB9",
    "Home and lifestyle": "#008080",
    "Sports and travel": "#FF5733",
}

data["Product line"] = pd.Categorical(
    data["Product line"],
    categories=[
        "Food and beverages",
        "Sports and travel",
        "Electronic accessories",
        "Fashion accessories",
        "Home and lifestyle",
        "Health and beauty",
    ],
    ordered=True,
)

product_gross = data.groupby("Product line")["gross income"].sum().reset_index()
fig, ax = plt.subplots(figsize=(3, 3))
ax.bar(
    product_gross["Product line"],
    product_gross["gross income"],
    color=[colors[line] for line in product_gross["Product line"]],
)
ax.set_xticks([])
ax.set_xticklabels([])
ax.tick_params(axis="y", labelsize=8)
ax.set_title("Net Revenue from differnet Product lines", fontsize=15, loc="left")
fig.patch.set_facecolor("#B1BDC5")

legend_handles = []

for line in product_gross["Product line"]:
    legend_handles.append(plt.Rectangle((0, 0), 1, 1, color=colors[line], label=line))

legend = ax.legend(
    handles=legend_handles,
    title="<---Product Lines--->",
    bbox_to_anchor=(2.01, 0.8),
    loc="upper right",
)

plot_pane = pn.pane.Matplotlib(fig, tight=True)
product_gross_layout = pn.Column(
    plot_pane, sizing_mode="stretch_width", styles={"margin-top": "8px"}
)


# -------------------------------------------------------------------------------------------------------------
# Revenue Section (Continued)


TimeFrameSelector = pn.widgets.Select(
    options=["January", "February", "March"],
    styles={"font-size": "20pt"},
)


def update_sales(event):
    selected_month = event.new
    filtered_data = data[data["month"] == selected_month]
    MonthlySale.value = (
        filtered_data["Total"].dropna().drop(columns="month", axis=0).sum() / 1000
    ).round(2)
    MonthlyOrders.value = filtered_data["Total"].count()
    MonthlyRatings.value = (
        filtered_data["gross income"].dropna().drop(columns="month", axis=0).sum()
        / 1000
    ).round(2)


MonthlyOrders = pn.indicators.Number(
    name="Orders",
    format="{value}",
    value=data["Total"]
    .where(data["month"] == "January")
    .dropna()
    .drop(columns="month", axis=0)
    .count(),
    styles={
        "background-color": "#FAF8FF",
        "font-size": "24pt",
        "padding": "3px 10px",
        "border-radius": "10px",
    },
)

MonthlySale = pn.indicators.Number(
    name="Total Sales",
    format="${value}k",
    value=(
        data["Total"]
        .where(data["month"] == TimeFrameSelector.value)
        .dropna()
        .drop(columns="month", axis=0)
        .sum()
        / 1000
    ).round(2),
    styles={
        "background-color": "#FAF8FF",
        "font-size": "24pt",
        "padding": "3px 10px",
        "border-radius": "10px",
    },
    width=310,
)


MonthlyRevenue = pn.indicators.Number(
    name="Gross Income",
    format="${value}k",
    value=(
        data["gross income"]
        .where(data["month"] == "January")
        .dropna()
        .drop(columns="month", axis=0)
        .sum()
        / 1000
    ).round(2),
    styles={
        "background-color": "#FAF8FF",
        "font-size": "24pt",
        "padding": "3px 10px",
        "border-radius": "10px",
    },
)

TimeFrameSelector.param.watch(update_sales, "value")

MonthlyStatsSH = pn.pane.Str(
    "Monthly Statistics", styles={"font-size": "28px", "font-weight": "bold"}
)

PDHeading = pn.pane.Str(
    "Product Line Statistics",
    styles={
        "font-size": "50px",
        "margin-left": "15px",
        "font-weight": "bold",
    },
)

MonthlyStats = pn.Column(
    pn.Row(MonthlyStatsSH, TimeFrameSelector),
    pn.Row(
        MonthlySale,
        MonthlyRevenue,
        MonthlyOrders,
    ),
    styles={"padding": "5px"},
    sizing_mode="stretch_width",
)

RevenueContent = pn.Column(
    EconomicsHeading,
    pn.Row(
        RevenueAmount,
        PurchaseMean,
        GrossIncomeMean,
        styles={"padding": "5px"},
    ),
    MonthlyStats,
    product_gross_layout,
    PDHeading,
    sizing_mode="stretch_width",
)

# -----------------------------------------------------------------------------------------------------------
# Customer Demographics

CDHeading = pn.pane.Str(
    "Customer Demographics",
    styles={
        "font-size": "50px",
        "margin-left": "15px",
        "font-weight": "bold",
    },
)

member_colors = ["#00c6c8", "#FFD700"]

fig, ax = plt.subplots(figsize=(2, 2))
customer_types = ["Normal", "Member"]
portions = [
    data["Invoice ID"].where(data["Customer type"] == "Normal").count(),
    data["Invoice ID"].where(data["Customer type"] == "Member").count(),
]

wedges, _, autotexts = ax.pie(
    portions, autopct="%1.1f%%", startangle=90, colors=member_colors
)
ax.axis("equal")

legend_handles = [
    plt.Rectangle((0, 0), 0, 0, color=wedges[i].get_facecolor())
    for i in range(len(customer_types))
]
ax.patch.set_alpha(0)
ax.legend(
    legend_handles,
    customer_types,
    title="Customer Type",
    bbox_to_anchor=(0.08, 0),
    loc="upper left",
)
fig.patch.set_facecolor("#ffffff00")

member_pie = pn.pane.Matplotlib(fig, tight=True)
member_pie_layout = pn.Column(member_pie, sizing_mode="stretch_width")

payment_colors = ["#ff6f61", "#2ca02c", "#fdc74f"]

payment_fig, payment_ax = plt.subplots(figsize=(2, 2))
payment_methods = ["Ewallet", "Cash", "Credit card"]
payment_stats = [
    data["Invoice ID"].where(data["Payment"] == "Ewallet").count(),
    data["Invoice ID"].where(data["Payment"] == "Cash").count(),
    data["Invoice ID"].where(data["Payment"] == "Credit card").count(),
]

wedges, _, autotexts = payment_ax.pie(
    payment_stats, autopct="%1.1f%%", startangle=90, colors=payment_colors
)
payment_ax.axis("equal")

gender_legend_handles = [
    plt.Rectangle((0, 0), 0, 0, color=wedges[i].get_facecolor())
    for i in range(len(payment_methods))
]

payment_ax.legend(
    gender_legend_handles,
    payment_methods,
    title="Payment Methods",
    bbox_to_anchor=(0.02, 0),
    loc="upper left",
)
payment_fig.patch.set_facecolor("#00000000")

Payment_pie = pn.pane.Matplotlib(payment_fig, tight=True)
Payment_pie_layout = pn.Column(
    Payment_pie,
    sizing_mode="stretch_width",
)

gender_colors = ["#0077ff", "#ff5733"]

Gender_fig, gender_ax = plt.subplots(figsize=(2, 2))
genders = ["Female", "Male"]
gender_stats = [
    data["Invoice ID"].where(data["Gender"] == "Female").count(),
    data["Invoice ID"].where(data["Gender"] == "Male").count(),
]

wedges, _, autotexts = gender_ax.pie(
    gender_stats, autopct="%1.1f%%", startangle=90, colors=gender_colors
)
gender_ax.axis("equal")

gender_legend_handles = [
    plt.Rectangle((0, 0), 0, 0, color=wedges[i].get_facecolor())
    for i in range(len(genders))
]

gender_ax.legend(
    gender_legend_handles,
    genders,
    title="Shoppers",
    bbox_to_anchor=(0.13, 0),
    loc="upper left",
)
Gender_fig.patch.set_facecolor("#00000000")

Gender_pie = pn.pane.Matplotlib(Gender_fig, tight=True)
Gender_pie_layout = pn.Column(
    Gender_pie,
    sizing_mode="stretch_width",
)


# -------------------------------------------------------------------------------------------------------
# Product Stats (Part 2)

data["Product line"] = pd.Categorical(
    data["Product line"],
    categories=[
        "Health and beauty",
        "Fashion accessories",
        "Home and lifestyle",
        "Sports and travel",
        "Food and beverages",
        "Electronic accessories",
    ],
    ordered=True,
)

product_quantity = data.groupby("Product line")["Quantity"].sum().reset_index()
fig, ax = plt.subplots(figsize=(6.5, 3))
ax.barh(
    product_quantity["Product line"],
    product_quantity["Quantity"],
    color=[colors[line] for line in product_quantity["Product line"]],
)
ax.set_yticks([])
ax.set_yticklabels([])
ax.tick_params(axis="y", labelsize=8)
ax.set_title("Units sold from differnet Product lines", fontsize=15)
fig.patch.set_facecolor("#B1BDC500")

plot_pane = pn.pane.Matplotlib(fig, tight=True)
product_quantity_layout = pn.Column(plot_pane, sizing_mode="stretch_width")

# ------------------------------------------------------------------------------------------------------------
# Customer Demographics (Continues)

CustomerDemographices = pn.Column(
    CDHeading,
    pn.Row(Payment_pie_layout, member_pie_layout, Gender_pie_layout),
    product_quantity_layout,
)

# -------------------------------------------------------------------------------------------------------
# Final Assembly

page_content = pn.Row(
    sideBar,
    RevenueContent,
    CustomerDemographices,
    styles={"background-color": "#B1BDC5"},
)

page_content.servable()
