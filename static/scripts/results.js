function toggleAdvancedSearch() {
    var advSearchInput = document.getElementById("advSearchInput");
    advSearchInput.style.display = (advSearchInput.style.display === "none" || advSearchInput.style.display === "") ? "block" : "none";
}

function search() {
    // Get the search input value
    const searchInput = document.getElementById('searchInput');
    const searchTerm = searchInput.value.trim();

    // Get the optional website input value
    const websiteInput = document.getElementById('advSearchInput');
    const websiteTerm = websiteInput.value.trim();

    // Perform any necessary validation or processing on the search and website terms

    // Redirect to the search results page with the search and website terms as parameters
    window.location.href = 'search?q=' + encodeURIComponent(searchTerm) +
                           '&website=' + encodeURIComponent(websiteTerm);
}