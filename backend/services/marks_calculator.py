def calculate_potential_marks(cert_type, category, participation):
    """
    Calculates the suggested grace marks based on certificate details.
    """
    marks = 0

    try:
        if cert_type == 'Sports':
            if 'South Zone' in category:
                if 'First' in participation: marks = 5
                elif 'Second' in participation: marks = 4
                elif 'Third' in participation: marks = 3
                elif 'Participation' in participation: marks = 2
            elif 'All India' in category:
                if 'First' in participation: marks = 7
                elif 'Second' in participation: marks = 6
                elif 'Third' in participation: marks = 5
                elif 'Participation' in participation: marks = 3
        
        elif cert_type == 'Cultural':
            if 'South Zone' in category:
                if 'First' in participation: marks = 5
                elif 'Second' in participation: marks = 4
                elif 'Third' in participation: marks = 3
                elif 'Participation' in participation: marks = 2
            elif 'All India' in category:
                if 'First' in participation: marks = 7
                elif 'Second' in participation: marks = 6
                elif 'Third' in participation: marks = 5
                elif 'Participation' in participation: marks = 3

        elif cert_type == 'Technical':
            if 'National' in category:
                if 'First' in participation: marks = 6
                elif 'Second' in participation: marks = 5
                elif 'Third' in participation: marks = 4
            elif 'International' in category:
                if 'First' in participation: marks = 8
                elif 'Second' in participation: marks = 7
                elif 'Third' in participation: marks = 6
        
        elif cert_type == 'Amma Service':
            if 'Ashram' in category: marks = 3
            elif 'Disaster' in category: marks = 5
        
        elif cert_type == 'Research Paper':
            # As per the document, this is 10 marks per paper.
            marks = 10

    except Exception:
        # Return 0 if any error occurs
        return 0

    return marks