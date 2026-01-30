import os
from config import LLM_MAX_TOKENS, LLM_TEMPERATURE

def generate_explanation(clause_text, legal_check, relevant_law):
    """
    Generate simple English explanation of clause and legal implications
    Uses LLM with strict guardrails to avoid giving legal advice
    
    Args:
        clause_text: str - Contract clause
        legal_check: dict - Results from rule_engine
        relevant_law: dict - Relevant Indian law section
    
    Returns:
        str: ELI5 explanation
    """
    # Build context
    violations = legal_check.get('violations', [])
    has_violations = len(violations) > 0
    
    # Generate explanation without LLM (deterministic fallback)
    # In production, you can integrate OpenAI/Anthropic API here
    explanation = generate_template_explanation(
        clause_text, 
        violations, 
        relevant_law
    )
    
    return explanation

def generate_template_explanation(clause_text, violations, relevant_law):
    """
    Generate explanation using templates (no LLM needed)
    Safe and predictable
    """
    explanation_parts = []
    
    # Part 1: What the clause says (simplified)
    clause_summary = summarize_clause(clause_text)
    explanation_parts.append(f"**What this clause means:** {clause_summary}")
    
    # Part 2: Legal context
    if relevant_law:
        law_context = f"This relates to {relevant_law['section']} of the {relevant_law['act']}, which deals with {relevant_law['title'].lower()}."
        explanation_parts.append(f"\n\n**Legal context:** {law_context}")
    
    # Part 3: Issues found (if any)
    if violations:
        explanation_parts.append("\n\n**Potential issues:**")
        for idx, violation in enumerate(violations[:3], 1):  # Limit to top 3
            issue_text = explain_violation(violation)
            explanation_parts.append(f"\n{idx}. {issue_text}")
    else:
        explanation_parts.append("\n\n**Assessment:** This clause appears generally fair and doesn't violate major Indian contract law provisions.")
    
    # Part 4: Disclaimer
    disclaimer = "\n\n⚠️ **Note:** This is educational information, not legal advice. Consult a lawyer for your specific situation."
    explanation_parts.append(disclaimer)
    
    return "".join(explanation_parts)

def summarize_clause(clause_text):
    """
    Create simple summary of clause
    """
    clause_lower = clause_text.lower()
    
    # Pattern matching for common clause types
    if 'non-compete' in clause_lower or 'not compete' in clause_lower:
        return "This clause attempts to restrict you from working in similar roles or companies after leaving."
    
    elif 'intellectual property' in clause_lower or 'copyright' in clause_lower:
        return "This clause defines who owns the work, ideas, or creations you produce."
    
    elif 'termination' in clause_lower or 'terminate' in clause_lower:
        return "This clause explains when and how the employment relationship can be ended."
    
    elif 'penalty' in clause_lower or 'liquidated damages' in clause_lower:
        return "This clause specifies financial penalties if the contract is broken."
    
    elif 'notice period' in clause_lower or 'notice' in clause_lower:
        return "This clause defines how much advance notice is required before leaving the job."
    
    elif 'confidentiality' in clause_lower or 'nda' in clause_lower:
        return "This clause requires you to keep certain information private."
    
    else:
        # Generic summary
        return f"This clause covers: {clause_text[:100]}..."

def explain_violation(violation):
    """
    Explain a specific violation in simple terms
    """
    violation_type = violation.get('type', '')
    severity = violation.get('severity', 'low')
    
    # Severity indicator
    severity_emoji = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }
    emoji = severity_emoji.get(severity, '⚪')
    
    # Type-specific explanations
    explanations = {
        'section_27_violation': f"{emoji} **Non-compete restriction**: In India, clauses that prevent you from working in your field are generally not enforceable. You have the right to earn a livelihood.",
        
        'section_23_violation': f"{emoji} **Unlawful purpose**: This clause may involve something illegal or against public policy, making it void.",
        
        'section_74_violation': f"{emoji} **Excessive penalty**: The penalty amount seems unreasonably high. Indian courts typically reduce excessive penalties to actual losses only.",
        
        'ip_overreach': f"{emoji} **Overly broad IP claim**: The company is claiming ownership of too much - potentially including your personal projects or work done outside of work hours.",
        
        'unfair_terms': f"{emoji} **One-sided terms**: This clause gives too much power to one party without reasonable protections for you.",
        
        'unclear_terms': f"{emoji} **Vague language**: The clause uses unclear terms that could lead to different interpretations and disputes.",
    }
    
    base_explanation = explanations.get(
        violation_type, 
        f"{emoji} Potential issue: {violation.get('description', 'Unknown issue')}"
    )
    
    # Add recommendation if available
    recommendation = violation.get('recommendation')
    if recommendation:
        base_explanation += f" **Suggested action:** {recommendation}"
    
    return base_explanation

def generate_llm_explanation(clause_text, violations, relevant_law):
    """
    Generate explanation using LLM (OpenAI/Anthropic)
    Use this if you want dynamic, context-aware explanations
    """
    # This is a placeholder for LLM integration
    # You would call OpenAI API or Anthropic Claude API here
    
    prompt = build_safe_prompt(clause_text, violations, relevant_law)
    
    # Example with OpenAI (uncomment and configure):
    """
    import openai
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": prompt}
        ],
        max_tokens=LLM_MAX_TOKENS,
        temperature=LLM_TEMPERATURE
    )
    
    return response.choices[0].message.content
    """
    
    # For now, return template-based explanation
    return generate_template_explanation(clause_text, violations, relevant_law)

def build_safe_prompt(clause_text, violations, relevant_law):
    """
    Build LLM prompt with strict safety guardrails
    """
    prompt = f"""Explain this contract clause in simple English (ELI5 level):

CLAUSE:
{clause_text[:500]}

LEGAL CONTEXT:
{relevant_law['section'] if relevant_law else 'N/A'}: {relevant_law['title'] if relevant_law else 'N/A'}

ISSUES FOUND:
{', '.join(v.get('description', '') for v in violations) if violations else 'None'}

INSTRUCTIONS:
1. Explain what the clause means in 2-3 simple sentences
2. Mention any legal concerns in plain English
3. DO NOT give specific legal advice
4. DO NOT tell them what to do
5. Always end with: "This is educational information only. Consult a qualified lawyer for advice on your specific situation."
6. Keep it under 150 words
"""
    return prompt

def get_system_prompt():
    """
    System prompt for LLM to enforce safety
    """
    return """You are an educational legal information assistant. Your role is to explain contract clauses in simple English.

STRICT RULES:
- NEVER give legal advice
- NEVER tell users what action to take
- NEVER say "you should" or "you must"
- Always explain in simple, neutral terms
- Always include disclaimer about consulting a lawyer
- Focus on education, not recommendations

You help people understand legal concepts, but you do NOT practice law."""