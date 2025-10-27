<?php
include "header.php";
include "conn.php";
include "navbar.php";

// Ensure user is logged in
if (!isset($_SESSION['username'])) {
    header("Location: login.php");
    exit;
}

// Get username from session
$username = $_SESSION['username'];

// Fetch user information
$user_query = "SELECT * FROM users WHERE username = '$username'";
$user_result = mysqli_query($conn, $user_query);
$user = mysqli_fetch_assoc($user_result);

// Fetch notifications for the user
$notifications_query = "SELECT * FROM notifications WHERE user_id = " . $user['user_id'] . " ORDER BY notif_id DESC";
$notifications_result = mysqli_query($conn, $notifications_query);

// Process tags from session to display language roles and general admin/superadmin
$language_roles = array();
foreach ($_SESSION['tags'] as $tag) {
    if (in_array($tag, ['admin', 'superadmin'])) {
        // General admin/superadmin
        $role = strtolower($tag);

        $language_roles[-1] = array(
            "name" => "Site",
            "role" => $role
        );
    } else if ($tag){
        $parts = explode('_', $tag);
        $lang_id = $parts[0];
        $role = $parts[1];

        if ($role == "sa"){
            $role = "superadmin";
        } else if ($role == "a"){
            $role = "admin";
        }

        // Get language name from ID
        $lang_name_query = "SELECT lang_name FROM languages WHERE lang_id = $lang_id";
        $lang_name_result = mysqli_query($conn, $lang_name_query);
        $lang_name_row = mysqli_fetch_assoc($lang_name_result);
        $lang_name = $lang_name_row['lang_name'];

        $language_roles[$lang_id] = array(
            "name" => $lang_name,
            "role" => $role
        );
    }
}

// Show tutorial modal if intro parameter is true
if (isset($_GET["intro"]) && $_GET["intro"] == "true") {
    echo '<div id="tutorialModal" class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
        <div class="bg-white p-6 rounded-lg shadow-sm max-w-lg w-full relative">
            <div class="flex justify-between items-center border-b pb-3">
                <h5 class="text-xl font-semibold">Site Tutorial</h5>
                <button class="text-gray-500 hover:text-gray-700" onclick="closeModal()">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>
            </div>
            <div class="py-4">
                <p>Welcome to our site!<br><br>
                Now that you have your account set up, you can get started by <a href="index.php" class="text-blue-500 hover:underline">browsing languages</a> or <a href="language_request.php" class="text-blue-500 hover:underline">creating your own language</a>!<br><br>
                If you would like to contribute a phrase to a language, it’s as easy as going to the language page and submitting a request. Once the phrase is approved by an admin, you will get a notification in your notification section, and it will be added to the language. If you would like to edit a phrase, simply click the edit icon on the right-hand side of the phrase.<br><br>
                Once you have submitted 5 approved phrases to a language, congrats! You’re now an admin. This means that you can approve phrase submissions by accessing the admin portal found on the language page.<br><br>
                Enjoy our site, and we hope you join us in our journey towards a more linguistically inclusive world.
                </p>
            </div>
            <div class="flex justify-end pt-3 border-t">
                <button class="bg-blue-500 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-600" onclick="closeModal()">Got it!</button>
            </div>
        </div>
    </div>';
}
?>

<div class="min-h-screen flex flex-col">
    <main class="flex-grow container mx-auto p-6 bg-white rounded-lg shadow-sm">
        <h2 class="text-3xl font-bold mb-4">Welcome, <?php echo htmlspecialchars($user['username']); ?>!</h2>

        <div class="bg-white p-8 rounded-lg shadow-sm mb-6 border border-gray-100">
            <h3 class="text-xl font-semibold mb-2">User Information</h3>
            <ul class="space-y-2">
                <li class="p-3 border-b border-gray-200"><strong class="font-medium">Username:</strong> <?php echo htmlspecialchars($user['username']); ?></li>
                <li class="p-3 border-b border-gray-200">
                    <strong class="font-medium">Language Roles:</strong>
                    <ul class="list-disc list-inside mt-2">
                        <?php foreach ($language_roles as $lang_id => $role_info): ?>
                            <li>
                                <?php if ($lang_id): ?>
                                    <?php echo "{$role_info['name']} "; ?>
                                <?php endif; ?>
                                <?php echo ucfirst($role_info['role']); ?>
                            </li>
                        <?php endforeach; ?>
                    </ul>
                </li>
            </ul>
        </div>

        <a href="users.php?intro=true" class="inline-block bg-blue-500 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-600 mb-6">Site Tutorial</a>

        <h3 class="text-xl font-semibold mb-2">Notifications</h3>

        <?php if (mysqli_num_rows($notifications_result) > 0): ?>
            <ul class="space-y-2">
                <?php while ($notification = mysqli_fetch_assoc($notifications_result)): ?>
                    <li class="bg-<?php echo $notification['notif_type'] == 'success' ? 'green' : 'red'; ?>-100 text-<?php echo $notification['notif_type'] == 'success' ? 'green' : 'red'; ?>-700 p-3 rounded-lg shadow-sm">
                        <?php echo htmlspecialchars($notification['notif_text']); ?>
                    </li>
                <?php endwhile; ?>
            </ul>
        <?php else: ?>
            <p class="text-gray-600">You currently have no notifications.</p>
        <?php endif; ?>
    </main>

    <?php include "footer.php"; ?>
</div>

<?php mysqli_close($conn); ?>

<script>
    function closeModal() {
        document.getElementById('tutorialModal').style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    document.addEventListener('DOMContentLoaded', function() {
        if (window.location.search.includes('intro=true')) {
            document.getElementById('tutorialModal').style.display = 'flex';
            document.body.style.overflow = 'hidden'; // Prevent scrolling when modal is open
        }
    });
</script>
