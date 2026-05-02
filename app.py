from flask import Flask, render_template_string, request, jsonify
import pandas as pd
import numpy as np
import mne
from scipy.signal import welch
import io
import base64
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)

# --- FUTURISTIC UI WITH SIDE-BY-SIDE LAYOUT ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NEURO-CORE | WAVEFORM ANALYTICS</title>
    <style>
        :root { --neon: #00f2ff; --bg: #050505; --card: #10121d; --text: #e0e0e0; --accent: #ffff00; }
        body { background-color: var(--bg); color: var(--text); font-family: 'Courier New', monospace; margin: 0; padding: 20px; }
        .container { max-width: 1400px; margin: auto; border: 1px solid var(--neon); box-shadow: 0 0 30px rgba(0,242,255,0.2); padding: 30px; border-radius: 15px; }
        h1 { text-align: center; text-transform: uppercase; letter-spacing: 8px; text-shadow: 0 0 15px var(--neon); color: var(--neon); }
        .upload-section { border: 2px dashed var(--neon); padding: 20px; text-align: center; margin-bottom: 30px; background: rgba(0, 242, 255, 0.05); }
        .results { display: none; }
        .card { background: var(--card); border: 1px solid var(--neon); padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .metric-title { color: var(--neon); font-size: 0.9em; text-transform: uppercase; margin-bottom: 15px; border-left: 3px solid var(--neon); padding-left: 10px; }
        
        /* SIDE-BY-SIDE WAVEFORM GRID */
        .wave-row { display: grid; grid-template-columns: 1.5fr 1fr; gap: 20px; align-items: center; margin-bottom: 15px; padding: 10px; background: rgba(0,0,0,0.4); border-radius: 5px; }
        .wave-img { background: #000; border: 1px solid #222; padding: 5px; border-radius: 4px; }
        .wave-data-table { width: 100%; border-collapse: collapse; font-size: 0.8em; }
        .wave-data-table td { padding: 8px; border-bottom: 1px solid #222; }
        .label { color: var(--neon); font-weight: bold; width: 40%; }
        
        button { background: transparent; border: 2px solid var(--neon); color: var(--neon); padding: 15px 40px; cursor: pointer; font-weight: bold; text-transform: uppercase; }
        button:hover { background: var(--neon); color: black; box-shadow: 0 0 25px var(--neon); }
        #status-bar { text-align: center; margin-bottom: 20px; color: var(--accent); font-weight: bold; }
        img { width: 100%; display: block; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚡ NEURO-CORE : SIGNAL MATRIX ⚡</h1>
        <div id="status-bar">SYSTEM STATUS: READY</div>
        
        <div class="upload-section">
            <input type="file" id="csvInput" style="display:none" accept=".csv">
            <button onclick="document.getElementById('csvInput').click()">UPLINK EEG DATA</button>
        </div>

        <div id="resultsArea" class="results">
            <div class="card">
                <div class="metric-title">COGNITIVE SUMMARY</div>
                <div style="display: flex; gap: 40px; align-items: center;">
                    <div>
                        <small>DOMINANT BAND</small>
                        <div id="domWave" style="font-size: 2em; font-weight: bold; color: #fff;">--</div>
                    </div>
                    <div>
                        <small>OPTIMAL DOMAIN</small>
                        <div id="domainTitle" style="font-size: 1.5em; color: #ffd700; font-weight: bold;">--</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="metric-title">NEURAL OSCILLATION DECOMPOSITION (SIDE-BY-SIDE)</div>
                <div id="waveMatrix"></div>
            </div>

            <div class="card">
                <div class="metric-title">CHANNEL INTEGRITY DIAGNOSTIC</div>
                <div class="wave-img"><img id="boxGraph"></div>
            </div>
        </div>
    </div>

    <script>
        const input = document.getElementById('csvInput');
        input.onchange = async () => {
            if (!input.files[0]) return;
            const formData = new FormData();
            formData.append('file', input.files[0]);
            document.getElementById('status-bar').innerText = "STATUS: GENERATING_WAVEFORM_MATRIX...";
            
            const resp = await fetch('/process', { method: 'POST', body: formData });
            const data = await resp.json();
            
            if (data.success) {
                document.getElementById('resultsArea').style.display = 'block';
                document.getElementById('domWave').innerText = data.dominant;
                document.getElementById('domainTitle').innerText = data.domain_title;
                document.getElementById('boxGraph').src = "data:image/png;base64," + data.box_plot;
                
                // Build the Matrix of Waves + Tables
                let matrixHtml = "";
                data.bands.forEach(b => {
                    matrixHtml += `
                    <div class="wave-row">
                        <div class="wave-img">
                            <img src="data:image/png;base64,${b.plot}" alt="${b.name}">
                        </div>
                        <div class="wave-stats">
                            <table class="wave-data-table">
                                <tr><td class="label">BAND</td><td style="color:${b.color}; font-weight:bold">${b.name.toUpperCase()}</td></tr>
                                <tr><td class="label">FREQUENCY</td><td>${b.freq_range}</td></tr>
                                <tr><td class="label">MEAN POWER</td><td>${b.power.toFixed(6)} µV²</td></tr>
                                <tr><td class="label">RELATIVE</td><td>${b.relative.toFixed(2)} %</td></tr>
                            </table>
                        </div>
                    </div>`;
                });
                document.getElementById('waveMatrix').innerHTML = matrixHtml;
                document.getElementById('status-bar').innerText = "STATUS: DECODING_COMPLETE";
            }
        };
    </script>
</body>
</html>
"""

# --- BACKEND LOGIC ---
def run_analysis(file_storage):
    df = pd.read_csv(file_storage, skiprows=1)
    channels = ['EEG.AF3', 'EEG.F7', 'EEG.F3', 'EEG.FC5', 'EEG.T7', 'EEG.P7', 'EEG.O1', 
                'EEG.O2', 'EEG.P8', 'EEG.T8', 'EEG.FC6', 'EEG.F4', 'EEG.F8', 'EEG.AF4']
    valid_ch = [c for c in channels if c in df.columns]
    
    sfreq = 128
    raw_data = df[valid_ch].values.T / 1e6
    info = mne.create_info(ch_names=[c.replace('EEG.', '') for c in valid_ch], sfreq=sfreq, ch_types='eeg')
    raw = mne.io.RawArray(raw_data, info)
    
    # 1. Frequency Calculations
    raw_filt = raw.copy().filter(1.0, 40.0, verbose=False)
    clean_data = raw_filt.get_data()
    freqs, psds = welch(clean_data, fs=sfreq, nperseg=sfreq*2)
    psd_avg = psds.mean(axis=0)
    
    bands_config = {
        'Delta': {'range': (0.5, 4), 'color': '#FF007F'},
        'Theta': {'range': (4, 8), 'color': '#7F00FF'},
        'Alpha': {'range': (8, 13), 'color': '#007FFF'},
        'Beta':  {'range': (13, 30), 'color': '#00FF7F'},
        'Gamma': {'range': (30, 40), 'color': '#FFD700'}
    }
    
    total_power = psd_avg[(freqs >= 0.5) & (freqs <= 40)].sum()
    band_data_list = []
    t_plot = np.arange(0, 1.5, 1/sfreq) # 1.5s snippet
    
    for name, config in bands_config.items():
        low, high = config['range']
        # Calculate Power
        mask = (freqs >= low) & (freqs <= high)
        p_val = float(psd_avg[mask].mean() * 1e12)
        rel_p = (psd_avg[mask].sum() / total_power) * 100
        
        # 2. Generate Individual Waveform Plot
        # Apply Zero-Phase Digital Filtering to isolate band
        band_sig = raw.copy().filter(low, high, verbose=False).get_data().mean(axis=0)[:len(t_plot)]
        
        plt.figure(figsize=(6, 1.5), facecolor='#000000')
        plt.plot(t_plot, band_sig, color=config['color'], linewidth=2)
        plt.axis('off')
        plt.tight_layout(pad=0)
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#000000')
        plot_b64 = base64.b64encode(buf.getvalue()).decode()
        plt.close()
        
        band_data_list.append({
            'name': name,
            'color': config['color'],
            'freq_range': f"{low}-{high} Hz",
            'power': p_val,
            'relative': rel_p,
            'plot': plot_b64
        })

    dominant = max(band_data_list, key=lambda x: x['power'])['name']

    # 3. Channel Stability Boxplot
    stds = np.std(clean_data, axis=1)
    low_p, mid_p = np.percentile(stds, [33, 66])
    colors = ['#003300' if s <= low_p else '#331a00' if s <= mid_p else '#330000' for s in stds]
    edges = ['#00ff00' if s <= low_p else '#ff8800' if s <= mid_p else '#ff0000' for s in stds]
    
    plt.figure(figsize=(10, 4), facecolor='#10121d')
    ax = plt.gca(); ax.set_facecolor('#000000')
    box_df = pd.DataFrame(clean_data.T * 1e6, columns=[c.replace('EEG.', '') for c in valid_ch])
    bp = ax.boxplot([box_df[c] for c in box_df.columns], patch_artist=True, labels=box_df.columns)
    for i, box in enumerate(bp['boxes']):
        box.set(facecolor=colors[i], edgecolor=edges[i], linewidth=2)
    for m in bp['medians']: m.set(color='white', linewidth=2)
    plt.xticks(color='#00f2ff', rotation=45); plt.yticks(color='#00f2ff')
    
    box_buf = io.BytesIO()
    plt.savefig(box_buf, format='png', facecolor='#10121d')
    box_base64 = base64.b64encode(box_buf.getvalue()).decode()
    plt.close()

    career_info = {"Delta": "Recovery", "Theta": "Creative", "Alpha": "Wellness", "Beta": "Engineering", "Gamma": "Research"}

    return dominant, career_info[dominant], box_base64, band_data_list

# --- ROUTES ---
@app.route('/')
def index(): return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process():
    try:
        f = request.files['file']
        dom, d_title, box_p, bands = run_analysis(f)
        return jsonify(success=True, dominant=dom, domain_title=d_title, box_plot=box_p, bands=bands)
    except Exception as e: return jsonify(success=False, error=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=5000)