import pandas as pd
import random

def generate_sample_questions():
    """
    Generate sample questions for the feedback survey with four options each
    and save them to an Excel file.
    """
    # Define categories
    categories = ["Cultural", "Development", "Ways of Working"]
    
    # Sample questions for each category
    cultural_questions = [
        "How satisfied are you with the company culture?",
        "How well does the organization promote diversity and inclusion?",
        "To what extent do you feel valued as a team member?",
        "How comfortable are you providing feedback to management?",
        "How well does the company maintain work-life balance?"
    ]
    
    development_questions = [
        "How satisfied are you with the learning opportunities provided?",
        "How effective are the training programs in enhancing your skills?",
        "How well does your manager support your career development?",
        "To what extent do you feel challenged in your current role?",
        "How clear is your career progression path?"
    ]
    
    ways_of_working_questions = [
        "How effective are the team meetings?",
        "How well does collaboration work within your team?",
        "How satisfied are you with the communication across departments?",
        "How well does the company implement feedback from employees?",
        "How efficient are the current tools and processes for your job?"
    ]
    
    # Option templates - these will be customized for each question
    option_templates = [
        # Template for first option (usually negative)
        ["Not at all satisfied", "Very poor", "Not at all", "Highly ineffective", "Very unclear"],
        # Template for second option (usually somewhat negative)
        ["Somewhat dissatisfied", "Poor", "To a small extent", "Ineffective", "Unclear"],
        # Template for third option (usually somewhat positive)
        ["Somewhat satisfied", "Good", "To a moderate extent", "Effective", "Clear"],
        # Template for fourth option (usually very positive)
        ["Very satisfied", "Excellent", "To a great extent", "Highly effective", "Very clear"]
    ]
    
    # Create a list to hold all question data
    all_questions = []
    question_id = 1
    
    # Generate questions for each category
    for category, questions in [
        ("Cultural", cultural_questions),
        ("Development", development_questions),
        ("Ways of Working", ways_of_working_questions)
    ]:
        for question in questions:
            # Randomly select a set of option templates
            option_set_idx = random.randint(0, len(option_templates[0]) - 1)
            
            # Create options based on templates
            options = [template[option_set_idx] for template in option_templates]
            
            question_data = {
                "QuestionID": f"Q{question_id:02d}",
                "Category": category,
                "Question": question,
                "Option1": options[0],
                "Option2": options[1],
                "Option3": options[2],
                "Option4": options[3]
            }
            
            all_questions.append(question_data)
            question_id += 1
    
    # Create DataFrame and save to Excel
    questions_df = pd.DataFrame(all_questions)
    questions_df.to_excel("survey_questions.xlsx", index=False)
    
    print(f"Generated {len(all_questions)} sample questions and saved to survey_questions.xlsx")
    return questions_df

if __name__ == "__main__":
    generate_sample_questions()