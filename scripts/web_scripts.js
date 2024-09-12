// Function to populate the matchup data table
function populateMatchupData() {
    const tableBody = document.querySelector('tbody');

    // Function to count the occurrences of each team in the winner and loser columns
    function countOccurrences(data) {
        const teams = {};

        // Loop through each row in the CSV data
        data.forEach(row => {
            const winner = row.Winner;
            const loser = row.Loser;

            // Count the wins for each team
            if (winner in teams) {
                teams[winner].wins++;
            } else {
                teams[winner] = { wins: 1, losses: 0 };
            }

            // Count the losses for each team
            if (loser in teams) {
                teams[loser].losses++;
            } else {
                teams[loser] = { wins: 0, losses: 1 };
            }
        });

        // Calculate win percentage for each team
        Object.keys(teams).forEach(team => {
            const totalGames = teams[team].wins + teams[team].losses;
            teams[team].winPercentage = (teams[team].wins / totalGames).toFixed(2);
        });

        return teams;
    }

    // Fetch the CSV data from the correct path
    fetch('data/league_outcomes.csv')
        .then(response => response.text())
        .then(data => {
            // Parse the CSV data
            const parsedData = Papa.parse(data, { header: true }).data;

            // Count the occurrences of each team
            const teamOccurrences = countOccurrences(parsedData);

            // Convert the object to an array and sort by win percentage
            const sortedTeams = Object.keys(teamOccurrences).map(team => ({
                team,
                ...teamOccurrences[team]
            })).sort((a, b) => b.winPercentage - a.winPercentage); // Sort by win percentage in descending order

            // Populate the table with the team data in sorted order
            sortedTeams.forEach(teamData => {
                const row = document.createElement('tr');

                const teamCell = document.createElement('td');
                teamCell.textContent = teamData.team;
                row.appendChild(teamCell);

                const winsCell = document.createElement('td');
                winsCell.textContent = teamData.wins;
                row.appendChild(winsCell);

                const lossesCell = document.createElement('td');
                lossesCell.textContent = teamData.losses;
                row.appendChild(lossesCell);

                const winPercentageCell = document.createElement('td');
                winPercentageCell.textContent = teamData.winPercentage;
                row.appendChild(winPercentageCell);

                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error:', error);
        });
}