document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('file-input');
    const predictButton = document.getElementById('predict-button');
    const checkModelButton = document.getElementById('check-model-button');
    const resultDiv = document.getElementById('result');
    const predictionOutput = document.getElementById('prediction-output');
    const errorDiv = document.getElementById('error');
    const errorOutput = document.getElementById('error-output');
    const modelStatusDiv = document.getElementById('model-status');
    const modelStatusOutput = document.getElementById('model-status-output');

    const showElement = (element) => element.classList.remove('hidden');
    const hideElement = (element) => element.classList.add('hidden');

    const handlePredict = async () => {
        hideElement(resultDiv);
        hideElement(errorDiv);
        predictionOutput.textContent = '';
        errorOutput.textContent = '';
        predictButton.disabled = true;

        const file = fileInput.files[0];
        if (!file) {
            showError('Please select a file to upload.');
            predictButton.disabled = false;
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                let errMsg = 'Prediction failed.';
                try {
                    const errData = await response.json();
                    errMsg = errData.detail || errMsg;
                } catch {}
                throw new Error(errMsg);
            }

            const data = await response.json();
            predictionOutput.textContent = data.prediction;
            showElement(resultDiv);
        } catch (err) {
            showError(err.message);
        } finally {
            predictButton.disabled = false;
        }
    };

    const handleCheckModel = async () => {
        hideElement(modelStatusDiv);
        modelStatusOutput.textContent = '';
        try {
            const response = await fetch('/api/health');
            if (!response.ok) throw new Error('Could not check model status.');
            const data = await response.json();
            if (data.model_loaded) {
                modelStatusOutput.textContent = `Model loaded: ${data.model_file}`;
            } else {
                modelStatusOutput.textContent = 'Model is NOT loaded.';
            }
            showElement(modelStatusDiv);
        } catch (err) {
            modelStatusOutput.textContent = err.message;
            showElement(modelStatusDiv);
        }
    };

    const showError = (message) => {
        if (message.includes("Model is not available")) {
            errorOutput.textContent = "The prediction model is currently unavailable. Please contact the administrator or try again later.";
        } else {
            errorOutput.textContent = message;
        }
        showElement(errorDiv);
    };

    predictButton.addEventListener('click', handlePredict);
    checkModelButton.addEventListener('click', handleCheckModel);
});