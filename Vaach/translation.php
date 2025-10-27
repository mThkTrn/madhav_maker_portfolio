<?php
// Start session
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Include header
$pageTitle = "Translation Tool - Vaach";
include_once 'header.php';
include_once 'navbar.php';

// Include database connection
include_once 'conn.php';

// Function to get all languages from the database
function getAllLanguages($conn) {
    $languages = [];
    $query = "SELECT lang_id, lang_name FROM languages ORDER BY lang_name";
    $result = mysqli_query($conn, $query);
    
    if ($result) {
        while ($row = mysqli_fetch_assoc($result)) {
            $languages[] = $row;
        }
    }
    
    return $languages;
}

// Function to get phrases for a specific language
function getLanguagePhrases($conn, $lang_id) {
    $phrases = [];
    $query = "SELECT phrase, translation FROM phrases WHERE lang_id = ?";
    $stmt = $conn->prepare($query);
    $stmt->bind_param("i", $lang_id);
    $stmt->execute();
    $result = $stmt->get_result();
    
    while ($row = $result->fetch_assoc()) {
        $phrases[] = $row;
    }
    
    return $phrases;
}

// Function to call OpenAI API with context from the database
function translateWithOpenAI($conn, $text, $lang_id, $lang_name) {
    // Replace with your actual OpenAI API key
    $apiKey = 'obfuscated';
    
    // Get phrases for the selected language
    $phrases = getLanguagePhrases($conn, $lang_id);
    
    // Build context from phrases
    $context = "Here are some phrases and their translations in $lang_name:\n\n";
    foreach ($phrases as $phrase) {
        $context .= "English: " . $phrase['phrase'] . "\n";
        $context .= "$lang_name: " . $phrase['translation'] . "\n\n";
    }
    
    $prompt = "You are a professional translator. Translate the following English text to $lang_name. " .
              "Use the following context to ensure accurate translation, especially for specialized terms or phrases. " .
              "Maintain the same tone and style as the original text." .
              "If you are not sure about a particular piece of vocabulary, leave that as an english word, but surround it in the \"@\" sign (e.g. @word@).\n\n" .
              "Context:\n$context\n" .
              "English: $text\n" .
              "$lang_name: ";
    
    $data = [
        'model' => 'gpt-3.5-turbo',
        'messages' => [
            [
                'role' => 'system',
                'content' => "You are a helpful researcher with a PhD in linguistics, specializing in translation. You are translating text to $lang_name. " .
                           "When translating a phrase, provide ONLY the plain text translation at the very top of your response. " .
                           "If you're unsure of a word, represent it with curly brackets {} around it. " .
                           "Do not include any explanations, notes, or additional text - ONLY output the translation itself. " .
                           "Use the following context for reference, but DO NOT include it in your response:\n\n$context"
            ],
            [
                'role' => 'user',
                'content' => "Translate this to $lang_name: $text"
            ]
        ],
        'max_tokens' => 1000,
        'temperature' => 0.3,  // Lower temperature for more consistent translations
        'top_p' => 1,
        'frequency_penalty' => 0,
        'presence_penalty' => 0
    ];
    
    // Initialize cURL
    $ch = curl_init('https://api.openai.com/v1/chat/completions');
    
    // Set cURL options
    $curlOptions = [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($data),
        CURLOPT_HTTPHEADER => [
            'Content-Type: application/json',
            'Authorization: Bearer ' . $apiKey
        ],
        CURLOPT_TIMEOUT => 30
    ];
    
    // Set CA bundle path if available
    $cacert = __DIR__ . '/cacert.pem';
    if (file_exists($cacert)) {
        $curlOptions[CURLOPT_CAINFO] = $cacert;
        $curlOptions[CURLOPT_SSL_VERIFYPEER] = true;
        $curlOptions[CURLOPT_SSL_VERIFYHOST] = 2;
    } else {
        $curlOptions[CURLOPT_SSL_VERIFYPEER] = false;
        $curlOptions[CURLOPT_SSL_VERIFYHOST] = 0;
    }
    
    curl_setopt_array($ch, $curlOptions);
    
    // Execute the request
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    $curlError = curl_error($ch);
    
    // Close cURL resource
    curl_close($ch);
    
    
    // Process the response
    if ($response === false) {
        error_log("cURL Error: " . $curlError);
        return "Error: Could not connect to the translation service. Please check your internet connection.";
    }
    
    $result = json_decode($response, true);
    
    if ($httpCode === 200 && isset($result['choices'][0]['message']['content'])) {
        $translation = trim($result['choices'][0]['message']['content']);
        
        // Clean up the translation - remove any leading/trailing quotes or special characters
        $translation = preg_replace('/^[^\p{L}\p{N}\s]+/u', '', $translation);
        $translation = preg_replace('/[^\p{L}\p{N}\s]+$/u', '', $translation);
        
        return $translation;
    } else {
        $errorMsg = "Error: Could not translate at this time. ";
        $errorMsg .= "Status: $httpCode\n";
        $errorMsg .= "Response: " . print_r($result, true);
        error_log($errorMsg);
        
        return $errorMsg;
    }
}

