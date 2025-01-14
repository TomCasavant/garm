var isLoading = false;
var page = 2;

function fetchMessages() {
    isLoading = true;
    var loadingContainer = document.getElementById('loading-container');
    loadingContainer.innerHTML = 'Loading...';
    fetch('/posts?page=' + page)
        .then(function(response) {
            return response.text();
        })
        .then(function(html) {
            var messageContainer = document.getElementById('screenshot_feed');
            messageContainer.insertAdjacentHTML('beforeend', html);
            isLoading = false;
            page += 1;
        });
}


window.addEventListener('scroll', function() {
    // Check if the user is near the bottom of the page
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 100) {
        // Only trigger if not already loading
        if (!isLoading) {
            isLoading = true;  // Prevent multiple fetches at the same time
            fetchMessages().then(() => {
                isLoading = false;  // Reset loading flag once fetch is complete
            });
        }
    }
});

fetchMessages();
