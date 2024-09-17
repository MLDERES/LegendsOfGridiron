// Function to populate the combined data table
function populateMatchupData() {
    const combinedTableBody = document.querySelector('#win-loss tbody'); // For the combined table (overall + MEDIAN)
    const opponentTableBody = document.querySelector('#opponent-table tbody'); // For the second table (coach vs. coach matchups)

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

                // Track matchups where the same winner plays the same loser
                const matchupKey = `${winner}_vs_${loser}`;
                const reverseMatchupKey = `${loser}_vs_${winner}`;

                if (matchups[matchupKey]) {
                    matchups[matchupKey].wins++;
                } else if (matchups[reverseMatchupKey]) {
                    matchups[reverseMatchupKey].losses++;
                } else {
                    matchups[matchupKey] = { winner, loser, wins: 1, losses: 0 };
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

            // Convert teams into an array and calculate win percentages for both overall and against "MEDIAN"
            const combinedRecords = Object.keys(teams).map(coach => {
                const overallRecord = teams[coach];
                const totalGames = overallRecord.wins + overallRecord.losses;
                const overallWinPercentage = totalGames > 0 ? overallRecord.wins / totalGames : 0;

                const medianRecord = medianRecords[coach] || { wins: 0, losses: 0 };
                const medianTotalGames = medianRecord.wins + medianRecord.losses;
                const medianWinPercentage = medianTotalGames > 0 ? medianRecord.wins / medianTotalGames : 0;

                return {
                    coach,
                    overallWins: overallRecord.wins,
                    overallLosses: overallRecord.losses,
                    overallWinPercentage,
                    medianWins: medianRecord.wins,
                    medianLosses: medianRecord.losses,
                    medianWinPercentage,
                    totalGames
                };
            })
                .sort((a, b) => {
                    // Sort by overall win percentage first, and then by total games played
                    if (b.overallWinPercentage !== a.overallWinPercentage) {
                        return b.overallWinPercentage - a.overallWinPercentage;
                    } else {
                        return b.totalGames - a.totalGames; // Secondary sort by total games played
                    }
                });

            // Populate the combined table (overall + MEDIAN records)
            combinedRecords.forEach(record => {
                const row = document.createElement('tr');
                row.innerHTML = `
                <td>${record.coach}</td>
                <td>${record.overallWins}-${record.overallLosses} (${(record.overallWinPercentage * 100).toFixed(2)}%)</td>
                <td>${record.medianWins}-${record.medianLosses} (${(record.medianWinPercentage * 100).toFixed(2)}%)</td>
            `;
                combinedTableBody.appendChild(row);
            });

            // Sort opponent matchups by number of wins before displaying
            const sortedMatchups = Object.values(matchups).filter(matchup => matchup.losses === 0 && matchup.wins >= 2)
                .sort((a, b) => b.wins - a.wins);  // Sort by number of wins in descending order

            // Populate the second table (opponent matchups) with only undefeated records with at least 2 wins
            sortedMatchups.forEach(matchup => {
                const row = document.createElement('tr');
                row.innerHTML = `
                <td>${matchup.winner}</td>
                <td>${matchup.loser}</td>
                <td>${matchup.wins}-0</td>
            `;
                opponentTableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching or parsing data:', error);
        });

    }
