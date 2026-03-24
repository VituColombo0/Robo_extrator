# Robo_extrator

A high-performance meteorological data extraction and processing engine. This system automates the retrieval of raw weather data from remote Streamlit-based monitoring stations, applies advanced signal processing to sanitize the inputs, and generates analytical visualizations.

## 🏗 Architecture Overview

The system is architected as a robust automation pipeline:

1.  **Ingestion Layer**: Utilizes **Selenium (EdgeChromium)** with custom retry logic and exception handling to navigate and scrape data from distributed meteorological stations.
2.  **Processing Layer**: 
    - **Physical Validation**: Clips and rounds values (e.g., ensuring non-negative radiation).
    - **Gap Filling**: Uses **Akima 1D Interpolation** for smooth, physically plausible data reconstruction in periods of sensor downtime.
    - **Signal Smoothing**: Applies **Savitzky-Golay filters** to reduce noise while preserving important high-frequency meteorological trends.
3.  **Visualization Layer**: Generates verification plots using **Matplotlib** to compare raw vs. processed data across multiple dimensions (Temperature, Humidity, Radiation, Wind Velocity, etc.).
4.  **Interface**: A **Tkinter-based GUI** for parameter entry, station selection, and real-time execution monitoring.

## 🛠 Prerequisites

- **Python 3.10+**
- **Microsoft Edge** & **Edge WebDriver**
- Dependencies: `selenium`, `pandas`, `numpy`, `scipy`, `matplotlib`, `webdriver-manager`, `openpyxl`

## 🚀 Installation

```bash
pip install -r requirements.txt
```

## 📈 Usage

1. Run the main script:
   ```bash
   python robo_extrator.py
   ```
2. Select the desired stations and date range in the GUI.
3. Click **INICIAR EXTRAÇÃO**.
4. Results will be generated in the `said/` directory.

## 📁 Project Structure

- `robo_extrator.py`: Core logic and GUI.
- `saida/`: 
    - `ORIGINAL/`: Raw CSV files.
    - `CORRIGIDO/`: Validated CSV data.
    - `EXCEL_TRATADO/`: Final processed Excel files.
    - `GRAFICOS/`: Validation visualizations.
    - `LOGS/`: Detailed execution history.
