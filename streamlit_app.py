import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ================================
# 💫 Titel och introduktion
# ================================
st.set_page_config(page_title="Diamantanalys", page_icon="💎", layout="centered")

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fascinate+Inline&display=swap" rel="stylesheet">
<style>
.caveat-rubrik, h1.custom-title {
  font-family: "Caveat", cursive !important;
  font-optical-sizing: auto;
  font-weight: 700;
  font-style: normal;
  color: #DAA520;
  font-size: 4.8em;
  margin-bottom: 0.1em;
}
</style>
<h1 class='custom-title caveat-rubrik'>Diamantanalys – Guldfynd</h1>
""", unsafe_allow_html=True)

st.markdown("""
Företaget Guldfynd överväger att sälja diamanter.  
Denna app visar insikter från analysen av över 50 000 diamanter.
""", unsafe_allow_html=True)

# ================================
# Läs in städad data
# ================================
@st.cache_data
def load_data():
    df = pd.read_csv("diamonds_clean.csv")
    return df[(df['x'] > 0) & (df['y'] > 0) & (df['z'] > 0)].copy()

df = load_data()

cut_order = ["Fair", "Good", "Very Good", "Premium", "Ideal"]
clarity_order = ["I1", "SI2", "SI1", "VS2", "VS1", "VVS2", "VVS1", "IF"]
color_order = list("JIHGFED")

df['cut'] = pd.Categorical(df['cut'], categories=cut_order, ordered=True)
df['clarity'] = pd.Categorical(df['clarity'], categories=clarity_order, ordered=True)
df['color'] = pd.Categorical(df['color'], categories=color_order, ordered=True)

# ================================
# Filter i sidomeny
# ================================
st.sidebar.image("guldfynd_logo.png", width=150, use_container_width=True)

st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("### Filtrera analysen")

selected_cut = st.sidebar.multiselect("Välj slipning (cut)", df['cut'].unique(), default=list(df['cut'].unique()))
selected_color = st.sidebar.multiselect("Välj färg", df['color'].unique(), default=list(df['color'].unique()))
selected_clarity = st.sidebar.multiselect("Välj klarhet", df['clarity'].unique(), default=list(df['clarity'].unique()))

price_range = st.sidebar.slider("Prisintervall (USD)", int(df['price'].min()), int(df['price'].max()), (1000, 10000))
carat_range = st.sidebar.slider("Karatintervall", float(df['carat'].min()), float(df['carat'].max()), (0.5, 2.0))

filtered_df = df[
    (df['price'] >= price_range[0]) & (df['price'] <= price_range[1]) &
    (df['carat'] >= carat_range[0]) & (df['carat'] <= carat_range[1]) &
    (df['cut'].isin(selected_cut)) &
    (df['color'].isin(selected_color)) &
    (df['clarity'].isin(selected_clarity))
].copy()

filtered_df['carat_group'] = pd.cut(filtered_df['carat'], bins=[0, 0.5, 1, 1.5, 2, 5],
                                    labels=['0-0.5', '0.5-1', '1-1.5', '1.5-2', '2-5'])

if filtered_df.empty:
    st.warning("🙁 Ingen diamant matchar dina val. Justera filtren till vänster.")
    st.stop()

st.info(f"Antal diamanter som matchar filtren: {len(filtered_df)}")
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.markdown("### 📊 Nyckeltal")
st.sidebar.metric("📈 Genomsnittspris", f"${int(filtered_df['price'].mean())}")
st.sidebar.metric("💎 Genomsnittlig carat", round(filtered_df['carat'].mean(), 2))
st.sidebar.markdown("<hr>", unsafe_allow_html=True)
st.sidebar.info("""
**Filtrera diamanterna**
Justera filtret för slipning, färg, klarhet, pris och carat för att anpassa analysen efter olika kundsegment eller prisklasser.
""")

# ================================
# Funktionsbaserade diagram
# ================================

def plot_price_distribution(df, ax):
    sns.histplot(
        df['price'],
        bins=10,
        color='gold',
        edgecolor='black',
        element='bars',
        shrink=0.9,
        ax=ax
    )
    ax.set_xlabel("Pris (USD)")
    ax.set_ylabel("Antal")
    yticks = ax.get_yticks()
    ax.set_yticks([int(y) for y in yticks if y == int(y)])
    ax.set_title("Prisfördelning för diamanter")

def plot_price_per_clarity(df, ax):
    avg_price_clarity = df.groupby('clarity', observed=True)['price'].mean().sort_values()
    avg_price_clarity.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_ylabel("Pris (USD)")
    ax.set_title("Genomsnittligt pris per klarhet")

def plot_price_per_color(df, ax):
    avg_price_color = df.groupby('color', observed=True)['price'].mean().sort_values()
    avg_price_color.plot(kind='bar', color='mediumseagreen', ax=ax)
    ax.set_ylabel("Pris (USD)")
    ax.set_title("Genomsnittligt pris per färg")

def plot_price_vs_carat(df, ax):
    clarities = df['clarity'].cat.categories if hasattr(df['clarity'], 'cat') else df['clarity'].unique()
    colors = plt.cm.tab10.colors  # Anpassa om du har fler än 10 klasser

    for i, clarity in enumerate(clarities):
        subset = df[df['clarity'] == clarity]
        ax.scatter(
            subset['carat'], subset['price'],
            alpha=0.4, s=15,
            color=colors[i % len(colors)],
            label=str(clarity)
        )
    ax.set_xlabel("Carat")
    ax.set_ylabel("Pris (USD)")
    ax.set_title("Pris vs Carat (färgad efter klarhet)")
    ax.legend(title='Clarity', bbox_to_anchor=(1.05, 1), loc='upper left')

def plot_corr_heatmap(df):
    base_cols = ['price', 'carat', 'depth', 'table', 'x', 'y', 'z']
    extra_cols = []
    if 'cut_encoded' in df.columns:
        extra_cols.append('cut_encoded')
    if 'clarity_encoded' in df.columns:
        extra_cols.append('clarity_encoded')
    if 'color_encoded' in df.columns:
        extra_cols.append('color_encoded')
    corr_cols = base_cols + extra_cols

    corr_df = df[corr_cols].copy()
    corr_df.columns = [
        'Pris', 'Carat', 'Depth', 'Table', 'X', 'Y', 'Z',
        'Cut', 'Clarity', 'Color'
    ][:corr_df.shape[1]]

    corr_matrix = corr_df.corr()
    fig = plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='YlGnBu', vmin=-1, vmax=1, linewidths=0.5, fmt=".2f", square=True)
    plt.title("Korrelation mellan variabler")
    return fig

def plot_pca(df):
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA

    features = ['carat', 'depth', 'table', 'x', 'y', 'z']
    X = StandardScaler().fit_transform(df[features])
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    fig, ax = plt.subplots()
    scatter = ax.scatter(X_pca[:,0], X_pca[:,1], c=df['clarity_encoded'], cmap='viridis', alpha=0.5)
    ax.set_xlabel('PCA 1')
    ax.set_ylabel('PCA 2')
    ax.set_title('PCA av diamantdata (färgad efter klarhet)')
    fig.colorbar(scatter, label='Clarity')
    return fig

# ================================
# Diagram
# ================================

show_all = st.checkbox("Visa alla diagram", value=True)

diagram_options = [
    "Prisfördelning",
    "Pris per klarhet",
    "Pris per färg",
    "Pris vs Carat",
    "Korrelationsmatris",
    "PCA-visualisering"
]

if show_all:
    fig1, ax1 = plt.subplots()
    plot_price_distribution(filtered_df, ax1)
    st.pyplot(fig1)
    with st.expander("Vad visar diagrammet?"):
        st.markdown("""
        Histogrammet visar hur priset är fördelat bland alla diamanter som matchar dina filter.
        Ger en snabb överblick om marknaden har flest billigare eller dyrare diamanter, och om det finns extremvärden.
        """)

    fig2, ax2 = plt.subplots()
    plot_price_per_clarity(filtered_df, ax2)
    st.pyplot(fig2)
    with st.expander("Vad visar diagrammet?"):
        st.markdown("""
        Stapeldiagrammet jämför medelpriset för diamanter beroende på deras klarhetsgrad.
        Det är viktigt för att förstå hur mycket klarheten (dvs. hur "ren" stenen är) faktiskt påverkar priset.
        """)

    fig3, ax3 = plt.subplots()
    plot_price_per_color(filtered_df, ax3)
    st.pyplot(fig3)
    with st.expander("Vad visar diagrammet?"):
        st.markdown("""
        Här ser du hur priset varierar beroende på diamantens färgskala (D–J).
        Det hjälper Guldfynd förstå vilka färggrader som är mest värdefulla på marknaden.
        """)

    fig4, ax4 = plt.subplots()
    plot_price_vs_carat(filtered_df, ax4)
    st.pyplot(fig4)
    with st.expander("Vad visar diagrammet?"):
        st.markdown("""
        Punktdiagrammet visar sambandet mellan vikt (carat) och pris.
        Ju större stenen är, desto mer ökar priset – ofta exponentiellt snarare än linjärt.
        """)

    fig_corr = plot_corr_heatmap(filtered_df)
    st.pyplot(fig_corr)
    with st.expander("Vad visar diagrammet?"):
        st.markdown("""
        Visar sambanden mellan numeriska variabler i datasetet.
        Här kan man se om vissa egenskaper (t.ex. carat och pris) har starkt samband, vilket kan påverka Guldfynds prissättning.
        """)

    fig_pca = plot_pca(filtered_df)
    st.pyplot(fig_pca)
    with st.expander("Vad visar diagrammet?"):
        st.markdown("""
        Principal Component Analysis (PCA) reducerar datan till två dimensioner för att visualisera mönster och grupperingar, färgat efter klarhet.
        Det hjälper till att upptäcka om vissa egenskaper "hänger ihop" på oväntade sätt.
        """)

else:
    plot_option = st.selectbox(
        
        "Välj ett specifikt diagram:",
        diagram_options,
        index=0
    )

    if plot_option == "Prisfördelning":
        fig, ax = plt.subplots()
        plot_price_distribution(filtered_df, ax)
        st.pyplot(fig)
        with st.expander("Vad visar diagrammet?"):
            st.markdown("""
            Histogrammet visar hur priset är fördelat bland alla diamanter som matchar dina filter.
            Ger en snabb överblick om marknaden har flest billigare eller dyrare diamanter, och om det finns extremvärden.
            """)

    elif plot_option == "Pris per klarhet":
        fig, ax = plt.subplots()
        plot_price_per_clarity(filtered_df, ax)
        st.pyplot(fig)
        with st.expander("Vad visar diagrammet?"):
            st.markdown("""
            Stapeldiagrammet jämför medelpriset för diamanter beroende på deras klarhetsgrad.
            Det är viktigt för att förstå hur mycket klarheten (dvs. hur "ren" stenen är) faktiskt påverkar priset.
            """)

    elif plot_option == "Pris per färg":
        fig, ax = plt.subplots()
        plot_price_per_color(filtered_df, ax)
        st.pyplot(fig)
        with st.expander("Vad visar diagrammet?"):
            st.markdown("""
            Här ser du hur priset varierar beroende på diamantens färgskala (D–J).
            Det hjälper Guldfynd förstå vilka färggrader som är mest värdefulla på marknaden.
            """)

    elif plot_option == "Pris vs Carat":
        fig, ax = plt.subplots()
        plot_price_vs_carat(filtered_df, ax)
        st.pyplot(fig)
        with st.expander("Vad visar diagrammet?"):
            st.markdown("""
            Punktdiagrammet visar sambandet mellan vikt (carat) och pris.
            Ju större stenen är, desto mer ökar priset – ofta exponentiellt snarare än linjärt.
            """)

    elif plot_option == "Korrelationsmatris":
        fig = plot_corr_heatmap(filtered_df)
        st.pyplot(fig)
        with st.expander("Vad visar diagrammet?"):
            st.markdown("""
            Visar sambanden mellan numeriska variabler i datasetet.
            Här kan man se om vissa egenskaper (t.ex. carat och pris) har starkt samband, vilket kan påverka Guldfynds prissättning.
            """)

    elif plot_option == "PCA-visualisering":
        fig = plot_pca(filtered_df)
        st.pyplot(fig)
        with st.expander("Vad visar diagrammet?"):
            st.markdown("""
            Principal Component Analysis (PCA) reducerar datan till två dimensioner för att visualisera mönster och grupperingar, färgat efter klarhet.
            Det hjälper till att upptäcka om vissa egenskaper "hänger ihop" på oväntade sätt.
            """)

st.markdown("""
**Om urvalet av diagram:**  
För att ge en tydlig och relevant bild av diamantmarknaden har jag valt ut sex diagram som tillsammans fångar de viktigaste sambanden i datan.  
Dessa visualiseringar visar hur priset påverkas av storlek (carat), klarhet och färg, samt ger en översikt av prisfördelningen och sambanden mellan variabler.  
Urvalet är gjort för att fokusera på kvalitet och insikt snarare än kvantitet.
""")

# ================================
# Ladda ner filtrerad data
# ================================
st.download_button(
    label="Ladda ner filtrerad data som CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='filtrerade_diamanter.csv',
    mime='text/csv'
)

st.markdown("""
---
""")

# ================================
# Executive Summary
# ================================
with st.expander("Executive Summary"):
    st.markdown("""
    - Pris påverkas mest av carat (storlek), följt av klarhet och färg.  
    - För att Guldfynd ska ge sig in på diamantmarknaden bör fokus ligga på:
        - Stenar med hög carat (≥1.5), då dessa ger störst avkastning.
        - Klarhet VS1 eller bättre.
    - Slipning påverkar utseende men är inte den viktigaste prisfaktorn.
    """)

required_cols = ['price', 'carat', 'cut', 'color', 'clarity']
for col in required_cols:
    if col not in filtered_df.columns:
        st.error(f"Saknar kolumnen '{col}' i datafilen!")
        st.stop()

