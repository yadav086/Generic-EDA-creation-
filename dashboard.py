import io
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# --- 1. DASHBOARD CONFIGURATION ---
st.set_page_config(
    page_title="Universal Seaborn Dashboard", page_icon="📊", layout="wide"
)

st.title("📊 Universal Seaborn Analytics Engine")
st.markdown(
    "Upload any Excel (.xlsx) or CSV (.csv) file to dynamically build interactive Seaborn visualizations."
)

# --- INTEGRATED CUSTOM FUNCTION ---
def plot_value_counts(df, column, topn=None):
    """Generates a side-by-side layout containing a pie and a labeled bar chart."""
    value_counts = df[column].value_counts()

    if topn:
        value_counts = value_counts.head(topn)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Pie Chart
    value_counts.plot(
        kind="pie",
        ax=axes[0],
        autopct="%.1f%%",
        startangle=45,
        colors=sns.color_palette("pastel"),
    )
    axes[0].set_ylabel("")
    axes[0].set_title(f"Percentage of {column}", fontsize=14)

    # Bar Chart
    sns.barplot(
        x=value_counts.index,
        y=value_counts.values,
        ax=axes[1],
        palette="pastel",
    )
    axes[1].set_title(f"Count of {column}", fontsize=14)
    axes[1].set_xlabel(column)
    axes[1].set_ylabel("Count")

    axes[1].set_xticklabels(
        axes[1].get_xticklabels(), rotation=45, ha="right"
    )

    # Add count labels
    for i, v in enumerate(value_counts.values):
        axes[1].text(
            i, v + 0.5, str(v), horizontalalignment="center", fontsize=12
        )

    fig.suptitle(f"{column} Distribution", fontsize=18, y=1.03)
    plt.tight_layout()
    return fig

