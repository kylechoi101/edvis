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
)
df_full['ROI'] = df_full.Issuance_Billion_USD / df_full.Wildfire

# Option B: wildfires averted per $1B issuance
# first calculate year-over-year change in wildfires
df_full['ΔWildfire'] = df_full.Wildfire.shift(1) - df_full.Wildfire
# then ROI = # wildfires averted per $1B
df_full['ROI_averted'] = df_full['ΔWildfire'] / df_full.Issuance_Billion_USD

# drop the first row (NaN in shift) if you use ΔWildfire
df_full = df_full.dropna(subset=['ROI', 'ROI_averted'])
df_full = df_full[df_full['Year'] > 2014]
df_full = df_full[df_full['Year'] < 2021]

fig, ax1 = plt.subplots(figsize=(10,6))

# area for Issuance
ax1.fill_between(df_full.Year,
                 df_full.Issuance_Billion_USD,
                 color="#2ECC71", alpha=0.5,
                 label="Green Bond")

# area for Wildfire
ax1.fill_between(df_full.Year,
                 df_full.Wildfire *5,
                 color="#d73027", alpha=0.5,
                 label="Wildfire Count")

ax1.set_xlabel("Year")
ax1.set_ylabel("Billions of Dollars")
ax1.margins(x=0, y =0)

ax1.grid(True, linestyle="--", alpha=0.3)

# — twin axis just for ROI line —
ax2 = ax1.twinx()
ax2.plot(df_full.Year,
         df_full.ROI,
         color="steelblue",
         linewidth=2,
         label="ROI")
ax2.spines['right'].set_visible(False)
ax2.tick_params(axis='y',       # affecting the y‐axis…
                which='both',   # both major and minor ticks
                left=False,     # turn off ticks on left (none exist)
                right=False,    # turn off ticks on right
                labelright=False)  # turn off labels on right

# (you can also hide any leftover ticks via)
ax2.set_yticks([])

# — combine legends —
handles1, labels1 = ax1.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(handles1 + handles2,
           labels1 + labels2,
           loc="upper left",
           frameon=False)

# … your plotting code …

# leave extra space at the top
fig.subplots_adjust(top=0.80)

# main title: bigger & outside
fig.suptitle(
    "Green Bonds Effect on Wildfire", 
    x=0.5,   # center
    y=0.99,  # almost at the very top of the figure
    fontsize=24,
    fontweight='bold'
)

# subtitle: bigger & just below the title
fig.text(
    0.5,                     # x center
    0.91,                    # just under the title
    "Return on Investment (ROI) as metric",
    ha='center', 
    va='center',
    fontsize=16,
    color='gray'
)

plt.tight_layout()
plt.savefig("pro_with_roi.png", dpi=300, bbox_inches="tight")
plt.show()
