// ================================================= Working one best till now ==========================================
// ================================================= Working one best till now ==========================================
// ================================================= Working one best till now ==========================================


const charts = {}; // To store references to charts

const createChart = (ctx, vehicleCounts, location) => {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Cars', 'Buses', 'Trucks', 'Motorcycles'],
            datasets: [{
                label: 'Vehicle Count',
                data: [
                    vehicleCounts.car || 0, 
                    vehicleCounts.bus || 0, 
                    vehicleCounts.truck || 0, 
                    vehicleCounts.motorcycle || 0
                ],
                backgroundColor: [
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltips: {
                    mode: 'index',
                    intercept: true,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Vehicle Type'
                    }
                }
            }
        }
    });
};

const fetchVehicleCounts = async () => {
    try {
        const response = await fetch('/vehicle-counts/');
        const data = await response.json();

        // Clear previous results to handle only updated data
        const resultsContainer = document.getElementById('results');

        // Loop through the data and update the dashboard
        for (const location in data) {
            const vehicleCounts = data[location];

            let resultDiv = document.getElementById(`location-${location}`);
            if (!resultDiv) {
                resultDiv = document.createElement('div');
                resultDiv.classList.add('location-result');
                resultDiv.id = `location-${location}`;

                const title = document.createElement('h3');
                title.classList.add('main-title');
                title.textContent = location; // Display the location as a title
                resultDiv.appendChild(title);

                const canvas = document.createElement('canvas');
                resultDiv.appendChild(canvas);

                resultsContainer.appendChild(resultDiv);
            }

            const ctx = resultDiv.querySelector('canvas').getContext('2d');
            if (charts[location]) {
                charts[location].destroy(); // Destroy the previous chart instance
            }
            charts[location] = createChart(ctx, vehicleCounts, location);
        }
    } catch (error) {
        console.error('Error fetching vehicle counts:', error);
    }
};

// Initial fetch on page load
fetchVehicleCounts();

// Call the function every 5 seconds
setInterval(fetchVehicleCounts, 5000);

// Handle location button click for highlighting
document.querySelectorAll('.traffic-button').forEach(button => {
    button.addEventListener('click', () => {
        const locationId = button.id;
        
        // Reset all results to full opacity
        document.querySelectorAll('.location-result').forEach(result => {
            result.style.opacity = 1;
        });

        // Highlight only the selected location, reduce opacity of others
        document.querySelectorAll('.location-result').forEach(result => {
            if (!result.id.includes(locationId)) {
                result.style.opacity = 0.5;
            }
        });
    });
});