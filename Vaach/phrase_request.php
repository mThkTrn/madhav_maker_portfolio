<?php
// Start session at the very beginning
session_start();

include "conn.php";

// Get language ID from URL or redirect to index.php
$lang_id = $_GET["id"] ?? null;
if (!$lang_id or !isset($_SESSION["user_id"])) {
    header("Location: index.php");
    exit;
}

// Fetch language information using prepared statement
$lang_stmt = $conn->prepare("SELECT * FROM languages WHERE lang_id = ?");
$lang_stmt->bind_param("i", $lang_id);
$lang_stmt->execute();
$lang_result = $lang_stmt->get_result();
$lang_info = $lang_result->fetch_assoc();

if (!$lang_info) {
    header("Location: index.php");
    exit;
}

$success_message = '';
$error_message = '';

// Handle form submission
if (isset($_POST['submit']) && isset($_SESSION["user_id"])) {
    // Get and sanitize input
    $phrase = trim($_POST['phrase']);
    $romanization = trim($_POST["romanization"] ?? '');
    $speech_part = $_POST["speech_part"];
    
    if ($speech_part == "other") {
        $speech_part = trim(strtolower($_POST["other_speech_part"]));
    }
    
    $translation = trim($_POST['translation']);
    $phonetic = trim($_POST['phonetic'] ?? '');
    $ipa = trim($_POST["ipa"] ?? '');
    $user_id = $_SESSION["user_id"];
    
    // Basic validation
    if (empty($phrase) || empty($translation)) {
        $error_message = 'Phrase and translation are required fields.';
    } else {
        // Prepare and execute the insert query
        $stmt = $conn->prepare("INSERT INTO phrases (lang_id, phrase, romanization, speech_part, translation, phonetic, ipa, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");
        $stmt->bind_param("issssssi", $lang_id, $phrase, $romanization, $speech_part, $translation, $phonetic, $ipa, $user_id);
        
        if ($stmt->execute()) {
            $success_message = 'Your phrase has been submitted successfully! It will be reviewed by our team.';
            // Clear form fields
            $phrase = $romanization = $speech_part = $translation = $phonetic = $ipa = '';
        } else {
            $error_message = 'There was an error submitting your phrase. Please try again.';
        }
        $stmt->close();
    }
}

