import re
import json
import os
from config import DEVIATION_THRESHOLDS, FAIR_CONTRACT_JSON

def check_deviation(clause_text):
    """
    Compare clause against fair contract template standards
    
    Args:
        clause_text: str - Contract clause
    
    Returns:
        dict: {
            "has_deviation": bool,
            "deviations": list,
            "severity": str,
            "fair_standard": dict
        }
    """
    deviations = []
    
    # Load fair contract standards
    fair_standards = load_fair_contract()
    
    # Check duration deviations (e.g., notice period, contract term)
    duration_deviation = check_duration_deviation(clause_text, fair_standards)
    if duration_deviation:
        deviations.append(duration_deviation)
    
    # Check penalty deviations
    penalty_deviation = check_penalty_deviation(clause_text, fair_standards)
    if penalty_deviation:
        deviations.append(penalty_deviation)
    
    # Check IP scope deviations
    ip_deviation = check_ip_scope_deviation(clause_text, fair_standards)
    if ip_deviation:
        deviations.append(ip_deviation)
    
    # Check termination deviations
    termination_deviation = check_termination_deviation(clause_text, fair_standards)
    if termination_deviation:
        deviations.append(termination_deviation)
    
    # Determine overall severity
    if deviations:
        severity_levels = [d['severity'] for d in deviations]
        if 'critical' in severity_levels:
            severity = 'critical'
        elif 'high' in severity_levels:
            severity = 'high'
        elif 'medium' in severity_levels:
            severity = 'medium'
        else:
            severity = 'low'
    else:
        severity = 'none'
    
    return {
        "has_deviation": len(deviations) > 0,
        "deviations": deviations,
        "severity": severity,
        "total_deviations": len(deviations)
    }

