import React, { useEffect, useState } from 'react';
import api from '../api';

function Listings({ token }) {
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    source: '',
    min_price: '',
    max_price: ''
  });

  const fetchListings = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.source) params.source = filters.source;
      if (filters.min_price) params.min_price = filters.min_price;
      if (filters.max_price) params.max_price = filters.max_price;

      const response = await api.get('/listings', { params });
      setListings(response.data);
    } catch (error) {
      console.error('Error fetching listings:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchListings();
    }
  }, [token]);

  const handleFilterChange = (e) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value
    });
  };

  const handleFilterSubmit = (e) => {
    e.preventDefault();
    fetchListings();
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.reload();
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1>Real Estate Listings</h1>
        <button onClick={handleLogout} style={{ padding: '8px 16px', backgroundColor: '#dc3545', color: 'white', border: 'none' }}>
          Logout
        </button>
      </div>

      {/* Filters */}
      <form onSubmit={handleFilterSubmit} style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
        <div style={{ display: 'flex', gap: '15px', alignItems: 'end' }}>
          <div>
            <label>Source:</label>
            <select name="source" value={filters.source} onChange={handleFilterChange} style={{ padding: '5px', marginLeft: '5px' }}>
              <option value="">All</option>
              <option value="kleinanzeigen">Kleinanzeigen</option>
              <option value="immowelt">Immowelt</option>
              <option value="immobilienscout">Immobilienscout</option>
            </select>
          </div>
          <div>
            <label>Min Price:</label>
            <input 
              type="number" 
              name="min_price" 
              value={filters.min_price} 
              onChange={handleFilterChange}
              style={{ padding: '5px', marginLeft: '5px', width: '100px' }}
            />
          </div>
          <div>
            <label>Max Price:</label>
            <input 
              type="number" 
              name="max_price" 
              value={filters.max_price} 
              onChange={handleFilterChange}
              style={{ padding: '5px', marginLeft: '5px', width: '100px' }}
            />
          </div>
          <button type="submit" style={{ padding: '6px 12px', backgroundColor: '#28a745', color: 'white', border: 'none' }}>
            Filter
          </button>
        </div>
      </form>

      {/* Listings */}
      <div>
        <p>Found {listings.length} listings</p>
        {listings.map((listing, index) => (
          <div key={listing.id || index} style={{ 
            border: '1px solid #ddd', 
            padding: '15px', 
            marginBottom: '10px', 
            borderRadius: '5px',
            backgroundColor: 'white'
          }}>
            <h3 style={{ margin: '0 0 10px 0' }}>{listing.title}</h3>
            <p><strong>Price:</strong> €{listing.price}</p>
            <p><strong>Location:</strong> {listing.location}</p>
            <p><strong>Source:</strong> {listing.source}</p>
            {listing.url && (
              <a href={listing.url} target="_blank" rel="noopener noreferrer" style={{ color: '#007bff' }}>
                View Original
              </a>
            )}
          </div>
        ))}
        {listings.length === 0 && (
          <p style={{ textAlign: 'center', color: '#666', marginTop: '50px' }}>
            No listings found. Try adjusting your filters or run the scraper first.
          </p>
        )}
      </div>
    </div>
  );
}

export default Listings;
