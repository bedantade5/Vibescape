document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("searchInput");
    const searchButton = document.getElementById("searchButton");
    const moodButtons = document.querySelectorAll(".mood-btn");
    const songGrid = document.getElementById("songGrid");
    const loading = document.getElementById("loading");
    const noResults = document.getElementById("noResults");
    const API_BASE_URL = 'http://127.0.0.1:5000/api';
    
    let sessionId = localStorage.getItem('music_session_id');
    if (!sessionId) {
        sessionId = Math.random().toString(36).substring(2, 15);
        localStorage.setItem('music_session_id', sessionId);
    }

    function fetchMoodSongs(mood) {
        loading.style.display = "block";
        noResults.style.display = "none";
        songGrid.innerHTML = "";

        fetch(`${API_BASE_URL}/mood/${mood}?session_id=${sessionId}`)
            .then(response => response.json())
            .then(data => {
                loading.style.display = "none";

                if (data.length === 0) {
                    noResults.style.display = "block";
                } else {
                    displaySongs(data);
                }
            })
            .catch(error => {
                loading.style.display = "none";
                noResults.style.display = "block";
                console.error("Error fetching songs:", error);
            });
    }

    function searchSongs(query) {
        loading.style.display = "block";
        noResults.style.display = "none";
        songGrid.innerHTML = "";

        let searchType = null;
        
        if (query.toLowerCase().includes("artist:")) {
            query = query.replace(/artist:/i, "").trim();
            searchType = "artist";
        } 
        else if (query.toLowerCase().includes("genre:")) {
            query = query.replace(/genre:/i, "").trim();
            searchType = "genre";
        }

        const endpoint = `${API_BASE_URL}/search?q=${encodeURIComponent(query)}` + 
                         (searchType ? `&type=${searchType}` : "") + 
                         `&session_id=${sessionId}`;

        fetch(endpoint)
            .then(response => response.json())
            .then(data => {
                loading.style.display = "none";

                if (data.length === 0) {
                    noResults.style.display = "block";
                } else {
                    displaySongs(data);
                }
            })
            .catch(error => {
                loading.style.display = "none";
                noResults.style.display = "block";
                console.error("Error searching songs:", error);
            });
    }

    function displaySongs(songs) {
        songGrid.innerHTML = songs.map(song => `
            <div class="song-card">
                <h3>${song.track_name}</h3>
                <p>Artist: ${song.artists}</p>
                <p>Genre: ${song.track_genre}</p>
                <p>Mood: ${song.mood}</p>
            </div>
        `).join("");
    }

    searchInput.placeholder = "Search or type 'artist:' / 'genre:' for specific search";

    searchButton.addEventListener("click", () => {
        const query = searchInput.value.trim();
        if (query) searchSongs(query);
    });

    searchInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            const query = searchInput.value.trim();
            if (query) searchSongs(query);
        }
    });

    moodButtons.forEach(button => {
        button.addEventListener("click", () => {
            const mood = button.dataset.mood;
            fetchMoodSongs(mood);
        });
    });
});