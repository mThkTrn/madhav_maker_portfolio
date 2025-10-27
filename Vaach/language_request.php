<?php
include "header.php";
include "navbar.php";
include "conn.php";
include "countries.php";

$countries = array("Afghanistan", "Albania", "Algeria" /* ... */); // Your list of countries

if (isset($_POST['submit'])) {
    $lang_name = mysqli_real_escape_string($conn, $_POST['lang_name']);
    $lang_place = isset($_POST['lang_place']) ? mysqli_real_escape_string($conn, $_POST['lang_place']) : "";
    $lang_info = mysqli_real_escape_string($conn, $_POST['lang_info']);
    $lang_vital = mysqli_real_escape_string($conn, $_POST['vitality']);

    // Get user_id from session
    $username = $_SESSION['username'];
    $user_id = $_SESSION["user_id"];

    // Prepared statement
    $stmt = $conn->prepare("INSERT INTO languages (lang_name, lang_place, lang_info, lang_vitality, user_id, approved) VALUES (?, ?, ?, ?, ?, 0)");
    $stmt->bind_param("sssss", $lang_name, $lang_place, $lang_info, $lang_vital, $user_id);
    $stmt->execute();

    $success = "Language request submitted successfully!";
}
?>

<div class="min-h-screen flex flex-col">
    <main class="flex-grow">
        <div class="container mx-auto p-6 max-w-4xl">
            <h2 class="text-3xl font-bold mb-6 text-gray-900">Request a Language to be Added</h2>

            <?php if (isset($success)) : ?>
                <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4" role="alert">
                    <strong class="font-bold">Success!</strong>
                    <span class="block sm:inline"><?php echo $success; ?></span>
                </div>
            <?php endif; ?>

            <form method="post" class="space-y-6">
                <div class="form-group">
                    <label for="lang_name" class="block text-sm font-medium text-gray-700">Language Name:</label>
                    <input type="text" id="lang_name" name="lang_name" required 
                           class="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm bg-gray-50">
                </div>

                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700">Geographical Location:</label>
                    <div class="flex items-center mt-2">
                        <input type="checkbox" id="has_location" name="has_location" 
                               class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded">
                        <label for="has_location" class="ml-2 text-sm text-gray-700">
                            Language is tied to a geographic location
                        </label>
                    </div>
                    <div id="location_field" class="mt-4 hidden">
                        <label for="lang_place" class="block text-sm font-medium text-gray-700">Country/Countries:</label>
                        <input type="text" id="lang_place" name="lang_place" autocomplete="off" 
                               class="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm bg-gray-50">
                        <div id="country-suggestions" class="mt-1 border border-gray-300 rounded-md shadow-sm hidden"></div>
                    </div>
                </div>

                <div class="form-group">
                    <label class="block text-sm font-medium text-gray-700">Language Vitality</label>
                    <div class="mt-2 space-y-2">
                        <div class="flex items-center">
                            <input type="radio" id="safe" name="vitality" value="safe" required 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                            <label for="safe" class="ml-2 text-sm text-gray-700">Safe</label>
                        </div>
                        <div class="flex items-center">
                            <input type="radio" id="unsafe" name="vitality" value="unsafe" required 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                            <label for="unsafe" class="ml-2 text-sm text-gray-700">Unsafe</label>
                        </div>
                        <div class="flex items-center">
                            <input type="radio" id="definitively_endangered" name="vitality" value="definitively_endangered" required 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                            <label for="definitively_endangered" class="ml-2 text-sm text-gray-700">Definitively Endangered</label>
                        </div>
                        <div class="flex items-center">
                            <input type="radio" id="severely_endangered" name="vitality" value="severely_endangered" required 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                            <label for="severely_endangered" class="ml-2 text-sm text-gray-700">Severely Endangered</label>
                        </div>
                        <div class="flex items-center">
                            <input type="radio" id="critically_endangered" name="vitality" value="critically_endangered" required 
                                   class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300">
                            <label for="critically_endangered" class="ml-2 text-sm text-gray-700">Critically Endangered</label>
                        </div>
                    </div>
                </div>

                <div class="form-group">
                    <label for="lang_info" class="block text-sm font-medium text-gray-700">Language Information</label>
                    <textarea id="lang_info" name="lang_info" rows="5" required 
                              class="mt-1 block w-full border-gray-300 rounded-lg shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm bg-gray-50"></textarea>
                </div>

                <button type="submit" name="submit" 
                        class="bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    Submit Request
                </button>
            </form>
        </div>
    </main>
    <?php include 'footer.php'; ?>
</div>

<script>
    // Toggle location field
    document.getElementById("has_location").addEventListener("change", function() {
        const locationField = document.getElementById("location_field");
        locationField.classList.toggle("hidden");
        if (!locationField.classList.contains("hidden")) {
            document.getElementById("lang_place").focus();
        }
    });

    // Country suggestions
    const countryInput = document.getElementById("lang_place");
    const countrySuggestions = document.getElementById("country-suggestions");

    countryInput.addEventListener("input", function() {
        const query = countryInput.value.toLowerCase();
        if (query.length > 0) {
            const filteredCountries = <?php echo json_encode($countries); ?>.filter(country => 
                country.toLowerCase().startsWith(query)
            );
            populateSuggestions(filteredCountries);
            countrySuggestions.classList.remove("hidden");
        } else {
            countrySuggestions.classList.add("hidden");
        }
    });

    function populateSuggestions(countries) {
        countrySuggestions.innerHTML = "";
        if (countries.length === 0) {
            const noResults = document.createElement("div");
            noResults.classList.add("px-4", "py-2", "text-gray-500", "text-sm");
            noResults.textContent = "No matching countries found";
            countrySuggestions.appendChild(noResults);
            return;
        }

        countries.forEach(country => {
            const suggestionItem = document.createElement("div");
            suggestionItem.classList.add("px-4", "py-2", "text-gray-700", "hover:bg-gray-100", "cursor-pointer");
            suggestionItem.textContent = country;
            suggestionItem.addEventListener("click", function() {
                countryInput.value = country;
                countrySuggestions.classList.add("hidden");
            });
            countrySuggestions.appendChild(suggestionItem);
        });
    }

    // Hide suggestions when clicking outside
    document.addEventListener("click", function(event) {
        if (!event.target.closest("#location_field")) {
            countrySuggestions.classList.add("hidden");
        }
    });
</script>
