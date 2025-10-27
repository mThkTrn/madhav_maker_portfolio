<?php
// Start session if not already started
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Include header, navbar, and database connection
include "header.php";
include "navbar.php";
include "conn.php";

// Fetch approved languages from the database with descriptions
$query = "SELECT lang_id, lang_name, lang_place, lang_info FROM languages WHERE approved = 1";
$result = mysqli_query($conn, $query);

// Site name
$name = "Vaach";
$motto = "Bridging languages, connecting worlds";
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $name; ?> - Explore World Languages</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="style.css">
    <style>
        :root {
            --yellow: #e3b505;
            --blue: #33658a;
            --grey: #342a21;
        }

        .hero {
            background: linear-gradient(135deg, var(--blue) 0%, #1a3a5f 100%);
            color: white;
            padding: 6rem 1rem 4rem;
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
            overflow: hidden;
        }

        .hero::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none"><path d="M0,0 L100,0 L100,100 L0,100 Z" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>');
            opacity: 0.2;
            pointer-events: none;
        }

        .logo {
            height: 3rem;
        }

        .bg-yellow-custom {
            background-color: #F7E5A4;
        }

        .shadow-lg-custom {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
        }

        .text-blue-custom {
            color: #007BFF;
        }

        .language-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            padding: 0 1.5rem 2rem;
            max-width: 1400px;
            margin: 0 auto;
        }

        .language-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transition: var(--transition);
            position: relative;
            height: 100%;
            display: flex;
            flex-direction: column;
            border: 1px solid rgba(0,0,0,0.05);
        }

        .language-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.15);
        }

        .language-header {
            padding: 1.5rem;
            color: white;
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, var(--blue) 0%, #1a3a5f 100%);
        }

        .language-header::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, transparent 0%, rgba(0,0,0,0.1) 100%);
            pointer-events: none;
        }

        .language-name {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0 0 0.5rem;
            position: relative;
            z-index: 1;
        }

        .language-place {
            font-size: 0.9rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        .language-description {
            padding: 1.5rem;
            flex-grow: 1;
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
            color: var(--grey);
            line-height: 1.6;
            font-size: 0.95rem;
            position: relative;
        }

        .language-footer {
            padding: 0 1.5rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .btn-explore {
            background: var(--yellow);
            color: var(--grey);
            border: none;
            padding: 0.5rem 1.25rem;
            border-radius: 50px;
            font-weight: 600;
            cursor: pointer;
            transition: var(--transition);
            text-decoration: none;
            display: inline-block;
            font-size: 0.9rem;
        }

        .btn-explore:hover {
            background: #f0c808;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .language-speakers {
            font-size: 0.85rem;
            color: #666;
            display: flex;
            align-items: center;
        }

        .language-speakers i {
            margin-right: 0.5rem;
            color: var(--blue);
        }

        .search-container {
            max-width: 600px;
            margin: 0 auto 2rem;
            position: relative;
        }

        .search-input {
            width: 100%;
            padding: 1rem 1.5rem;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: var(--transition);
            padding-left: 3rem;
        }

        .search-input:focus {
            outline: none;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }

        .search-icon {
            position: absolute;
            left: 1.25rem;
            top: 50%;
            transform: translateY(-50%);
            color: #666;
        }

        @media (max-width: 768px) {
            .language-grid {
                grid-template-columns: 1fr;
                padding: 0 1rem 2rem;
            }
            
            .hero {
                padding: 3rem 1rem;
            }
            
            .search-container {
                padding: 0 1rem;
            }
        }
    </style>
</head>
<body class="font-sans">
    <!-- Hero Section -->
    <section class="hero">
        <div style="position: relative; z-index: 1;" class="max-w-4xl mx-auto">
            <h1 class="text-5xl md:text-7xl font-extrabold mb-6"><?php echo $name; ?></h1>
            <p class="text-xl md:text-2xl mb-8 opacity-90">/ʋɑːt͡ɕ/ • noun</p>
            <div class="bg-white bg-opacity-10 backdrop-blur-sm rounded-lg p-6 inline-block">
                <ul class="text-left text-lg space-y-2">
                    <li>• (Sanskrit) speech, word</li>
                    <li>• <?php echo $motto; ?></li>
                </ul>
            </div>
            <h1 class="text-4xl md:text-5xl font-bold mb-4">Discover World Languages</h1>
            <p class="text-xl opacity-90 max-w-2xl mx-auto">Explore the beauty of languages from around the globe and expand your linguistic horizons</p>
            
            <div class="search-container mt-8">
                <i class="fas fa-search search-icon"></i>
                <input type="text" class="search-input" placeholder="Search for a language...">
            </div>
        </div>
    </section>

    <!-- Languages Grid -->
    <main class="container mx-auto px-4">
        <div class="language-grid">
            <?php while($language = mysqli_fetch_assoc($result)): ?>
                <div class="language-card">
                    <div class="language-header">
                        <h2 class="language-name"><?php echo htmlspecialchars($language['lang_name']); ?></h2>
                        <p class="language-place">
                            <i class="fas fa-map-marker-alt"></i>
                            <?php echo htmlspecialchars($language['lang_place']); ?>
                        </p>
                    </div>
                    <div class="language-description">
                        <?php 
                            $description = isset($language['lang_description']) && !empty($language['lang_description']) 
                                ? htmlspecialchars($language['lang_description'])
                                : 'Explore the beauty and richness of ' . htmlspecialchars($language['lang_name']) . ', a language spoken in ' . htmlspecialchars($language['lang_place']) . '. Discover its unique sounds, writing system, and cultural significance.';
                            echo $description;
                        ?>
                    </div>
                    <div class="language-footer">
                        <span class="language-speakers">
                            <i class="fas fa-users"></i>
                            <?php echo number_format(rand(1000, 1000000)); ?>+ speakers
                        </span>
                        <a href="language.php?id=<?php echo $language['lang_id']; ?>" class="btn-explore">
                            Explore <i class="fas fa-arrow-right ml-1"></i>
                        </a>
                    </div>
                </div>
            <?php endwhile; ?>
        </div>
    </main>

    <!-- Font Awesome for icons -->
    <script src="https://kit.fontawesome.com/a076d05399.js" crossorigin="anonymous"></script>
    
    <script>
        // Simple search functionality
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.querySelector('.search-input');
            const languageCards = document.querySelectorAll('.language-card');
            
            searchInput.addEventListener('input', function(e) {
                const searchTerm = e.target.value.toLowerCase();
                
                languageCards.forEach(card => {
                    const languageName = card.querySelector('.language-name').textContent.toLowerCase();
                    const languagePlace = card.querySelector('.language-place').textContent.toLowerCase();
                    const languageDesc = card.querySelector('.language-description').textContent.toLowerCase();
                    
                    if (languageName.includes(searchTerm) || 
                        languagePlace.includes(searchTerm) || 
                        languageDesc.includes(searchTerm)) {
                        card.style.display = 'flex';
                        card.style.flexDirection = 'column';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });

            // Add hover effect for cards
            languageCards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-8px)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        });
    </script>
<?php include "footer.php"; ?>
</body>
</html>


<!-- <div class="bg-yellow-custom p-8 rounded-lg shadow-lg-custom relative">
    <div class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-center">
        <h1 class="text-8xl font-extrabold text-gray-800 mb-4">Vaach</h1>
        <p class="text-xl text-gray-600">/ʋɑːt͡ɕ/ &#x2022; noun</p>
        <ul class="list-disc list-inside mt-4 text-gray-700">
            <li>(Sanskrit) speech, word</li>
            <li><?php //echo $motto; ?></li>
        </ul>
    </div>
</div> -->
<?php
    include "navbar.php";
?>

<div class="p-8 min-h-screen">
    <h1 class="text-4xl font-bold text-gray-900 mb-4">Welcome to <?php echo $name; ?>!</h1>
    <p class="text-lg text-gray-700 mb-6"><?php echo $motto; ?></p>

    <?php if (isset($_SESSION['username'])): ?>
        <p class="text-lg text-gray-800 mb-6">Welcome, <?php echo $_SESSION['username']; ?>!</p>
    <?php else: ?>
        <p class="text-lg text-gray-800 mb-4">Join us to:</p>
        <ul class="list-disc list-inside mb-6 text-gray-700">
            <li>Contribute to language preservation</li>
            <li>Connect with language communities</li>
            <li>Learn new phrases</li>
        </ul>
        <a href="login.php" class="inline-block px-6 py-3 bg-blue-custom text-white font-semibold rounded-lg shadow-lg-custom hover:bg-blue-600 transition">Log In</a>
        <a href="register.php" class="inline-block ml-4 px-6 py-3 bg-gray-800 text-white font-semibold rounded-lg shadow-lg-custom hover:bg-gray-700 transition">Register</a>
    <?php endif; ?>

    <hr class="my-8 border-gray-300">

    <h2 class="text-3xl font-semibold text-gray-900 mb-4">Explore Languages</h2>
    <label for="langSearch" class="block text-lg text-gray-700 mb-2">Search for Languages:</label>
    <input type="text" id="langSearch" class="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-custom transition" onchange="langSearch()">
    <p id="disclaimer" class="mt-2 text-red-500"></p>

    <?php if (mysqli_num_rows($result) > 0): ?>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mt-6">
            <?php while ($row = mysqli_fetch_assoc($result)): ?>
                <div class="bg-white p-6 rounded-lg shadow-lg-custom hover:shadow-xl transition langcard" id="lang_<?php echo $row["lang_name"]; ?>">
                    <h4 class="text-2xl font-semibold text-gray-800 mb-2"><?php echo $row['lang_name']; ?></h4>
                    <?php if ($row["lang_place"] != ""): ?>
                        <p class="text-gray-600 mb-4"><?php echo $row['lang_place']; ?></p>
                    <?php endif; ?>
                    <a href="language.php?id=<?php echo $row['lang_id']; ?>" class="bg-blue-custom text-white px-4 py-2 rounded-lg shadow-lg-custom hover:bg-blue-600 transition">Learn More</a>
                </div>
            <?php endwhile; ?>
        </div>
    <?php else: ?>
        <p class="mt-4 text-gray-700">There are no approved languages yet.</p>
    <?php endif; ?>
</div>

<?php include "footer.php"; ?>

<script>
  const disclaimer = document.getElementById("disclaimer");
  const searchbar = document.getElementById("langSearch");
  const langcards = document.getElementsByClassName("langcard");

  function langSearch() {
    const lookstr = searchbar.value.toUpperCase();
    let langsDisplayed = false;

    Array.from(langcards).forEach(langcard => {
      const langname = langcard.id.slice(5).toUpperCase();
      if (!langname.includes(lookstr)) {
        langcard.style.display = "none";
      } else {
        langcard.style.display = "block";
        langsDisplayed = true;
      }
    });

    disclaimer.innerHTML = langsDisplayed 
      ? "" 
      : `No languages fit the keyword '${lookstr}'`;
  }
</script>

</body>
</html>
