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
                populateTable(results.data);
                createChart(results.data);
            }
        },
        error: function(error) {
            console.error("Error parsing CSV:", error);
            const dataContainer = document.getElementById('data-table-container');
            if (dataContainer) {
                dataContainer.innerHTML = "<p>Error loading or parsing data. Please check the console for details and ensure the Google Sheet is correctly published as a CSV.</p>";
            }
            const chartContainer = document.getElementById('chart-container');
            if (chartContainer) {
                chartContainer.innerHTML = "<p>Could not load data for chart.</p>"
            }
        }
    });

    function populateTable(data) {
        const tableHead = document.querySelector('#data-table thead tr');
        const tableBody = document.querySelector('#data-table tbody');

        if (!tableHead || !tableBody) {
            console.error("Table elements not found in the DOM");
            return;
        }

        // Clear existing headers and rows
        tableHead.innerHTML = '';
        tableBody.innerHTML = '';

        // Populate headers
        const headers = Object.keys(data[0]);
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            tableHead.appendChild(th);
        });

        // Populate rows
        data.forEach(row => {
            const tr = document.createElement('tr');
            headers.forEach(header => {
                const td = document.createElement('td');
                td.textContent = row[header] || ''; // Handle potential undefined values
                tr.appendChild(td);
            });
            tableBody.appendChild(tr);
        });
    }

    function createChart(data) {
        const insiderTransactions = {};
        data.forEach(row => {
            const insiderName = row['Insider Name'] || 'Unknown Insider';
            insiderTransactions[insiderName] = (insiderTransactions[insiderName] || 0) + 1;
        });

        const chartData = {
            labels: Object.keys(insiderTransactions),
            datasets: [{
                label: 'Number of Transactions',
                data: Object.values(insiderTransactions),
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        };

        const ctx = document.createElement('canvas').getContext('2d');
        document.getElementById('chart-container').appendChild(ctx.canvas);

        new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                           stepSize: 1 // Ensure y-axis shows whole numbers for counts
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Transactions by Insider Name'
                    }
                }
            }
        });
    }
}); 