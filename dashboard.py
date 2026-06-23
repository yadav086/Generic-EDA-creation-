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
    "Upload any Excel (`.xlsx`) or CSV (`.csv`) file to dynamically build interactive Seaborn visualizations."
)

# --- 2. MULTI-FORMAT FILE HANDLING ---
uploaded_file = st.sidebar.file_uploader(
    "Step 1: Upload Data File", type=["csv", "xlsx"]
)

if uploaded_file is not None:
    # Handle multi-tab Excel files or plain CSVs
    if uploaded_file.name.endswith(".xlsx"):
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_name = st.sidebar.selectbox(
            "Select Excel Sheet/Tab", excel_file.sheet_names
        )
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
    else:
        df = pd.read_csv(uploaded_file)

    # Automatically set row boundary limits from the file
    excel_total_rows = len(df)

    # UI Split Layout: Controls on the Left, Canvas on the Right
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("⚙️ Control Dashboard")
        st.markdown(f"**Total dataset size:** `{excel_total_rows:,}` rows")

                # Dynamic data slicing slider locked completely to the total row count
        row_range = st.slider(
            "Filter Row Segment Range:",
            min_value=1,
            max_value=excel_total_rows,
            value=(1, min(2000, excel_total_rows)),
        )

        # FIXED: Extract start and end bounds from the slider tuple safely
        start_row, end_row = row_range
        filtered_df = df.iloc[start_row - 1 : end_row]

        # Automatic schema column categorization
        all_cols = filtered_df.columns.tolist()
        num_cols = filtered_df.select_dtypes(include=["number"]).columns.tolist()
        cat_cols = filtered_df.select_dtypes(
            include=["object", "category", "bool"]
        ).columns.tolist()

        st.markdown("---")

        # --- SEABORN MASTER PLOT SELECTOR ---
        chart_type = st.selectbox(
            "Select Seaborn Chart Type",
            [
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

        # Dynamic variable mapping based on column data types
        x_var, y_var, hue_var = None, None, None

        if chart_type in [
            "Scatter Plot (sns.scatterplot)",
            "Line Plot (sns.lineplot)",
        ]:
            x_var = st.selectbox(
                "X-Axis (Numerical)", num_cols if num_cols else all_cols
            )
            y_var = st.selectbox(
                "Y-Axis (Numerical)", num_cols if num_cols else all_cols
            )
            hue_var = st.selectbox(
                "Grouping (Hue) - Optional", [None] + cat_cols
            )

        elif chart_type in [
            "Bar Plot (sns.barplot)",
            "Box Plot (sns.boxplot)",
            "Violin Plot (sns.violinplot)",
        ]:
            x_var = st.selectbox(
                "X-Axis (Categorical)", cat_cols if cat_cols else all_cols
            )
            y_var = st.selectbox(
                "Y-Axis (Numerical)", num_cols if num_cols else all_cols
            )
            hue_var = st.selectbox(
                "Sub-Grouping (Hue) - Optional", [None] + cat_cols
            )

        elif chart_type == "Count Plot (sns.countplot)":
            x_var = st.selectbox(
                "Target Category Column", cat_cols if cat_cols else all_cols
            )
            hue_var = st.selectbox(
                "Split Count (Hue) - Optional", [None] + cat_cols
            )

        elif chart_type == "Histogram / Density (sns.histplot)":
            x_var = st.selectbox(
                "Distribution Axis Column", num_cols if num_cols else all_cols
            )
            hue_var = st.selectbox(
                "Stack Subdivisions (Hue) - Optional", [None] + cat_cols
            )

        elif chart_type == "Pair Plot Matrix (sns.pairplot)":
            st.info("⚠️ Note: Pairplots can be slow if many columns are selected.")
            selected_pair_cols = st.multiselect(
                "Select Numerical Columns to Compare", num_cols, default=num_cols[:3]
            )
            hue_var = st.selectbox(
                "Color Theme Splitting (Hue)", [None] + cat_cols
            )

        # Global Aesthetic Adjustments
        st.markdown("---")
        seaborn_style = st.selectbox(
            "Visual Backdrop Theme", ["whitegrid", "darkgrid", "white", "ticks"]
        )
        color_palette = st.selectbox(
            "Color Swatch Palette",
            ["pastel", "muted", "deep", "bright", "coolwarm", "viridis", "rocket"],
        )

        with col2:
            st.subheader("📈 Rendered Output Grid")

            # Initialize the chosen Seaborn style theme
            sns.set_theme(style=seaborn_style)

            # Pair plots build their own unique multi-figure grids natively
            if chart_type == "Pair Plot Matrix (sns.pairplot)":
                if selected_pair_cols:
                    with st.spinner("Processing Matrix Grid Plot..."):
                        g = sns.pairplot(
                            filtered_df,
                            vars=selected_pair_cols,
                            hue=hue_var if hue_var else None,
                            palette=color_palette,
                        )
                        st.pyplot(g.fig)
                else:
                    st.warning("Please choose at least one data column to map.")
            else:
                # Standard single figure canvas configuration
                fig, ax = plt.subplots(figsize=(10, 5.5))

                try:
                    if chart_type == "Bar Plot (sns.barplot)":
                        sns.barplot(
                            data=filtered_df,
                            x=x_var,
                            y=y_var,
                            hue=hue_var,
                            palette=color_palette,
                            ax=ax,
                        )
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Averaged Metric Evaluation: {y_var} vs {x_var}")

                    elif chart_type == "Count Plot (sns.countplot)":
                        sns.countplot(
                            data=filtered_df,
                            x=x_var,
                            hue=hue_var,
                            palette=color_palette,
                            ax=ax,
                        )
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Total Occurrence Frequency Count: {x_var}")

                    elif chart_type == "Scatter Plot (sns.scatterplot)":
                        sns.scatterplot(
                            data=filtered_df,
                            x=x_var,
                            y=y_var,
                            hue=hue_var,
                            palette=color_palette,
                            ax=ax,
                        )
                        ax.set_title(f"Scatter Correlation Assessment: {y_var} vs {x_var}")

                    elif chart_type == "Line Plot (sns.lineplot)":
                        sns.lineplot(
                            data=filtered_df,
                            x=x_var,
                            y=y_var,
                            hue=hue_var,
                            palette=color_palette,
                            ax=ax,
                        )
                        ax.set_title(f"Linear Progression Sequence Trend: {y_var} vs {x_var}")

                    elif chart_type == "Histogram / Density (sns.histplot)":
                        sns.histplot(
                            data=filtered_df,
                            x=x_var,
                            hue=hue_var,
                            palette=color_palette,
                            kde=True,
                            multiple="stack",
                            ax=ax,
                        )
                        ax.set_title(f"Continuous Numerical Density Curve: {x_var}")

                    elif chart_type == "Box Plot (sns.boxplot)":
                        sns.boxplot(
                            data=filtered_df,
                            x=x_var,
                            y=y_var,
                            hue=hue_var,
                            palette=color_palette,
                            ax=ax,
                        )
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Quartile Distribution Boundaries: {y_var} vs {x_var}")

                    elif chart_type == "Violin Plot (sns.violinplot)":
                        sns.violinplot(
                            data=filtered_df,
                            x=x_var,
                            y=y_var,
                            hue=hue_var,
                            palette=color_palette,
                            ax=ax,
                        )
                        plt.xticks(rotation=45, ha="right")
                        ax.set_title(f"Probability Structure Breakdown: {y_var} vs {x_var}")

                    elif chart_type == "Correlation Matrix Heatmap (sns.heatmap)":
                        if len(num_cols) >= 2:
                            corr_matrix = filtered_df[num_cols].corr()
                            sns.heatmap(
                                corr_matrix,
                                annot=True,
                                cmap=color_palette,
                                fmt=".2f",
                                linewidths=0.5,
                                ax=ax,
                            )
                            ax.set_title("Feature Interactions Correlation Heatmap")
                        else:
                            st.warning("Heatmaps require at least 2 numerical columns.")

                    # These operations run if the plotting commands inside the try-block succeed
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
                    st.error(
                        f"Mismatched data types selected for {chart_type}. Specific Error: {e}"
                    )

        # --- 3. LIVE RAW DATA ROWS SLICE PREVIEW ---
                st.markdown("---")
                st.subheader(
            f"🔍 Interactive Slice Data Viewer (`{len(filtered_df):,}` active rows)"
        )
                st.dataframe(filtered_df, use_container_width=True)

else:
    st.info(
            "💡 System waiting for file input. Drop a valid .xlsx or .csv dataset into the sidebar panel."
        )
                    