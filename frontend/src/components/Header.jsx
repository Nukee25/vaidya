import React from 'react';

export default function Header() {
  return (
    <header className="header">
      <div className="container">
        <div className="header-inner">
          <div className="header-logo" aria-hidden="true">🩺</div>
          <div className="header-text">
            <h1>Vaidya</h1>
            <p>AI-Powered Disease Prediction</p>
          </div>
        </div>
      </div>
    </header>
  );
}
