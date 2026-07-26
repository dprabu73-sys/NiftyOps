# TradingView Data Extractor Pro (Web GUI)

A standalone Windows local web application designed to extract historical market data from TradingView via `tvDatafeed` and save it directly into formatted Excel (`.xlsx`) files.

## Features
- **Premium Responsive UI**: Sleek dark dashboard with Inter font.
- **Localhost Execution**: Runs as a lightweight local web server and automatically launches in your browser.
- **Asynchronous Processing**: Extraction runs on background worker threads, preventing webpage freeze and request timeouts.
- **Interactive Log Terminal**: Real-time console showing credentials connection, bar downloads, data preview, and download state.
- **Instant Browser Downloads**: The generated Excel file is pushed directly to your browser's download folder upon completion.

---

## Running Locally

To run the application directly using your local Python environment:

1. **Install Dependencies**: Make sure you have python and the following dependencies:
   ```bash
   pip install pandas tvdatafeed openpyxl flask
   ```

2. **Launch the application**:
   ```bash
   py main.py
   ```
   *The server will start at `http://127.0.0.1:5000` and automatically open your default browser to show the interface.*

---

## Compiling to a Standalone Executable (.exe)

You can package this web application into a single, standalone Windows Executable (`.exe`) file. It compiles the Python interpreter, Flask server, and HTML templates into a single double-clickable file.

### 1. Install PyInstaller
Ensure PyInstaller is installed in your python environment:
```bash
pip install pyinstaller
```

### 2. Build the Executable
Open your terminal (PowerShell or Command Prompt) in the project directory and run the compilation command:
```bash
pyinstaller --noconsole --onefile --add-data "templates;templates" --name "TradingView_Extractor_Web" main.py
```

* **`--onefile`**: Bundles all code and files into a single `.exe` file.
* **`--noconsole`**: Hides the black terminal command-line window behind your browser GUI.
* **`--add-data "templates;templates"`**: Packages the HTML template folder inside the EXE (required for Flask to work).
* **`--name`**: Sets the name of the final application file.

### 3. Retrieve your EXE
Once the build completes (this takes a minute):
1. Navigate to the newly generated **`dist/`** directory.
2. Find the file **`TradingView_Extractor_Web.exe`**.
3. Move this EXE anywhere (like your Desktop) and run it by double-clicking. It will launch the local server and open your default browser automatically.
