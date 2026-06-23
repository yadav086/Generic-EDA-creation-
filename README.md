# 📊 Universal Seaborn Analytics Dashboard

A production-ready, interactive data visualization engine built with **Streamlit** and **Seaborn**. This dashboard allows you to upload any Excel (`.xlsx`) or CSV (`.csv`) file, dynamically maps its schema, and renders virtually every classic Seaborn plot type instantly with safety controls for large datasets.

## 🚀 Key Features

*   **Multi-Format File Support:** Seamlessly load `.csv` or multi-tab Excel files (`.xlsx`).
*   **Dynamic Data Guard Rails:** Limits visualization row sizes automatically to prevent browser execution or memory lag.
*   **Automatic Schema Sort:** Introspects data fields dynamically, segregating string indices into category fields and numerical columns into scale axes.
*   **Complete Seaborn Library:** Render Bar, Count, Scatter, Line, Histogram, Box, Violin, Correlation Heatmaps, and Pair Plots.
*   **Theme Engine:** Real-time adjustments for background themes (`darkgrid`, `whitegrid`, etc.) and color palettes (`pastel`, `viridis`, `rocket`).
*   **HD Exports:** High-quality `300 DPI PNG` asset download button hooked directly into the active Matplotlib buffer pipeline.

---

## 🛠️ Quick Start Installation

Follow these steps to set up your virtual environment and run the application locally.

### 1. Clone or Open Your Directory
Navigate to your specific project workspace path:
```bash
cd D:\DATASCIENCE\PRACTICAL\Lecture\Level3\HR-Employee-Attrition
```

### 2. Set Up a Virtual Environment
Create and activate an isolated development environment:
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Dependencies
Install the package versions pinned inside your `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 4. Run the Engine Execution
Launch the Streamlit web application dashboard:
```bash
streamlit run dashboard.py
```

Once running, the application will automatically open inside your web browser at **`http://localhost:8501`**.

---

## 📁 Project Structure

```text
HR-Employee-Attrition/
│
├── .venv/                  # Python isolated environment folder
├── dashboard.py           # Core application backend logic 
├── requirements.txt       # Environment package locks
└── README.md              # Documentation manual
```

---

## 💡 Usage Workflow Guide

1.  **Upload File:** Expand the left side panel drawer and drop a target dataset (e.g., your HR Employee Attrition file).
2.  **Filter Row Segment:** Adjust the row segment slider boundaries to select your active dataframe slice.
3.  **Select Chart Type:** Toggle the primary selector dropdown list to change plot architectures.
4.  **Assign Column Variables:** Map categorical columns to text fields or numerical metrics to standard scale coordinate positions.
5.  **Export Output:** Click the `💾 Download Generated Plot Image` button underneath the output grid to instantly save the crisp visualization asset to your hard drive.