# --- 2. MULTI-FORMAT FILE HANDLING ---
uploaded_file = st.sidebar.file_uploader(
    "Step 1: Upload Data File", type=["csv", "xlsx"]
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".xlsx"):
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_name = st.sidebar.selectbox(
            "Select Excel Sheet/Tab", excel_file.sheet_names
        )
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    else:
        df = pd.read_csv(uploaded_file)

    excel_total_rows = len(df)
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚙️ Control Dashboard")
        st.markdown(f"Total dataset size: {excel_total_rows:,} rows")

        row_range = st.slider(
            "Filter Row Segment Range:",
            min_value=1,
            max_value=excel_total_rows,
            value=(1, min(2000, excel_total_rows)),
        )

        start_row, end_row = row_range
        filtered_df = df.iloc[start_row - 1 : end_row]

        all_cols = filtered_df.columns.tolist()
        num_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = filtered_df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()

        st.markdown("---")

        chart_type = st.selectbox(
            "Select Seaborn Chart Type",
            [
                "Custom: Pie & Labeled Bar Subplots",
                "Bar Plot (sns.barplot)",
                "Count Plot (sns.countplot)",
                "Scatter Plot (sns.scatterplot)",
                "Line Plot (sns.lineplot)",
                "Histogram / Density (sns.histplot)",
                "Box Plot (sns.boxplot)",
                "Violin Plot (sns.violinplot)",
                "Correlation Matrix Heatmap (sns.heatmap)",
                "Pair Plot Matrix (sns.pairplot)",
            ],
        )

        xvar, yvar, huevar, topn_categories = None, None, None, None

        if chart_type == "Custom: Pie & Labeled Bar Subplots":
            xvar = st.selectbox("Select Categorical Column", cat_cols if cat_cols else all_cols)
            topn_categories = st.number_input("Limit to Top N (0 for All)", 0, 100, 0)

        elif chart_type in ["Scatter Plot (sns.scatterplot)", "Line Plot (sns.lineplot)"]:
            xvar = st.selectbox("X-Axis (Numerical)", num_cols if num_cols else all_cols)
            yvar = st.selectbox("Y-Axis (Numerical)", num_cols if num_cols else all_cols)
            huevar = st.selectbox("Grouping (Hue)", [None] + cat_cols)

        elif chart_type in ["Bar Plot (sns.barplot)", "Box Plot (sns.boxplot)", "Violin Plot (sns.violinplot)"]:
            xvar = st.selectbox("X-Axis (Categorical)", cat_cols if cat_cols else all_cols)
            yvar = st.selectbox("Y-Axis (Numerical)", num_cols if num_cols else all_cols)
            huevar = st.selectbox("Sub-Grouping (Hue)", [None] + cat_cols)

        elif chart_type == "Count Plot (sns.countplot)":
            xvar = st.selectbox("Target Category", cat_cols if cat_cols else all_cols)
            huevar = st.selectbox("Split Count (Hue)", [None] + cat_cols)

        elif chart_type == "Histogram / Density (sns.histplot)":
            xvar = st.selectbox("Distribution Axis", num_cols if num_cols else all_cols)
            huevar = st.selectbox("Stack Subdivisions (Hue)", [None] + cat_cols)

        elif chart_type == "Pair Plot Matrix (sns.pairplot)":
            selected_pair_cols = st.multiselect("Select Numerical Columns", num_cols, default=num_cols[:3])
            huevar = st.selectbox("Color Theme Splitting (Hue)", [None] + cat_cols)

        st.markdown("---")
        seaborn_style = st.selectbox("Theme", ["whitegrid", "darkgrid", "white", "ticks"])
        color_palette = st.selectbox("Palette", ["pastel", "muted", "deep", "coolwarm", "viridis"])

    with col2:
        st.subheader("📈 Rendered Output Grid")
        sns.set_theme(style=seaborn_style)

        try:
            if chart_type == "Custom: Pie & Labeled Bar Subplots":
                topn_val = None if topn_categories == 0 else int(topn_categories)
                fig = plot_value_counts(filtered_df, column=xvar, topn=topn_val)
                st.pyplot(fig)
                
            elif chart_type == "Pair Plot Matrix (sns.pairplot)":
                if selected_pair_cols:
                    with st.spinner("Generating Pairplot..."):
                        g = sns.pairplot(filtered_df, vars=selected_pair_cols, hue=huevar, palette=color_palette)
                        st.pyplot(g.fig)
                        fig = g.fig
                else:
                    st.warning("Select columns.")

            else:
                fig, ax = plt.subplots(figsize=(10, 5.5))
                if chart_type == "Bar Plot (sns.barplot)":
                    sns.barplot(data=filtered_df, x=xvar, y=yvar, hue=huevar, palette=color_palette, ax=ax)
                    for p in ax.patches:
                        height = p.get_height()
                        ax.annotate(f'{int(height)}', 
                                    (p.get_x() + p.get_width()/2., height),
                                    ha='center', va='bottom', fontsize=9)

                elif chart_type == "Count Plot (sns.countplot)":
                    sns.countplot(data=filtered_df, x=xvar, hue=huevar, palette=color_palette, ax=ax)
                    for p in ax.patches:
                        height = p.get_height()
                        ax.annotate(f'{int(height)}', 
                                    (p.get_x() + p.get_width()/2., height),
                                    ha='center', va='bottom', fontsize=9)

                elif chart_type == "Scatter Plot (sns.scatterplot)":
                    sns.scatterplot(data=filtered_df, x=xvar, y=yvar, hue=huevar, palette=color_palette, ax=ax)
                    for i, point in enumerate(filtered_df[[xvar, yvar]].values):
                        ax.text(point[0], point[1], str(i+1), fontsize=7)

                elif chart_type == "Line Plot (sns.lineplot)":
                    sns.lineplot(data=filtered_df, x=xvar, y=yvar, hue=huevar, palette=color_palette, ax=ax)
                    for x, y in zip(filtered_df[xvar], filtered_df[yvar]):
                        ax.text(x, y, f'{y}', fontsize=7, ha='center')

                elif chart_type == "Histogram / Density (sns.histplot)":
                    sns.histplot(data=filtered_df, x=xvar, hue=huevar, palette=color_palette, kde=True, ax=ax)
                    for p in ax.patches:
                        height = p.get_height()
                        ax.annotate(f'{int(height)}',
                                    (p.get_x() + p.get_width()/2., height),
                                    ha='center', va='bottom', fontsize=8)

                elif chart_type == "Box Plot (sns.boxplot)":
                    sns.boxplot(data=filtered_df, x=xvar, y=yvar, hue=huevar, palette=color_palette, ax=ax)
                    # Annotate counts per category
                    group_counts = filtered_df[xvar].value_counts()
                    for i, cat in enumerate(group_counts.index):
                        ax.text(i, ax.get_ylim()[1]*0.95, f'n={group_counts[cat]}',
                                ha='center', fontsize=9, color='black')

                elif chart_type == "Violin Plot (sns.violinplot)":
                    sns.violinplot(data=filtered_df, x=xvar, y=yvar, hue=huevar, palette=color_palette, ax=ax)
                    # Annotate counts per category
                    group_counts = filtered_df[xvar].value_counts()
                    for i, cat in enumerate(group_counts.index):
                        ax.text(i, ax.get_ylim()[1]*0.95, f'n={group_counts[cat]}',
                                ha='center', fontsize=9, color='black')

                elif chart_type == "Correlation Matrix Heatmap (sns.heatmap)":
                    if len(num_cols) >= 2:
                        corr = filtered_df[num_cols].corr()
                        sns.heatmap(corr, annot=True, cmap=color_palette, ax=ax)
                        # Annotate correlation matrix size
                        ax.set_title(f'Correlation Matrix ({len(num_cols)} variables)')
                    else:
                        st.warning("Need 2+ numerical columns.")

                plt.xticks(rotation=45, ha="right")
                plt.tight_layout()
                st.pyplot(fig)

            # Export Logic
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format="png", dpi=300)
            st.download_button("💾 Download Plot", img_buffer.getvalue(), "plot.png", "image/png")

        except Exception as e:
            st.error(f"Error rendering chart: {e}")

    st.markdown("---")
    st.subheader(f"🔍 Data Preview ({len(filtered_df):,} rows)")
    st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("💡 Please upload a CSV or Excel file to begin.")
