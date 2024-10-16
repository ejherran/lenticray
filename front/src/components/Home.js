// src/components/Home.js
import React from 'react';

function Home() {
  return (
    <div className="container mt-5">
      <h2 className="text-center mb-4">Welcome to Lenticray</h2>
      <p>
        Lenticray is an advanced analysis and prediction system for algae proliferation in freshwater bodies. 
        Using a combination of fuzzy logic and neural networks, Lenticray analyzes data sets related to key water variables 
        to determine the trophic level of a body of water. Our system reconstructs time series over days, weeks, or months, 
        providing insights into past trends and offering projections for the future.
      </p>
      <p>
        Whether you are a researcher, environmental manager, or simply curious about the health of water ecosystems, 
        Lenticray empowers you with detailed analysis and predictive capabilities, allowing you to better understand 
        and manage the complex dynamics of freshwater environments.
      </p>
      <p className="text-center mt-4">
        Dive into the data and explore the future of water quality with Lenticray!
      </p>
    </div>
  );
}

export default Home;
