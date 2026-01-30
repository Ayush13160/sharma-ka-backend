from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import traceback
from datetime import datetime
from flask_swagger_ui import get_swaggerui_blueprint

# Import pipeline modules
from extractor import extract_text
from clause_splitter import split_clauses
from law_dataset import load_indian_laws
from vector_store import VectorStore
from rule_engine import verify_clause
from deviation_engine import check_deviation
from risk_score import calculate_risk_score
from explanation import generate_explanation
from privacy_ttl import SessionManager

# -------------------------------------------------
# App setup
# -------------------------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------------------------
# Swagger UI setup
# -------------------------------------------------
SWAGGER_URL = "/swagger"
API_URL = "/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "Contract Analysis Backend"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/swagger.json")
def swagger_spec():
    return send_from_directory(".", "swagger.json")

# -------------------------------------------------
# Initialize components
# -------------------------------------------------
session_manager = SessionManager()
vector_store = None

@app.before_request
def initialize_vector_store():
    """Initialize vector store on first request"""
    global vector_store
    if vector_store is None:
        laws = load_indian_laws()
        vector_store = VectorStore(laws)

# -------------------------------------------------
# Routes
# -------------------------------------------------
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/analyze-contract', methods=['POST'])
def analyze_contract():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        allowed_extensions = {'.pdf', '.docx', '.doc'}
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            return jsonify({
                "error": f"Unsupported file type. Allowed: {allowed_extensions}"
            }), 400

        session_id = session_manager.create_session()

        # STEP 1: Extract text
        text = extract_text(file, file_ext)
        if not text or len(text.strip()) < 50:
            return jsonify({"error": "Insufficient text extracted"}), 400

        # STEP 2: Split clauses
        clauses = split_clauses(text)
        if not clauses:
            return jsonify({"error": "No clauses found"}), 400

        results = []

        for idx, clause_text in enumerate(clauses, start=1):
            relevant_law = vector_store.find_relevant_law(clause_text)
            legal_check = verify_clause(clause_text, relevant_law)
            deviation = check_deviation(clause_text)
            risk_score = calculate_risk_score(legal_check, deviation)
            explanation = generate_explanation(
                clause_text, legal_check, relevant_law
            )

            results.append({
                "clause_id": idx,
                "clause_text": clause_text[:200] + "..." if len(clause_text) > 200 else clause_text,
                "full_clause": clause_text,
                "relevant_law": relevant_law,
                "legal_check": legal_check,
                "deviation": deviation,
                "risk_score": risk_score,
                "explanation": explanation
            })

        overall_risk = (
            sum(r["risk_score"] for r in results) / len(results)
            if results else 0
        )

        session_manager.store_analysis(session_id, {
            "filename": file.filename,
            "total_clauses": len(results),
            "overall_risk": overall_risk,
            "results": results
        })

        return jsonify({
            "session_id": session_id,
            "filename": file.filename,
            "total_clauses": len(results),
            "overall_risk_score": round(overall_risk, 2),
            "analysis": results,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    data = session_manager.get_session(session_id)
    if data:
        return jsonify(data)
    return jsonify({"error": "Session not found or expired"}), 404

@app.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    session_manager.delete_session(session_id)
    return jsonify({"message": "Session deleted"}), 200

# -------------------------------------------------
# Run app
# -------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
