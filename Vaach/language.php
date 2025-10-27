<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo htmlspecialchars($lang_info['lang_name'] ?? 'Language Details'); ?> - Vaach</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.2.0/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .hero-gradient {
            background: linear-gradient(135deg, #1a56db 0%, #1e40af 100%);
        }
        .phrase-card {
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .phrase-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        }
        .animate-fade-in {
            animation: fadeIn 0.6s ease-out forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body class="bg-gray-50 font-sans antialiased">

    <?php
    // Import database connection and header files
    include "conn.php";
    include "header.php";
    include "navbar.php";

    // Get language ID from URL or redirect to index.php
    $lang_id = $_GET["id"] ?? null;
    if (!$lang_id) {
        header("Location: index.php");
        exit;
    }

    // Fetch language information
    $lang_info_query = "SELECT * FROM languages WHERE lang_id = $lang_id AND approved = 1";
    $lang_info_result = mysqli_query($conn, $lang_info_query);
    $lang_info = mysqli_fetch_assoc($lang_info_result);

    if (!$lang_info) {
        header("Location: index.php");
        exit;
    }

    // Fetch phrases for the language
    $phrases_query = "SELECT * FROM phrases WHERE lang_id = $lang_id AND approved = 1 ORDER BY phrase ASC";
    $phrases_result = mysqli_query($conn, $phrases_query);
    $phrases_count = mysqli_num_rows($phrases_result);
    ?>

    <!-- Hero Section -->
    <div class="hero-gradient text-white py-12 md:py-20 relative overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
            <div class="absolute -top-20 -left-20 w-64 h-64 bg-yellow-400 rounded-full mix-blend-multiply filter blur-xl opacity-20"></div>
            <div class="absolute top-1/2 right-0 w-1/3 h-1/2 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20"></div>
            <div class="absolute -bottom-20 right-20 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-20"></div>
        </div>
        <div class="container mx-auto px-4 relative z-10">
            <div class="max-w-4xl mx-auto text-center">
                <h1 class="text-4xl md:text-5xl font-bold mb-4"><?php echo htmlspecialchars($lang_info['lang_name']); ?></h1>
                <div class="w-24 h-1.5 bg-yellow-400 mx-auto mb-6 rounded-full"></div>
                
                <div class="flex flex-wrap justify-center gap-4 mb-8">
                    <?php if (!empty($lang_info['lang_place'])): ?>
                        <span class="bg-white bg-opacity-90 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium text-gray-800">
                            <i class="fas fa-map-marker-alt mr-2 text-blue-600"></i>
                            <?php echo htmlspecialchars($lang_info['lang_place']); ?>
                        </span>
                    <?php endif; ?>
                    
                    <span class="bg-white bg-opacity-90 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium text-gray-800">
                        <i class="fas fa-language mr-2 text-blue-600"></i>
                        <?php echo $phrases_count; ?> phrase<?php echo $phrases_count != 1 ? 's' : ''; ?>
                    </span>
                    
                    <?php if (!empty($lang_info['lang_vitality'])): ?>
                        <?php 
                        $vitality = str_replace("_", " ", ucfirst($lang_info['lang_vitality']));
                        $vitality_class = [
                            'Vital' => 'bg-green-100 text-green-800',
                            'Endangered' => 'bg-yellow-100 text-yellow-800',
                            'Extinct' => 'bg-red-100 text-red-800',
                            'Dormant' => 'bg-gray-100 text-gray-800',
                            'Revitalization' => 'bg-blue-100 text-blue-800'
                        ][$vitality] ?? 'bg-gray-100 text-gray-800';
                        ?>
                        <span class="<?php echo $vitality_class; ?> px-4 py-2 rounded-full text-sm font-medium">
                            <i class="fas fa-heartbeat mr-2"></i>
                            <?php echo $vitality; ?>
                        </span>
                    <?php endif; ?>
                </div>
                
                <?php if (isset($_SESSION["user_id"])): ?>
                    <a href="phrase_request.php?id=<?php echo $lang_id; ?>" class="inline-flex items-center bg-white text-blue-700 hover:bg-blue-50 font-semibold py-3 px-6 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
                        <i class="fas fa-plus-circle mr-2"></i>
                        Suggest a Phrase
                    </a>
                <?php else: ?>
                    <div class="bg-white p-4 rounded-lg max-w-2xl mx-auto shadow-sm border border-gray-200">
                        <p class="text-gray-800">Log in to suggest or edit phrases</p>
                    </div>
                <?php endif; ?>
                
                <?php if (isset($_SESSION["tags"]) && (in_array($lang_id . '_a', $_SESSION["tags"]) || in_array($lang_id . '_sa', $_SESSION["tags"]))): ?>
                    <div class="mt-6">
                        <a href="language_admin.php?id=<?php echo $lang_id; ?>" class="inline-flex items-center bg-yellow-600 text-white hover:bg-yellow-700 font-semibold py-2 px-4 rounded-lg text-sm transition-colors">
                            <i class="fas fa-cog mr-2"></i>
                            Admin Panel
                        </a>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-12">
        <!-- Search Section -->
        <div class="max-w-3xl mx-auto mb-12">
            <div class="relative">
                <input 
                    type="text" 
                    id="phraseSearch" 
                    placeholder="Search phrases..." 
                    class="w-full py-3 px-5 pr-12 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm transition-all duration-200"
                    oninput="phraseSearch()"
                >
                <div class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                    <i class="fas fa-search"></i>
                </div>
            </div>
            <p id="searchResults" class="mt-2 text-sm text-gray-500 text-center">
                <?php echo $phrases_count; ?> phrase<?php echo $phrases_count != 1 ? 's' : ''; ?> available
            </p>
        </div>

        <?php if ($phrases_count === 0): ?>
            <div class="text-center py-16 bg-white rounded-xl shadow-sm">
                <div class="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
                    <i class="fas fa-inbox text-3xl text-blue-500"></i>
                </div>
                <h3 class="text-xl font-semibold text-gray-800 mb-2">No phrases yet</h3>
                <p class="text-gray-600 max-w-md mx-auto mb-6">Be the first to contribute to this language!</p>
                <?php if (isset($_SESSION["user_id"])): ?>
                    <a href="phrase_request.php?id=<?php echo $lang_id; ?>" class="inline-flex items-center bg-blue-600 text-white hover:bg-blue-700 font-semibold py-2 px-6 rounded-lg transition-colors">
                        <i class="fas fa-plus-circle mr-2"></i>
                        Add First Phrase
                    </a>
                <?php endif; ?>
            </div>
        <?php else: ?>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" id="phrasesContainer">
                <?php while ($row = mysqli_fetch_assoc($phrases_result)): ?>
                    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden phrase-card hover:shadow-md transition-all duration-300 animate-fade-in flex flex-col h-full">
                        <div class="p-6 flex-grow">
                            <div class="flex justify-between items-start mb-4">
                                <h3 class="text-xl font-bold text-gray-900"><?php echo htmlspecialchars($row['phrase']); ?></h3>
                                <?php if (!empty($row['speech_part'])): ?>
                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                        <?php echo htmlspecialchars($row['speech_part']); ?>
                                    </span>
                                <?php endif; ?>
                            </div>
                            
                            <?php if (!empty($row['romanization'])): ?>
                                <p class="text-gray-600 text-sm italic mb-4"><?php echo htmlspecialchars($row['romanization']); ?></p>
                            <?php endif; ?>
                            
                            <div class="space-y-3 flex-grow">
                                <div>
                                    <p class="text-sm font-medium text-gray-500">Translation</p>
                                    <p class="text-gray-800"><?php echo htmlspecialchars($row['translation']); ?></p>
                                </div>
                                
                                <?php if (!empty($row['phonetic'])): ?>
                                <div>
                                    <p class="text-sm font-medium text-gray-500">Phonetic</p>
                                    <p class="font-mono text-gray-700">/<?php echo htmlspecialchars($row['phonetic']); ?>/</p>
                                </div>
                                <?php endif; ?>
                                
                                <?php if (!empty($row['ipa'])): ?>
                                <div>
                                    <p class="text-sm font-medium text-gray-500">IPA</p>
                                    <p class="font-sans text-gray-700">[<?php echo htmlspecialchars($row['ipa']); ?>]</p>
                                </div>
                                <?php endif; ?>
                            </div>
                        </div>
                        
                        <?php if (isset($_SESSION["user_id"])): ?>
                            <div class="bg-gray-50 px-6 py-3 border-t border-gray-100 flex justify-end">
                                <a href="phrase_edit.php?phrase_id=<?php echo $row['phrase_id']; ?>&lang_id=<?php echo $lang_id; ?>" class="text-sm font-medium text-blue-600 hover:text-blue-800 flex items-center">
                                    <i class="fas fa-edit mr-1"></i>
                                    Edit
                                </a>
                            </div>
                        <?php endif; ?>
                    </div>
                <?php endwhile; ?>
            </div>
        <?php endif; ?>
        
        <?php if ($phrases_count > 0): ?>
        <div class="mt-12 text-center">
            <a href="#" class="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium">
                <span>Back to top</span>
                <i class="fas fa-arrow-up ml-2"></i>
            </a>
        </div>
        <?php endif; ?>
    </main>

    <?php include "footer.php"; ?>

    <script>
        function phraseSearch() {
            const searchTerm = document.getElementById("phraseSearch").value.toLowerCase();
            const phraseCards = document.querySelectorAll(".phrase-card");
            let visibleCount = 0;
            
            phraseCards.forEach(card => {
                const cardText = card.textContent.toLowerCase();
                if (cardText.includes(searchTerm)) {
                    card.style.display = "";
                    visibleCount++;
                    // Add animation class
                    card.classList.add("animate-fade-in");
                    // Remove the class after animation completes
                    setTimeout(() => card.classList.remove("animate-fade-in"), 600);
                } else {
                    card.style.display = "none";
                }
            });
            
            // Update results count
            const resultsText = document.getElementById("searchResults");
            if (resultsText) {
                if (searchTerm && visibleCount === 0) {
                    resultsText.textContent = `No phrases found matching '${searchTerm}'`;
                } else {
                    resultsText.textContent = `${visibleCount} phrase${visibleCount !== 1 ? 's' : ''} found`;
                }
            }
        }
        </script>
    </div>
</body>
</html>
