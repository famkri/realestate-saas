import React, { useState, useEffect } from 'react';
import Login from './components/Login';
import Listings from './components/Listings';
import './App.css';

function App() {
  const [token, setToken] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
    }
  }, []);

  return (
    <div className="App">
      {token ? (
        <Listings token={token} />
      ) : (
        <Login setToken={setToken} />
      )}
    </div>
  );
}

export default App;
