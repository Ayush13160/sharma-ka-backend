import re
from config import SEVERITY_SCORES

def verify_clause(clause_text, relevant_law=None):
    """
    CORE LEGAL VERIFICATION ENGINE
    Deterministic rule-based checking against Indian Contract Act
    
    Args:
        clause_text: str - Contract clause to verify
        relevant_law: dict - Most relevant law from vector store
    
    Returns:
        dict: {
            "is_valid": bool,
            "violations": list of violation dicts,
            "risk_level": str,
            "applicable_sections": list
        }
    """
    violations = []
    applicable_sections = []
    
    # RULE 1: Check Section 27 - Non-Compete Violations
    section_27_violation = check_section_27(clause_text)
    if section_27_violation:
        violations.append(section_27_violation)
        applicable_sections.append("Section 27")
    
    # RULE 2: Check Section 23 - Unlawful Object
    section_23_violation = check_section_23(clause_text)
    if section_23_violation:
        violations.append(section_23_violation)
        applicable_sections.append("Section 23")
    
    # RULE 3: Check Section 74 - Excessive Penalty
    section_74_violation = check_section_74(clause_text)
    if section_74_violation:
        violations.append(section_74_violation)
        applicable_sections.append("Section 74")
    
    # RULE 4: Check IP Overreach
    ip_violation = check_ip_overreach(clause_text)
    if ip_violation:
        violations.append(ip_violation)
        applicable_sections.append("Copyright Act / IP Law")
    
    # RULE 5: Check Undue Influence / Unfair Terms
    unfair_violation = check_unfair_terms(clause_text)
    if unfair_violation:
        violations.append(unfair_violation)
        applicable_sections.append("Section 16")
    
    # RULE 6: Check for vague/unclear terms
    clarity_violation = check_clarity(clause_text)
    if clarity_violation:
        violations.append(clarity_violation)
    
    # Determine overall validity
    is_valid = len([v for v in violations if v['severity'] in ['critical', 'high']]) == 0
    
    # Calculate risk level
    if violations:
        max_severity = max([SEVERITY_SCORES.get(v['type'], 0) for v in violations])
        if max_severity >= 85:
            risk_level = "critical"
        elif max_severity >= 60:
            risk_level = "high"
        elif max_severity >= 30:
            risk_level = "medium"
        else:
            risk_level = "low"
    else:
        risk_level = "low"
    
    return {
        "is_valid": is_valid,
        "violations": violations,
        "risk_level": risk_level,
        "applicable_sections": applicable_sections,
        "total_violations": len(violations)
    }

def check_section_27(clause_text):
    """
    Check for Section 27 violations (Non-Compete / Restraint of Trade)
    VOID in India except for business sale with goodwill
    """
    clause_lower = clause_text.lower()
    
    # Keywords indicating non-compete
    non_compete_keywords = [
        'non-compete', 'non compete', 'not compete', 'refrain from engaging',
        'shall not engage', 'prohibited from working', 'restrain from',
        'covenant not to compete', 'restriction on employment'
    ]
    
    has_non_compete = any(keyword in clause_lower for keyword in non_compete_keywords)
    
    if has_non_compete:
        # Check if it's an exception (sale of business/goodwill)
        exception_keywords = ['sale of business', 'goodwill', 'transfer of business']
        is_exception = any(keyword in clause_lower for keyword in exception_keywords)
        
        if not is_exception:
            return {
                "type": "section_27_violation",
                "severity": "critical",
                "law": "Section 27, Indian Contract Act, 1872",
                "description": "Non-compete clause detected. Agreements restraining lawful profession/trade are VOID in India.",
                "recommendation": "Remove or modify clause. Non-compete restrictions are unenforceable except in sale of business."
            }
    
    return None

def check_section_23(clause_text):
    """
    Check for Section 23 violations (Unlawful Object/Consideration)
    """
    clause_lower = clause_text.lower()
    
    # Keywords indicating potentially unlawful object
    unlawful_keywords = [
        'illegal', 'fraudulent', 'defeat the law', 'circumvent',
        'evade', 'money laundering', 'bribe', 'kickback'
    ]
    
    has_unlawful = any(keyword in clause_lower for keyword in unlawful_keywords)
    
    if has_unlawful:
        return {
            "type": "section_23_violation",
            "severity": "critical",
            "law": "Section 23, Indian Contract Act, 1872",
            "description": "Clause may involve unlawful consideration or object.",
            "recommendation": "Remove clause. Agreements with unlawful objects are void."
        }
    
    return None

