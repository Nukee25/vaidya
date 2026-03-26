import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import Header from './components/Header';
import SymptomInput from './components/SymptomInput';
import PredictionResult from './components/PredictionResult';
import './index.css';

export default function App() {
  const [symptoms, setSymptoms] = useState([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState([]);
  const [predictions, setPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [symptomsLoading, setSymptomsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch symptom list from the backend
  useEffect(() => {
    axios
      .get('/api/symptoms/')
      .then((res) => setSymptoms(res.data))
      .catch(() =>
        setError('Could not load symptoms. Make sure the backend is running.')
      )
      .finally(() => setSymptomsLoading(false));
  }, []);

  const handleToggle = useCallback((name) => {
    setSelectedSymptoms((prev) =>
      prev.includes(name) ? prev.filter((s) => s !== name) : [...prev, name]
    );
  }, []);

  const handlePredict = useCallback(async () => {
    if (selectedSymptoms.length === 0) return;
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post('/api/predict/', { symptoms: selectedSymptoms });
      setPredictions(res.data.predictions);
    } catch (err) {
      const msg =
        err.response?.data?.error
          ? JSON.stringify(err.response.data.error)
          : 'Prediction failed. Please try again.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, [selectedSymptoms]);

  const handleReset = useCallback(() => {
    setPredictions(null);
    setSelectedSymptoms([]);
    setError(null);
  }, []);

  return (
    <div className="app">
      <Header />
      <main className="app-main">
        <div className="container">
          {symptomsLoading ? (
            <div className="spinner" role="status" aria-label="Loading symptoms" />
          ) : (
            <>
              {error && (
                <div className="alert-error" role="alert">
                  {error}
                </div>
              )}
              <div className="two-panel" style={{ marginTop: '2rem' }}>
                <SymptomInput
                  symptoms={symptoms}
                  selectedSymptoms={selectedSymptoms}
                  onToggle={handleToggle}
                  onPredict={handlePredict}
                  loading={loading}
                />
                <PredictionResult predictions={predictions} onReset={handleReset} />
              </div>
            </>
          )}
        </div>
      </main>
      <footer className="footer">
        <div className="container">
          Vaidya © {new Date().getFullYear()} — For educational purposes only. Not medical advice.
        </div>
      </footer>
    </div>
  );
}
