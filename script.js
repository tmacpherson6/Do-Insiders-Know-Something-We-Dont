// JavaScript code will go here 

document.addEventListener('DOMContentLoaded', () => {
    const csvUrl = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTgszNwy78OqGoabOHIQ2mRKMrYU1ZNfjsl1F2GD7Y9VVTDQKJQEIhfNKLO4A9A5uE1JRH5rxG7yt8T/pub?gid=1833183151&single=true&output=csv';

    Papa.parse(csvUrl, {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            console.log("Parsed data:", results.data);
            if (results.data && results.data.length > 0) {
                createInsiderTransactionsChart(results.data);
                createSharesByTxCodeChart(results.data);
                createTopIssuersChart(results.data);
            } else {
                displayErrorOnAllCharts("No data found or data is empty after parsing.");
            }
        },
        error: function(error) {
            console.error("Error parsing CSV:", error);
            displayErrorOnAllCharts("Error loading or parsing data. Please check the console and ensure the Google Sheet is correctly published as a CSV.");
        }
    });

    function displayErrorOnAllCharts(message) {
        const chartContainerIds = [
            'insider-transactions-chart-container',
            'shares-by-tx-code-chart-container',
            'issuer-transactions-chart-container'
        ];
        chartContainerIds.forEach(containerId => {
            const chartContainer = document.getElementById(containerId);
            if (chartContainer) {
                chartContainer.innerHTML = `<p style="color: red; text-align: center; padding-top: 20px;">${message}</p>`;
            }
        });
    }

    function createCanvasInContainer(containerId) {
        const chartContainer = document.getElementById(containerId);
        if (!chartContainer) {
            console.error(`Chart container with ID '${containerId}' not found.`);
            return null;
        }
        chartContainer.innerHTML = ''; // Clear previous content (like error messages or old canvas)
        const canvas = document.createElement('canvas');
        chartContainer.appendChild(canvas);
        return canvas.getContext('2d');
    }

    function getSharedChartOptions(showYAxis = true, yAxisStepSize = null) {
        const options = {
            responsive: true,
            maintainAspectRatio: false, 
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                },
                title: {
                    display: false, // Using H2 tags in HTML for titles
                }
            }
        };
        if (showYAxis) {
            options.scales = {
                y: {
                    beginAtZero: true,
                    ticks: {}
                }
            };
            if (yAxisStepSize !== null && Number.isInteger(yAxisStepSize)) {
                options.scales.y.ticks.stepSize = yAxisStepSize;
            } else {
                 // Let Chart.js decide the step size automatically if not an integer or null
            }
        }
        return options;
    }

    function createInsiderTransactionsChart(data) {
        const containerId = 'insider-transactions-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const insiderTransactions = {};
        data.forEach(row => {
            const insiderName = row['Insider Name'] ? row['Insider Name'].trim() : 'Unknown Insider';
            if (insiderName) { // Ensure not an empty string after trim
                insiderTransactions[insiderName] = (insiderTransactions[insiderName] || 0) + 1;
            }
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(insiderTransactions),
                datasets: [{
                    label: 'Number of Transactions',
                    data: Object.values(insiderTransactions),
                    backgroundColor: 'rgba(54, 162, 235, 0.7)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: getSharedChartOptions(true, 1) // Show Y-axis, step size 1 for counts
        });
    }

    function createSharesByTxCodeChart(data) {
        const containerId = 'shares-by-tx-code-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const sharesByTxCode = {}; 
        data.forEach(row => {
            const txCode = row['Transaction Code'] ? row['Transaction Code'].trim().toUpperCase() : 'Unknown';
            const shares = parseFloat(row['Shares']);
            if (txCode && !isNaN(shares)) {
                sharesByTxCode[txCode] = (sharesByTxCode[txCode] || 0) + shares;
            }
        });
        
        const backgroundColors = [
            'rgba(255, 99, 132, 0.7)', 
            'rgba(75, 192, 192, 0.7)', 
            'rgba(255, 205, 86, 0.7)', 
            'rgba(201, 203, 207, 0.7)', 
            'rgba(54, 162, 235, 0.7)',
            'rgba(153, 102, 255, 0.7)',
            'rgba(255, 159, 64, 0.7)'
        ];
        const borderColors = backgroundColors.map(color => color.replace('0.7', '1')); // Make border fully opaque

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(sharesByTxCode),
                datasets: [{
                    label: 'Total Shares',
                    data: Object.values(sharesByTxCode),
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                }]
            },
            options: getSharedChartOptions(false) // No Y-axis for pie chart
        });
    }

    function createTopIssuersChart(data, topN = 5) {
        const containerId = 'issuer-transactions-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const issuerCounts = {};
        data.forEach(row => {
            const issuer = row['Issuer'] ? row['Issuer'].trim() : 'Unknown Issuer';
            if (issuer) {
                issuerCounts[issuer] = (issuerCounts[issuer] || 0) + 1;
            }
        });

        const sortedIssuers = Object.entries(issuerCounts)
            .sort(([, countA], [, countB]) => countB - countA)
            .slice(0, topN);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedIssuers.map(item => item[0]),
                datasets: [{
                    label: `Number of Transactions (Top ${topN})`,
                    data: sortedIssuers.map(item => item[1]),
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: getSharedChartOptions(true, 1) // Show Y-axis, step size 1
        });
    }
}); 