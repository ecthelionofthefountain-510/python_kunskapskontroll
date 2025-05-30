import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ================================
# 💫 Titel och introduktion
# ================================
st.set_page_config(page_title="Diamantanalys – Guldfynd", page_icon="💎", layout="centered")

st.title("Diamantanalys – Guldfynd")
st.markdown("""
Företaget Guldfynd undersöker möjligheten att erbjuda diamanter i sitt sortiment.  
Denna app visar insikter från en analys av över 50 000 diamanter, där vi tittar på pris, vikt, färg och klarhet.
""")

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
]

filtered_df = filtered_df.copy()
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
st.sidebar.info("Filtrera datan och välj analys för att visualisera samband och dra slutsatser.")

# ================================
# Diagram
# ================================
st.subheader("📊 Välj analys:")
show_all = st.checkbox("Visa alla analyser samtidigt")

if show_all:
    st.markdown("### Prisfördelning")
    fig1, ax1 = plt.subplots()
    sns.histplot(
        filtered_df['price'],
        bins=10,
        color='gold',
        edgecolor='black',
        element='bars',
        shrink=0.9,
        ax=ax1
    )
    ax1.set_xlabel("Pris (USD)")
    ax1.set_ylabel("Antal")
    yticks = ax1.get_yticks()
    ax1.set_yticks([int(y) for y in yticks if y == int(y)])
    st.pyplot(fig1)

    st.markdown("### Genomsnittligt pris per klarhet")
    fig2, ax2 = plt.subplots()
    # Genomsnittligt pris per klarhet
    avg_price_clarity = filtered_df.groupby('clarity', observed=True)['price'].mean().sort_values()
    avg_price_clarity.plot(kind='bar', color='skyblue', ax=ax2)
    ax2.set_ylabel("Pris (USD)")
    st.pyplot(fig2)

    st.markdown("### Genomsnittligt pris per färg")
    fig4, ax4 = plt.subplots()
    # Genomsnittligt pris per färg
    avg_price_color = filtered_df.groupby('color', observed=True)['price'].mean().sort_values()
    avg_price_color.plot(kind='bar', color='mediumseagreen', ax=ax4)
    ax4.set_ylabel("Pris (USD)")
    st.pyplot(fig4)

    st.markdown("### Pris vs Carat")
    fig5, ax5 = plt.subplots()
    ax5.scatter(filtered_df['carat'], filtered_df['price'], alpha=0.3, color='darkblue')
    ax5.set_xlabel("Carat")
    ax5.set_ylabel("Pris (USD)")
    st.pyplot(fig5)

    st.markdown("### Korrelationsmatris")
    # Skapa en lista på kolumner som finns och som du vill ha med
    base_cols = ['price', 'carat', 'depth', 'table', 'x', 'y', 'z']
    extra_cols = []
    if 'cut_encoded' in filtered_df.columns:
        extra_cols.append('cut_encoded')
    if 'clarity_encoded' in filtered_df.columns:
        extra_cols.append('clarity_encoded')
    if 'color_encoded' in filtered_df.columns:
        extra_cols.append('color_encoded')
    corr_cols = base_cols + extra_cols

    corr_df = filtered_df[corr_cols].copy()
    # Snygga kolumnnamn för heatmapen
    corr_df.columns = [
        'Pris', 'Carat', 'Depth', 'Table', 'X', 'Y', 'Z',
        'Cut', 'Clarity', 'Color'
    ][:corr_df.shape[1]]

    corr_matrix = corr_df.corr()
    fig_corr = plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='YlGnBu', vmin=-1, vmax=1, linewidths=0.5, fmt=".2f", square=True)
    plt.title("Korrelation mellan variabler")
    st.pyplot(fig_corr)

    st.subheader("Topp 5 dyraste diamanter")
    st.dataframe(filtered_df.nlargest(5, 'price')[['carat', 'cut', 'color', 'clarity', 'price']])

