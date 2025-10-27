<!-- Refined Tailwind CSS Footer -->
<footer class="bg-gray-900 text-gray-400 w-full">
    <div class="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div class="md:col-span-2">
                <h3 class="text-white text-lg font-semibold mb-4"><?php echo $name; ?></h3>
                <p class="text-sm"><?php echo $motto; ?></p>
                <p class="text-xs mt-4">© Madhavendra Thakur, <?php echo date("Y"); ?> | New York, NY</p>
            </div>
            
            <div>
                <h4 class="text-white text-sm font-semibold uppercase tracking-wider mb-4">Legal</h4>
                <ul class="space-y-2">
                    <li><a href="terms.php" class="text-sm hover:text-white transition-colors">Terms of Service</a></li>
                    <li><a href="privacy.php" class="text-sm hover:text-white transition-colors">Privacy Policy</a></li>
                    <li><a href="guidelines.php" class="text-sm hover:text-white transition-colors">Community Guidelines</a></li>
                </ul>
            </div>
            
            <div>
                <h4 class="text-white text-sm font-semibold uppercase tracking-wider mb-4">Quick Links</h4>
                <ul class="space-y-2">
                    <li><a href="index.php" class="text-sm hover:text-white transition-colors">Home</a></li>
                    <li><a href="language_request.php" class="text-sm hover:text-white transition-colors">Request Language</a></li>
                    <?php if (isset($_SESSION["user_id"])): ?>
                        <li><a href="users.php" class="text-sm hover:text-white transition-colors">My Profile</a></li>
                        <?php if (isset($_SESSION["is_admin"]) && $_SESSION["is_admin"]): ?>
                            <li><a href="admin/" class="text-sm hover:text-white transition-colors">Admin Panel</a></li>
                        <?php endif; ?>
                    <?php else: ?>
                        <li><a href="login.php" class="text-sm hover:text-white transition-colors">Login / Register</a></li>
                    <?php endif; ?>
                </ul>
            </div>
        </div>
        
        <div class="mt-8 pt-8 border-t border-gray-800 text-center text-sm">
            <p>Vaach is dedicated to preserving and sharing the world's languages and cultures.</p>
        </div>
    </div>
</footer>
