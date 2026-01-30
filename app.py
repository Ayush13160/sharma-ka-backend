from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from flask import send_from_directory

import os
import traceback
from datetime import datetime

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
from contract_summary import generate_contract_summary
from ai_engine import get_ai_risk_explanation
import json


app = Flask(__name__)
CORS(app)

# -----------------------------
# Swagger Configuration
SWAGGER_URL = "/swagger"
API_URL = "/swagger.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        "app_name": "AI Legal Sentinel – Contract Analyzer API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route("/swagger.json")
def swagger_spec():
    return {
        "swagger": "2.0",
        "info": {
            "title": "AI Legal Sentinel – Contract Analyzer API",
            "description": "Analyze contracts for illegal, unfair, or risky clauses under Indian law",
            "version": "1.0.0"
        },
        "basePath": "/",
        "schemes": ["http"],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {"200": {"description": "Healthy"}}
                }
            },
            "/analyze-contract": {
                "post": {
                    "summary": "Analyze contract",
                    "consumes": ["multipart/form-data"],
                    "parameters": [
                        {
                            "name": "file",
                            "in": "formData",
                            "type": "file",
                            "required": True
                        }
                    ],
                    "responses": {
                        "200": {"description": "Analysis result"},
                        "400": {"description": "Bad request"}
                    }
                }
            }
        }
    }

# -----------------------------
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "swagger",
            "route": "/swagger.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/swagger",
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "AI Legal Sentinel – Contract Analyzer API",
        "description": "Analyze contracts for illegal, unfair, or risky clauses under Indian law",
        "version": "1.0.0"
    }
}

# -----------------------------
# Initialize components
# -----------------------------
session_manager = SessionManager()
vector_store = None

@app.before_request
def initialize_vector_store():
    global vector_store
    if vector_store is None:
        laws = load_indian_laws()
        vector_store = VectorStore(laws)

# -----------------------------
# Health Check
# -----------------------------
@app.route('/health', methods=['GET'])
def health_check():
    """
    Health Check
    ---
    responses:
      200:
        description: Backend is healthy
    """
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    })

# -----------------------------
# Analyze Contract
# -----------------------------
@app.route('/analyze-contract', methods=['POST'])
def analyze_contract():
    """
    Analyze Contract
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: PDF or DOCX contract file
    responses:
      200:
        description: Contract analysis result
      400:
        description: Invalid input
      500:
        description: Internal server error
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "Empty filename"}), 400

        allowed_extensions = {'.pdf', '.docx', '.doc'}
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in allowed_extensions:
            return jsonify({"error": "Unsupported file type"}), 400

        session_id = session_manager.create_session()

        text = extract_text(file, file_ext)
        if not text or len(text.strip()) < 50:
            return jsonify({"error": "Insufficient text extracted"}), 400

        clauses = split_clauses(text)
        if not clauses:
            return jsonify({"error": "No clauses found"}), 400

        results = []

        for idx, clause_text in enumerate(clauses):
            relevant_law = vector_store.find_relevant_law(clause_text)
            legal_check = verify_clause(clause_text, relevant_law)
            deviation = check_deviation(clause_text)
            risk = calculate_risk_score(legal_check, deviation)
            explanation = generate_explanation(clause_text, legal_check, relevant_law)

            results.append({
                "clause_id": idx + 1,
                "clause_text": clause_text,
                "relevant_law": relevant_law,
                "legal_check": legal_check,
                "deviation": deviation,
                "risk_score": risk,
                "explanation": explanation
            })

        overall_risk = sum(r["risk_score"] for r in results) / len(results)
        contract_summary = generate_contract_summary(results, overall_risk)

        # -----------------------------
        # AI EXPLANATION (DeepSeek)
        # -----------------------------
        try:
            ai_response_raw = get_ai_risk_explanation(
                document_risk=contract_summary,
                analysis=results
            )
            ai_response = json.loads(ai_response_raw)
        except Exception as ai_error:
            ai_response = {
                "error": "AI service unavailable",
                "details": str(ai_error)
            }

        session_manager.store_analysis(session_id, {
            "filename": file.filename,
            "results": results,
            "overall_risk": overall_risk,
            "summary": contract_summary
        })

        return jsonify({
            "session_id": session_id,
            "filename": file.filename,
            "total_clauses": len(results),
            "overall_risk_score": round(overall_risk, 2),
            "rule_based_summary": contract_summary,
            "ai_risk_explanation": ai_response,
            "analysis": results,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

# -----------------------------
# Session APIs
# -----------------------------
@app.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    data = session_manager.get_session(session_id)
    if data:
        return jsonify(data)
    return jsonify({"error": "Session not found"}), 404

@app.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    session_manager.delete_session(session_id)
    return jsonify({"message": "Session deleted"})

# -----------------------------
# Run Server
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
