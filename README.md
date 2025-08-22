![Logo](PensievePlotter.png)

# 🧙 The Pensieve Plotter
An interactive Streamlit application for visualizing Extended Bayesian Skyline Plots (EBSP) from BEAST log files. This tool allows you to look into the "memories" of your population data, revealing demographic histories with a user-friendly and interactive interface.

## 📜 Features
- Interactive Plotting: Visualize EBSP data using Plotly for a fully interactive experience (zoom, pan, inspect data points).
- Multiple Plot Types: Generate standard Bayesian Skyline Plots or view a histogram of event times.
- Customizable Analysis: Adjust the burn-in percentage to discard initial states from your MCMC run.
- Flexible Axis Control:
  - Toggle logarithmic or linear scales for both X and Y axes.
  - Reverse the time axis to display "Years Before Present" in the standard convention (past on the left).
  - Manually set a custom range for the X-axis.
- Confidence Intervals: Choose between 95% Highest Posterior Density (HPD) or Central Posterior Density (CPD) intervals.
- Example Data: Load a built-in EBSP.log example file with a single click to see the app in action.

## 🛠️ Setup and Installation
Follow these steps to get The Pensieve Plotter running on your local machine.

### Requirements
Python 3.8+

The following Python libraries: Streamlit, Pandas, NumPy, and Plotly.

You can install all required libraries with a single command:

```
pip install streamlit pandas numpy plotly
```

### File Structure
For the application to work correctly, place the following files in the same project folder:

```
your-project-folder/
├── app.py              # The main application script
├── PensievePlotter.png   # The application logo
└── EBSP.log            # The example data file
```
### How to Run
Navigate to the project directory in your terminal.

```
cd path/to/your-project-folder
```
Run the application using the Streamlit command:

```
streamlit run app.py
```

Your web browser will automatically open a new tab with the running application.

## 📖 How to Use the App
The application interface is controlled by the sidebar on the left.

### Main Controls
- Burn-in percentage: A slider to set the percentage of initial samples to discard from the log file.
- Select Plot Type:
    - EBSP Skyline Plot: The main plot showing effective population size through time.
    - Event Times Histogram: A histogram showing the distribution of event times (e.g., coalescence or migration events) from the log.
### Skyline Plot Options
These options appear only when "EBSP Skyline Plot" is selected.
- Confidence Interval: Choose to display the shaded region as either 95% HPD or 95% CPD.
- Reverse Time Axis: When checked (default), the X-axis is reversed, showing time increasing from right to left (e.g., 0 years before present is on the right).
- Use Log Scale for Y-Axis: When checked (default), the Y-axis (Effective Population Size) is displayed on a logarithmic scale, which is ideal for viewing large demographic changes.

### Set X-axis Range (Optional):
- X-axis Min / Max: Manually enter minimum and maximum values to zoom in on a specific time interval. Leave blank for an automatic range.