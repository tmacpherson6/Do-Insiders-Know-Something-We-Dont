// JavaScript code will go here 

document.addEventListener('DOMContentLoaded', () => {
    const csvUrl = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTgszNwy78OqGoabOHIQ2mRKMrYU1ZNfjsl1F2GD7Y9VVTDQKJQEIhfNKLO4A9A5uE1JRH5rxG7yt8T/pub?gid=1833183151&single=true&output=csv';

    Papa.parse(csvUrl, {
        download: true,
        header: true,
        skipEmptyLines: true,
        complete: function(results) {
            if (results.data && results.data.length > 0) {
                createInsiderTransactionsChart(results.data);
                createSharesByTxCodeChart(results.data);
                createTopIssuersChart(results.data);
                createTransactionValueChart(results.data);
                createOwnershipTypeChart(results.data);
                createInsiderRoleChart(results.data);
                createTransactionSizeChart(results.data);
                createPriceDistributionChart(results.data);
            }
            // If data is not valid or empty, charts will simply not be rendered.
        }

    });

    function createCanvasInContainer(containerId) {
        const chartContainer = document.getElementById(containerId);
        if (!chartContainer) {
            return null; // Silently return null if container not found
        }
        chartContainer.innerHTML = ''; 
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
                    display: false,
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
            if (insiderName && insiderName !== 'Unknown Insider') { // Also check against 'Unknown Insider' if it means no data
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
            options: getSharedChartOptions(true, 1)
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
            if (txCode && txCode !== 'Unknown' && !isNaN(shares)) {
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
        const borderColors = backgroundColors.map(color => color.replace('0.7', '1'));

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
            options: getSharedChartOptions(false)
        });
    }

    function createTopIssuersChart(data, topN = 5) {
        const containerId = 'issuer-transactions-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const issuerCounts = {};
        data.forEach(row => {
            const issuer = row['Issuer'] ? row['Issuer'].trim() : 'Unknown Issuer';
            if (issuer && issuer !== 'Unknown Issuer') {
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
            options: getSharedChartOptions(true, 1)
        });
    }

    function createTransactionValueChart(data) {
        const containerId = 'transaction-value-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const insiderValues = {};
        data.forEach(row => {
            const insiderName = row['Insider Name'] ? row['Insider Name'].trim() : 'Unknown';
            const shares = parseFloat(row['Shares']) || 0;
            const price = parseFloat(row['Price per Share']) || 0;
            const value = shares * price;
            
            if (insiderName !== 'Unknown' && !isNaN(value) && value > 0) { // Ensure value is positive
                insiderValues[insiderName] = (insiderValues[insiderName] || 0) + value;
            }
        });

        const topInsiders = Object.entries(insiderValues)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10); // Show top 10 by value

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topInsiders.map(item => item[0]),
                datasets: [{
                    label: 'Total Transaction Value ($)',
                    data: topInsiders.map(item => item[1]),
                    backgroundColor: 'rgba(153, 102, 255, 0.7)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: getSharedChartOptions(true) // Y-axis step size will be auto by Chart.js
        });
    }

    function createOwnershipTypeChart(data) {
        const containerId = 'ownership-type-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const ownershipCounts = {
            'Direct (D)': 0,
            'Indirect (I)': 0,
            'Other/Unknown': 0 // Group empty or other types
        };
        
        data.forEach(row => {
            const ownershipType = row['Ownership Type'] ? row['Ownership Type'].trim().toUpperCase() : '';
            if (ownershipType === 'D') {
                ownershipCounts['Direct (D)']++;
            } else if (ownershipType === 'I') {
                ownershipCounts['Indirect (I)']++;
            } else {
                ownershipCounts['Other/Unknown']++;
            }
        });

        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: Object.keys(ownershipCounts),
                datasets: [{
                    label: 'Transactions by Ownership Type',
                    data: Object.values(ownershipCounts),
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.7)', 
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(255, 206, 86, 0.7)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)', 
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 206, 86, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: getSharedChartOptions(false)
        });
    }

    function createInsiderRoleChart(data) {
        const containerId = 'insider-role-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const roleCounts = {};
        data.forEach(row => {
            let role = row['Insider Role'] ? row['Insider Role'].trim() : 'Unknown';
            if (role === '') role = 'Unknown'; // Consolidate empty strings to 'Unknown'
            roleCounts[role] = (roleCounts[role] || 0) + 1;
        });

        const sortedRoles = Object.entries(roleCounts)
            .filter(([roleName, count]) => count > 0) // Only include roles with counts > 0
            .sort((a, b) => b[1] - a[1])
            .slice(0, 10); // Show top 10 roles, or fewer if not that many distinct roles

        new Chart(ctx, {
            type: 'bar', // Using standard bar chart
            data: {
                labels: sortedRoles.map(item => item[0]),
                datasets: [{
                    label: 'Number of Transactions by Role',
                    data: sortedRoles.map(item => item[1]),
                    backgroundColor: 'rgba(75, 192, 192, 0.7)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: getSharedChartOptions(true, 1)
        });
    }

    function createTransactionSizeChart(data) {
        const containerId = 'transaction-size-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const sizeBins = {
            '< 1,000 Shares': 0,
            '1,000-10,000 Shares': 0,
            '10,001-50,000 Shares': 0,
            '50,001-100,000 Shares': 0,
            '100,001-500,000 Shares': 0,
            '> 500,000 Shares': 0
        };
        
        data.forEach(row => {
            const shares = parseFloat(row['Shares']) || 0;
            if (shares <= 0) return; // Ignore non-positive share counts

            if (shares < 1000) {
                sizeBins['< 1,000 Shares']++;
            } else if (shares <= 10000) {
                sizeBins['1,000-10,000 Shares']++;
            } else if (shares <= 50000) {
                sizeBins['10,001-50,000 Shares']++;
            } else if (shares <= 100000) {
                sizeBins['50,001-100,000 Shares']++;
            } else if (shares <= 500000) {
                sizeBins['100,001-500,000 Shares']++;
            } else {
                sizeBins['> 500,000 Shares']++;
            }
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(sizeBins),
                datasets: [{
                    label: 'Number of Transactions by Size',
                    data: Object.values(sizeBins),
                    backgroundColor: 'rgba(255, 159, 64, 0.7)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                }]
            },
            options: getSharedChartOptions(true, null) // Let Chart.js determine step size
        });
    }

    function createPriceDistributionChart(data) {
        const containerId = 'price-distribution-chart-container';
        const ctx = createCanvasInContainer(containerId);
        if (!ctx) return;

        const priceBins = {
            '< $1': 0,
            '$1-$10': 0,
            '$10.01-$25': 0, // Adjusted to avoid overlap with $10
            '$25.01-$50': 0, // Adjusted
            '$50.01-$100': 0, // Adjusted
            '> $100': 0
        };
        
        data.forEach(row => {
            const price = parseFloat(row['Price per Share']) || 0;
            if (price <= 0) return; // Ignore non-positive prices

            if (price < 1) {
                priceBins['< $1']++;
            } else if (price <= 10) {
                priceBins['$1-$10']++;
            } else if (price <= 25) {
                priceBins['$10.01-$25']++;
            } else if (price <= 50) {
                priceBins['$25.01-$50']++;
            } else if (price <= 100) {
                priceBins['$50.01-$100']++;
            } else {
                priceBins['> $100']++;
            }
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: Object.keys(priceBins),
                datasets: [{
                    label: 'Number of Transactions by Price',
                    data: Object.values(priceBins),
                    backgroundColor: 'rgba(255, 99, 132, 0.7)', // Re-using a color, can be changed
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            options: getSharedChartOptions(true, null) // Let Chart.js determine step size
        });
    }
}); 