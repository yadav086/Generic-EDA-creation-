import io
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

# --- DASHBOARD CONFIGURATION ---
st.set_page_config(page_title="Universal Seaborn Dashboard", page_icon="📊", layout="wide")

st.title("📊 Universal Seaborn Analytics Engine")
st.markdown("Upload any Excel (`.xlsx`) or CSV (`.csv`) file to dynamically build interactive Seaborn visualizations.")


# --- CUSTOM FUNCTION ---
def plot_value_counts(df, column, top_n=None):
    """Generates a pie chart and labeled bar chart for value counts."""
    value_counts = df[column].value_counts()
    if top_n:
        value_counts = value_counts.head(top_n)

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
    sns.barplot(x=value_counts.index, y=value_counts.values, ax=axes[1], palette="pastel")
    axes[1].set_title(f"Count of {column}", fontsize=14)
    axes[1].set_xlabel(column)
    axes[1].set_ylabel("Count")
    axes[1].set_xticklabels(axes[1].get_xticklabels(), rotation=45, ha="right")

    # Add labels
    for i, v in enumerate(value_counts.values):
        axes[1].text(i, v + 0.5, str(v), ha="center", fontsize=12)

    fig.suptitle(f"{column} Distribution", fontsize=18, y=1.03)
    plt.tight_layout()
    return fig


# --- FILE UPLOAD ---
uploaded_file = st.sidebar.file_uploader("Step 1: Upload Data File", type=["csv", "xlsx"])