else:
    plot_option = st.selectbox(
        "Välj vilket diagram du vill se:",
        [
            "Prisfördelning",
            "Pris vs Carat",
            "Pris per klarhet",
            "Pris per färg",
            "Korrelationsmatris"
        ],
        index=0
    )

    fig, ax = plt.subplots()

    if plot_option == "Prisfördelning":
        sns.histplot(
            filtered_df['price'],
            bins=10,
            color='gold',
            edgecolor='black',
            element='bars',
            shrink=0.9,
            ax=ax
        )
        ax.set_title("Prisfördelning för diamanter")
        ax.set_xlabel("Pris (USD)")
        ax.set_ylabel("Antal")
        yticks = ax.get_yticks()
        ax.set_yticks([int(y) for y in yticks if y == int(y)])

    elif plot_option == "Pris per klarhet":
        filtered_df.groupby('clarity', observed=True)['price'].mean().sort_values().plot(kind='bar', color='skyblue', ax=ax)
        ax.set_title("Genomsnittligt pris per klarhet")
        ax.set_ylabel("Pris (USD)")

    elif plot_option == "Pris per caratgrupp":
        filtered_df.loc[:, 'carat_group'] = pd.cut(filtered_df['carat'], bins=[0, 0.5, 1, 1.5, 2, 5],
                                            labels=['0-0.5', '0.5-1', '1-1.5', '1.5-2', '2-5'])
        filtered_df.groupby('carat_group', observed=True)['price'].mean().plot(kind='bar', color='lightcoral', ax=ax)
        ax.set_title("Genomsnittligt pris per caratgrupp")
        ax.set_ylabel("Pris (USD)")

    elif plot_option == "Pris per färg":
        filtered_df.groupby('color', observed=True)['price'].mean().sort_values().plot(kind='bar', color='mediumseagreen', ax=ax)
        ax.set_title("Genomsnittligt pris per färg")
        ax.set_ylabel("Pris (USD)")

    elif plot_option == "Pris vs Carat":
        ax.scatter(filtered_df['carat'], filtered_df['price'], alpha=0.3, color='darkblue')
        ax.set_title("Pris vs Carat")
        ax.set_xlabel("Carat")
        ax.set_ylabel("Pris (USD)")

    elif plot_option == "Fördelning per slipning":
        cut_counts = filtered_df['cut'].value_counts()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(cut_counts, labels=cut_counts.index, autopct='%1.1f%%', startangle=140, colors=plt.cm.Pastel1.colors)
        ax.set_title("Fördelning av slipningstyper")

    elif plot_option == "Pris vs mått (x/y/z)":
        fig = plt.figure(figsize=(12, 8))
        plt.scatter(filtered_df['x'], filtered_df['price'], alpha=0.3, s=1, label='x (Längd)')
        plt.scatter(filtered_df['y'], filtered_df['price'], alpha=0.3, s=1, label='y (Bredd)')
        plt.scatter(filtered_df['z'], filtered_df['price'], alpha=0.3, s=1, label='z (Höjd)')
        plt.xlabel('Dimensioner (mm)')
        plt.ylabel('Pris (USD)')
        plt.title('Pris vs Dimensioner')
        plt.legend()
        plt.grid(True, alpha=0.3)

    elif plot_option == "Korrelationsmatris":
        # Skapa en lista på kolumner som finns och som du vill ha med
        base_cols = ['price', 'carat', 'depth', 'table', 'x', 'y', 'z']
        extra_cols = []
        if 'cut_encoded' in filtered_df.columns:
            extra_cols.append('cut_encoded')
        if 'clarity_encoded' in filtered_df.columns:
            extra_cols.append('clarity_encoded')
        if 'color_encoded' in filtered_df.columns:
            extra_cols.append('color_encoded')
        corr_cols = base_cols + extra_cols

        corr_df = filtered_df[corr_cols].copy()
        # Snygga kolumnnamn för heatmapen
        corr_df.columns = [
            'Pris', 'Carat', 'Depth', 'Table', 'X', 'Y', 'Z',
            'Cut', 'Clarity', 'Color'
        ][:corr_df.shape[1]]

        corr_matrix = corr_df.corr()
        fig = plt.figure(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='YlGnBu', vmin=-1, vmax=1, linewidths=0.5, fmt=".2f", square=True)
        plt.title("Korrelation mellan variabler")

    st.pyplot(fig)

st.markdown("""
**Om urvalet av diagram:**  
För att ge en tydlig och relevant bild av diamantmarknaden har jag valt ut fem diagram som tillsammans fångar de viktigaste sambanden i datan.  
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
