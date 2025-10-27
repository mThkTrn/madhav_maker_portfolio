
<?php
// Start output buffering to prevent headers already sent error
ob_start();

// Include database connection
include "conn.php";

// Include header which handles session start
include "header.php";

// Check for required session and GET parameters before including header/navbar
if (!isset($_SESSION["user_id"]) || !isset($_SESSION["tags"]) || !isset($_GET["phrase_id"]) || !isset($_GET["lang_id"])) {
    header("Location: index.php");
    exit;
}

$phrase_id = (int)$_GET["phrase_id"];
$lang_id = (int)$_GET["lang_id"];

// Get language name for the page title
$lang_stmt = $conn->prepare("SELECT lang_name FROM languages WHERE lang_id = ?");
$lang_stmt->bind_param("i", $lang_id);
$lang_stmt->execute();
$lang_result = $lang_stmt->get_result();
$lang_data = $lang_result->fetch_assoc();
$lang_name = $lang_data ? $lang_data['lang_name'] : 'Language';

// Now include header and navbar after we've done our checks
include "header.php";
include "navbar.php";

$is_admin = false;

if(in_array($lang_id."_a", $_SESSION["tags"]) or in_array($lang_id."_sa", $_SESSION["tags"])){
    $is_admin = true;
}

// Handle form submission
if (isset($_POST["phrase"]) and isset($_POST["translation"]) and isset($_POST["phonetic"])){
    $speech_part = $_POST["speech_part"];
    if($speech_part == "other"){
        $speech_part = $_POST["other_speech_part"];
    }
    
    // Prepare the statement to prevent SQL injection
    $approved = (int)$is_admin;
    $user_id = $_SESSION["user_id"];
    
    $stmt = $conn->prepare("INSERT INTO phrases (lang_id, phrase, romanization, speech_part, translation, phonetic, ipa, user_id, approved, replacing) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
    $stmt->bind_param("issssssiii", 
        $lang_id, 
        $_POST["phrase"], 
        $_POST["romanization"], 
        $speech_part, 
        $_POST["translation"], 
        $_POST["phonetic"], 
        $_POST["ipa"], 
        $user_id, 
        $approved, 
        $phrase_id
    );
    
    if($stmt->execute()){
        if($is_admin){
            $expiration_query = $conn->prepare("DELETE FROM phrases WHERE phrase_id = ?");
            $expiration_query->bind_param("i", $phrase_id);
            $expiration_query->execute();
        }
        header("Location: language.php?id=".$lang_id);
        exit;
    } else {
        $error = "Error saving your changes. Please try again.";
    }
}

// Fetch the phrase to edit
$stmt = $conn->prepare("SELECT * FROM phrases WHERE lang_id = ? AND phrase_id = ?");
$stmt->bind_param("ii", $lang_id, $phrase_id);
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();

if ($row and $row["approved"]==1) {
    $phrase = $row["phrase"];
    $romanization = $row["romanization"];
    $speech_part = $row["speech_part"];
    $translation = $row["translation"];
    $phonetic = $row["phonetic"];
    $ipa = $row["ipa"];
    $user_id = $row["user_id"];
} else {
    header("Location: index.php");
    exit;
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $is_admin ? 'Edit' : 'Suggest Edit for'; ?> "<?php echo htmlspecialchars($phrase); ?>" - <?php echo htmlspecialchars($lang_name); ?> - Vaach</title>
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
    </style>
</head>
<body class="bg-gray-50 font-sans antialiased">

<main class="py-8 px-4 sm:px-6 lg:px-8">
    <div class="max-w-4xl mx-auto">
        <!-- Back button -->
        <div class="mb-4">
            <a href="language.php?id=<?php echo $lang_id; ?>" class="text-blue-600 hover:text-blue-800 flex items-center">
                <i class="fas fa-arrow-left mr-2"></i> Back to <?php echo htmlspecialchars($lang_name); ?>
            </a>
        </div>
        
        <!-- Title -->
        <h1 class="text-2xl font-bold text-gray-900 mb-8">
            <?php echo $is_admin ? 'Edit Phrase' : 'Suggest an Edit to Phrase'; ?>
        </h1>

        <?php if (isset($error)): ?>
            <div class="bg-red-50 border-l-4 border-red-400 p-4 mb-6 rounded">
                <div class="flex">
                    <div class="flex-shrink-0">
                        <svg class="h-5 w-5 text-red-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-sm text-red-700"><?php echo htmlspecialchars($error); ?></p>
                    </div>
                </div>
            </div>
        <?php endif; ?>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- Current Phrase Card -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h2 class="text-lg font-medium text-gray-900">Current Phrase</h2>
                </div>
                <div class="p-6">
                    <div class="mb-4">
                        <h3 class="text-2xl font-semibold text-gray-900"><?php echo htmlspecialchars($phrase); ?></h3>
                        <?php if (!empty($romanization)): ?>
                            <p class="text-gray-500 italic mt-1"><?php echo htmlspecialchars($romanization); ?></p>
                        <?php endif; ?>
                        <?php if (!empty($speech_part)): ?>
                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mt-2">
                                <?php echo htmlspecialchars(ucfirst($speech_part)); ?>
                            </span>
                        <?php endif; ?>
                    </div>
                    
                    <div class="space-y-4">
                        <div>
                            <p class="text-sm font-medium text-gray-500">Translation</p>
                            <p class="text-gray-900"><?php echo htmlspecialchars($translation); ?></p>
                        </div>
                        
                        <?php if (!empty($phonetic)): ?>
                        <div>
                            <p class="text-sm font-medium text-gray-500">Phonetic Pronunciation</p>
                            <p class="font-mono text-gray-900">/<?php echo htmlspecialchars($phonetic); ?>/</p>
                        </div>
                        <?php endif; ?>
                        
                        <?php if (!empty($ipa)): ?>
                        <div>
                            <p class="text-sm font-medium text-gray-500">IPA</p>
                            <p class="font-sans text-gray-900">[<?php echo htmlspecialchars($ipa); ?>]</p>
                        </div>
                        <?php endif; ?>
                    </div>
                </div>
            </div>

            <!-- Edit Form -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h2 class="text-lg font-medium text-gray-900"><?php echo $is_admin ? 'Edit Phrase' : 'Suggest Edit'; ?></h2>
                </div>
                <div class="p-6">
                    <form method="POST" class="space-y-6">
                        <!-- Phrase -->
                        <div>
                            <label for="phrase" class="block text-sm font-medium text-gray-700 mb-1">Phrase in <?php echo htmlspecialchars($lang_name); ?></label>
                            <input type="text" id="phrase" name="phrase" required 
                                   class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                   value="<?php echo htmlspecialchars($phrase); ?>">
                        </div>

                        <!-- Romanization -->
                        <div>
                            <label for="romanization" class="block text-sm font-medium text-gray-700 mb-1">Romanization (optional)</label>
                            <input type="text" id="romanization" name="romanization" 
                                   class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                   value="<?php echo htmlspecialchars($romanization); ?>">
                        </div>

                        <!-- Part of Speech Dropdown -->
                        <div>
                            <label for="speech_part" class="block text-sm font-medium text-gray-700 mb-1">Part of Speech</label>
                            <select id="speech_part" name="speech_part" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md">
                                <option value="" <?php echo empty($speech_part) ? 'selected' : ''; ?>>Select a part of speech</option>
                                <option value="noun" <?php echo $speech_part === 'noun' ? 'selected' : ''; ?>>Noun</option>
                                <option value="verb" <?php echo $speech_part === 'verb' ? 'selected' : ''; ?>>Verb</option>
                                <option value="adjective" <?php echo $speech_part === 'adjective' ? 'selected' : ''; ?>>Adjective</option>
                                <option value="adverb" <?php echo $speech_part === 'adverb' ? 'selected' : ''; ?>>Adverb</option>
                                <option value="pronoun" <?php echo $speech_part === 'pronoun' ? 'selected' : ''; ?>>Pronoun</option>
                                <option value="preposition" <?php echo $speech_part === 'preposition' ? 'selected' : ''; ?>>Preposition</option>
                                <option value="conjunction" <?php echo $speech_part === 'conjunction' ? 'selected' : ''; ?>>Conjunction</option>
                                <option value="interjection" <?php echo $speech_part === 'interjection' ? 'selected' : ''; ?>>Interjection</option>
                                <option value="phrase" <?php echo $speech_part === 'phrase' ? 'selected' : ''; ?>>Phrase</option>
                                <option value="other">Other (specify)</option>
                            </select>
                            
                            <div id="other_speech_part_container" class="mt-3" style="display: <?php echo !in_array($speech_part, ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection', 'phrase', '']) ? 'block' : 'none'; ?>">
                                <label for="other_speech_part" class="block text-sm font-medium text-gray-700 mb-1">Specify Part of Speech</label>
                                <input type="text" id="other_speech_part" name="other_speech_part" 
                                       class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                       value="<?php echo !in_array($speech_part, ['noun', 'verb', 'adjective', 'adverb', 'pronoun', 'preposition', 'conjunction', 'interjection', 'phrase', '']) ? htmlspecialchars($speech_part) : ''; ?>">
                            </div>
                        </div>

                        <!-- Translation -->
                        <div>
                            <input type="text" id="translation" name="translation" required 
                                   class="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                   value="<?php echo htmlspecialchars($translation); ?>">
                        </div>

                        <!-- Phonetic -->
                        <div>
                            <label for="phonetic" class="block text-sm font-medium text-gray-700 mb-1">Phonetic Pronunciation (optional)</label>
                            <div class="mt-1 relative rounded-md shadow-sm">
                                <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">/</span>
                                <input type="text" id="phonetic" name="phonetic" 
                                       class="block w-full pl-4 pr-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                       placeholder="fəʊnɛtɪk"
                                       value="<?php echo htmlspecialchars($phonetic); ?>">
                                <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">/</span>
                            </div>
                        </div>

                        <!-- IPA -->
                        <div>
                            <label for="ipa" class="block text-sm font-medium text-gray-700 mb-1">IPA Pronunciation (optional)</label>
                            <div class="mt-1 relative rounded-md shadow-sm">
                                <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">[</span>
                                <input type="text" id="ipa" name="ipa" 
                                       class="block w-full pl-6 pr-6 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                       placeholder="fəˈnɛtɪk"
                                       value="<?php echo htmlspecialchars($ipa); ?>">
                                <span class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">]</span>
                            </div>
                        </div>

                        <!-- Submit Button -->
                        <div class="pt-4">
                            <button type="submit" name="submit" class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                <?php echo $is_admin ? 'Save Changes' : 'Suggest Edit'; ?>
                            </button>
                        </div>
                    </form>
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

    // If page loads with 'other' selected, ensure the input is visible
    if (speechPartSelect.value === 'other') {
        otherContainer.style.display = 'block';
        otherInput.required = true;
    }
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
// Toggle other part of speech field
function toggleOtherSpeechPart(selectedValue) {
    const otherContainer = document.getElementById('other_speech_part_container');
    if (selectedValue === 'other') {
        otherContainer.style.display = 'block';
        document.getElementById('other_speech_part').setAttribute('required', 'required');
    } else {
        otherContainer.style.display = 'none';
        document.getElementById('other_speech_part').removeAttribute('required');
    }
}

// Set up event listeners for part of speech radio buttons
document.querySelectorAll('input[name="speech_part"]').forEach(radio => {
    radio.addEventListener('change', function() {
        toggleOtherSpeechPart(this.value);
    });
});

// Initialize the form state
document.addEventListener('DOMContentLoaded', function() {
    const selectedRadio = document.querySelector('input[name="speech_part"]:checked');
    if (selectedRadio) {
        toggleOtherSpeechPart(selectedRadio.value);
    }
});
</script>

</body>