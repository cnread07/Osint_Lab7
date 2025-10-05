# Osint_Lab7
## 📖 Overview
Automated Social Media OSINT Aggregation Pipeline — collects, cleans, analyzes, and visualizes intelligence data from multiple social media platforms using Python.

It performs data collection, cleaning, enrichment (language & sentiment analysis), and visualization — all using Python.  
The collected data is stored in an **SQLite database** for further intelligence analysis.

---

## 🎯 Objectives
- Understand and use **social media APIs** for OSINT data collection.
- Build a **modular automated OSINT pipeline** in Python.
- Perform **preprocessing, language detection, sentiment analysis**, and visualization.
- Store and manage all collected OSINT data in a structured database.

---

## 🧩 Project Structure
Osint_Lab7/
│
├── main.py # Entry point for the pipeline
├── .env # API keys and tokens (not uploaded)
├── requirements.txt # Python dependencies
│
├── collectors/ # Collectors for each social platform
│ ├── twitter_collector.py
│ ├── reddit_collector.py
│ ├── facebook_collector.py
│ ├── instagram_collector.py
│ └── snscrape_collector.py
│
├── utils/ # Utilities for data cleaning, storage, analysis
│ ├── cleaner.py
│ ├── database.py
│ ├── sentiment.py
│ └── visualizer.py
│
├── data/
│ └── osint.db # SQLite database
│
└── screenshots/ # Evidence of working pipeline

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/Osint_Lab7.git
cd Osint_Lab7

