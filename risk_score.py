from config import RISK_WEIGHTS, SEVERITY_SCORES

def calculate_risk_score(legal_check, deviation):
    """
    Calculate overall risk score (0-100) for a clause
    Combines:
    - Legal invalidity (from rule_engine)
    - Deviation from fair template (from deviation_engine)
    - Frequency/severity factors
    
    Args:
        legal_check: dict from verify_clause()
        deviation: dict from check_deviation()
    
    Returns:
        float: Risk score 0-100
    """
    # Component 1: Legal invalidity score
    legal_score = calculate_legal_invalidity_score(legal_check)
    
    # Component 2: Deviation severity score
    deviation_score = calculate_deviation_score(deviation)
    
    # Component 3: Frequency factor (how many violations)
    frequency_score = calculate_frequency_score(legal_check, deviation)
    
    # Weighted combination
    weights = RISK_WEIGHTS
    
    risk_score = (
        legal_score * weights['legal_invalidity'] +
        deviation_score * weights['deviation_severity'] +
        frequency_score * weights['frequency_factor']
    )
    
    # Ensure within bounds
    risk_score = max(0, min(100, risk_score))
    
    return round(risk_score, 2)

def calculate_legal_invalidity_score(legal_check):
    """
    Calculate score based on legal violations
    Returns: 0-100
    """
    if not legal_check.get('violations'):
        return 0
    
    violations = legal_check['violations']
    
    # Get maximum severity score from violations
    max_score = 0
    
    for violation in violations:
        violation_type = violation.get('type', '')
        score = SEVERITY_SCORES.get(violation_type, 0)
        max_score = max(max_score, score)
    
    # Apply multiplier if multiple critical violations
    critical_count = sum(1 for v in violations if v.get('severity') == 'critical')
    if critical_count > 1:
        max_score = min(100, max_score * 1.2)  # 20% boost, capped at 100
    
    return max_score

def calculate_deviation_score(deviation):
    """
    Calculate score based on deviation from fair template
    Returns: 0-100
    """
    if not deviation.get('has_deviation'):
        return 0
    
    deviations = deviation.get('deviations', [])
    
    severity_points = {
        'critical': 30,
        'high': 20,
        'medium': 12,
        'low': 5
    }
    
    total_score = 0
    
    for dev in deviations:
        severity = dev.get('severity', 'low')
        total_score += severity_points.get(severity, 0)
    
    # Cap at 100
    return min(total_score, 100)

def calculate_frequency_score(legal_check, deviation):
    """
    Calculate score based on number of issues found
    More issues = higher risk
    Returns: 0-100
    """
    total_issues = 0
    
    # Count legal violations
    if legal_check.get('violations'):
        total_issues += len(legal_check['violations'])
    
    # Count deviations
    if deviation.get('deviations'):
        total_issues += len(deviation['deviations'])
    
    # Scale: 0 issues = 0, 5+ issues = 100
    frequency_score = min(total_issues * 20, 100)
    
    return frequency_score

def get_risk_level(risk_score):
    """
    Convert numeric risk score to categorical level
    
    Returns: "low", "medium", "high", or "critical"
    """
    if risk_score >= 85:
        return "critical"
    elif risk_score >= 60:
        return "high"
    elif risk_score >= 30:
        return "medium"
    else:
        return "low"

def get_risk_color(risk_level):
    """
    Get color code for risk level (for frontend display)
    """
    colors = {
        "low": "#22c55e",      # green
        "medium": "#eab308",   # yellow
        "high": "#f97316",     # orange
        "critical": "#ef4444"  # red
    }
    return colors.get(risk_level, "#6b7280")

def aggregate_document_risk(clause_results):
    """
    Calculate overall document risk from all clause results
    
    Args:
        clause_results: list of clause analysis results
    
    Returns:
        dict: {
            "overall_score": float,
            "risk_level": str,
            "critical_count": int,
            "high_count": int,
            "medium_count": int,
            "low_count": int
        }
    """
    if not clause_results:
        return {
            "overall_score": 0,
            "risk_level": "low",
            "critical_count": 0,
            "high_count": 0,
            "medium_count": 0,
            "low_count": 0
        }
    
    # Calculate average risk score
    total_score = sum(r.get('risk_score', 0) for r in clause_results)
    overall_score = total_score / len(clause_results)
    
    # Count by risk level
    counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    for result in clause_results:
        risk_score = result.get('risk_score', 0)
        level = get_risk_level(risk_score)
        counts[level] += 1
    
    # Determine overall risk level
    # If any critical issues, overall is critical
    if counts['critical'] > 0:
        overall_level = "critical"
    elif counts['high'] > 0:
        overall_level = "high"
    elif counts['medium'] > 0:
        overall_level = "medium"
    else:
        overall_level = "low"
    
    return {
        "overall_score": round(overall_score, 2),
        "risk_level": overall_level,
        "critical_count": counts['critical'],
        "high_count": counts['high'],
        "medium_count": counts['medium'],
        "low_count": counts['low'],
        "total_clauses": len(clause_results)
    }