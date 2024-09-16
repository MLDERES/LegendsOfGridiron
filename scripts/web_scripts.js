// Function to populate the matchup data table
function populateMatchupData() {
    const tableBody = document.querySelector('tbody');
    const opponentTableBody = document.querySelector('#opponent-table tbody'); // For the new table

    // Function to count occurrences for wins/losses
    function countOccurrences(data) {
        const teams = {};
        const matchups = {}; // For tracking matchups

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
            
            // Track matchups where the median team is involved
            // Initialize median records
            const medianRecords = {};

            // Populate the median matchup data
            parsedData.forEach(matchup => {
                const winner = matchup.Winner;
                const loser = matchup.Loser;
                const count = parseInt(matchup.Count, 10);

                if (loser === "MEDIAN" || winner === "MEDIAN") {
                    const coach = loser === "MEDIAN" ? winner : loser;

                    if (!medianRecords[coach]) {
                        medianRecords[coach] = { wins: 0, losses: 0 };
                    }

                    if (loser === "MEDIAN") {
                        // If the coach beat MEDIAN
                        medianRecords[coach].wins += count;
                    } else {
                        // If the coach lost to MEDIAN
                        medianRecords[coach].losses += count;
                    }
                }
            });

        });

        return { teams, matchups, medianRecords};
    }
    // Fetch the CSV data from the correct path
    fetch('data/league_outcomes.csv')
        .then(response => response.text())
        .then(data => {
            // Parse the CSV data
            const parsedData = Papa.parse(data, { header: true }).data;

            // Count occurrences
            const { teams, matchups } = countOccurrences(parsedData);

            // Convert teams into an array and calculate win percentages
            const sortedTeams = Object.keys(teams).map(team => ({
                team,
                ...teams[team],
                winPercentage: teams[team].wins / (teams[team].wins + teams[team].losses)
            }))
                .filter(teamData => teamData.team !== "MEDIAN") // Exclude "MEDIAN"
                .sort((a, b) => b.winPercentage - a.winPercentage); // Sort by win percentage in descending order

            // Populate the main table (team stats)
            sortedTeams.forEach(teamData => {
                const row = document.createElement('tr');
                row.innerHTML = `
                <td>${teamData.team}</td>
                <td>${teamData.wins}</td>
                <td>${teamData.losses}</td>
                <td>${teamData.winPercentage.toFixed(2)}</td>
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

            // Initialize median records
            const medianRecords = {};

            // Populate the median matchup data
            parsedData.forEach(matchup => {
                const winner = matchup.Winner;
                const loser = matchup.Loser;
                const count = parseInt(matchup.Count, 10);

                if (loser === "MEDIAN" || winner === "MEDIAN") {
                    const coach = loser === "MEDIAN" ? winner : loser;

                    if (!medianRecords[coach]) {
                        medianRecords[coach] = { wins: 0, losses: 0 };
                    }

                    if (loser === "MEDIAN") {
                        // If the coach beat MEDIAN
                        medianRecords[coach].wins += count;
                    } else {
                        // If the coach lost to MEDIAN
                        medianRecords[coach].losses += count;
                    }
                }
            });

            // Populate the median matchup table
            Object.keys(medianRecords).forEach(coach => {
                const record = medianRecords[coach];
                const row = document.createElement('tr');
                row.innerHTML = `
                <td>${coach}</td>
                <td>${record.wins}</td>
                <td>${record.losses}</td>
            `;
                medianTableBody.appendChild(row);  // Append to the median table
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
