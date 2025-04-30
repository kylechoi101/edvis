import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# — 1) Load and reshape Green Bonds data —
bonds = pd.read_csv("Green_Bonds.csv")
us_bonds = bonds[bonds["Country"] == "United States"]
year_cols_bonds = [c for c in us_bonds.columns if c.startswith("F")]
bonds_long = us_bonds.melt(
    id_vars=["Country","ISO2","ISO3","Indicator","Unit"],
    value_vars=year_cols_bonds,
    var_name="Year",
    value_name="Issuance_Billion_USD"
)
bonds_long["Year"] = bonds_long["Year"].str[1:].astype(int)
bonds_by_year = bonds_long[["Year","Issuance_Billion_USD"]]

# — 2) Load and reshape Disasters data —
disasters = pd.read_csv("14_Climate-related_Disasters_Frequency.csv")
us_disasters = disasters[disasters["Country"] == "United States"]
year_cols = [c for c in us_disasters.columns if c.isdigit()]
disasters_long = us_disasters.melt(
    id_vars=["Country","ISO2","ISO3","Indicator","Unit"],
    value_vars=year_cols,
    var_name="Year",
    value_name="Disaster_Count"
)
disasters_long["Year"] = disasters_long["Year"].astype(int)

# keep only “Number of Disasters”
mask = disasters_long["Indicator"].str.contains("Number of Disasters")
disasters_nd = disasters_long[mask].copy()

# pull out subtype after last “: ”
disasters_nd["Disaster_Type"] = (
    disasters_nd["Indicator"]
      .str.rsplit(": ", n=1)
      .str[-1]
)

# aggregate by Year & Type
disasters_by_type = (
    disasters_nd
    .groupby(["Year","Disaster_Type"], as_index=False)
    ["Disaster_Count"]
    .sum()
)

# pivot so each Disaster_Type is its own column
disaster_pivot = (
    disasters_by_type
    .pivot(index="Year", columns="Disaster_Type", values="Disaster_Count")
    .reset_index()
)

# — 3) Merge bonds + disasters, filter, and drop NaNs —
df_full = pd.merge(
    bonds_by_year,
    disaster_pivot,
    on="Year",
    how="inner"
).dropna()
df_full = df_full[df_full["Year"] > 2011]

# — 4) Plot —
offset = df_full.Issuance_Billion_USD.max() * 0.6

fig, ax = plt.subplots(figsize=(10, 4))

#  ► Green Bond issuance
line1, = ax.plot(
    df_full.Year,
    df_full.Issuance_Billion_USD,
    color="green",
    marker="o",
    linewidth=2,
    label="Issuance of Green Bond"
)

#  ► Wildfire count + offset
line2, = ax.plot(
    df_full.Year,
    df_full.Wildfire + offset,
    color="red",
    marker="s",
    linewidth=2,
    label="Disaster Level Wildfire Count"
)



ax.set_xlabel("Year")
ax.set_ylabel("Billions of Dollars")
# — 5) Custom legend with mixed font sizes —
blank = Line2D([], [], linestyle="", linewidth=0)

handles = [line1, line2, blank, blank]
labels = [
    "Issuance of Green Bond",
    "'Disaster' Level Wildfire Count",
    "  - Deaths >= 10",
    "  - Affected >= 100",
]

leg = ax.legend(handles, labels, loc="upper left", frameon=False)

# make the last two labels smaller
for txt in leg.get_texts()[:2]:
    txt.set_fontsize(15)
for txt in leg.get_texts()[2:]:
    txt.set_fontsize(11)

fig.suptitle(
    "US Issuance of Green Bond and Wildfire", 
    x=0.5,   # center
    y=0.93,  # almost at the very top of the figure
    fontsize=20,
    fontweight='bold'
)
plt.tight_layout()
plt.savefig("plot.png", dpi=300, bbox_inches="tight")
plt.show()
