# Cognitive_Analysis_Using_BCI
# NEURO-CORE | WAVEFORM ANALYTICS ⚡

A futuristic real-time **EEG Brainwave Analysis Dashboard** built with Flask, MNE-Python, and SciPy. Visualizes neural oscillations (Delta, Theta, Alpha, Beta, Gamma) with stunning cyberpunk aesthetics.

![NEURO-CORE Screenshot](https://via.placeholder.com/800x400/050505/00f2ff?text=NEURO-CORE+Dashboard)  
*(Add a real screenshot here after running the app)*

---

## ✨ Features

- **Modern Cyberpunk UI** with neon glow effects and side-by-side waveform layout
- **EEG Signal Processing** using MNE-Python
- **Power Spectral Density Analysis** via Welch's method
- **Band-specific Waveform Isolation** (Delta → Gamma)
- **Channel Integrity Diagnostics** with color-coded box plots
- **Cognitive Domain Mapping** (Recovery, Creative, Wellness, Engineering, Research)
- **Fully Responsive & Interactive** frontend

---

## 🛠️ Tech Stack

- **Backend**: Flask, Pandas, NumPy, MNE-Python, SciPy
- **Frontend**: HTML5, CSS3 (Custom Neon Theme), Vanilla JavaScript
- **Visualization**: Matplotlib + Base64 encoding

---

## 🚀 Installation & Setup

### 1. Clone the Repository
bash
git clone https://github.com/yourusername/neuro-core.git
cd neuro-core

Create Virtual Environment
Bashpython -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
3. Install Dependencies
Bashpip install flask pandas numpy mne scipy matplotlib seaborn
Note: MNE-Python may require additional system dependencies on some platforms.
4. Run the Application
Bashpython app.py
Open your browser and go to: http://127.0.0.1:5000

📁 Project Structure
textneuro-core/
├── app.py                 # Main Flask application
├── README.md
├── requirements.txt
├── static/                # (Optional) for future CSS/JS files
└── templates/             # (Optional) if you separate templates

📊 How It Works

Upload a CSV EEG recording (Emotiv-style format supported)
System automatically:
Filters noise (1–40 Hz bandpass)
Computes Power Spectral Density
Isolates each brainwave band
Generates individual waveform plots
Performs channel stability analysis

Displays Cognitive Summary and optimal mental domain


📥 Sample Data
Place your EEG CSV files in the project folder. The app expects columns like:

EEG.AF3, EEG.F7, EEG.F3, ..., EEG.AF4
Sampling rate: 128 Hz


🎯 Use Cases

Neurofeedback research
Brain-computer interface (BCI) prototyping
Meditation / Focus tracking
Cognitive performance analysis
Educational neuroscience demos


🖼️ Screenshots
(Add screenshots of the dashboard here)

🔮 Future Enhancements

Real-time streaming support (LSL)
Machine Learning-based cognitive state classification
Exportable PDF reports
Dark/Light theme toggle
Multiple file comparison


📜 License
MIT License - feel free to use for research or personal projects.

🤝 Contributing
Pull requests are welcome! Especially for:

New visualization styles
Support for other EEG formats (EDF, BDF, etc.)
Performance optimizations