def check_section_74(clause_text):
    """
    Check for Section 74 violations (Excessive Penalty/Liquidated Damages)
    """
    clause_lower = clause_text.lower()
    
    # Check for penalty/liquidated damages clauses
    penalty_keywords = ['penalty', 'liquidated damages', 'damages', 'compensation for breach']
    has_penalty = any(keyword in clause_lower for keyword in penalty_keywords)
    
    if has_penalty:
        # Extract amounts/percentages
        amounts = re.findall(r'(\d+)\s*(?:lakh|crore|rupees|rs\.?|inr)', clause_lower)
        percentages = re.findall(r'(\d+)\s*(?:%|percent)', clause_lower)
        
        # Check if penalty seems excessive
        is_excessive = False
        
        if percentages:
            for pct in percentages:
                if int(pct) > 20:  # >20% of salary/contract value is often excessive
                    is_excessive = True
        
        # Check for absolute prohibition keywords
        absolute_keywords = ['shall pay', 'must pay', 'liable to pay', 'required to pay']
        is_absolute = any(keyword in clause_lower for keyword in absolute_keywords)
        
        if is_excessive or (amounts and is_absolute):
            return {
                "type": "section_74_violation",
                "severity": "high",
                "law": "Section 74, Indian Contract Act, 1872",
                "description": "Penalty clause may be excessive. Courts award only reasonable compensation, not punitive damages.",
                "recommendation": "Ensure penalty is reasonable estimate of actual loss, not punitive."
            }
    
    return None

def check_ip_overreach(clause_text):
    """
    Check for IP assignment overreach
    """
    clause_lower = clause_text.lower()
    
    # Keywords for IP assignment
    ip_keywords = ['intellectual property', 'ip', 'copyright', 'patent', 'invention', 'creation']
    has_ip = any(keyword in clause_lower for keyword in ip_keywords)
    
    if has_ip:
        # Check for overreach indicators
        overreach_keywords = [
            'all work', 'any work', 'everything created', 'all inventions',
            'automatically assigned', 'perpetual', 'irrevocable', 'worldwide',
            'including personal projects', 'off-duty', 'outside work hours'
        ]
        
        has_overreach = any(keyword in clause_lower for keyword in overreach_keywords)
        
        if has_overreach:
            return {
                "type": "ip_overreach",
                "severity": "medium",
                "law": "Copyright Act, 1957 / Contract Law Principles",
                "description": "IP assignment clause is overly broad. May claim rights to work unrelated to employment.",
                "recommendation": "Limit IP assignment to work created during employment for company purposes only."
            }
    
    return None

def check_unfair_terms(clause_text):
    """
    Check for potentially unfair or one-sided terms
    """
    clause_lower = clause_text.lower()
    
    # Indicators of unfair terms
    unfair_keywords = [
        'at sole discretion', 'sole discretion of company', 'without cause',
        'without reason', 'without notice', 'unilateral right',
        'company may change', 'company reserves the right'
    ]
    
    has_unfair = any(keyword in clause_lower for keyword in unfair_keywords)
    
    if has_unfair:
        return {
            "type": "unfair_terms",
            "severity": "medium",
            "law": "Section 16, Indian Contract Act (Undue Influence) / General Contract Principles",
            "description": "Clause appears one-sided with excessive discretion to one party.",
            "recommendation": "Add mutual consent requirements or reasonable limitations to discretionary powers."
        }
    
    return None

def check_clarity(clause_text):
    """
    Check if clause is clear and unambiguous
    """
    # Very basic checks for clarity
    if len(clause_text) < 20:
        return {
            "type": "unclear_terms",
            "severity": "low",
            "description": "Clause is very short and may lack detail.",
            "recommendation": "Ensure clause has sufficient detail and clarity."
        }
    
    # Check for vague terms
    vague_keywords = ['reasonable time', 'as appropriate', 'if necessary', 'at discretion']
    clause_lower = clause_text.lower()
    
    vague_count = sum(1 for keyword in vague_keywords if keyword in clause_lower)
    
    if vague_count >= 2:
        return {
            "type": "unclear_terms",
            "severity": "low",
            "description": "Clause contains vague terms that may lead to disputes.",
            "recommendation": "Define vague terms more specifically."
        }
    
    return None