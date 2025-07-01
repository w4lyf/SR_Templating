let gameData = {};

        function showAlert(message, type = 'error') {
            const alertsContainer = document.getElementById('alerts');
            const alert = document.createElement('div');
            alert.className = `alert ${type} show`;
            alert.textContent = message;
            alertsContainer.appendChild(alert);
            
            setTimeout(() => {
                alert.remove();
            }, 5000);
        }

        function showLoading(elementId, show) {
            const spinner = document.getElementById(elementId);
            if (show) {
                spinner.style.display = 'inline-block';
            } else {
                spinner.style.display = 'none';
            }
        }

        async function fetchGameInfo() {
            const appid = document.getElementById('appid').value.trim();
            
            if (!appid) {
                showAlert('Please enter a Steam App ID');
                return;
            }

            showLoading('fetch-spinner', true);
            
            try {
                const response = await fetch('/fetch_game_info', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ appid })
                });

                const data = await response.json();

                gameData = data;
                //console.log('Fetched Game Data:', gameData);
                displayGameInfo(data);
                updateSidePanel(data);
                showAlert('Game information fetched successfully!', 'success');

            } catch (error) {
                showAlert(error.message);
            } finally {
                showLoading('fetch-spinner', false);
            }
        }

        function displayGameInfo(data) {
            const gameInfo = document.getElementById('game-info');
            const gameDetails = document.getElementById('game-details');
            
            gameDetails.innerHTML = `
                <div class="info-item"><strong>Name:</strong> ${data.game_name}</div>
                <div class="info-item"><strong>Developer:</strong> ${data.developer || 'N/A'}</div>
                <div class="info-item"><strong>Publisher:</strong> ${data.publisher || 'N/A'}</div>
                <div class="info-item"><strong>Genres:</strong> ${data.genres.join(', ') || 'N/A'}</div>
                <div class="info-item"><strong>Screenshots Found:</strong> ${data.ss1_url && data.ss2_url ? '2' : data.ss1_url || data.ss2_url ? '1' : '0'}</div>
            `;
            
            gameInfo.classList.add('show');
        }

        function updateSidePanel(data) {
            // Update Publisher
            const publisherContent = document.getElementById('publisher-content');
            publisherContent.textContent = data.publisher || 'N/A';

            // Update Categories
            const categoriesContent = document.getElementById('categories-content');
            if (data.categories && data.categories.length > 0) {
                categoriesContent.innerHTML = data.categories.map(category => 
                    `<span class="category-tag">${category}</span>`
                ).join('');
            } else {
                categoriesContent.innerHTML = '<span style="color: #8b949e; font-size: 0.85rem;">No categories found</span>';
            }

            // Update Focus Keyphrase
            const keyphraseContent = document.getElementById('keyphrase-content');
            keyphraseContent.textContent = data.focus_keyphrase || 'N/A';

            // Update Meta Description
            const metaContent = document.getElementById('meta-content');
            metaContent.textContent = data.meta_description || 'N/A';
        }

        async function copyCode() {
            if (!gameData.game_name) {
                showAlert('Please fetch game information first');
                return;
            }

            // Collect all form data
            const formData = {
                ...gameData,
                game_size: document.getElementById('game-size').value.trim(),
                released_by: document.getElementById('released-by').value.trim(),
                version: document.getElementById('version').value.trim(),
                gofile_link: document.getElementById('gofile-link').value.trim(),
                buzzheavier_link: document.getElementById('buzzheavier-link').value.trim()
            };
            //console.log('Form Data:', formData);

            try {
                const response = await fetch('/generate_page', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (!response.ok) {
                    throw new Error(data.error || 'Failed to generate code');
                }
                //console.log(data);

                // Display the HTML code
                document.getElementById('html-output').value = data.html_content;
                document.getElementById('html-code').classList.add('show');
                copyToClipboard();
                showAlert('HTML code generated and copied!', 'success');

            } catch (error) {
                showAlert(error.message || 'Failed to generate HTML');
            } 
        }

        function copyToClipboard(id = 'html-output') {
            const element = document.getElementById(id);
            if (!element) {
                showAlert('Element to copy not found');
                return;
            }

            navigator.clipboard.writeText(element.value || element.textContent)
                .then(() => showAlert('Copied to clipboard!', 'success'))
                .catch(err => showAlert('Failed to copy', 'error'));
        }


        async function generateSEO() {
            const gameName = document.getElementById("gameName").value;
            const response = await fetch("/generate_seo", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ game_name: gameName })
            });
            const data = await response.json();
            //console.log(data);

            // Update Focus Keyphrase
            const keyphraseContent = document.getElementById('keyphrase-content');
            keyphraseContent.textContent = data.focus_keyphrase || 'N/A';

            // Update Meta Description
            const metaContent = document.getElementById('meta-content');
            metaContent.textContent = data.meta_description || 'N/A';
            }


        async function processThumbnail() {
            const thumbnailUrl = document.getElementById("thumbnailUrl").value;
            const response = await fetch("/process_thumbnail", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: thumbnailUrl, game_name: gameData.game_name || "untitled" })
            });
            const data = await response.json();
            //console.log(data)
            document.getElementById("thumbnailUrl").value = data.message;
            const thumbLink = document.getElementById("thumbnailLink");
            thumbLink.href = data.image_url;
            thumbLink.style.display = 'inline';
            }

        async function processFeatured() {
            let featuredURL = document.getElementById("featuredImageUrl").value;
            featuredURL = featuredURL.split('?')[0];
            const response = await fetch("/process_featured", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: featuredURL, game_name: gameData.game_name || "untitled", api_key: 'eyJraWQiOiI5NzIxYmUzNi1iMjcwLTQ5ZDUtOTc1Ni05ZDU5N2M4NmIwNTEiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJhdXRoLXNlcnZpY2UtNTYzOTM2ODItMzc4YS00MmE0LTkwMzItMWU4OWI2N2UwNDNjIiwiYXVkIjoiNDg4MzYxOTYxMDE4MTAxIiwibmJmIjoxNzUwNjY2MDMyLCJzY29wZSI6WyJiMmItYXBpLmdlbl9haSIsImIyYi1hcGkuaW1hZ2VfYXBpIl0sImlzcyI6Imh0dHBzOi8vYXBpLnBpY3NhcnQuY29tL3Rva2VuLXNlcnZpY2UiLCJvd25lcklkIjoiNDg4MzYxOTYxMDE4MTAxIiwiaWF0IjoxNzUwNjY2MDMyLCJqdGkiOiJhMDZlOGFiNi1iYzM4LTQ3MmItOGRiYi00MTA5NGY2NTkyMGIifQ.dHoQ_bGn7t8GKPS1cfkKjMK6IUdfJKsIzRGkmMZHDXdaBbB2xYD-rFuM_WyBUoGzmkzePREzVpuH4JgzaKuz2bL8w7hh05CCcuQDOQVkqAu7Oj5C5b8Rm1b4Wy7T9K6wAZZ7M5Dnh_FEK25XoF7P1Vqwl6l25PLiOMowISr2hxuNyl2HhBkk5AvFgD8EFIlf_UX9YHrRWz8DNDhUtuXhBrcDpPQPBIZnSV24VqQt7ID6s2JsWRtjlBbs3fQLnbJjHRJiNgsn_xPeKBiMwR74HH5ZC-zYfXRolu3Lwlq_xebCocppsr5WzsWJ8mS_Ge2sXC5WqE7SEfH6n0ZjsvaP0w' })
            });
            const data = await response.json();
            document.getElementById("featuredImageUrl").value = data.message;
            const featLink = document.getElementById("featuredLink");
            featLink.href = data.image_url;
            featLink.style.display = 'inline';
            }

