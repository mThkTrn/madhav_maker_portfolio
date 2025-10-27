<head>

    <style>
        .logo {
            height: 3rem;
        }
    </style>
</head>
<body>
    <nav class="bg-gray-900 text-white shadow-md w-full flex items-center justify-between px-4 py-2">
        <a href="index.php">
            <img src="images/vaach_logo_dark_no_bg.png" class="logo" alt="Vaach Logo"/>
        </a>
        <button id="navbar-toggle" class="lg:hidden p-2 border border-gray-700 rounded text-gray-300 hover:text-white hover:border-white focus:outline-none focus:border-white focus:ring focus:ring-gray-600 focus:ring-opacity-50">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
            </svg>
        </button>
        <div id="navbar-collapse" class="hidden lg:flex lg:items-center lg:space-x-6">
            <a href="index.php" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">Home</a>
            <a href="translation.php" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">Translator</a>
            <a href="https://chatgpt.com/g/g-6776f1d3c2648191b92c2b586c78acfc-vaach-org-translator" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">Converse</a>
            <?php if (isset($_SESSION['username'])): ?>
                <a href="language_request.php" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">Add a Language</a>
                <?php if (in_array("admin", $_SESSION["tags"]) || in_array("superadmin", $_SESSION["tags"])): ?>
                    <a href="admin_panel.php" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">Admin Panel</a>
                <?php endif; ?>
                <a href="users.php" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">My Account</a>
                <a href="logout.php" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">Logout</a>
            <?php else: ?>
                <a href="login.php" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">Login</a>
                <a href="register.php" class="text-gray-300 hover:text-white transition-colors duration-200 text-sm">Register</a>
            <?php endif; ?>
        </div>
    </nav>

    <!-- Mobile Menu -->
    <div id="mobile-menu" class="lg:hidden fixed inset-0 bg-gray-800 bg-opacity-75 z-50 hidden">
        <div class="flex justify-end p-4">
            <button id="close-menu" class="text-white text-3xl">&times;</button>
        </div>
        <div class="flex flex-col items-center">
            <a href="index.php" class="text-white text-lg py-2">Home</a>
            <a href="translation.php" class="text-white text-lg py-2">Translator</a>
            <a href="https://chatgpt.com/g/g-6776f1d3c2648191b92c2b586c78acfc-vaach-org-translator" class="text-white text-lg py-2">Converse</a>
            <?php if (isset($_SESSION['username'])): ?>
                <a href="language_request.php" class="text-white text-lg py-2">Add a Language</a>
                <?php if (in_array("admin", $_SESSION["tags"]) || in_array("superadmin", $_SESSION["tags"])): ?>
                    <a href="admin_panel.php" class="text-white text-lg py-2">Admin Panel</a>
                <?php endif; ?>
                <a href="users.php" class="text-white text-lg py-2">My Account</a>
                <a href="logout.php" class="text-white text-lg py-2">Logout</a>
            <?php else: ?>
                <a href="login.php" class="text-white text-lg py-2">Login</a>
                <a href="register.php" class="text-white text-lg py-2">Register</a>
            <?php endif; ?>
        </div>
    </div>

    <script>
        document.getElementById('navbar-toggle').addEventListener('click', function() {
            document.getElementById('mobile-menu').classList.toggle('hidden');
        });

        document.getElementById('close-menu').addEventListener('click', function() {
            document.getElementById('mobile-menu').classList.add('hidden');
        });
    </script>
</body>
