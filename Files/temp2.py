import pandas as pd
import random

def generate_sample_survey_excel(filename="sample_survey.xlsx", questions_per_section=5):
    """
    Generate a sample Excel file for the survey application with sections
    
    Parameters:
    filename (str): Output Excel filename
    questions_per_section (int): Number of questions per section
    """
    # Sample questions for each section
    survey_questions = {
        "cultural": [
            {
                "Question": "How strongly do you agree that the company values align with your personal values?",
                "Option1": "Strongly Disagree",
                "Option2": "Disagree",
                "Option3": "Agree",
                "Option4": "Strongly Agree"
            },
            {
                "Question": "How inclusive is the workplace culture?",
                "Option1": "Not inclusive at all",
                "Option2": "Somewhat inclusive",
                "Option3": "Very inclusive",
                "Option4": "Extremely inclusive"
            },
            {
                "Question": "How satisfied are you with the work-life balance in the company?",
                "Option1": "Very Dissatisfied",
                "Option2": "Dissatisfied",
                "Option3": "Satisfied",
                "Option4": "Very Satisfied"
            },
            {
                "Question": "How well does management recognize employee achievements?",
                "Option1": "Poorly",
                "Option2": "Adequately",
                "Option3": "Well",
                "Option4": "Exceptionally Well"
            },
            {
                "Question": "How comfortable do you feel expressing your opinions in team meetings?",
                "Option1": "Not comfortable at all",
                "Option2": "Somewhat comfortable",
                "Option3": "Comfortable",
                "Option4": "Very comfortable"
            },
            {
                "Question": "How would you rate the level of collaboration between departments?",
                "Option1": "Poor",
                "Option2": "Fair",
                "Option3": "Good",
                "Option4": "Excellent"
            },
            {
                "Question": "How effectively does the company communicate its goals and strategies?",
                "Option1": "Not effectively at all",
                "Option2": "Somewhat effectively",
                "Option3": "Effectively",
                "Option4": "Very effectively"
            },
            {
                "Question": "How strongly do you feel that diverse perspectives are valued?",
                "Option1": "Not valued at all",
                "Option2": "Somewhat valued",
                "Option3": "Valued",
                "Option4": "Highly valued"
            }
        ],
        "development": [
            {
                "Question": "How satisfied are you with the professional development opportunities?",
                "Option1": "Very Dissatisfied",
                "Option2": "Dissatisfied",
                "Option3": "Satisfied",
                "Option4": "Very Satisfied"
            },
            {
                "Question": "How clear is your career path within the company?",
                "Option1": "Not clear at all",
                "Option2": "Somewhat clear",
                "Option3": "Clear",
                "Option4": "Very clear"
            },
            {
                "Question": "How useful has the feedback from your manager been for your growth?",
                "Option1": "Not useful at all",
                "Option2": "Somewhat useful",
                "Option3": "Useful",
                "Option4": "Very useful"
            },
            {
                "Question": "How well does the company support learning new skills?",
                "Option1": "Poorly",
                "Option2": "Adequately",
                "Option3": "Well",
                "Option4": "Exceptionally Well"
            },
            {
                "Question": "How often do you have opportunity to work on challenging projects?",
                "Option1": "Never",
                "Option2": "Rarely",
                "Option3": "Sometimes",
                "Option4": "Often"
            },
            {
                "Question": "How satisfied are you with the mentoring available to you?",
                "Option1": "Very Dissatisfied",
                "Option2": "Dissatisfied",
                "Option3": "Satisfied",
                "Option4": "Very Satisfied"
            },
            {
                "Question": "How well do performance evaluations reflect your actual contribution?",
                "Option1": "Poorly",
                "Option2": "Adequately",
                "Option3": "Well",
                "Option4": "Very Well"
            },
            {
                "Question": "How accessible are training resources when you need them?",
                "Option1": "Not accessible",
                "Option2": "Somewhat accessible",
                "Option3": "Accessible",
                "Option4": "Very accessible"
            }
        ],
        "ways of working": [
            {
                "Question": "How efficient are team meetings?",
                "Option1": "Not efficient at all",
                "Option2": "Somewhat efficient",
                "Option3": "Efficient",
                "Option4": "Very efficient"
            },
            {
                "Question": "How effective are the current project management tools?",
                "Option1": "Not effective at all",
                "Option2": "Somewhat effective",
                "Option3": "Effective",
                "Option4": "Very effective"
            },
            {
                "Question": "How well do team members communicate with each other?",
                "Option1": "Poorly",
                "Option2": "Adequately",
                "Option3": "Well",
                "Option4": "Exceptionally Well"
            },
            {
                "Question": "How satisfied are you with the decision-making processes?",
                "Option1": "Very Dissatisfied",
                "Option2": "Dissatisfied",
                "Option3": "Satisfied",
                "Option4": "Very Satisfied"
            },
            {
                "Question": "How appropriate is the workload distribution within your team?",
                "Option1": "Very inappropriate",
                "Option2": "Somewhat inappropriate",
                "Option3": "Appropriate",
                "Option4": "Very appropriate"
            },
            {
                "Question": "How clearly defined are the roles and responsibilities in your team?",
                "Option1": "Not clear at all",
                "Option2": "Somewhat clear",
                "Option3": "Clear",
                "Option4": "Very clear"
            },
            {
                "Question": "How effectively does your team handle conflicts or disagreements?",
                "Option1": "Not effectively at all",
                "Option2": "Somewhat effectively",
                "Option3": "Effectively",
                "Option4": "Very effectively"
            },
            {
                "Question": "How well does remote/hybrid work function in your team?",
                "Option1": "Poorly",
                "Option2": "Adequately",
                "Option3": "Well",
                "Option4": "Exceptionally Well"
            }
        ]
    }
    
    # Create the full dataset
    all_questions = []
    
    for section, questions in survey_questions.items():
        # Select the requested number of questions per section
        # If more requested than available, use all and cycle through
        section_questions = []
        for i in range(questions_per_section):
            question_idx = i % len(questions)
            question_copy = questions[question_idx].copy()
            question_copy["Section"] = section
            section_questions.append(question_copy)
        
        all_questions.extend(section_questions)
    
    # Shuffle questions (optional)
    # random.shuffle(all_questions)
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(all_questions)
    df.to_excel(filename, index=False)
    
    print(f"Sample survey with {len(all_questions)} questions "
          f"({questions_per_section} per section) has been created as '{filename}'")
    return filename

if __name__ == "__main__":
    generate_sample_survey_excel()