// Now include header and navbar after we've done our checks and processing
include "header.php";
include "navbar.php";
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Suggest a Phrase - <?php echo htmlspecialchars($lang_info['lang_name']); ?> - Vaach</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.2.0/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .hero-gradient {
            background: linear-gradient(135deg, #1a56db 0%, #1e40af 100%);
        }
        .animate-fade-in {
            animation: fadeIn 0.6s ease-out forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .part-of-speech-option {
            transition: all 0.2s ease;
        }
        .part-of-speech-option:hover {
            background-color: #f3f4f6;
            transform: translateY(-1px);
        }
        .part-of-speech-option input[type="radio"]:checked + label {
            background-color: #3b82f6;
            color: white;
            border-color: #3b82f6;
        }
        .form-section {
            background-color: #f9fafb;
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
    </style>
</head>
<body class="bg-gray-50 font-sans antialiased">

<main class="py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-3xl mx-auto">
        <!-- Back button -->
        <div class="mb-4">
            <a href="language.php?id=<?php echo $lang_id; ?>" class="text-blue-600 hover:text-blue-800 flex items-center">
                <i class="fas fa-arrow-left mr-2"></i> Back to <?php echo htmlspecialchars($lang_info['lang_name']); ?>
            </a>
        </div>
        
        <!-- Title -->
        <h1 class="text-2xl font-bold text-gray-900 mb-8">Suggest a New Phrase</h1>

        <?php if ($success_message): ?>
            <div class="bg-green-50 border-l-4 border-green-400 p-4 mb-6 rounded">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-green-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-green-700"><?php echo htmlspecialchars($success_message); ?></p>
                    </div>
                </div>
            </div>
        <?php endif; ?>

        <?php if ($error_message): ?>
            <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700"><?php echo htmlspecialchars($error_message); ?></p>
                    </div>
                </div>
            </div>
        <?php endif; ?>

        <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2 class="text-lg font-medium text-gray-900">New Phrase Details</h2>
                <p class="mt-1 text-sm text-gray-500">Help us expand the <?php echo htmlspecialchars($lang_info['lang_name']); ?> dictionary by suggesting a new phrase.</p>
            </div>
            
            <div class="p-6">
                <form method="POST" class="space-y-6">
                    <!-- Phrase -->
                    <div class="form-section">
                        <label for="phrase" class="block text-sm font-medium text-gray-700 mb-1">Phrase in <?php echo htmlspecialchars($lang_info['lang_name']); ?> *</label>
                        <p class="text-xs text-gray-500 mb-2">Enter the word or phrase in the original language.</p>
                        <input type="text" id="phrase" name="phrase" required 
                               class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                               value="<?php echo isset($phrase) ? htmlspecialchars($phrase) : ''; ?>">
                    </div>

                    <!-- Romanization -->
                    <div class="form-section">
                        <label for="romanization" class="block text-sm font-medium text-gray-700 mb-1">Romanization</label>
                        <p class="text-xs text-gray-500 mb-2">How the phrase is pronounced using the Latin alphabet (optional).</p>
                        <input type="text" id="romanization" name="romanization" 
                               class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                               value="<?php echo isset($romanization) ? htmlspecialchars($romanization) : ''; ?>">
                    </div>

                    <!-- Part of Speech Dropdown -->
                    <div class="form-section">
                        <label for="speech_part" class="block text-sm font-medium text-gray-700 mb-1">Part of Speech *</label>
                        <p class="text-xs text-gray-500 mb-2">Select the grammatical category that best describes this phrase.</p>
                        <select id="speech_part" name="speech_part" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
                            <option value="" disabled <?php echo !isset($speech_part) ? 'selected' : ''; ?>>Select a part of speech</option>
                            <option value="noun" <?php echo (isset($speech_part) && $speech_part === 'noun') ? 'selected' : ''; ?>>Noun</option>
                            <option value="verb" <?php echo (isset($speech_part) && $speech_part === 'verb') ? 'selected' : ''; ?>>Verb</option>
                            <option value="adjective" <?php echo (isset($speech_part) && $speech_part === 'adjective') ? 'selected' : ''; ?>>Adjective</option>
                            <option value="adverb" <?php echo (isset($speech_part) && $speech_part === 'adverb') ? 'selected' : ''; ?>>Adverb</option>
                            <option value="pronoun" <?php echo (isset($speech_part) && $speech_part === 'pronoun') ? 'selected' : ''; ?>>Pronoun</option>
                            <option value="preposition" <?php echo (isset($speech_part) && $speech_part === 'preposition') ? 'selected' : ''; ?>>Preposition</option>
                            <option value="conjunction" <?php echo (isset($speech_part) && $speech_part === 'conjunction') ? 'selected' : ''; ?>>Conjunction</option>
                            <option value="interjection" <?php echo (isset($speech_part) && $speech_part === 'interjection') ? 'selected' : ''; ?>>Interjection</option>
                            <option value="phrase" <?php echo (isset($speech_part) && $speech_part === 'phrase') ? 'selected' : ''; ?>>Phrase</option>
                            <option value="other" <?php echo (isset($speech_part) && !in_array($speech_part, ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection', 'phrase', ''])) ? 'selected' : ''; ?>>Other (specify)</option>
                        </select>
                        
                        <div id="other_speech_part_container" class="mt-3" style="display: <?php echo (isset($speech_part) && !in_array($speech_part, ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection', 'phrase', ''])) ? 'block' : 'none'; ?>">
                            <label for="other_speech_part" class="block text-sm font-medium text-gray-700 mb-1">Specify Part of Speech</label>
                            <input type="text" id="other_speech_part" name="other_speech_part" 
                                   class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                   value="<?php echo (isset($speech_part) && !in_array($speech_part, ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection', 'phrase', ''])) ? htmlspecialchars($speech_part) : ''; ?>">
                        </div>
                    </div>

                    <!-- Translation -->
                    <div class="form-section">
                        <label for="translation" class="block text-sm font-medium text-gray-700 mb-1">English Translation *</label>
                        <p class="text-xs text-gray-500 mb-2">Provide the English translation of the phrase.</p>
                        <input type="text" id="translation" name="translation" required 
                               class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                               value="<?php echo isset($translation) ? htmlspecialchars($translation) : ''; ?>">
                    </div>

                    <!-- Phonetic -->
                    <div class="form-section">
                        <label for="phonetic" class="block text-sm font-medium text-gray-700 mb-1">Phonetic Pronunciation</label>
                        <p class="text-xs text-gray-500 mb-2">How the phrase sounds phonetically (optional).</p>
                        <div class="mt-1 relative rounded-md shadow-sm">
                            <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">/</span>
                            <input type="text" id="phonetic" name="phonetic" 
                                   class="block w-full pl-4 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                   placeholder="fəʊnɛtɪk"
                                   value="<?php echo isset($phonetic) ? htmlspecialchars($phonetic) : ''; ?>">
                            <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">/</span>
                        </div>
                    </div>

                    <!-- IPA -->
                    <div class="form-section">
                        <label for="ipa" class="block text-sm font-medium text-gray-700 mb-1">IPA Pronunciation</label>
                        <p class="text-xs text-gray-500 mb-2">International Phonetic Alphabet representation (optional).</p>
                        <div class="mt-1 relative rounded-md shadow-sm">
                            <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">[</span>
                            <input type="text" id="ipa" name="ipa" 
                                   class="block w-full pl-6 pr-6 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                   placeholder="fəˈnɛtɪk"
                                   value="<?php echo isset($ipa) ? htmlspecialchars($ipa) : ''; ?>">
                            <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">]</span>
                        </div>
                    </div>

                    <!-- Submit Button -->
                    <div class="pt-2">
                        <button type="submit" name="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                            <i class="fas fa-paper-plane mr-2"></i> Submit Phrase
                        </button>
                    </div>
                    
                    <p class="text-xs text-gray-500 mt-2">
                        By submitting this phrase, you agree to our <a href="terms.php" class="text-blue-600 hover:text-blue-500 hover:underline">Terms of Service</a> and <a href="guidelines.php" class="text-blue-600 hover:text-blue-500 hover:underline">Community Guidelines</a>.
                    </p>
                </form>
            </div>
        </div>
        
        <!-- Help Section -->
        <div class="mt-8 bg-blue-50 border-l-4 border-blue-400 p-4 rounded">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h2a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3">
                    <h3 class="text-sm font-medium text-blue-800">Tips for submitting a good phrase</h3>
                    <div class="mt-2 text-sm text-blue-700">
                        <ul class="list-disc pl-5 space-y-1">
                            <li>Ensure the phrase is accurate and commonly used in <?php echo htmlspecialchars($lang_info['lang_name']); ?>.</li>
                            <li>Provide as much detail as possible in the translation and pronunciation fields.</li>
                            <li>Use the IPA field for precise pronunciation using the International Phonetic Alphabet.</li>
                            <li>All submissions will be reviewed by our team before being added to the dictionary.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>
</main>

<?php include "footer.php"; ?>

<script>
// Handle part of speech dropdown
const speechPartSelect = document.getElementById('speech_part');
const otherContainer = document.getElementById('other_speech_part_container');
const otherInput = document.getElementById('other_speech_part');

if (speechPartSelect) {
    // Show/hide other input based on selection
    speechPartSelect.addEventListener('change', function() {
        if (this.value === 'other') {
            otherContainer.style.display = 'block';
            otherInput.required = true;
        } else {
            otherContainer.style.display = 'none';
            otherInput.required = false;
        }
    });

    // Initialize the form state
    if (speechPartSelect.value === 'other') {
        otherContainer.style.display = 'block';
        otherInput.required = true;
    }

    // Make sure the form submits the correct value
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            if (speechPartSelect.value === 'other' && otherInput.value.trim() !== '') {
                // Create a hidden input to submit the other value
                const hiddenInput = document.createElement('input');
                hiddenInput.type = 'hidden';
                hiddenInput.name = 'speech_part';
                hiddenInput.value = otherInput.value.trim();
                form.appendChild(hiddenInput);
            }
        });
    }
}
</script>

</body>
</script>