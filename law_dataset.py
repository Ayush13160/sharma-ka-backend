import json
import os
from config import INDIAN_LAWS_JSON

def load_indian_laws():
    """
    Load Indian law sections from JSON file
    
    Returns:
        list: List of law objects with structure:
        {
            "section": "Section 27",
            "act": "Indian Contract Act, 1872",
            "title": "Agreement in restraint of trade",
            "text": "Full legal text...",
            "summary": "Brief summary..."
        }
    """
    try:
        # Check if file exists
        if not os.path.exists(INDIAN_LAWS_JSON):
            print(f"Warning: {INDIAN_LAWS_JSON} not found. Using default laws.")
            return get_default_laws()
        
        with open(INDIAN_LAWS_JSON, 'r', encoding='utf-8') as f:
            laws = json.load(f)
        
        return laws
    
    except Exception as e:
        print(f"Error loading laws: {str(e)}")
        return get_default_laws()

def get_default_laws():
    """
    Return default set of critical Indian Contract Act sections
    Used as fallback if JSON file is missing
    """
    return [
        {
            "section": "Section 10",
            "act": "Indian Contract Act, 1872",
            "title": "What agreements are contracts",
            "text": "All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void.",
            "summary": "Defines essential elements of a valid contract: free consent, competent parties, lawful consideration, and lawful object."
        },
        {
            "section": "Section 23",
            "act": "Indian Contract Act, 1872",
            "title": "What considerations and objects are unlawful",
            "text": "The consideration or object of an agreement is unlawful if it is forbidden by law, or is of such a nature that, if permitted, it would defeat the provisions of any law, or is fraudulent, or involves or implies injury to the person or property of another, or the Court regards it as immoral or opposed to public policy.",
            "summary": "Agreements with unlawful consideration or object are void. This includes illegal activities, fraud, injury to others, immoral acts, or violations of public policy."
        },
        {
            "section": "Section 27",
            "act": "Indian Contract Act, 1872",
            "title": "Agreement in restraint of trade",
            "text": "Every agreement by which anyone is restrained from exercising a lawful profession, trade or business of any kind, is to that extent void. Exception: One who sells the goodwill of a business may agree with the buyer to refrain from carrying on a similar business, within specified local limits.",
            "summary": "Non-compete agreements that prevent someone from working in their profession are void in India, except in cases of business sale with goodwill."
        },
        {
            "section": "Section 28",
            "act": "Indian Contract Act, 1872",
            "title": "Agreement in restraint of legal proceedings",
            "text": "Every agreement, by which any party thereto is restricted absolutely from enforcing his rights under or in respect of any contract, by the usual legal proceedings in the ordinary tribunals, or which limits the time within which he may thus enforce his rights, is void to that extent.",
            "summary": "Agreements that prevent parties from taking legal action are void."
        },
        {
            "section": "Section 74",
            "act": "Indian Contract Act, 1872",
            "title": "Compensation for breach of contract where penalty stipulated for",
            "text": "When a contract has been broken, if a sum is named in the contract as the amount to be paid in case of such breach, or if the contract contains any other stipulation by way of penalty, the party complaining of the breach is entitled, whether or not actual damage or loss is proved to have been caused thereby, to receive from the party who has broken the contract reasonable compensation not exceeding the amount so named or, as the case may be, the penalty stipulated for.",
            "summary": "Penalty clauses must be reasonable compensation for actual losses, not punitive. Courts can reduce excessive penalties."
        },
        {
            "section": "Section 16",
            "act": "Indian Contract Act, 1872",
            "title": "Undue influence",
            "text": "A contract is said to be induced by 'undue influence' where the relations subsisting between the parties are such that one of the parties is in a position to dominate the will of the other and uses that position to obtain an unfair advantage.",
            "summary": "Contracts obtained through undue influence (dominating the other party's will) are voidable."
        },
        {
            "section": "Section 19",
            "act": "Indian Contract Act, 1872",
            "title": "Voidability of agreements without free consent",
            "text": "When consent to an agreement is caused by coercion, fraud, or misrepresentation, the agreement is a contract voidable at the option of the party whose consent was so caused.",
            "summary": "Contracts made without free consent (due to coercion, fraud, or misrepresentation) can be canceled by the affected party."
        },
        {
            "section": "Section 64",
            "act": "Indian Copyright Act, 1957",
            "title": "Assignment of copyright",
            "text": "The owner of the copyright in an existing work or the prospective owner of the copyright in a future work may assign to any person the copyright either wholly or partially and for a limited period or for the duration of the copyright.",
            "summary": "Copyright can be assigned, but any assignment must be clearly defined in scope and duration."
        }
    ]

def get_law_by_section(section_number):
    """
    Get specific law by section number
    
    Args:
        section_number: str (e.g., "Section 27", "27")
    
    Returns:
        dict or None
    """
    laws = load_indian_laws()
    
    # Normalize section number
    section_number = section_number.strip().lower()
    if not section_number.startswith('section'):
        section_number = f'section {section_number}'
    
    for law in laws:
        if law['section'].lower() == section_number:
            return law
    
    return None