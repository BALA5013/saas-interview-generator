import React, { useState } from 'react';
import axios from 'axios';
import './index.css';

// Using the API Gateway port
const API_URL = 'http://localhost:8000';

function App() {
  const [formData, setFormData] = useState({
    job_role: '',
    experience_level: 'entry',
    difficulty: 'medium'
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!formData.job_role) {
      setError("Please enter a job role.");
      return;
    }
    
    setLoading(true);
    setError(null);
    setResults(null);
    
    try {
      // Connects to the API Gateway which forwards to AI Service
      const response = await axios.post(`${API_URL}/generate-questions`, formData);
      setResults(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to generate questions. Ensure backend services are running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header>
        <h1>InterviewGenius AI</h1>
        <div className="subtitle">AI-Powered Interview Question Generator</div>
      </header>
      
      <div className="container">
        <form onSubmit={handleGenerate}>
          <div className="form-group">
            <label htmlFor="job_role">Target Job Role</label>
            <input 
              type="text" 
              id="job_role"
              name="job_role" 
              placeholder="e.g. Frontend Developer, Data Scientist..." 
              value={formData.job_role}
              onChange={handleChange}
              required
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="experience_level">Experience Level</label>
            <select 
              id="experience_level"
              name="experience_level" 
              value={formData.experience_level}
              onChange={handleChange}
            >
              <option value="intern">Internship</option>
              <option value="entry">Entry Level (0-2 years)</option>
              <option value="mid">Mid Level (3-5 years)</option>
              <option value="senior">Senior (5+ years)</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="difficulty">Difficulty</label>
            <select 
              id="difficulty"
              name="difficulty" 
              value={formData.difficulty}
              onChange={handleChange}
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          
          {error && <div style={{ color: '#ef4444', marginBottom: '1rem' }}>{error}</div>}
          
          <button type="submit" className="btn-generate" disabled={loading}>
            {loading ? <span className="loader"></span> : 'Generate Interview Questions'}
          </button>
        </form>

        {results && results.questions && (
          <div className="results">
            <h2>Generated Questions for {results.job_role} ({results.difficulty})</h2>
            
            <div className="category-card">
              <h3>Technical Questions</h3>
              <ul>
                {results.questions.technical.map((q, idx) => (
                  <li key={`tech-${idx}`}>{q}</li>
                ))}
              </ul>
            </div>
            
            <div className="category-card">
              <h3>HR & Behavioral Questions</h3>
              <ul>
                {results.questions.hr.map((q, idx) => (
                  <li key={`hr-${idx}`}>{q}</li>
                ))}
              </ul>
            </div>
            
            <div className="category-card">
              <h3>Coding / Practical Challenges</h3>
              <ul>
                {results.questions.coding.map((q, idx) => (
                  <li key={`code-${idx}`}>{q}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