// Get all available languages
$languages = getAllLanguages($conn);

// Handle form submission
$translationResult = '';
$selectedLanguage = '';
$inputText = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['translate'])) {
    $inputText = trim($_POST['text']);
    $lang_id = (int)$_POST['lang_id'];
    
    // Find the language name
    $lang_name = '';
    foreach ($languages as $lang) {
        if ($lang['lang_id'] == $lang_id) {
            $lang_name = $lang['lang_name'];
            $selectedLanguage = $lang_id;
            break;
        }
    }
    
    if (!empty($inputText) && !empty($lang_name)) {
        // Call the translation function with database context
        $translationResult = translateWithOpenAI($conn, $inputText, $lang_id, $lang_name);
    } elseif (empty($lang_name)) {
        $translationResult = "Error: Invalid language selected.";
    }
}
?>

<div class="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
        <div class="text-center mb-8">
            <div class="flex items-center justify-center gap-2 mb-2">
                <h1 class="text-3xl font-bold text-gray-900">Translation Tool</h1>
                <div class="relative group">
                    <svg class="w-5 h-5 text-gray-400 hover:text-gray-600 cursor-help" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h2a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path>
                    </svg>
                    <div class="hidden group-hover:block absolute z-10 w-64 p-2 -ml-32 mt-2 text-sm text-gray-700 bg-white border border-gray-200 rounded-lg shadow-lg">
                        This AI-powered translation tool provides instant translations. Note that it may contain inaccuracies. If the system encounters unknown words, they will be displayed in English.
                    </div>
                </div>
            </div>
            <p class="text-gray-600">Translate text to various languages using AI-powered translation</p>
        </div>
        
        <div class="bg-white shadow-md rounded-lg p-6 mb-8">
            <form id="translationForm" method="POST" action="translation.php" class="space-y-6">
                <div>
                    <label for="target_language" class="block text-sm font-medium text-gray-700 mb-1">
                        Target Language
                    </label>
                    <select id="lang_id" name="lang_id" required
                            class="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md">
                        <option value="">Select a language</option>
                        <?php foreach ($languages as $lang): ?>
                            <option value="<?php echo $lang['lang_id']; ?>" <?php echo ($selectedLanguage == $lang['lang_id']) ? 'selected' : ''; ?>>
                                <?php echo htmlspecialchars($lang['lang_name']); ?>
                            </option>
                        <?php endforeach; ?>
                    </select>
                </div>
                
                <div class="relative mt-4">
                    <div class="flex items-center justify-between mb-2 px-1">
                        <span id="sourceLang" class="text-sm font-medium text-gray-700">English</span>
                        <button type="button" id="swapLanguages" class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fill-rule="evenodd" d="M8 7a1 1 0 01.707.293l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414-1.414L10.586 12 7.293 8.707A1 1 0 018 7z" clip-rule="evenodd" />
                            </svg>
                        </button>
                        <span id="targetLang" class="text-sm font-medium text-gray-700"><?php 
                            $selectedLangName = '';
                            if (isset($_POST['lang_id'])) {
                                foreach ($languages as $lang) {
                                    if ($lang['lang_id'] == $_POST['lang_id']) {
                                        $selectedLangName = htmlspecialchars($lang['lang_name']);
                                        break;
                                    }
                                }
                            }
                            echo $selectedLangName ?: 'Select a language';
                        ?></span>
                        <input type="hidden" id="direction" name="direction" value="en_to_target">
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                        <div class="flex flex-col h-full">
                            <div class="flex-1 flex flex-col">
                                <textarea id="sourceText" name="text" rows="8" required
                                        class="flex-1 shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border border-gray-300 rounded-md p-3 resize-none"
                                        placeholder="Enter text to translate"><?php echo htmlspecialchars($inputText); ?></textarea>
                            </div>
                        </div>
                        <div class="flex flex-col h-full">
                            <div class="flex-1">
                                <div id="translationResult" class="h-full min-h-[200px] bg-gray-50 p-3 rounded-md border border-gray-300 overflow-auto">
                                    <?php if (isset($translationResult)): ?>
                                        <?php echo nl2br(htmlspecialchars($translationResult)); ?>
                                    <?php else: ?>
                                        <div class="text-gray-400 h-full flex items-center justify-center">Translation will appear here...</div>
                                    <?php endif; ?>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div>
                    <button type="submit" name="translate"
                            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        Translate
                    </button>
                </div>
            </form>
        </div>
        </div>
    </div>
