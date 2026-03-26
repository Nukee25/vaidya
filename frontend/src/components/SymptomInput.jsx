import React, { useState, useMemo } from 'react';

export default function SymptomInput({ symptoms, selectedSymptoms, onToggle, onPredict, loading }) {
  const [search, setSearch] = useState('');

  const filtered = useMemo(() => {
    const q = search.toLowerCase().trim();
    if (!q) return symptoms;
    return symptoms.filter((s) => s.name.toLowerCase().includes(q));
  }, [symptoms, search]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') e.preventDefault();
  };

  return (
    <div className="card symptom-panel">
      <h2>Select Your Symptoms</h2>
      <p className="subtitle">Choose all symptoms you are experiencing, then click Predict.</p>

      {/* Selected symptom tags */}
      {selectedSymptoms.length > 0 && (
        <div className="selected-symptoms" aria-label="Selected symptoms">
          {selectedSymptoms.map((s) => (
            <span key={s} className="symptom-tag">
              {s}
              <button
                onClick={() => onToggle(s)}
                aria-label={`Remove ${s}`}
                title={`Remove ${s}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Search */}
      <div className="search-box">
        <span className="search-icon" aria-hidden="true">🔍</span>
        <input
          type="text"
          placeholder="Search symptoms…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onKeyDown={handleKeyDown}
          aria-label="Search symptoms"
        />
      </div>

      <p className="symptom-count">
        Showing {filtered.length} of {symptoms.length} symptoms
      </p>

      {/* Symptom grid */}
      <div className="symptoms-grid" role="group" aria-label="Available symptoms">
        {filtered.map((symptom) => {
          const isSelected = selectedSymptoms.includes(symptom.name);
          return (
            <label
              key={symptom.id ?? symptom.name}
              className={`symptom-checkbox${isSelected ? ' selected' : ''}`}
            >
              <input
                type="checkbox"
                checked={isSelected}
                onChange={() => onToggle(symptom.name)}
              />
              {symptom.name}
            </label>
          );
        })}
        {filtered.length === 0 && (
          <p style={{ gridColumn: '1/-1', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            No symptoms match your search.
          </p>
        )}
      </div>

      {/* Predict button */}
      <div className="predict-btn-wrapper">
        <span className="selected-count">
          {selectedSymptoms.length === 0
            ? 'No symptoms selected'
            : `${selectedSymptoms.length} symptom${selectedSymptoms.length > 1 ? 's' : ''} selected`}
        </span>
        <button
          className="btn btn-primary"
          onClick={onPredict}
          disabled={selectedSymptoms.length === 0 || loading}
          aria-busy={loading}
        >
          {loading ? (
            <>
              <span className="spinner" style={{ width: '1rem', height: '1rem', margin: 0 }} />
              Analyzing…
            </>
          ) : (
            '🔬 Predict Disease'
          )}
        </button>
      </div>
    </div>
  );
}
