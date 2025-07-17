@echo off
echo Starting Mississippi WMA Hunt Analysis Dashboard...
echo.
echo Installing/checking dependencies...
pip install -r requirements.txt
echo.
echo Launching dashboard...
echo Dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.
streamlit run streamlit_dashboard.py