def load_fair_contract():
    """
    Load fair contract template standards
    """
    try:
        if os.path.exists(FAIR_CONTRACT_JSON):
            with open(FAIR_CONTRACT_JSON, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading fair contract: {e}")
    
    # Default fair standards
    return {
        "notice_period_days": 30,
        "probation_months": 3,
        "non_compete_months": 0,  # Should be 0 (invalid in India)
        "penalty_percentage": 10,
        "ip_scope": "work-related only",
        "termination_notice_days": 30,
        "working_hours_per_week": 40
    }

def check_duration_deviation(clause_text, fair_standards):
    """
    Check if duration/time periods deviate from fair standards
    """
    clause_lower = clause_text.lower()
    
    # Extract duration mentions
    duration_patterns = [
        (r'(\d+)\s*months?', 'months'),
        (r'(\d+)\s*years?', 'years'),
        (r'(\d+)\s*days?', 'days')
    ]
    
    for pattern, unit in duration_patterns:
        matches = re.findall(pattern, clause_lower)
        
        if matches:
            duration = int(matches[0])
            
            # Convert to months for comparison
            if unit == 'years':
                duration_months = duration * 12
            elif unit == 'days':
                duration_months = duration / 30
            else:
                duration_months = duration
            
            # Check notice period
            if 'notice' in clause_lower:
                fair_notice_days = fair_standards.get('notice_period_days', 30)
                if unit == 'days' and duration > fair_notice_days * 1.5:
                    return {
                        "type": "excessive_notice_period",
                        "severity": "medium",
                        "actual": f"{duration} {unit}",
                        "fair_standard": f"{fair_notice_days} days",
                        "description": f"Notice period of {duration} days exceeds fair standard of {fair_notice_days} days."
                    }
            
            # Check non-compete (should be 0 in India)
            if 'non-compete' in clause_lower or 'not compete' in clause_lower:
                if duration_months > 0:
                    return {
                        "type": "non_compete_duration",
                        "severity": "critical",
                        "actual": f"{duration} {unit}",
                        "fair_standard": "0 (invalid in India)",
                        "description": "Non-compete clauses are generally unenforceable in India regardless of duration."
                    }
    
    return None

def check_penalty_deviation(clause_text, fair_standards):
    """
    Check if penalty amounts deviate from fair standards
    """
    clause_lower = clause_text.lower()
    
    # Check for penalty mentions
    penalty_keywords = ['penalty', 'liquidated damages', 'damages', 'shall pay']
    has_penalty = any(keyword in clause_lower for keyword in penalty_keywords)
    
    if has_penalty:
        # Extract percentages
        percentages = re.findall(r'(\d+)\s*(?:%|percent)', clause_lower)
        
        if percentages:
            penalty_pct = int(percentages[0])
            fair_pct = fair_standards.get('penalty_percentage', 10)
            
            if penalty_pct > fair_pct * 2:  # More than 2x fair standard
                return {
                    "type": "excessive_penalty",
                    "severity": "high",
                    "actual": f"{penalty_pct}%",
                    "fair_standard": f"≤{fair_pct}%",
                    "description": f"Penalty of {penalty_pct}% significantly exceeds fair standard of {fair_pct}%."
                }
        
        # Check for fixed amounts
        amounts = re.findall(r'(\d+)\s*(?:lakh|lakhs)', clause_lower)
        if amounts and int(amounts[0]) >= 5:  # 5+ lakhs is significant
            return {
                "type": "high_penalty_amount",
                "severity": "medium",
                "actual": f"{amounts[0]} lakhs",
                "fair_standard": "Reasonable compensation only",
                "description": "High fixed penalty amount may be deemed excessive by courts."
            }
    
    return None

def check_ip_scope_deviation(clause_text, fair_standards):
    """
    Check if IP assignment scope is overly broad
    """
    clause_lower = clause_text.lower()
    
    ip_keywords = ['intellectual property', 'ip', 'copyright', 'invention', 'work product']
    has_ip = any(keyword in clause_lower for keyword in ip_keywords)
    
    if has_ip:
        # Check for overreach indicators
        overreach_indicators = [
            ('all work', 'critical'),
            ('any work', 'critical'),
            ('personal projects', 'high'),
            ('outside work', 'high'),
            ('off-duty', 'high'),
            ('perpetual', 'medium'),
            ('irrevocable', 'medium')
        ]
        
        for indicator, severity in overreach_indicators:
            if indicator in clause_lower:
                return {
                    "type": "ip_scope_deviation",
                    "severity": severity,
                    "actual": f"Contains '{indicator}'",
                    "fair_standard": "Work-related IP created during employment only",
                    "description": f"IP clause is overly broad - includes '{indicator}'."
                }
    
    return None

def check_termination_deviation(clause_text, fair_standards):
    """
    Check termination clause fairness
    """
    clause_lower = clause_text.lower()
    
    termination_keywords = ['termination', 'terminate', 'dismissal', 'dismiss']
    has_termination = any(keyword in clause_lower for keyword in termination_keywords)
    
    if has_termination:
        # Check for unfair termination terms
        unfair_indicators = [
            ('without cause', 'high'),
            ('at will', 'high'),
            ('without notice', 'medium'),
            ('immediate termination', 'medium'),
            ('sole discretion', 'medium')
        ]
        
        for indicator, severity in unfair_indicators:
            if indicator in clause_lower:
                return {
                    "type": "unfair_termination",
                    "severity": severity,
                    "actual": f"Contains '{indicator}'",
                    "fair_standard": "Termination with cause and notice",
                    "description": f"Termination clause allows '{indicator}' which may be unfair to employee."
                }
    
    return None

def calculate_deviation_score(deviations):
    """
    Calculate numeric deviation score (0-100)
    """
    if not deviations:
        return 0
    
    severity_weights = {
        'critical': 25,
        'high': 15,
        'medium': 10,
        'low': 5
    }
    
    score = sum(severity_weights.get(d['severity'], 0) for d in deviations)
    
    return min(score, 100)  # Cap at 100