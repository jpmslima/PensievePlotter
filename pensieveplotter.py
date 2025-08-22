import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Core Data Processing Functions ---
def get_pop_size(t, change_times, change_pops, is_linear):
    if is_linear: return np.interp(t, change_times, change_pops)
    else:
        i = np.searchsorted(change_times, t, side='right')
        return change_pops[np.clip(i - 1, 0, len(change_pops) - 1)]

def compute_hpd(x, alpha=0.95):
    y = np.sort(x)
    n = len(y)
    n_alpha = int(round(alpha * n))
    if n_alpha >= n: return y[0], y[-1]
    interval_widths = y[n_alpha:] - y[:-n_alpha]
    if len(interval_widths) == 0: return y[0], y[-1]
    min_idx = np.argmin(interval_widths)
    return y[min_idx], y[min_idx + n_alpha]

def process_ebsp_data(df, is_linear):
    data_cols = df.columns.drop(['state', 'Sample'], errors='ignore')
    n_samples, n_times = len(df), len(data_cols)
    all_times_matrix = np.zeros((n_samples, n_times))
    change_times_list, change_pops_list = [], []
    for i in range(n_samples):
        these_change_times, these_change_pops = [], []
        for j, col in enumerate(data_cols):
            val = str(df.iloc[i][col]); parts = val.split(':'); time = float(parts[0])
            all_times_matrix[i, j] = time
            if len(parts) > 1:
                these_change_times.append(time); these_change_pops.append(float(parts[1]))
        change_times_list.append(np.array(these_change_times))
        change_pops_list.append(np.array(these_change_pops))
    mean_times = all_times_matrix.mean(axis=0)
    pop_sizes_at_mean_times = np.zeros((n_samples, n_times))
    for i in range(n_samples):
        if len(change_times_list[i]) > 0:
            pop_sizes_at_mean_times[i, :] = get_pop_size(mean_times, change_times_list[i], change_pops_list[i], is_linear)
    n_median = np.median(pop_sizes_at_mean_times, axis=0)
    n_lower_cpd, n_upper_cpd = np.quantile(pop_sizes_at_mean_times, [0.025, 0.975], axis=0)
    n_lower_hpd, n_upper_hpd = np.zeros(n_times), np.zeros(n_times)
    for i in range(n_times):
        n_lower_hpd[i], n_upper_hpd[i] = compute_hpd(pop_sizes_at_mean_times[:, i])
    return {'mean_times': mean_times, 'n_median': n_median, 'n_lower_hpd': n_lower_hpd, 'n_upper_hpd': n_upper_hpd, 'n_lower_cpd': n_lower_cpd, 'n_upper_cpd': n_upper_cpd}

def get_times(df):
    times = []
    data_cols = df.columns.drop(['state', 'Sample'], errors='ignore')
    for _, row in df.iterrows():
        for col in data_cols:
            times.append(float(str(row[col]).split(':')[0]))
    return np.array(times)

# --- Streamlit UI and Plotting ---
st.set_page_config(layout="wide")
st.title("🧙 The Pensieve Plotter")
st.write("An interactive tool for visualizing Extended Bayesian Skyline Plots (EBSP) from BEAST log files. See [documentation](https://github.com/jpmslima/PensievePlotter) for more details.")

# --- Sidebar Setup ---
st.sidebar.image("PensievePlotter.png", use_container_width=True)
st.sidebar.markdown('Developed by the EvoMol-Lab (github.com/evomol-lab).\n'
                    'BioME, UFRN, Brazil (bioinfo.imd.ufrn.br)')
st.sidebar.header("⚙️ Plotting Controls")
burnin = st.sidebar.slider("Burn-in percentage", 0, 90, 10, 5, format="%d%%") / 100.0
plot_type = st.sidebar.radio("Select Plot Type", ("EBSP Skyline Plot", "Event Times Histogram"))
st.sidebar.markdown("---")

