import React from 'react';

function ConfidenceBar({ value, rank }) {
  const pct = Math.round(value * 100);
  return (
    <div className="confidence-bar-wrap">
      <div className="confidence-label">
        <span>Confidence</span>
        <span>{pct}%</span>
      </div>
      <div className="confidence-bar" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <div className="confidence-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

export default function PredictionResult({ predictions, onReset }) {
  if (!predictions) {
    return (
      <div className="card results-panel">
        <h2>Predictions</h2>
        <div className="empty-state">
          <div className="empty-icon">🏥</div>
          <p>Select your symptoms and click <strong>Predict Disease</strong> to see results.</p>
        </div>
      </div>
    );
  }

  const rankLabel = (i) => ['#1 Most Likely', '#2 Possible', '#3 Also Consider'][i] ?? `#${i + 1}`;
  const rankClass = (i) => ['rank-1', 'rank-2', 'rank-3'][i] ?? 'rank-3';

  return (
    <div className="card results-panel">
      <h2>Prediction Results</h2>

      {predictions.map((p, i) => (
        <div key={p.disease} className={`prediction-card ${rankClass(i)}`}>
          <span className="rank-badge" aria-label={rankLabel(i)}>{i + 1}</span>
          <div className="prediction-disease-name">{p.disease}</div>
          <ConfidenceBar value={p.confidence} rank={i} />
          {p.description && (
            <p className="disease-description">{p.description}</p>
          )}
          {p.precautions && (
            <div className="precautions-section">
              <strong>💊 Precautions</strong>
              {p.precautions}
            </div>
          )}
        </div>
      ))}

      <div className="disclaimer">
        <strong>⚠️ Medical Disclaimer</strong>
        This tool provides general information only and is NOT a substitute for professional
        medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider.
      </div>

      <div className="try-again-btn">
        <button className="btn btn-secondary" onClick={onReset}>
          ↩ Try Again
        </button>
      </div>
    </div>
  );
}
