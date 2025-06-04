<template>
  <div id="app">
    <header>
      <h1>Model Prediction Service</h1>
    </header>

    <main>
      <div class="input-group">
        <label for="record-select">Select Record ID:</label>
        <select
          id="record-select"
          v-model="selectedRecordId"
          @change="prediction = null; error = null"
        >
          <option value="" disabled>-- Please choose an option --</option>
          <option v-for="id in availableRecords" :key="id" :value="id">
            {{ id }}
          </option>
        </select>
        <button @click="handlePredict" :disabled="!selectedRecordId || isLoading">
          {{ isLoading ? 'Predicting...' : 'Get Prediction' }}
        </button>
      </div>

      <div v-if="prediction !== null" class="result">
        <h2>Prediction:</h2>
        <p>{{ prediction }}</p>
      </div>

      <div v-if="error" class="error">
        <h2>Error:</h2>
        <p>{{ error }}</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const selectedRecordId = ref('');
const prediction = ref(null);
const error = ref(null);
const availableRecords = ref([]);
const isLoading = ref(false);

const fetchRecords = async () => {
  try {
    const response = await fetch('/api/records'); // NGINX will route this to the API
    if (!response.ok) {
      throw new Error(`Failed to fetch records: ${response.statusText}`);
    }
    const data = await response.json();
    availableRecords.value = data.record_ids;
    if (availableRecords.value.length > 0) {
      selectedRecordId.value = availableRecords.value[0]; // Pre-select the first record
    }
  } catch (err) {
    console.error('Error fetching records:', err);
    error.value = `Could not load record IDs: ${err.message}`;
  }
};

const handlePredict = async () => {
  error.value = null;
  prediction.value = null;
  isLoading.value = true;
  try {
    const response = await fetch('/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ record_id: selectedRecordId.value }),
    });

    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Prediction failed.');
    }

    const data = await response.json();
    prediction.value = data.prediction;
  } catch (err) {
    error.value = err.message;
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  fetchRecords();
});
</script>

<style>
/* Basic styling for App.vue */
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

header {
  margin-bottom: 30px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  margin-right: 10px;
}

.input-group select,
.input-group button {
  padding: 8px 15px;
  border-radius: 5px;
  border: 1px solid #ccc;
  font-size: 16px;
}

.input-group button {
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  margin-left: 10px;
}

.input-group button:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}

.result {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #42b983;
  border-radius: 8px;
  background-color: #e6ffe6;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.error {
  margin-top: 30px;
  padding: 20px;
  border: 1px solid #ff4d4d;
  border-radius: 8px;
  background-color: #ffe6e6;
  color: #cc0000;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}
</style>