let isAdvancedSearchVisible = false;

function search() {
    const container = document.getElementById('container');
    const searchContainer = document.getElementById('search-container');
    
    // Move title and search bar up
    container.style.marginTop = '-100px';

    // Get the search input value
    const searchInput = document.getElementById('search-input');
    const searchTerm = searchInput.value.trim();

    // Get the optional website input value
    const websiteInput = document.getElementById('website-input');
    const websiteTerm = websiteInput.value.trim();

    // Perform any necessary validation or processing on the search and website terms

    // Redirect to the search results page with the search and website terms as parameters
    window.location.href = 'search?q=' + encodeURIComponent(searchTerm) +
                           '&website=' + encodeURIComponent(websiteTerm);
}

function showAdvancedSearch() {
    // No need to implement anything here, as the tooltip is handled with CSS
}

function toggleAdvancedSearch() {
    const websiteInput = document.getElementById('website-input');
    isAdvancedSearchVisible = !isAdvancedSearchVisible;
    websiteInput.style.display = isAdvancedSearchVisible ? 'block' : 'none';

}

