document.addEventListener('DOMContentLoaded', function () {
  const imageInput = document.getElementById('imageInput');
  const previewImage = document.getElementById('previewImage');
  const imageUploadForm = document.getElementById('imageUploadForm');
  const resultDiv = document.getElementById('result');
  const confidenceDiv = document.getElementById('confidence-score');
  const predictionContainer = document.getElementById('predictionContainer');
  const saveButton = document.getElementById('saveResult');
  const downloadFileName = "prediction_result.txt";

  // Image Preview
  imageInput.addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file) {
      predictionContainer.classList.remove('hidden');
      const reader = new FileReader();
      reader.onload = function (event) {
        previewImage.src = event.target.result;
        previewImage.classList.remove('hidden');
      };
      reader.readAsDataURL(file);
    } else {
      predictionContainer.classList.add('hidden');
    }
  });

  // Smooth Scroll for "Check Now"
  const checkNowButton = document.querySelector('a[href="#check-image-section"]');
  if (checkNowButton) {
    checkNowButton.addEventListener('click', function (e) {
      e.preventDefault();
      document.querySelector('#check-image-section').scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    });
  }

  // Form Submission and Prediction API call
  imageUploadForm.addEventListener('submit', async function (e) {
    e.preventDefault();
    resultDiv.textContent = "Processing...";
    confidenceDiv.textContent = "";
    saveButton.classList.add('hidden');
    
    const file = imageInput.files[0];
    if (!file) {
      resultDiv.textContent = "No file selected!";
      return;
    }
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        body: formData
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server error: ${response.status} ${errorText}`);
      }
      
      const data = await response.json();
      resultDiv.innerHTML = data.prediction;
      confidenceDiv.innerHTML = "Confidence Score: " + (data.confidence * 100).toFixed(2) + "%";
      saveButton.classList.remove('hidden');
    } catch (error) {
      console.error("Error during prediction:", error);
      resultDiv.textContent = "Error: Unable to get prediction. " + error.message;
    }
  });

  // Save result functionality: download the result and update button text to "Download"
  saveButton.addEventListener('click', function () {
    const resultText = resultDiv.textContent + "\n" + confidenceDiv.textContent;
    const blob = new Blob([resultText], { type: "text/plain;charset=utf-8" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = downloadFileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    saveButton.innerHTML = `<i class="fas fa-download"></i> Download`;
  });

  // Mobile Navigation Toggle
  const menuToggle = document.getElementById('menu-toggle');
  const navMenu = document.getElementById('nav-menu');
  menuToggle.addEventListener('click', function () {
    navMenu.classList.toggle('hidden');
    const isHidden = navMenu.classList.contains('hidden');
    menuToggle.setAttribute('aria-expanded', !isHidden);
  });
});
