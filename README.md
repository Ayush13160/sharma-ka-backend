# Contract Analysis Backend - Flask API

This is a Flask backend that analyzes employment contracts against Indian law (Indian Contract Act, 1872) and identifies risky or unfair clauses.

## 🏗️ Architecture

```
backend/
├── app.py                  # Main Flask application
├── config.py               # Configuration & constants
├── extractor.py            # PDF/DOCX/OCR text extraction
├── clause_splitter.py      # Clause segmentation
├── law_dataset.py          # Indian law loader
├── vector_store.py         # ChromaDB semantic search
├── rule_engine.py          # Legal verification (CORE LOGIC)
├── deviation_engine.py     # Fair template comparison
├── risk_score.py           # Risk scoring
├── explanation.py          # ELI5 explanations
├── privacy_ttl.py          # Auto-delete sessions
├── utils.py                # Utility functions
├── requirements.txt        # Python dependencies
└── data/
    ├── indian_laws.json    # Indian law sections
    └── fair_contract.json  # Fair contract standards
```

## 🚀 Setup & Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Install System Dependencies (for OCR)

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### 3. Run the Server

```bash
python app.py
```

Server runs at: `http://localhost:5000`

## 📡 API Endpoints

### 1. Health Check
```
GET /health
```

### 2. Analyze Contract
```
POST /analyze-contract
Content-Type: multipart/form-data

Body:
- file: PDF or DOCX file
```

**Response:**
```json
{
  "session_id": "abc-123",
  "filename": "contract.pdf",
  "total_clauses": 15,
  "overall_risk_score": 67.5,
  "analysis": [
    {
      "clause_id": 1,
      "clause_text": "...",
      "relevant_law": {...},
      "legal_check": {...},
      "deviation": {...},
      "risk_score": 85,
      "explanation": "..."
    }
  ]
}
```

### 3. Get Session
```
GET /session/<session_id>
```

### 4. Delete Session
```
DELETE /session/<session_id>
```

## 🔍 How It Works

### Step 1: Extract Text
- Extracts text from PDF/DOCX
- Falls back to OCR if needed
- In-memory processing (no files saved)

### Step 2: Split into Clauses
- Uses regex patterns to identify clause boundaries
- Filters out noise and headers
- Returns clean clause list

### Step 3: Legal Analysis (PER CLAUSE)

#### 3a. Find Relevant Law
- Uses sentence-transformers to embed clause
- Searches ChromaDB for most relevant Indian law section
- Returns Section 27, 23, 74, etc.

#### 3b. Rule Engine (CORE)
Checks for violations:
- **Section 27**: Non-compete (VOID in India)
- **Section 23**: Unlawful object
- **Section 74**: Excessive penalty
- **IP Overreach**: Too broad IP assignment
- **Unfair Terms**: One-sided clauses

#### 3c. Deviation Check
Compares against fair template:
- Duration (notice period, contract term)
- Penalties (percentages, amounts)
- IP scope
- Termination terms

#### 3d. Risk Score
Weighted combination:
- Legal invalidity: 50%
- Deviation: 30%
- Frequency: 20%

#### 3e. Explanation
Generates ELI5 explanation:
- What clause means
- Legal context
- Issues found
- Disclaimer

### Step 4: Return Results
- JSON response with all analysis
- Session stored with TTL (auto-delete after 30 min)

## 🎯 Key Features

### ✅ Privacy First
- **No persistent storage** - all in-memory
- **Auto-delete** - sessions expire after 30 minutes
- **No file saving** - documents processed in memory only

### ✅ Legal Accuracy
- Based on **Indian Contract Act, 1872**
- Deterministic rule engine (no AI hallucination)
- Citations to specific sections

### ✅ User-Friendly
- ELI5 explanations
- Risk scores (0-100)
- Color-coded severity
- Recommendations

## 🔧 Configuration

Edit `config.py` to customize:

```python
SESSION_TTL_MINUTES = 30  # Session expiry
MAX_FILE_SIZE_MB = 10     # Max upload size
RISK_WEIGHTS = {          # Risk calculation weights
    "legal_invalidity": 0.5,
    "deviation_severity": 0.3,
    "frequency_factor": 0.2
}
```

## 🧪 Testing

### Test with cURL

```bash
# Analyze a contract
curl -X POST http://localhost:5000/analyze-contract \
  -F "file=@contract.pdf"

# Check health
curl http://localhost:5000/health
```

### Test with Python

```python
import requests

url = "http://localhost:5000/analyze-contract"
files = {"file": open("contract.pdf", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## 📚 Legal Basis

### Sections Covered

1. **Section 10** - Valid contract requirements
2. **Section 16** - Undue influence
3. **Section 19** - Voidable contracts
4. **Section 23** - Unlawful consideration/object
5. **Section 27** - Restraint of trade (non-compete)
6. **Section 28** - Restraint of legal proceedings
7. **Section 74** - Penalty clauses
8. **Copyright Act** - IP assignment

## 🔒 Security Notes

- No API authentication (add JWT/OAuth for production)
- No rate limiting (add for production)
- CORS enabled (restrict domains for production)
- Input validation present
- No persistent logs of documents

## 🚨 Important Disclaimers

⚠️ **This tool provides educational information, NOT legal advice**

- Always consult a qualified lawyer
- Laws and interpretations may vary
- Contract analysis is complex
- This is a starting point, not final answer

## 🤝 Integration with Next.js Frontend

The backend is CORS-enabled and ready to connect to your Next.js frontend.

### Example Frontend Code:

```typescript
// Next.js API route or client component
const analyzeContract = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:5000/analyze-contract', {
    method: 'POST',
    body: formData,
  });
  
  return await response.json();
};
```

## 📝 TODO / Future Enhancements

- [ ] Add authentication (JWT)
- [ ] Add rate limiting
- [ ] Integrate real LLM for explanations
- [ ] Add more Indian laws (Labour laws, etc.)
- [ ] Support more file formats
- [ ] Add clause comparison feature
- [ ] Generate reports (PDF export)
- [ ] Add analytics dashboard

## 📄 License

MIT License - See LICENSE file

## 👥 Contributing

1. Fork the repo
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📞 Support

For issues or questions, please open a GitHub issue.