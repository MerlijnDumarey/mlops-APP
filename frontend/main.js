document.addEventListener('DOMContentLoaded', () => {
    const recordSelect = document.getElementById('record-select');
    const predictButton = document.getElementById('predict-button');
    const resultDiv = document.getElementById('result');
    const predictionOutput = document.getElementById('prediction-output');
    const errorDiv = document.getElementById('error');
    const errorOutput = document.getElementById('error-output');

    const showElement = (element) => element.classList.remove('hidden');
    const hideElement = (element) => element.classList.add('hidden');

    const fetchRecords = async () => {
        try {
            const response = await fetch('/api/records'); 
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Failed to fetch records: ${response.status} ${response.statusText} - ${errorText}`);
            }
            const data = await response.json();
            
            recordSelect.innerHTML = '<option value="" disabled selected>-- Please choose an option --</option>';

            if (data.record_ids && data.record_ids.length > 0) {
                data.record_ids.forEach(id => {
                    const option = document.createElement('option');
                    option.value = id;
                    option.textContent = id;
                    recordSelect.appendChild(option);
                });
                recordSelect.value = data.record_ids[0]; 
                predictButton.disabled = false;
            } else {
                showError('No records found in the dataset.');
                predictButton.disabled = true;
            }
        } catch (err) {
            console.error('Error fetching records:', err);
            showError(`Could not load record IDs: ${err.message}`);
            predictButton.disabled = true;
        }
    };

    const handlePredict = async () => {
        hideElement(resultDiv);
        hideElement(errorDiv);
        predictionOutput.textContent = '';
        errorOutput.textContent = '';
        predictButton.disabled = true; 

        const selectedRecordId = recordSelect.value;
        if (!selectedRecordId) {
            showError('Please select a record ID.');
            predictButton.disabled = false;
            return;
        }

        try {
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ record_id: selectedRecordId }),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Prediction failed.');
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

    const showError = (message) => {
        errorOutput.textContent = message;
        showElement(errorDiv);
    };

    predictButton.addEventListener('click', handlePredict);

    fetchRecords();
});