import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [result, setResult] = useState(null);

  // The function to call Flask and fetch the route data
  const getRoute = async () => {
    try {
      // Sending the origin and destination to Flask API
      const res = await axios.post('http://localhost:5000/optimize-route', {
        from,
        to,
      });
      // Updating state with the response data (route, distance, ETA, cost)
      setResult(res.data);
    } catch (err) {
      // In case of error, show this message
      setResult({ error: "Could not fetch route. Make sure backend is running." });
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h2>🚛 Route Optimizer</h2>
      <input
        value={from}
        onChange={e => setFrom(e.target.value)}
        placeholder="Origin"
        style={{ marginRight: '1rem' }}
      />
      <input
        value={to}
        onChange={e => setTo(e.target.value)}
        placeholder="Destination"
      />
      <br /><br />
      <button onClick={getRoute}>Get Route</button>

      {result && !result.error && (
        <div style={{ marginTop: '1rem' }}>
          <p>📍 Route: {result.route}</p>
          <p>🛣️ Distance: {result.distance_km} km</p>
          <p>⏱️ ETA: {result.eta_hours} hours</p>
          <p>💸 Estimated Cost: ${result.estimated_cost_usd}</p>
        </div>
      )}

      {result?.error && (
        <p style={{ color: 'red', marginTop: '1rem' }}>{result.error}</p>
      )}
    </div>
  );
}

export default App;

