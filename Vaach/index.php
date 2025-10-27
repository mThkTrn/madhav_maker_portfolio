<?php
// Include header, navbar, and database connection
include "header.php";
include "navbar.php";
include "conn.php";

// Handle sorting
$sort = isset($_GET['sort']) ? $_GET['sort'] : 'recent';

// Base query
$base_query = "FROM languages 
               LEFT JOIN (SELECT lang_id, COUNT(*) as phrase_count FROM phrases GROUP BY lang_id) p 
               ON languages.lang_id = p.lang_id 
               WHERE approved = 1";

// Add sorting based on selection
switch($sort) {
    case 'name':
        $order_by = "ORDER BY lang_name ASC";
        break;
    case 'phrases':
        $order_by = "ORDER BY phrase_count DESC";
        break;
    default:
        $order_by = "ORDER BY timestamp DESC";
}

// Fetch approved languages from the database with sorting
$query = "SELECT languages.lang_id, lang_name, lang_place, lang_info, timestamp, COALESCE(phrase_count, 0) as phrase_count, lang_vitality 
          $base_query 
          $order_by";
$result = mysqli_query($conn, $query);

// Function to generate a consistent color from a string
function stringToColor($str) {
    $hash = md5($str);
    return [
        hexdec(substr($hash, 0, 2)),
        hexdec(substr($hash, 2, 2)),
        hexdec(substr($hash, 4, 2))
    ];
}

// Function to generate a mosaic pattern based on language name
function generateMosaic($name) {
    $hash = crc32($name);
    $colors = [];
    
    // Generate 3 base colors from the name
    for ($i = 0; $i < 3; $i++) {
        $r = ($hash >> ($i * 8)) & 0xFF;
        $g = ($hash >> (($i + 1) * 8)) & 0xFF;
        $b = ($hash >> (($i + 2) * 8)) & 0xFF;
        $colors[] = "rgb($r, $g, $b)";
    }
    
    // Create a 4x4 grid pattern
    $pattern = [];
    for ($i = 0; $i < 4; $i++) {
        $row = [];
        for ($j = 0; $j < 4; $j++) {
            $idx = ($i * 4 + $j + $hash) % 3; // Use hash to determine color index
            $row[] = $colors[$idx];
        }
        $pattern[] = $row;
    }
    
    return $pattern;
}
?>

<style>
    :root {
        --primary-blue: #1a56db;
        --secondary-blue: #3b82f6;
        --accent-yellow: #f59e0b;
        --light-yellow: #fef3c7;
        --dark-gray: #1f2937;
        --medium-gray: #6b7280;
        --light-gray: #f9fafb;
        --gradient-start: #1e40af;
        --gradient-end: #3b82f6;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    .hero-gradient {
        background: linear-gradient(135deg, var(--gradient-start) 0%, var(--gradient-end) 100%);
        position: relative;
        overflow: hidden;
    }

    .hero-gradient::before {
        content: '';
        position: absolute;
        width: 200%;
        height: 200%;
        top: -50%;
        left: -50%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        transform: rotate(30deg);
        animation: shine 15s infinite linear;
    }

    @keyframes shine {
        0% { transform: translateX(-100%) rotate(30deg); }
        100% { transform: translateX(100%) rotate(30deg); }
    }

    .language-card {
        transition: all 0.3s ease;
        border-radius: 12px;
        overflow: hidden;
        background: white;
        position: relative;
        z-index: 1;
    }

    .language-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-blue), var(--accent-yellow));
    }

    .language-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }

    .search-box {
        transition: all 0.3s ease;
        border: 2px solid transparent;
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }

    .search-box:focus {
        box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.3);
        border-color: var(--accent-yellow);
    }

    .btn-primary {
        background: var(--primary-blue);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        z-index: 1;
    }

    .btn-primary::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, var(--primary-blue), var(--secondary-blue));
        z-index: -1;
        transition: opacity 0.3s ease;
        opacity: 1;
    }

    .btn-primary:hover::after {
        opacity: 0.9;
    }

    .btn-secondary {
        background: var(--accent-yellow);
        color: #000;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
        z-index: 1;
    }

    .btn-secondary::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(45deg, #eab308, #f59e0b);
        z-index: -1;
        transition: opacity 0.3s ease;
        opacity: 1;
    }

    .btn-secondary:hover::after {
        opacity: 0.9;
    }

    .feature-card {
        transition: all 0.3s ease;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        position: relative;
        z-index: 1;
    }

    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    }

    .feature-icon {
        transition: all 0.3s ease;
    }

    .feature-card:hover .feature-icon {
        transform: scale(1.1);
    }

    .animate-float {
        animation: float 6s ease-in-out infinite;
    }

    .language-badge {
        background: linear-gradient(45deg, var(--primary-blue), var(--secondary-blue));
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
    }

    .language-image {
        height: 120px;
        width: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }

    .language-card:hover .language-image {
        transform: scale(1.05);
    }
