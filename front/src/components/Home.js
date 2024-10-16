// src/components/Home.js
import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';

function Home() {
  return (
    <div className="container mt-5">
      <div className="text-center mb-5">
        <h2 className="mb-3">Welcome to <span className="text-primary">Lenticray</span></h2>
        <p className="lead">
          Lenticray is an advanced analysis and prediction system for algae proliferation in freshwater bodies.
        </p>
      </div>

      <div className="mb-4">
        <div className="alert alert-info">
          <h4 className="alert-heading">About Lenticray</h4>
          <p>
            Using a combination of fuzzy logic and neural networks, Lenticray analyzes data sets related to key water variables
            to determine the trophic level of a body of water. Our system reconstructs time series over days, weeks, or months,
            providing insights into past trends and offering projections for the future.
          </p>
        </div>
      </div>

      <h2 className="mb-4 text-center">User Guide for Lenticray</h2>
      <div className="accordion" id="userGuide">
        <div className="accordion-item">
          <h2 className="accordion-header" id="headingOne">
            <button className="accordion-button" type="button" data-bs-toggle="collapse" data-bs-target="#collapseOne" aria-expanded="true" aria-controls="collapseOne">
              1. Define a Project
            </button>
          </h2>
          <div id="collapseOne" className="accordion-collapse collapse show" aria-labelledby="headingOne" data-bs-parent="#userGuide">
            <div className="accordion-body">
              The first step is to define a project, which represents the body of water you wish to study.
            </div>
          </div>
        </div>

        <div className="accordion-item">
          <h2 className="accordion-header" id="headingTwo">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTwo" aria-expanded="false" aria-controls="collapseTwo">
              2. Create a Dataset
            </button>
          </h2>
          <div id="collapseTwo" className="accordion-collapse collapse" aria-labelledby="headingTwo" data-bs-parent="#userGuide">
            <div className="accordion-body">
              The second step is to create a dataset associated with the project. In this dataset, you must define the variables you have available or plan to work with.
              <p>
                <em>Important:</em> Once a dataset is created, you cannot modify its variables or change its associated project. However, you can create as many datasets as you need.
              </p>
            </div>
          </div>
        </div>

        <div className="accordion-item">
          <h2 className="accordion-header" id="headingThree">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseThree" aria-expanded="false" aria-controls="collapseThree">
              3. Input Data
            </button>
          </h2>
          <div id="collapseThree" className="accordion-collapse collapse" aria-labelledby="headingThree" data-bs-parent="#userGuide">
            <div className="accordion-body">
              Once the dataset is defined, data can be entered manually through a grid, or by uploading a CSV file.
              The system will only consider columns that match the IDs of the variables chosen for the dataset. It is essential to include a "Sample Date" column, as the system uses it to build time series.
            </div>
          </div>
        </div>

        <div className="accordion-item">
          <h2 className="accordion-header" id="headingFour">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFour" aria-expanded="false" aria-controls="collapseFour">
              4. Create a Study
            </button>
          </h2>
          <div id="collapseFour" className="accordion-collapse collapse" aria-labelledby="headingFour" data-bs-parent="#userGuide">
            <div className="accordion-body">
              Once the dataset is loaded, you must create a study. In this study, you can define the time scale you wish to work with: days, weeks, or months, as well as the window size of data you want to use.
              <p><strong>Important Notes:</strong></p>
              <ul>
                <li>
                  <strong>Recommended Time Scale:</strong> It is generally recommended to use a monthly scale, as shorter scales may take longer to process and require more data for reliable estimates. However, weekly and daily scales can be useful for evaluating the behavior of the water body over shorter periods. For example, if you are starting with a new water body, it might be interesting to conduct studies over a few weeks or days to observe its behavior.
                </li>
                <li>
                  <strong>Data Date Range:</strong> Pay special attention to the oldest and newest dates in the dataset, as the system uses these two dates to calculate how many "time steps" need to be constructed. Based on the difference between these dates, the following scales are recommended:
                  <ul>
                    <li>More than 5 years: Monthly.</li>
                    <li>Between 2 and 5 years: Monthly or Weekly.</li>
                    <li>Between 6 months and 2 years: Weekly or Daily.</li>
                    <li>Less than 6 months: Daily.</li>
                  </ul>
                </li>
                <li>
                  <strong>Window Size:</strong> The window size should never exceed half of the "time steps" the system will generate. For example, if the dates span 10 years and you are working on a monthly scale, the system will generate 120 "time steps," so the window size should not exceed 60 months. However, the following values are recommended:
                  <ul>
                    <li>Monthly: 12</li>
                    <li>Weekly: 52</li>
                    <li>Daily: 365</li>
                  </ul>
                  These values are optimal when you have at least two years of data; otherwise, they should be adjusted downward.
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div className="accordion-item">
          <h2 className="accordion-header" id="headingFive">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseFive" aria-expanded="false" aria-controls="collapseFive">
              5. Training the Study
            </button>
          </h2>
          <div id="collapseFive" className="accordion-collapse collapse" aria-labelledby="headingFive" data-bs-parent="#userGuide">
            <div className="accordion-body">
              After defining the study, it can be sent for training. The training process may take varying amounts of time depending on the available data in the selected dataset, the chosen time scale, and the window size. Training occurs in the background and only one process can run at a time, so there is a queue for this process and you must wait for it to complete.
              <p><strong>Important Notes:</strong></p>
              <ul>
                <li>
                  A study can be in the following states:
                  <ul>
                    <li><strong>NEW:</strong> Defined and its configuration can be modified.</li>
                    <li><strong>PENDING:</strong> Queued for training.</li>
                    <li><strong>TRAINING:</strong> Currently being processed.</li>
                    <li><strong>TRAINED:</strong> Training process completed.</li>
                    <li><strong>FAILED:</strong> Training process failed.</li>
                  </ul>
                </li>
                <li>A study can only be edited if it is in the NEW state.</li>
                <li>A study cannot be deleted if it is in PENDING or TRAINING state.</li>
                <li>If a study reaches the FAILED state, it must be deleted, and a new one created. Common reasons for training failure include an empty dataset, a window size exceeding half the available time steps, or unrealistic values in the provided samples.</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="accordion-item">
          <h2 className="accordion-header" id="headingSix">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseSix" aria-expanded="false" aria-controls="collapseSix">
              6. Accessing Results
            </button>
          </h2>
          <div id="collapseSix" className="accordion-collapse collapse" aria-labelledby="headingSix" data-bs-parent="#userGuide">
            <div className="accordion-body">
              Once the study has completed its training process, you can access the results. This allows you to download the results dataset, view the associated graphs, and create predictions.
            </div>
          </div>
        </div>

        <div className="accordion-item">
          <h2 className="accordion-header" id="headingSeven">
            <button className="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#collapseSeven" aria-expanded="false" aria-controls="collapseSeven">
              7. Creating Predictions
            </button>
          </h2>
          <div id="collapseSeven" className="accordion-collapse collapse" aria-labelledby="headingSeven" data-bs-parent="#userGuide">
            <div className="accordion-body">
              To create a prediction, go to the study's results panel, where you will be directed to a form to create predictions.
              <p><strong>Important Notes:</strong></p>
              <ul>
                <li>
                  To create a prediction, the window size must be defined using the same criteria as for the study. You must also specify the number of "future steps" to predict. It is important not to try to predict a number of steps greater than the window size. For example, if you are working on a monthly scale with a 12-month window, it is not recommended to try predicting more than the next 12 months. Also, avoid using very large windows.
                </li>
                <li>
                  When creating a prediction, it is automatically queued for processing, and it can pass through the following states:
                  <ul>
                    <li><strong>PENDING:</strong> Pending execution.</li>
                    <li><strong>RUNNING:</strong> Currently being executed.</li>
                    <li><strong>COMPLETE:</strong> The process is completed, and results can be accessed.</li>
                    <li><strong>FAILED:</strong> The prediction process has failed.</li>
                  </ul>
                  The prediction process is much faster than training but shares the same engine, so predictions enter the same task queue. If a prediction takes a long time in the PENDING state, it is usually because one or more training processes are ahead in the queue.
                </li>
                <li>
                  A prediction cannot be modified once created, and it can only be deleted if it is COMPLETE or FAILED. However, you can create as many predictions as needed.
                </li>
                <li>
                  Once a prediction reaches the COMPLETE state, you can access its results, download the results dataset, and view the prediction graphs.
                </li>
                <li>
                  Among the prediction results, there is a special graph that compares the directly predicted trophic level with the one inferred using fuzzy logic based on the predicted values for the other variables.
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <br />

      <div className="mb-4">
        <div className="alert alert-secondary">
          <h4 className="alert-heading">Source Code Availability</h4>
          <p>
            The source code for the entire Lenticray system is available on GitHub. You can find the repository at: <a href="https://github.com/ejherran/lenticray" target="_blank" rel="noopener noreferrer">https://github.com/ejherran/lenticray</a>.
          </p>
          <p>
            This repository contains all the necessary code and documentation to set up your own instance of the Lenticray platform.
            By accessing the source code, you can customize, extend, and deploy the system to meet your specific needs,
            whether for research, environmental monitoring, or educational purposes.
          </p>
          <p>
            We encourage you to explore the repository, contribute to its development, and adapt Lenticray to support your work with freshwater bodies.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Home;
