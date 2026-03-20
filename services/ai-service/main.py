from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
import os
import json
from google import genai
from google.genai import types

app = FastAPI(title="AI Question Generator Service")

class QuestionRequest(BaseModel):
    job_role: str
    experience_level: str
    difficulty: str

# Static database of questions to simulate AI generation
STATIC_QUESTIONS = {
    "software engineer": {
        "technical": ["Explain the difference between threading and multiprocessing.", "How does garbage collection work in your primary language?", "Design a URL shortener system."],
        "hr": ["Tell me about a time you had a conflict with a teammate.", "Where do you see yourself in 5 years?", "Why do you want to work here?"],
        "coding": ["Reverse a linked list.", "Find the longest palindromic substring.", "Implement LRU Cache."]
    },
    "data scientist": {
        "technical": ["Explain the bias-variance tradeoff.", "How does a Random Forest work?", "What is the difference between L1 and L2 regularization?"],
        "hr": ["Describe a time you had to explain complex data to a non-technical audience.", "What is your greatest strength?", "How do you prioritize your work?"],
        "coding": ["Implement a quicksort algorithm.", "Write an SQL query to find the 2nd highest salary.", "Find duplicates in an array in O(n) time."]
    },
    "default": {
        "technical": ["What are the core responsibilities of this role as you understand them?", "Describe a challenging technical problem you solved.", "How do you keep your skills updated?"],
        "hr": ["Why are you leaving your current job?", "What are your salary expectations?", "Do you have any questions for us?"],
        "coding": ["Write a function to check if a string is a palindrome.", "FizzBuzz", "Find the maximum element in an array."]
    }
}

@app.post("/generate")
async def generate_questions(request: QuestionRequest):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not set. Falling back to static questions.")
        return fallback_generate(request)

    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Generate interview questions for a {request.experience_level} level {request.job_role}.
        The difficulty should be {request.difficulty}.
        
        Provide the response in the following JSON format ONLY:
        {{
            "technical": ["question 1", "question 2", "question 3"],
            "hr": ["question 1", "question 2"],
            "coding": ["challenge 1", "challenge 2"]
        }}
        Ensure the questions are highly relevant to the specific domain and role. If coding challenges are not applicable to the role, provide practical situational challenges instead in the "coding" array.
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        
        questions_data = json.loads(response.text)
        
        return {
            "job_role": request.job_role,
            "experience_level": request.experience_level,
            "difficulty": request.difficulty,
            "questions": questions_data
        }
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        print("Falling back to static questions.")
        return fallback_generate(request)

def fallback_generate(request: QuestionRequest):
    role = request.job_role.lower()
    
    # Find matching role or use default
    role_key = next((k for k in STATIC_QUESTIONS.keys() if k in role), "default")
    
    question_bank = STATIC_QUESTIONS[role_key]
    
    # Just select a random subset for the demo
    return {
        "job_role": request.job_role,
        "experience_level": request.experience_level,
        "difficulty": request.difficulty,
        "questions": {
            "technical": random.sample(question_bank["technical"], min(3, len(question_bank["technical"]))),
            "hr": random.sample(question_bank["hr"], min(2, len(question_bank["hr"]))),
            "coding": random.sample(question_bank["coding"], min(2, len(question_bank["coding"])))
        }
    }