</style>

<body class="bg-gray-50 font-sans antialiased">

    <!-- Hero Section -->
    <div class="hero-gradient text-white py-12 md:py-20 relative overflow-hidden">
        <div class="absolute inset-0 overflow-hidden">
            <div class="absolute -top-20 -left-20 w-64 h-64 bg-yellow-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
            <div class="absolute top-1/2 -right-20 w-72 h-72 bg-blue-400 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
            <div class="absolute -bottom-20 left-1/4 w-64 h-64 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
        </div>

        <div class="container mx-auto px-4 relative z-10">
            <div class="max-w-4xl mx-auto text-center">
                <h1 class="text-4xl md:text-5xl font-bold mb-4 leading-tight">
                    Welcome to <span class="text-yellow-300"><?php echo $name; ?></span>
                </h1>
                
                <p class="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
                    <?php echo $motto; ?>
                </p>
                
                <?php if (!isset($_SESSION['username'])): ?>
                <div class="flex flex-col sm:flex-row justify-center gap-4 mb-8">
                    <a href="login.php" class="btn-primary text-white font-semibold py-3 px-8 rounded-full shadow-lg hover:shadow-xl text-lg transform transition-all duration-300 hover:scale-105">
                        Get Started
                    </a>
                    <a href="register.php" class="btn-secondary font-semibold py-3 px-8 rounded-full shadow-lg hover:shadow-xl text-lg transform transition-all duration-300 hover:scale-105">
                        Create Account
                    </a>
                </div>
                <?php else: ?>
                <p class="text-lg text-blue-100 mb-6">Welcome back, <span class="font-semibold text-yellow-300"><?php echo $_SESSION['username']; ?></span>!</p>
                <?php endif; ?>
            </div>
        </div>
    </div>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-16 md:py-24">
        <!-- Languages Section -->
        <section class="mb-24">
            <div class="text-center mb-16">
                <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
                    Explore <span class="text-blue-600">Languages</span>
                </h2>
                <div class="w-24 h-1.5 bg-yellow-400 mx-auto mb-6 rounded-full"></div>
                <p class="text-gray-600 text-lg max-w-2xl mx-auto">
                    Discover and contribute to our growing collection of world languages. Each language tells a unique story.
                </p>
            </div>
            
            <!-- Search and Sort -->
            <div class="bg-white rounded-lg shadow-sm p-6 mb-8">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                    <!-- Search Bar -->
                    <div class="flex-1 max-w-2xl">
                        <div class="relative">
                            <input 
                                type="text" 
                                id="langSearch" 
                                placeholder="Search for a language..." 
                                class="w-full py-2.5 px-5 pr-10 rounded-full border border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                                onkeyup="langSearch()"
                            >
                            <div class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                                </svg>
                            </div>
                        </div>
                        <p id="disclaimer" class="mt-2 text-sm text-gray-500"></p>
                    </div>
                    
                    <!-- Sort Options -->
                    <div class="flex flex-col sm:flex-row sm:items-center gap-3">
                        <div class="flex items-center">
                            <span class="text-sm text-gray-600 mr-2">Sort by:</span>
                            <div class="relative">
                                <select id="sortSelect" onchange="window.location.href='?sort='+this.value" class="appearance-none bg-white border border-gray-200 rounded-full pl-3 pr-8 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200">
                                    <option value="recent" <?php echo ($sort === 'recent') ? 'selected' : ''; ?>>Most Recent</option>
                                    <option value="name" <?php echo ($sort === 'name') ? 'selected' : ''; ?>>Alphabetical (A-Z)</option>
                                    <option value="phrases" <?php echo ($sort === 'phrases') ? 'selected' : ''; ?>>Number of Phrases</option>
                                </select>
                                <div class="absolute right-2 top-1/2 transform -translate-y-1/2 pointer-events-none">
                                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                                    </svg>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <?php if (mysqli_num_rows($result) > 0): ?>
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8" id="languagesContainer">
                    <?php 
                    // Reset the result pointer to the beginning
                    mysqli_data_seek($result, 0);
                    $count = 0;
                    while ($row = mysqli_fetch_assoc($result)): 
                        $count++;
                        $animationDelay = ($count % 3) * 100; // Staggered animation delay
                    ?>
                        <div class="language-card hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1" 
                             style="animation-delay: <?php echo $animationDelay; ?>ms"
                             id="lang_<?php echo $row["lang_name"]; ?>">
                            <!-- Language Mosaic -->
                            <div class="h-48 bg-gray-100 overflow-hidden relative">
                                <?php 
                                $langName = isset($row['lang_name']) ? $row['lang_name'] : '';
                                $mosaic = generateMosaic($langName);
                                ?>
                                <div class="absolute inset-0 grid grid-cols-4 grid-rows-4 w-full h-full">
                                    <?php foreach ($mosaic as $i => $mosaicRow): ?>
                                        <?php foreach ($mosaicRow as $j => $color): ?>
                                            <div 
                                                class="transition-all duration-300 hover:opacity-75" 
                                                style="background-color: <?php echo htmlspecialchars($color); ?>;"
                                            ></div>
                                        <?php endforeach; ?>
                                    <?php endforeach; ?>
                                </div>
                                <div class="absolute inset-0 bg-black bg-opacity-10 hover:bg-opacity-0 transition-all duration-300"></div>
                            </div>
                            
                            <div class="p-6">
                                <div class="flex justify-between items-start mb-3">
                                    <div>
                                        <h3 class="text-xl font-bold text-gray-900">
                                            <?php echo isset($row['lang_name']) ? htmlspecialchars($row['lang_name']) : 'Unknown Language'; ?>
                                        </h3>
                                        <?php if (!empty($row['lang_vitality'])): 
                                            $vitality = str_replace("_", " ", ucfirst($row['lang_vitality']));
                                            $vitality_class = [
                                                'Vital' => 'bg-green-100 text-green-800',
                                                'Endangered' => 'bg-yellow-100 text-yellow-800',
                                                'Extinct' => 'bg-red-100 text-red-800',
                                                'Dormant' => 'bg-gray-100 text-gray-800',
                                                'Revitalization' => 'bg-blue-100 text-blue-800'
                                            ][$vitality] ?? 'bg-gray-100 text-gray-800';
                                        ?>
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 <?php echo $vitality_class; ?>">
                                            <?php echo $vitality; ?>
                                        </span>
                                        <?php endif; ?>
                                    </div>
                                    <span class="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                                        <?php echo !empty($row['lang_place']) ? htmlspecialchars($row['lang_place']) : 'Global'; ?>
                                    </span>
                                </div>
                                
                                <?php if (!empty($row['lang_info'])): ?>
                                    <p class="text-gray-600 mb-6 line-clamp-3 leading-relaxed">
                                        <?php echo htmlspecialchars(substr($row['lang_info'], 0, 120)); ?>
                                        <?php echo strlen($row['lang_info']) > 120 ? '...' : ''; ?>
                                    </p>
                                <?php else: ?>
                                    <p class="text-gray-400 mb-6 italic">No description available</p>
                                <?php endif; ?>
                                
                                <div class="flex justify-between items-center pt-4 border-t border-gray-100">
                                    <div class="flex items-center text-sm text-gray-500">
                                    </div>
                                    <a href="language.php?id=<?php echo $row['lang_id']; ?>" class="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium group transition-colors">
                                        <span class="mr-1">Explore</span>
                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 transform group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                        </svg>
                                    </a>
                                </div>
                            </div>
                        </div>
                    <?php endwhile; ?>
                </div>
                
                <!-- Pagination -->
                <div class="mt-12 flex justify-center">
                    <nav class="inline-flex rounded-md shadow-sm" aria-label="Pagination">
                        <a href="#" class="relative inline-flex items-center px-4 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                            <span class="sr-only">Previous</span>
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                            </svg>
                        </a>
                        <a href="#" aria-current="page" class="relative z-10 bg-blue-50 border-blue-500 text-blue-600 relative inline-flex items-center px-4 py-2 border text-sm font-medium">1</a>
                        <a href="#" class="bg-white border-gray-300 text-gray-500 hover:bg-gray-50 relative inline-flex items-center px-4 py-2 border text-sm font-medium">2</a>
                        <a href="#" class="bg-white border-gray-300 text-gray-500 hover:bg-gray-50 relative inline-flex items-center px-4 py-2 border text-sm font-medium">3</a>
                        <a href="#" class="relative inline-flex items-center px-4 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
                            <span class="sr-only">Next</span>
                            <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                                <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                            </svg>
                        </a>
                    </nav>
                </div>
                
            <?php else: ?>
                <div class="text-center py-16 bg-white rounded-xl shadow-sm">
                    <div class="w-20 h-20 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>
                    <h3 class="text-xl font-semibold text-gray-900 mb-2">No languages found</h3>
                    <p class="text-gray-600 max-w-md mx-auto mb-6">We couldn't find any languages matching your search. Check back later or contribute by adding a new language.</p>
                    <a href="language_request.php" class="inline-flex items-center px-6 py-2.5 border border-transparent text-sm font-medium rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                        </svg>
                        Request a Language
                    </a>
                </div>
            <?php endif; ?>
        </section>

    </main>


    <?php include "footer.php"; ?>

    <style>
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        
        .animate-fade-in-up {
            animation: fadeInUp 0.6s ease-out forwards;
        }
        
        .animate-float {
            animation: float 6s ease-in-out infinite;
        }
        
        .animation-delay-100 { animation-delay: 0.1s; }
        .animation-delay-200 { animation-delay: 0.2s; }
        .animation-delay-300 { animation-delay: 0.3s; }
        
        .hover-scale {
            transition: transform 0.3s ease;
        }
        
        .hover-scale:hover {
            transform: scale(1.02);
        }
        
        /* Smooth scroll behavior */
        html {
            scroll-behavior: smooth;
        }
    </style>

    <script>
        // Add animation classes on scroll
        document.addEventListener('DOMContentLoaded', function() {
            // Animate elements with the 'animate-on-scroll' class when they come into view
            const animateOnScroll = function() {
                const elements = document.querySelectorAll('.animate-on-scroll');
                
                elements.forEach(element => {
                    const elementTop = element.getBoundingClientRect().top;
                    const windowHeight = window.innerHeight;
                    
                    if (elementTop < windowHeight - 100) {
                        element.classList.add('animate-fade-in-up');
                    }
                });
            };
            
            // Run once on page load
            animateOnScroll();
            
            // Run on scroll
            window.addEventListener('scroll', animateOnScroll);
            
            // Search functionality
            function langSearch() {
                let input = document.getElementById('langSearch');
                let filter = input.value.toLowerCase();
                let cards = document.getElementsByClassName('langcard');
                let noResults = true;
                
                for (let i = 0; i < cards.length; i++) {
                    let cardTitle = cards[i].querySelector('h3').textContent.toLowerCase();
                    if (cardTitle.indexOf(filter) > -1) {
                        cards[i].style.display = '';
                        noResults = false;
                    } else {
                        cards[i].style.display = 'none';
                    }
                }
                
                let disclaimer = document.getElementById('disclaimer');
                if (noResults && filter.length > 0) {
                    disclaimer.textContent = 'No matching languages found. Try a different search term.';
                } else if (filter.length > 0) {
                    disclaimer.textContent = 'Showing results for: ' + filter;
                } else {
                    disclaimer.textContent = '';
                }
            }
            
            // Initialize tooltips
            const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        });
    </script>
    <script>
        function langSearch() {
            const searchTerm = document.getElementById('langSearch').value.toLowerCase();
            const languageCards = document.querySelectorAll('.language-card');
            let hasResults = false;

            languageCards.forEach(card => {
                const langName = card.id.replace('lang_', '').toLowerCase();
                const langPlace = card.querySelector('span').textContent.toLowerCase();
                
                if (langName.includes(searchTerm) || langPlace.includes(searchTerm)) {
                    card.style.display = 'block';
                    hasResults = true;
                } else {
                    card.style.display = 'none';
                }
            });

            const disclaimer = document.getElementById('disclaimer');
            if (!hasResults && searchTerm.length > 0) {
                disclaimer.textContent = `No languages found matching "${searchTerm}"`;
            } else if (searchTerm.length === 0) {
                disclaimer.textContent = '';
                languageCards.forEach(card => card.style.display = 'block');
            } else {
                disclaimer.textContent = '';
            }
        }

        // Add animation on scroll
        document.addEventListener('DOMContentLoaded', () => {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('animate-fadeIn');
                    }
                });
            }, { threshold: 0.1 });

            document.querySelectorAll('.language-card').forEach(card => {
                observer.observe(card);
            });
        });
    </script>
</body>
</html>
