<?php
// Include header, navbar, and database connection
include "header.php";
include "navbar.php";
include "conn.php";

// Fetch approved languages from the database
$query = "SELECT lang_id, lang_name, lang_place FROM languages WHERE approved = 1";
$result = mysqli_query($conn, $query);
?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vaach</title>
    <style>
        /* Custom Tailwind styles */
        .bg-yellow-custom {
            background-color: #F7E5A4; /* Light yellow color */
        }
        .bg-blue-custom {
            background-color: #007BFF; /* Bright blue */
        }
        .shadow-lg-custom {
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
        }
        .text-blue-custom {
            color: #007BFF; /* Bright blue text */
        }
    </style>
</head>
<body class="bg-gray-50 font-sans">


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

<div class="p-8">
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
