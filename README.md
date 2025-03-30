![HoodAI Logo](hoodAI.png)
# 🏙️ HoodAI - Your Smart Neighborhood Review Assistant

Welcome to **HoodAI**, your intelligent assistant for exploring, reviewing, and managing neighborhood information. With HoodAI, you can share your experiences, analyze reviews, and even generate AI-powered insights about neighborhoods. 🌟

---

## ✨ Features

### 🌍 **Explore Neighborhoods**
- View reviews of neighborhoods with ratings for **overall quality** and **safety**.
- Interactive **map visualization** with markers for reviewed locations.
- Filter and sort reviews by:
  - **Newest first**
  - **Highest rated**
  - **Most reviewed locations**

### 📝 **Create Reviews**
- Share your experiences by submitting reviews for neighborhoods.
- Rate neighborhoods on **overall quality** and **safety**.
- Select locations directly on an interactive map.

### 🛠️ **Manage Reviews**
- Edit or delete your previously submitted reviews.
- Keep your reviews up-to-date with ease.

### 🤖 **HoodAI Assistant**
- Ask HoodAI for insights about neighborhoods.
- Generate concise and objective reviews using AI.
- HoodAI ensures neutrality and avoids unrelated responses.

### 🎨 **Enhanced User Interface**
- Beautiful, responsive design with **custom CSS styling**.
- Dynamic **dark mode toggle** for a better user experience.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Required Python libraries:
  - `streamlit`
  - `requests`
  - `pandas`
  - `folium`
  - `streamlit-folium`
  - `sqlite3`
  - `geopy`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/hoodai.git
   cd hoodai
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. put config.tmol into .streamlit folder

  
4. Run the app:
   ```bash
   streamlit run hood.py
   ```

5. Open your browser and navigate to `http://localhost:XXXX`.

---

## 🛠️ Configuration

### Database
- The app uses an SQLite database (`reviews.db`) to store reviews.
- The database is automatically created and initialized when the app runs for the first time.

### OpenAI API
- HoodAI integrates with OpenAI's API for AI-generated reviews.
- Add your OpenAI API key in the `hood.py` file:
  ```python
  GPT_API="YOUR_API_KEY"
  ```

---

## 📂 Project Structure

```
📁 hoodai
├── hood.py               # Main application file
├── reviews.db            # SQLite database (auto-generated)
├── requirements.txt      # Python dependencies
├── HoodAI.png            # HoodAI Logo
└── README.md             # Project documentation
```
---

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## ❤️ Acknowledgments
- **Streamlit** for the amazing framework.
- **Folium** for interactive map visualizations.
- **OpenAI** for powering HoodAI's intelligent assistant.
- **Infomatrix** for inspiring innovation and competition. 
---

Enjoy exploring and sharing your neighborhood experiences with **HoodAI**! 🌟
```