if uploaded_file is not None:
    if uploaded_file.name.endswith(".xlsx"):
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_name = st.sidebar.selectbox("Select Excel Sheet/Tab", excel_file.sheet_names)
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    else:
        df = pd.read_csv(uploaded_file)

    # Column lists
    initial_cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    # --- FILTER PANEL ---
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Data Segregation Filter")

    use_filter = st.sidebar.checkbox("Enable Group/Segment Filter")
    if use_filter and initial_cat_cols:
        filter_col = st.sidebar.selectbox("Segregate Data By Column:", initial_cat_cols)
        unique_vals = df[filter_col].dropna().unique().tolist()
        selected_val = st.sidebar.selectbox(f"Select specific {filter_col} value:", unique_vals)
        working_df = df[df[filter_col] == selected_val]
    else:
        working_df = df.copy()

    excel_total_rows = len(working_df)

    if excel_total_rows == 0:
        st.warning("The selected filter criteria returned 0 rows. Please broaden your segregation choices.")
    else:
        # Layout
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("⚙️ Control Dashboard")
            st.markdown(f"**Available records in segment:** `{excel_total_rows:,}` rows")

            row_range = st.slider(
                "Filter Row Segment Range:",
                min_value=1,
                max_value=excel_total_rows,
                value=(1, min(2000, excel_total_rows)),
            )
            start_row, end_row = row_range
            filtered_df = working_df.iloc[start_row - 1:end_row]

            # Column remap
            all_cols = filtered_df.columns.tolist()
            num_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
            cat_cols = filtered_df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

            st.markdown("---")

            # Chart selector
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

            # Variable mapping
            x_var, y_var, hue_var, top_n_categories = None, None, None, None

            if chart_type == "Custom: Pie & Labeled Bar Subplots":
                x_var = st.selectbox("Select Categorical Column to Track", cat_cols if cat_cols else all_cols)
                top_n_categories = st.number_input("Limit to Top N Categories? (0 for All)", min_value=0, max_value=100, value=0)

            elif chart_type in ["Scatter Plot (sns.scatterplot)", "Line Plot (sns.lineplot)"]:
                x_var = st.selectbox("X-Axis (Numerical)", num_cols if num_cols else all_cols)
                y_var = st.selectbox("Y-Axis (Numerical)", num_cols if num_cols else all_cols)
                hue_var = st.selectbox("Grouping (Hue) - Optional", [None] + cat_cols)

            elif chart_type in ["Bar Plot (sns.barplot)", "Box Plot (sns.boxplot)", "Violin Plot (sns.violinplot)"]:
                x_var = st.selectbox("X-Axis (Categorical)", cat_cols if cat_cols else all_cols)
                y_var = st.selectbox("Y-Axis (Numerical)", num_cols if num_cols else all_cols)
                hue_var = st.selectbox("Sub-Grouping (Hue) - Optional", [None] + cat_cols)

            elif chart_type == "Count Plot (sns.countplot)":
                x_var = st.selectbox("Target Category Column", cat_cols if cat_cols else all_cols)
                hue_var = st.selectbox("Split Count (Hue) - Optional", [None] + cat_cols)

            elif chart_type == "Histogram / Density (sns.histplot)":
                x_var = st.selectbox("Distribution Axis Column", num_cols if num_cols else all_cols)
                hue_var = st.selectbox("Stack Subdivisions (Hue) - Optional", [None] + cat_cols)

            elif chart_type == "Pair Plot Matrix (sns.pairplot)":
                st.info("⚠️ Note: Pairplots can be slow if many columns are selected.")
                selected_pair_cols = st.multiselect("Select Numerical Columns to Compare", num_cols, default=num_cols[:3])
                hue_var = st.selectbox("Color Theme Splitting (Hue)", [None] + cat_cols)

            # Aesthetic options
            st.markdown("---")
            seaborn_style = st.selectbox("Visual Backdrop Theme", ["whitegrid", "darkgrid", "white", "ticks"])
            color_palette = st.selectbox("Color Swatch Palette", ["pastel", "muted", "deep", "bright", "coolwarm", "viridis", "rocket"])

        with col2:
            st.subheader("📈 Rendered Output Grid")
            sns.set_theme(style=seaborn_style)

            try:
                if chart_type == "Custom: Pie & Labeled Bar Subplots":
                    top_n_val = None if top_n_categories == 0 else int(top_n_categories)
                    fig = plot_value_counts(filtered_df, column=x_var, top_n=top_n_val)
                    st.pyplot(fig)

                elif chart_type == "Pair Plot Matrix (sns.pairplot)":
                    if selected_pair_cols:
                        g = sns.pairplot(filtered_df, vars=selected_pair_cols, hue=hue_var if hue_var else None, palette=color_palette)
                        st.pyplot(g.fig)
                    else:
                        st.warning("Please choose at least one data column to map.")

                else:
                    fig, ax = plt.subplots(figsize=(10, 5.5))

                    if chart_type == "Bar Plot (sns.barplot)":
                        sns.barplot(data=filtered_df, x=x_var, y=y_var, hue=hue_var, palette=color_palette, ax=ax)
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Averaged Metric Evaluation: {y_var} vs {x_var}")

                    elif chart_type == "Count Plot (sns.countplot)":
                        sns.countplot(data=filtered_df, x=x_var, hue=hue_var, palette=color_palette, ax=ax)
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Total Occurrence Frequency Count: {x_var}")

                    elif chart_type == "Scatter Plot (sns.scatterplot)":
                        sns.scatterplot(data=filtered_df, x=x_var, y=y_var, hue=hue_var, palette=color_palette, ax=ax)
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Averaged Metric Evaluation: {y_var} vs {x_var}")
                                        
                    elif chart_type == "Line Plot (sns.lineplot)":
                        sns.lineplot(data=filtered_df, x=x_var, y=y_var, hue=hue_var, palette=color_palette, ax=ax)
                        ax.set_title(f"Linear Progression Sequence Trend: {y_var} vs {x_var}")

                    elif chart_type == "Histogram / Density (sns.histplot)":
                        sns.histplot(data=filtered_df, x=x_var, hue=hue_var, palette=color_palette, kde=True, multiple="stack", ax=ax)
                        ax.set_title(f"Continuous Numerical Density Curve: {x_var}")

                    elif chart_type == "Box Plot (sns.boxplot)":
                        sns.boxplot(data=filtered_df, x=x_var, y=y_var, hue=hue_var, palette=color_palette, ax=ax)
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Quartile Distribution Boundaries: {y_var} vs {x_var}")

                    elif chart_type == "Violin Plot (sns.violinplot)":
                        sns.violinplot(data=filtered_df, x=x_var, y=y_var, hue=hue_var, palette=color_palette, ax=ax)
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Probability Structure Breakdown: {y_var} vs {x_var}")

                    elif chart_type == "Correlation Matrix Heatmap (sns.heatmap)":
                        if len(num_cols) >= 2:
                            corr_matrix = filtered_df[num_cols].corr()
                            sns.heatmap(corr_matrix, annot=True, cmap=color_palette, fmt=".2f", linewidths=0.5, ax=ax)
                            ax.set_title("Feature Interactions Correlation Heatmap")
                        else:
                            st.warning("Heatmaps require at least 2 numerical columns.")

                    plt.tight_layout()
                    st.pyplot(fig)

                    # --- RAM BUFFER EXPORT FOR FILE DOWNLOADS ---
                    img_buffer = io.BytesIO()
                    plt.savefig(img_buffer, format="png", dpi=300)
                    img_buffer.seek(0)
                    st.download_button(
                        label="💾 Download Generated Plot Image (PNG)",
                        data=img_buffer,
                        file_name="seaborn_dashboard_export.png",
                        mime="image/png",
                    )
            except Exception as e:
                st.error(f"Mismatched data types selected for {chart_type}. Specific Error: {e}")

        # --- RAW DATA SLICE PREVIEW ---
        st.markdown("---")
        st.subheader(f"🔍 Interactive Slice Data Viewer ({len(filtered_df):,} active rows)")
        st.dataframe(filtered_df, use_container_width=True)

else:
    st.info("💡 System waiting for file input. Drop a valid .xlsx or .csv dataset into the sidebar panel.")
