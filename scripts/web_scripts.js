// Function to populate the matchup data table
function populateMatchupData() {
    const tableBody = document.querySelector('tbody'); // For the first table
    const opponentTableBody = document.querySelector('#opponent-table tbody'); // For the second table
    const medianTableBody = document.querySelector('#median-table tbody'); // For the third table (against MEDIAN)

    // Function to count occurrences for wins/losses
    function countOccurrences(data) {
        const teams = {};
        const matchups = {}; // For tracking matchups
        const medianRecords = {}; // For tracking wins/losses against "MEDIAN"

        data.forEach(row => {
            const winner = row.Winner;
            const loser = row.Loser;

            // Count the wins and losses for each team
            if (winner in teams) {
                teams[winner].wins++;
            } else {
                teams[winner] = { wins: 1, losses: 0 };
            }

            if (loser in teams) {
                teams[loser].losses++;
            } else {
                teams[loser] = { wins: 0, losses: 1 };
            }

            // Track matchups where the same winner beats the same loser
            const matchupKey = `${winner}_vs_${loser}`;
            if (matchups[matchupKey]) {
                matchups[matchupKey].count++;
            } else {
                matchups[matchupKey] = { winner, loser, count: 1 };
            }

            // Track records against the "MEDIAN"
            if (winner === "MEDIAN" || loser === "MEDIAN") {
                const coach = winner === "MEDIAN" ? loser : winner;
                const isWin = winner === coach;

                if (!medianRecords[coach]) {
                    medianRecords[coach] = { wins: 0, losses: 0 };
                }

                if (isWin) {
                    medianRecords[coach].wins++;
                } else {
                    medianRecords[coach].losses++;
                }
            }
        });

        return { teams, matchups, medianRecords };
    }

    // Fetch the CSV data from the correct path
    fetch('data/league_outcomes.csv')
        .then(response => response.text())
        .then(data => {
            // Parse the CSV data
            const parsedData = Papa.parse(data, { header: true }).data;

            // Count occurrences
            const { teams, matchups, medianRecords } = countOccurrences(parsedData);

            // Convert teams into an array and calculate win percentages
            const sortedTeams = Object.keys(teams).map(team => {
                const record = teams[team];
                const totalGames = record.wins + record.losses;
                const winPercentage = totalGames > 0 ? record.wins / totalGames : 0;
                return { coach: team, ...record, winPercentage, totalGames };
            })
                .sort((a, b) => {
                    // Sort by win percentage first, and then by total games played
                    if (b.winPercentage !== a.winPercentage) {
                        return b.winPercentage - a.winPercentage;
                    } else {
                        return b.totalGames - a.totalGames; // Secondary sort by games played
                    }
                });

            // Populate the first table (team stats)
            sortedTeams.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.coach}</td>
                    <td>${record.wins}-${record.losses} (${(record.winPercentage * 100).toFixed(2)}%)</td>
                `;
                tableBody.appendChild(row);
            });

            // Populate the opponent breakdown table
            Object.values(matchups).forEach(matchup => {
                if (matchup.count > 1 && matchup.loser !== "MEDIAN" && matchup.winner !== "MEDIAN") {  // Exclude rows with "MEDIAN"
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${matchup.winner}</td>
                        <td>${matchup.loser}</td>
                        <td>${matchup.count}</td>
                    `;
                    opponentTableBody.appendChild(row);
                }
            });

            // Convert the median records into an array and calculate win percentage
            const sortedMedianRecords = Object.keys(medianRecords).map(coach => {
                const record = medianRecords[coach];
                const totalGames = record.wins + record.losses;
                const winPercentage = totalGames > 0 ? record.wins / totalGames : 0;
                return { coach, ...record, winPercentage, totalGames };
            })
                .sort((a, b) => {
                    // Sort by win percentage first, and then by total games played
                    if (b.winPercentage !== a.winPercentage) {
                        return b.winPercentage - a.winPercentage;
                    } else {
                        return b.totalGames - a.totalGames; // Secondary sort by games played
                    }
                });

            // Populate the third table (record against MEDIAN)
            sortedMedianRecords.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${record.coach}</td>
                    <td>${record.wins}-${record.losses} (${(record.winPercentage * 100).toFixed(2)}%)</td>
                `;
                medianTableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}