</div>

<?php 
// Close database connection if it's open
if (isset($conn)) {
    mysqli_close($conn);
}
include_once 'footer.php'; 
?>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const swapBtn = document.getElementById('swapLanguages');
    const sourceLang = document.getElementById('sourceLang');
    const targetLang = document.getElementById('targetLang');
    const directionInput = document.getElementById('direction');
    const sourceText = document.getElementById('sourceText');
    const translationResult = document.getElementById('translationResult');
    const langSelect = document.getElementById('lang_id');
    
    // Update target language when select changes
    langSelect.addEventListener('change', function() {
        const selectedOption = langSelect.options[langSelect.selectedIndex];
        if (directionInput.value === 'en_to_target') {
            targetLang.textContent = selectedOption.text;
        } else {
            sourceLang.textContent = selectedOption.text;
        }
        // Clear all fields when language changes
        sourceText.value = '';
        translationResult.innerHTML = '<div class="text-gray-400 h-full flex items-center justify-center">Translation will appear here...</div>';
    });
    
    // Swap languages
    swapBtn.addEventListener('click', function() {
        const tempLang = sourceLang.textContent;
        sourceLang.textContent = targetLang.textContent;
        targetLang.textContent = tempLang;
        
        // Get the translation result text, handling both plain text and HTML content
        let resultText = '';
        if (translationResult.textContent === 'Translation will appear here...') {
            resultText = '';
        } else if (translationResult.innerText) {
            // Use innerText to get visible text without HTML tags
            resultText = translationResult.innerText.trim();
        } else {
            resultText = translationResult.textContent.trim();
        }
        
        // Swap input and result
        const tempText = sourceText.value;
        sourceText.value = resultText;
        
        // Clear the translation result
        translationResult.innerHTML = tempText ? 
            tempText.replace(/\n/g, '<br>') : 
            '<div class="text-gray-400 h-full flex items-center justify-center">Translation will appear here...</div>';
        
        // Clear the source text if it was showing the placeholder
        if (sourceText.value === 'Translation will appear here...') {
            sourceText.value = '';
        }
        
        // Update direction
        directionInput.value = directionInput.value === 'en_to_target' ? 'target_to_en' : 'en_to_target';
    });
});
</script>