if plot_type == "EBSP Skyline Plot":
    st.sidebar.subheader("Skyline Plot Options")
    use_hpd = st.sidebar.radio("Confidence Interval", ("95% HPD", "95% CPD")) == "95% HPD"
    reverse_x = st.sidebar.checkbox("Reverse Time Axis (Past on Left)", value=True)
    use_log_y = st.sidebar.checkbox("Use Log Scale for Y-Axis", value=True)
    st.sidebar.markdown("---")
    st.sidebar.write("**Set X-axis Range (Optional)**")
    x_min = st.sidebar.number_input("X-axis Min", value=None, placeholder="Auto", format="%f")
    x_max = st.sidebar.number_input("X-axis Max", value=None, placeholder="Auto", format="%f")
else: # Histogram options
    st.sidebar.subheader("Histogram Options")
    alpha_quantile = st.sidebar.slider("Quantile cutoff for x-axis", 0.80, 1.00, 0.95, 0.01)

# --- Main Page Logic ---
st.write("Upload your own EBSP log file or load the provided example.")

# Handling file upload OR example file button
col1, col2 = st.columns([3, 1])
with col1:
    uploaded_file = st.file_uploader("Choose an EBSP log file", type=["txt", "tsv", "log"], label_visibility="collapsed")
with col2:
    load_example = st.button("Load Example File", use_container_width=True)

data_source = None
if uploaded_file:
    data_source = uploaded_file
elif load_example:
    data_source = "EBSP.log"

# Only proceed if a data source has been selected
if data_source:
    try:
        df = pd.read_csv(data_source, sep='\t', comment='#')
        n_rows = len(df)
        df_processed = df.iloc[int(burnin * n_rows):].copy()
        
        st.subheader("Data Preview (after burn-in and comment removal)")
        st.dataframe(df_processed.head())
        
        fig = go.Figure()

        if plot_type == "EBSP Skyline Plot":
            res = process_ebsp_data(df_processed, is_linear=True)
            times = res['mean_times']
            y_lower = res['n_lower_hpd'] if use_hpd else res['n_lower_cpd']
            y_upper = res['n_upper_hpd'] if use_hpd else res['n_upper_cpd']
            ci_label = "95% HPD" if use_hpd else "95% CPD"

            fig.add_trace(go.Scatter(
                x=np.concatenate([times, times[::-1]]),
                y=np.concatenate([y_upper, y_lower[::-1]]),
                fill='toself', fillcolor='rgba(65, 105, 225, 0.2)',
                line=dict(width=0), name=ci_label,
            ))
            fig.add_trace(go.Scatter(
                x=times, y=res['n_median'], mode='lines', name='Median',
                line=dict(color='black', width=2)
            ))

            xaxis_config = {'title': "Time (Years Before Present)"}
            if x_min is not None and x_max is not None and x_min < x_max:
                if reverse_x:
                    xaxis_config['range'] = [x_max, x_min]
                else:
                    xaxis_config['range'] = [x_min, x_max]
            else:
                if reverse_x:
                    xaxis_config['autorange'] = 'reversed'

            yaxis_config = {'title': "Effective Population Size"}
            if use_log_y:
                yaxis_config['type'] = 'log'
                yaxis_config['title'] = "Effective Population Size (Log Scale)"
            else:
                yaxis_config['rangemode'] = 'tozero'

            fig.update_layout(title="Bayesian Skyline Plot", template='plotly_white',
                              xaxis=xaxis_config, yaxis=yaxis_config)

        elif plot_type == "Event Times Histogram":
            times = get_times(df_processed)
            xmax = np.quantile(times, alpha_quantile)
            times_filtered = times[times <= xmax]
            fig.add_trace(go.Histogram(x=times_filtered, nbinsx=100))
            fig.update_layout(title="Histogram of Event Times", xaxis_title="Time", yaxis_title="Frequency",
                              template='plotly_white', bargap=0.1)
        
        st.subheader("Generated Plot")
        st.plotly_chart(fig, use_container_width=True)

    # Specific error handling for missing example file
    except FileNotFoundError:
        st.error("Error: The example file 'EBSP.log' was not found. Please make sure it's in the same directory as your app.py script.")
    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
        st.warning("Please ensure the file is a tab-separated log file with the correct EBSP format.")
else:
    st.info("Please upload a file or load the example to begin.")