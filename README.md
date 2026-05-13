# Excel Master Worker

AI-powered Excel file generator, macro creator, and spreadsheet assistant. Works on both desktop and mobile browsers.

## Features

- **AI-Powered Excel Generation** — Describe what you need in plain English and get a downloadable `.xlsx` file with formulas, charts, formatting, and more.
- **Complex Formula Support** — VLOOKUP, INDEX/MATCH, SUMIFS, dynamic arrays, LAMBDA, structured references, and nested formulas.
- **VBA Macro Generation** — Request automation macros that are included as a reference sheet you can paste into the VBA editor.
- **Dashboard Creation** — Professional dashboards with charts, KPIs, conditional formatting, and data validation.
- **File Modification** — Upload your own Excel files and ask for formula additions, formatting changes, or structural modifications.
- **Step-by-Step Walkthroughs** — When a feature can't be generated directly, get detailed instructions to build it yourself.
- **Screenshot Upload** — Upload images of spreadsheets to describe what you want modified.
- **Mobile-Friendly** — Responsive design works on phones, tablets, and desktops.

## Tech Stack

- **Backend**: Python, FastAPI, OpenAI API, openpyxl, xlsxwriter
- **Frontend**: React, Vite, Lucide Icons
- **AI**: GPT-4o or DeepSeek for understanding requests and generating Excel specifications

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API key (OpenAI or DeepSeek)

### Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/ultimatelol92/excel-master-worker.git
   cd excel-master-worker
   ```

2. **Backend setup**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. **Set your API key** (choose one)

   For OpenAI:
   ```bash
   echo "OPENAI_API_KEY=your-key-here" > .env
   ```

   For DeepSeek:
   ```bash
   cat > .env << EOF
   OPENAI_API_KEY=your-deepseek-key
   OPENAI_MODEL=deepseek-chat
   OPENAI_BASE_URL=https://api.deepseek.com
   EOF
   ```

4. **Frontend setup**
   ```bash
   cd ../frontend
   npm install
   ```

5. **Run the app**

   Terminal 1 (backend):
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Terminal 2 (frontend):
   ```bash
   cd frontend
   npm run dev
   ```

6. Open `http://localhost:3000` in your browser.

## Usage Examples

- "Create a sales dashboard with monthly revenue chart and KPI cards"
- "Build a budget tracker with income/expense categories and pie charts"
- "Generate a VBA macro that cleans data and removes duplicates"
- "Create a project Gantt chart with task dependencies"
- Upload an Excel file → "Add a SUM formula to column E and highlight values over 1000"

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send a message and get an AI-generated Excel file or walkthrough |
| POST | `/api/files/upload` | Upload an Excel file for analysis/modification |
| GET | `/api/files/download/{id}` | Download a generated or modified file |
| POST | `/api/files/modify` | Modify an uploaded file with AI instructions |
| POST | `/api/files/upload-image` | Upload a screenshot of a spreadsheet |
| GET | `/api/health` | Health check |

## License

MIT
