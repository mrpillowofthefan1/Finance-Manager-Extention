// Get product information from the website (simplified example)
const product = document.querySelector('.product-title')?.innerText || "Unknown Product";

// Send product data to your backend
fetch('http://localhost:8000/analyze_purchase', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ product }),
})
.then(response => response.json())
.then(data => {
    console.log(`Recommendation: ${data.recommendation}`);
    alert(`Gemini says: ${data.recommendation}`);
})
.catch(error => console.error('Error:', error));
