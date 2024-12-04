// content.js
const productInfo = {
  name: document.title, // Get the product name from the page title
  price: document.querySelector('#priceblock_ourprice')?.textContent || "Price Not Found"
};

// Send product info to Flask backend
fetch('http://127.0.0.1:8000/analyze_purchase', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    product: productInfo.name
  })
})
.then(response => response.json())
.then(data => {
  // Send the recommendation back to the popup
  chrome.runtime.sendMessage({ recommendation: data.recommendation });
})
.catch(error => console.error('Error:', error));
