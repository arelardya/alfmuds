document.getElementById('checkUrl').addEventListener('click', function() {
    const url = document.getElementById('url').value;
    const progressBar = document.getElementById('progress-bar');
    const progressContainer = document.getElementById('progress-container');
    const resultDiv = document.getElementById('result');
  
    // Clear previous result and show progress bar
    resultDiv.textContent = '';
    progressContainer.style.display = 'block';
    progressBar.value = 0;
  
    // Simulate progress while waiting for server response
    const interval = setInterval(function() {
      if (progressBar.value < 90) {
        progressBar.value += 10;  // Increment progress every 500ms
      }
    }, 500);
  
    // Send URL to Flask server for prediction
    fetch('http://127.0.0.1:5000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
      clearInterval(interval);  // Stop progress once we have a response
      progressContainer.style.display = 'none';  // Hide the progress bar
  
      if (data.prediction === 'benign') {
        resultDiv.textContent = 'Prediction: Benign';
      } else {
        resultDiv.textContent = `Prediction: Malicious - ${data.prediction}`;
      }
    })
    .catch(error => {
      clearInterval(interval);
      progressContainer.style.display = 'none';
      resultDiv.textContent = 'Error occurred: ' + error;
      console.error('Error:', error);
    });
  });
  